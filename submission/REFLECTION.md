# Reflection — Lab 19

**Tên:** Phạm Hải Đăng
**Cohort:** A20-K1
**Path đã chạy:** docker

---

## Câu hỏi (≤ 200 chữ)

> Trên golden set 50 queries, mode nào thắng ở loại query nào (`exact` /
> `paraphrase` / `mixed`), và tại sao? Khi nào bạn **không** dùng hybrid
> (i.e. khi nào pure BM25 hoặc pure vector là lựa chọn đúng)?

Trên golden set 50 queries:
- **BM25** thắng ở loại `exact` (truy vấn từ khóa, tên riêng, mã lỗi) vì thuật toán tập trung đếm tần suất từ khóa chính xác mà không bị "nhòe" bởi ý nghĩa tương đương.
- **Vector** thắng ở `paraphrase` (truy vấn ngữ nghĩa) nhờ khả năng ánh xạ ý niệm vào không gian nhúng, tìm được tài liệu đồng nghĩa dù không khớp mặt chữ.
- **Hybrid (RRF)** thắng tuyệt đối ở `mixed` vì kết hợp sức mạnh của cả hai: vừa neo chặt từ khoá kỹ thuật (lexical), vừa hiểu ngữ cảnh bao quát (semantic).

**Không nên dùng Hybrid khi:**
1. Giới hạn độ trễ (latency) cực kỳ khắt khe hoặc tài nguyên hạn hẹp (chạy 2 luồng tìm kiếm và tính điểm RRF sẽ chậm và tốn kém hơn).
2. Domain đặc thù 100% dựa vào exact match (như tra cứu mã đơn hàng, log hệ thống) → Chỉ nên dùng pure BM25.
3. Chatbot hoàn toàn thiên về hội thoại tự nhiên, không có các thuật ngữ đặc thù → Dùng pure Vector là đủ.

---

## Điều ngạc nhiên nhất khi làm lab này

Sự đơn giản nhưng vô cùng hiệu quả của thuật toán RRF (Reciprocal Rank Fusion) trong việc dung hòa điểm số khác hệ (BM25 vs Cosine Similarity) mà không cần phải tinh chỉnh trọng số phức tạp. Bên cạnh đó, việc nhận thức được độ trễ (latency P99) khác biệt lớn thế nào khi thao tác File I/O (SQLite) trên môi trường Windows so với Production (Redis) cũng là một điểm rất thú vị.

---

## Bonus challenge

- [x] Đã làm bonus (xem `bonus/`)
- [ ] Pair work với: Không có
