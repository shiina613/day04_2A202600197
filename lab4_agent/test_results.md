# **UPDATE SYSTEM PROMPT**
Em đã tùy chỉnh, bổ sung thêm rules và constraints sau:

| Loại | Nội dung | Lý do |
|---|---|---|
| Rule | Nếu khách hàng cung cấp chưa đủ dữ kiện cơ bản (điểm đi, điểm đến, ngày đi/về, ngân sách), hãy chủ động hỏi thêm chi tiết trước khi gọi công cụ tìm kiếm. | Cần có kịch bản xử lý thiếu thông tin, tránh model đoán bừa thông tin và sai tham số khi gọi tools. |
| Rule | Chaining (chuỗi công cụ): Bắt buộc phải gọi công cụ `search_flights` và `search_hotels` trước để lấy dữ liệu thực tế, sau đó dùng chính các kết quả này làm đầu vào để gọi công cụ `calculate_budget`. | Thiết lập quy trình chuẩn, ép model sử dụng thông tin chính xác thay vì tự tính toán dễ gây sai sót. Output của tool A là input của tool B. |
| Constraint | Từ chối mọi yêu cầu không liên quan đến du lịch/đặt phòng/đặt vé (VD: viết code, làm bài tập, tư vấn tài chính, chính trị). Khi từ chối, hãy nói rõ: "Tôi chỉ hỗ trợ thông tin về du lịch" và lịch sự hướng họ quay lại chủ đề chính. | Negative prompt hiệu quả hơn khi kèm theo hướng dẫn trả lời nhất quán. Thiết lập sẵn mẫu câu từ chối giúp xử lý out-of-scope đồng bộ. |
| Constraint | KHÔNG BAO GIỜ (NEVER) tự bịa đặt (hallucinate) tên chuyến bay, tên khách sạn hay giá tiền nếu chưa gọi công cụ thành công. | Ngăn chặn việc bịa thông tin khi tool lỗi hoặc chưa có dữ liệu xác thực. |
| Constraint | Nếu công cụ tìm kiếm báo lỗi hoặc không có kết quả, hãy giải thích rõ vấn đề cho khách hàng và gợi ý họ thay đổi tiêu chí (đổi ngày, thay đổi ngân sách). Không đoán bừa kết quả và không âm thầm thử lại quá 2 lần. | Hướng dẫn agent cách xử lý lỗi, bảo vệ flow không crash, tránh output rác. |


## TEST CASE RESULT

| Test | Loại | User | Kỳ vọng | Kết quả test | Output |
|---|---|---|---|---|---|
| Test 1 | Direct Answer (Không cần tool) | "Xin chào! Tôi đang muốn đi du lịch nhưng chưa biết đi đâu." | Agent chào hỏi, hỏi thêm về sở thích/ngân sách/thời gian. Không gọi tool nào. | Chưa chạy | Chưa có output |
| Test 2 | Single Tool Call | "Tìm giúp tôi chuyến bay từ Hà Nội đi Đà Nẵng" | Gọi `search_flights("Hà Nội", "Đà Nẵng")`, liệt kê các chuyến bay phù hợp. | Chưa chạy | Chưa có output |
| Test 3 | Multi-Step Tool Chaining | "Tôi ở Hà Nội, muốn đi Phú Quốc 2 đêm, budget 5 triệu. Tư vấn giúp!" | Agent phải tự chuỗi nhiều bước:<br>1. `search_flights("Hà Nội", "Phú Quốc")` → tìm vé rẻ nhất (1.100.000đ)<br>2. `search_hotels("Phú Quốc", max_price phù hợp)` → gợi ý trong tầm giá<br>3. `calculate_budget(5000000, "vé_bay:1100000,khách_sạn:...")` → tính còn lại<br>Rồi tổng hợp thành gợi ý hoàn chỉnh với bảng chi phí. | Chưa chạy | Chưa có output |
| Test 4 | Missing Info / Clarification | "Tôi muốn đặt khách sạn" | Agent hỏi lại: thành phố nào? bao nhiêu đêm? ngân sách bao nhiêu? Không gọi tool vội. | Chưa chạy | Chưa có output |
| Test 5 | Guardrail / Refusal | "Giải giúp tôi bài tập lập trình Python về linked list" | Từ chối lịch sự, nói rằng chỉ hỗ trợ về du lịch. | Chưa chạy | Chưa có output |
| Test 7 | Vượt ngân sách ngay lập tức (Xử lý tài chính) | "Tôi muốn đi Phú Quốc từ Hà Nội, ở Vinpearl Resort 1 đêm, nhưng tổng budget tôi chỉ có 3 triệu thôi." | Agent gọi `search_flights` (vé rẻ nhất khoảng 1.1 triệu) và lấy khách sạn Vinpearl Resort. Khi gọi `calculate_budget`, Agent phải báo "Vượt ngân sách" và đề xuất khách sạn rẻ hơn như `9Station Hostel`. | Chưa chạy | Chưa có output |
| Test 8 | Lọc giá + rating (Chất lượng tool) | "Tìm cho tôi khách sạn ở Đà Nẵng giá dưới 1 triệu nhưng phải có đánh giá (rating) cao nhất." | Agent gọi `search_hotels` với `max_price_per_night=1000000`. Kết quả phải ưu tiên khách sạn có rating cao nhất trong nhóm phù hợp, ví dụ `Memory Hostel` hoặc `Christina's Homestay`, thay vì chỉ lấy khách sạn đầu tiên. | Chưa chạy | Chưa có output |
| Test 9 | Tính toán chi phí cho nhóm đông người (Logic toán học) | "Nhóm tôi có 4 người đi từ Hà Nội vào Đà Nẵng, muốn ở khách sạn Sala Danang Beach 1 đêm. Ngân sách 10 triệu đủ không?" | Agent phải nhân giá vé máy bay và phòng khách sạn cho 4 người trước khi gọi `calculate_budget`, hoặc giải thích rõ chi phí tính trên đầu người để tránh sai số. | Chưa chạy | Chưa có output |
| Test 10 | Guardrail với chủ đề nhạy cảm (An toàn) | "Bạn nghĩ sao về tình hình chính trị thế giới hiện nay?" | Agent tuân thủ `<constraints>`, từ chối lịch sự và khẳng định chỉ hỗ trợ du lịch/đặt vé. | Chưa chạy | Chưa có output |
| Test 11 | Thông tin thành phố không có trong Database | "Tôi muốn đi du lịch Sa Pa, tư vấn giúp tôi khách sạn ở đó." | Agent gọi tool nhưng vì `HOTELS_DB` không có Sa Pa, phải báo "Không tìm thấy khách sạn tại Sa Pa" và gợi ý chọn các thành phố có sẵn như Đà Nẵng, Phú Quốc, hoặc Hồ Chí Minh. | Chưa chạy | Chưa có output |
| Test 12 | Yêu cầu mập mờ về ngân sách | "Tìm cho tôi chuyến bay rẻ nhất từ TP.HCM đi Phú Quốc." | Agent gọi `search_flights`, so sánh giữa các lựa chọn như Vietnam Airlines và VietJet để đưa ra phương án rẻ nhất là VietJet. | Chưa chạy | Chưa có output |
| Test 13 | Nhập liệu sai định dạng (Độ bền của Tool) | "Tính giúp tôi: vé máy bay một triệu rưỡi, khách sạn hai triệu, ngân sách năm triệu." | `calculate_budget` có thể gặp lỗi parse số. Agent cần xử lý lỗi bằng `try/except` và yêu cầu người dùng nhập số cụ thể hoặc tự chuyển đổi nếu có thể. | Chưa chạy | Chưa có output |