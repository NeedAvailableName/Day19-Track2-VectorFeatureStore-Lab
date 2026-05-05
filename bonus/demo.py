import sys
from pathlib import Path

# Add parent dir to path to allow importing from bonus module
sys.path.append(str(Path(__file__).parent.parent))

from bonus.agent import HybridMemoryAgent

def main():
    print("Initializing Hybrid Memory Agent...")
    
    # Adjust this path if running from a different directory
    feast_repo_path = Path(__file__).parent.parent / "app" / "feast_repo"
    agent = HybridMemoryAgent(feast_repo_path=str(feast_repo_path))
    
    # Pre-seed some episodic memories
    print("Seeding episodic memories...")
    agent.remember("Gần đây tôi đang học về Kubernetes để quản lý container, rất thú vị nhưng hơi phức tạp.")
    agent.remember("Hệ thống tự động mở rộng (auto-scaling) là thứ tôi muốn áp dụng vào dự án sắp tới.")
    agent.remember("Đã đọc tài liệu về Cloud Security, đặc biệt là các vấn đề liên quan đến IAM và mã hoá dữ liệu.")
    
    queries = [
        "Tôi đã đọc gì về Kubernetes?",
        "Recommend đọc gì tiếp?",
        "Tôi đang quan tâm gì gần đây?",
        "Tài liệu về tự động mở rộng hạ tầng?",
        "Cho tôi summary cloud security"
    ]
    
    print("\n--- Running 5 Demo Queries ---\n")
    for i, q in enumerate(queries, 1):
        print(f"=== Query {i}: {q} ===")
        context = agent.recall(query=q, user_id="u_001")
        print(context)
        print("="*40 + "\n")

if __name__ == "__main__":
    main()
