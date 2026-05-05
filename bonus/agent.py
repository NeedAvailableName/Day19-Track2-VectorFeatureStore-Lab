import uuid
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from fastembed import TextEmbedding
from feast import FeatureStore

class HybridMemoryAgent:
    def __init__(self, feast_repo_path: str = "app/feast_repo"):
        # Initialize Qdrant (in-memory for POC)
        self.qdrant = QdrantClient(":memory:")
        self.collection_name = "episodic_memory"
        
        # Initialize Embedding Model
        self.embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        
        self.qdrant.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
        
        # Resolve path
        repo_path = Path(feast_repo_path).resolve()
        
        # Initialize Feast Feature Store
        self.fs = FeatureStore(repo_path=str(repo_path))
        
        self.request_features = [
            "user_profile_features:reading_speed_wpm",
            "user_profile_features:preferred_language",
            "user_profile_features:topic_affinity",
            "query_velocity_features:queries_last_hour",
            "query_velocity_features:distinct_topics_24h",
        ]

    def remember(self, text: str, user_id: str = "u_001") -> None:
        """Add a new piece of episodic memory for this user."""
        # Embed the text. prefixing with 'passage: ' is recommended for e5 models, 
        # but for simplicity we will just embed the text as is or follow fastembed defaults.
        embeddings = list(self.embedding_model.embed([text]))
        vector = embeddings[0].tolist()
        
        # Store in Qdrant with user_id payload
        point_id = str(uuid.uuid4())
        self.qdrant.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={"user_id": user_id, "text": text}
                )
            ]
        )

    def recall(self, query: str, user_id: str = "u_001") -> str:
        """Retrieve top-K memories + user profile features → return assembled context."""
        # 1. Get user profile + recent activity from Feast online store
        feature_dict = {}
        try:
            features = self.fs.get_online_features(
                features=self.request_features,
                entity_rows=[{"user_id": user_id}],
            ).to_dict()
            feature_dict = {k: v[0] for k, v in features.items()}
        except Exception as e:
            feature_dict = {"error": f"Could not load features: {e}"}

        # 2. Hybrid search Qdrant filtered by user_id
        # For e5 models query should ideally be prefixed with 'query: ', but fastembed might handle it
        # or we just embed it directly
        query_vector = list(self.embedding_model.embed([query]))[0].tolist()
        
        search_result = self.qdrant.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=user_id)
                    )
                ]
            ),
            limit=3
        ).points
        
        memories = [hit.payload.get("text", "") for hit in search_result]
        memories_str = "\n".join([f"- {m}" for m in memories]) if memories else "- No relevant memories found."
        
        # 3. Assemble context string
        context = (
            f"[User Profile Context]\n"
            f"User likes: {feature_dict.get('topic_affinity', 'Unknown')}\n"
            f"Reading Speed: {feature_dict.get('reading_speed_wpm', 'Unknown')} wpm\n"
            f"Preferred Language: {feature_dict.get('preferred_language', 'Unknown')}\n"
            f"\n"
            f"[Recent Activity Context]\n"
            f"Queries Last Hour: {feature_dict.get('queries_last_hour', 'Unknown')}\n"
            f"Distinct Topics 24h: {feature_dict.get('distinct_topics_24h', 'Unknown')}\n"
            f"\n"
            f"[Episodic Memory (Top matches for '{query}')]\n"
            f"{memories_str}"
        )
        return context
