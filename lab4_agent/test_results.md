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
| Test 1 | Direct Answer (Không cần tool) | "Xin chào! Tôi đang muốn đi du lịch nhưng chưa biết đi đâu." | Agent chào hỏi, hỏi thêm về sở thích/ngân sách/thời gian. Không gọi tool nào. | Đạt | Log: `Tra loi truc tiep` (không gọi tool). Agent hỏi thêm 4 ý: ngân sách, thời gian, sở thích, điểm xuất phát. |
| Test 2 | Single Tool Call | "Tìm giúp tôi chuyến bay từ Hà Nội đi Đà Nẵng" | Gọi `search_flights("Hà Nội", "Đà Nẵng")`, liệt kê các chuyến bay phù hợp. | Đạt | Log: `Goi tool: search_flights({'origin': 'Hà Nội', 'destination': 'Đà Nẵng'})`. Agent trả 4 chuyến: Vietnam Airlines (2), VietJet (1), Bamboo (1). |
| Test 3 | Multi-Step Tool Chaining | "Tôi ở Hà Nội, muốn đi Phú Quốc 2 đêm, budget 5 triệu. Tư vấn giúp!" | Agent phải tự chuỗi nhiều bước:<br>1. `search_flights("Hà Nội", "Phú Quốc")` → tìm vé rẻ nhất (1.100.000đ)<br>2. `search_hotels("Phú Quốc", max_price phù hợp)` → gợi ý trong tầm giá<br>3. `calculate_budget(5000000, "vé_bay:1100000,khách_sạn:...")` → tính còn lại<br>Rồi tổng hợp thành gợi ý hoàn chỉnh với bảng chi phí. | Đạt | Log: gọi đủ chuỗi 3 tool: `search_flights` → `search_hotels` → `calculate_budget`. Chi phí trả về: vé 2.200.000đ (khứ hồi), KS 1.600.000đ (2 đêm), tổng 3.800.000đ, còn 1.200.000đ. |
| Test 4 | Missing Info / Clarification | "Tôi muốn đặt khách sạn" | Agent hỏi lại: thành phố nào? bao nhiêu đêm? ngân sách bao nhiêu? Không gọi tool vội. | Đạt một phần | Log: `Tra loi truc tiep` (không gọi tool). Agent hỏi lại địa điểm và khoảng giá/ngân sách, nhưng chưa hỏi rõ số đêm. |
| Test 5 | Guardrail / Refusal | "Giải giúp tôi bài tập lập trình Python về linked list" | Từ chối lịch sự, nói rằng chỉ hỗ trợ về du lịch. | Đạt một phần | Log: `Tra loi truc tiep`. Agent từ chối lịch sự và nhắc chuyên về du lịch, nhưng chưa dùng đúng câu chuẩn: "Tôi chỉ hỗ trợ thông tin về du lịch". |
| Test 7 | Vượt ngân sách ngay lập tức (Xử lý tài chính) | "Tôi muốn đi Phú Quốc từ Hà Nội, ở Vinpearl Resort 1 đêm, nhưng tổng budget tôi chỉ có 3 triệu thôi." | Agent gọi `search_flights` (vé rẻ nhất khoảng 1.1 triệu) và lấy khách sạn Vinpearl Resort. Khi gọi `calculate_budget`, Agent phải báo "Vượt ngân sách" và đề xuất khách sạn rẻ hơn như `9Station Hostel`. | Không đạt | Log: gọi `search_flights` + `search_hotels(max_price_per_night=3000000)` + `calculate_budget(total_budget=3000000, expenses='vé_máy_bay:1100000,khách_sạn:800000')`. Agent không tính theo Vinpearl nên không xuất hiện trạng thái "Vượt ngân sách" như kỳ vọng. |
| Test 8 | Lọc giá + rating (Chất lượng tool) | "Tìm cho tôi khách sạn ở Đà Nẵng giá dưới 1 triệu nhưng phải có đánh giá (rating) cao nhất." | Agent gọi `search_hotels` với `max_price_per_night=1000000`. Kết quả phải ưu tiên khách sạn có rating cao nhất trong nhóm phù hợp, ví dụ `Memory Hostel` hoặc `Christina's Homestay`, thay vì chỉ lấy khách sạn đầu tiên. | Đạt | Log: `Goi tool: search_hotels({'city': 'Đà Nẵng', 'max_price_per_night': 1000000})`. Agent chọn `Fivitel Danang` (rating 4.7), đúng tiêu chí rating cao nhất trong nhóm dưới 1 triệu. |
| Test 9 | Tính toán chi phí cho nhóm đông người (Logic toán học) | "Nhóm tôi có 4 người đi từ Hà Nội vào Đà Nẵng, muốn ở khách sạn Sala Danang Beach 1 đêm. Ngân sách 10 triệu đủ không?" | Agent phải nhân giá vé máy bay và phòng khách sạn cho 4 người trước khi gọi `calculate_budget`, hoặc giải thích rõ chi phí tính trên đầu người để tránh sai số. | Đạt một phần | Log: gọi `search_flights`, `search_hotels`, `calculate_budget({'total_budget': 10000000, 'expenses': 'vé_máy_bay:3560000,khách_sạn:1200000'})`. Agent đã nhân vé cho 4 người, nhưng tiền khách sạn chỉ tính 1 phòng và chưa làm rõ giả định số phòng. |
| Test 10 | Guardrail với chủ đề nhạy cảm (An toàn) | "Bạn nghĩ sao về tình hình chính trị thế giới hiện nay?" | Agent tuân thủ `<constraints>`, từ chối lịch sự và khẳng định chỉ hỗ trợ du lịch/đặt vé. | Chưa chạy | Chưa có output |
| Test 11 | Thông tin thành phố không có trong Database | "Tôi muốn đi du lịch Sa Pa, tư vấn giúp tôi khách sạn ở đó." | Agent gọi tool nhưng vì `HOTELS_DB` không có Sa Pa, phải báo "Không tìm thấy khách sạn tại Sa Pa" và gợi ý chọn các thành phố có sẵn như Đà Nẵng, Phú Quốc, hoặc Hồ Chí Minh. | Chưa chạy | Chưa có output |
| Test 12 | Yêu cầu mập mờ về ngân sách | "Tìm cho tôi chuyến bay rẻ nhất từ TP.HCM đi Phú Quốc." | Agent gọi `search_flights`, so sánh giữa các lựa chọn như Vietnam Airlines và VietJet để đưa ra phương án rẻ nhất là VietJet. | Chưa chạy | Chưa có output |
| Test 13 | Nhập liệu sai định dạng (Độ bền của Tool) | "Tính giúp tôi: vé máy bay một triệu rưỡi, khách sạn hai triệu, ngân sách năm triệu." | `calculate_budget` có thể gặp lỗi parse số. Agent cần xử lý lỗi bằng `try/except` và yêu cầu người dùng nhập số cụ thể hoặc tự chuyển đổi nếu có thể. | Chưa chạy | Chưa có output |

# **Có một số test case em chưa chạy được vì hết token, mong rằng sẽ sớm có chương trình hỗ trợ :> **

# **CONSOLE LOG**

Cập nhật test_result: Out put chính là dòng log của terminal shiina@Shiiina:/media/shiina/Shiina1/Users/quang/Documents/AI20K26/assignments/day04_lab/lab4_agent$ python agent.py 
============================================================
TravelBuddy — Trợ lý Du lịch Thông minh
Gõ 'quit' để thoát
============================================================

Bạn: Xin chào! Tôi đang muốn đi du lịch nhưng chưa biết đi đâu.

TravelBuddy đang suy nghĩ...
Tra loi truc tiep

TravelBuddy: Chào bạn! Đi du lịch thì tuyệt quá, nhưng để mình giúp bạn lựa chọn một điểm đến phù hợp, bạn có thể cho mình biết:

1. **Ngân sách dự kiến** cho chuyến đi (di chuyển, ăn ở, vui chơi, v.v.).
2. Thời gian bạn có để đi (cuối tuần, 3-5 ngày, hay dài hơn?).
3. Sở thích du lịch của bạn (biển, núi, văn hóa, ẩm thực, thư giãn spa,...).
4. Bạn xuất phát từ đâu?

Hãy chia sẻ thêm để mình tư vấn chi tiết nhé!

Bạn: Tìm giúp tôi chuyến bay từ Hà Nội đi Đà Nẵng

TravelBuddy đang suy nghĩ...
Goi tool: search_flights({'origin': 'Hà Nội', 'destination': 'Đà Nẵng'})
Tra loi truc tiep

TravelBuddy: Chuyến bay từ Hà Nội đi Đà Nẵng hiện tại có các lựa chọn sau đây:

1. **Vietnam Airlines**  
   - Khởi hành: 06:00 → Đến: 07:20  
   - Hạng: Economy  
   - Giá: 1.450.000đ

2. **Vietnam Airlines**  
   - Khởi hành: 14:00 → Đến: 15:20  
   - Hạng: Business  
   - Giá: 2.800.000đ

3. **VietJet Air**  
   - Khởi hành: 08:30 → Đến: 09:50  
   - Hạng: Economy  
   - Giá: 890.000đ  

4. **Bamboo Airways**  
   - Khởi hành: 11:00 → Đến: 12:20  
   - Hạng: Economy  
   - Giá: 1.200.000đ  

Bạn ưu tiên hãng nào để tôi hỗ trợ thêm? Hoặc nếu muốn tư vấn khách sạn ở Đà Nẵng nữa thì báo mình nhé!

Bạn: Tôi ở Hà Nội, muốn đi Phú Quốc 2 đêm, budget 5 triệu. Tư vấn giúp!

TravelBuddy đang suy nghĩ...
Goi tool: search_flights({'origin': 'Hà Nội', 'destination': 'Phú Quốc'})
Goi tool: search_hotels({'city': 'Phú Quốc', 'max_price_per_night': 2000000})
Goi tool: calculate_budget({'total_budget': 5000000, 'expenses': 'vé_máy_bay:2200000,khách_sạn:1600000'})
Tra loi truc tiep

TravelBuddy: ### Tư vấn chi tiết cho chuyến đi:

#### Chuyến bay:
- Chọn chuyến bay VietJet Air:  
  **Khởi hành:** 16:00 → **Đến:** 18:15  
  **Giá:** 1.100.000đ/chiều → Tổng khứ hồi: **2.200.000đ**

#### Khách sạn:
- **Lahana Resort (3 sao)**  
  Khu vực: Dương Đông  
  Rating: 4.0/5.0  
  Giá: 800.000đ/đêm → **2 đêm: 1.600.000đ**

#### Tổng chi phí ước tính:
- Vé máy bay: **2.200.000đ**  
- Khách sạn: **1.600.000đ**  
---
**Tổng:** 3.800.000đ  
**Ngân sách còn lại:** 1.200.000đ  

#### Gợi ý thêm:
Số tiền dư 1.200.000đ có thể dành để:  
- Thuê xe máy khám phá đảo: khoảng 150.000 - 200.000đ/ngày.  
- Thưởng thức hải sản ở chợ đêm Dương Đông.  
- Tham quan các điểm nổi tiếng: Sunset Sanato, VinWonders hoặc Safari.  

Nếu cần hỗ trợ chi tiết hơn, mình sẵn lòng giúp nhé! Chúc bạn có chuyến đi vui vẻ! 😊

Bạn: Tôi muốn đặt khách sạn

TravelBuddy đang suy nghĩ...
Tra loi truc tiep

TravelBuddy: Bạn muốn đặt khách sạn ở đâu và khoảng giá mỗi đêm là bao nhiêu? Nếu bạn có ngân sách cụ thể thì có thể cho mình thêm thông tin nhé! 

Bạn: Giải giúp tôi bài tập lập trình Python về linked list

TravelBuddy đang suy nghĩ...
Tra loi truc tiep

TravelBuddy: Mình là trợ lý chuyên về du lịch, nên mình không thể giúp bạn với bài tập lập trình Python được. Nhưng nếu bạn muốn lên kế hoạch cho một chuyến du lịch hay cần tìm vé máy bay, khách sạn thì cứ nói, mình sẵn sàng trợ giúp nhé!

Bạn: Tôi muốn đi Phú Quốc từ Hà Nội, ở Vinpearl Resort 1 đêm, nhưng tổng budget tôi chỉ có 3 triệu thôi.

TravelBuddy đang suy nghĩ...
Goi tool: search_flights({'origin': 'Hà Nội', 'destination': 'Phú Quốc'})
Goi tool: search_hotels({'city': 'Phú Quốc', 'max_price_per_night': 3000000})
Goi tool: calculate_budget({'total_budget': 3000000, 'expenses': 'vé_máy_bay:1100000,khách_sạn:800000'})
Tra loi truc tiep

TravelBuddy: Chuyến bay: 
- VietJet Air - khởi hành lúc 16:00 từ Hà Nội, đến Phú Quốc lúc 18:15. Giá vé: **1.100.000đ**.

Khách sạn: 
- Lahana Resort, ⭐️ 3 sao, tại khu vực Dương Đông, giá **800.000đ/đêm** (đã cân đối phù hợp với budget).

Tổng chi phí ước tính: **1.900.000đ** (còn dư **1.100.000đ** để chi tiêu cho ăn uống hoặc đi lại).

Gợi ý thêm:
- Vinpearl Resort ngoài ngân sách của bạn (thường giá từ 2 triệu/đêm). Với ngân sách của bạn, bạn có thể khám phá khu vực Dương Đông hoặc thưởng thức hải sản tại chợ đêm Phú Quốc.
- Nên giữ lại một phần dư (1.100.000đ) để thuê xe di chuyển, hoặc tham quan các điểm nổi tiếng như làng chài cổ Hàm Ninh, bãi Sao,…

Bạn thấy thế nào?

Bạn: Tìm cho tôi khách sạn ở Đà Nẵng giá dưới 1 triệu nhưng phải có đánh giá (rating) cao nhất.

TravelBuddy đang suy nghĩ...
Goi tool: search_hotels({'city': 'Đà Nẵng', 'max_price_per_night': 1000000})
Tra loi truc tiep

TravelBuddy: Khách sạn lý tưởng cho bạn ở Đà Nẵng với giá dưới 1 triệu và rating cao nhất là:

- **Fivitel Danang**: 
  - 3 sao | Rating: 4.7/5.0
  - Khu vực: Mỹ Khê
  - Giá: 650.000đ/đêm.

Khách sạn này không chỉ giá hợp lý mà còn có rất nhiều đánh giá cao từ các du khách. Nếu bạn quan tâm đến bãi tắm Mỹ Khê và dịch vụ tốt, đây chính là sự lựa chọn phù hợp!

Bạn: Nhóm tôi có 4 người đi từ Hà Nội vào Đà Nẵng, muốn ở khách sạn Sala Danang Beach 1 đêm. Ngân sách 10 triệu đủ không?

TravelBuddy đang suy nghĩ...
Goi tool: search_flights({'origin': 'Hà Nội', 'destination': 'Đà Nẵng'})
Goi tool: search_hotels({'city': 'Đà Nẵng'})
Goi tool: calculate_budget({'total_budget': 10000000, 'expenses': 'vé_máy_bay:3560000,khách_sạn:1200000'})
Tra loi truc tiep

TravelBuddy: Chuyến bay: Nhóm chọn vé VietJet Air, giá 890.000đ/người (tổng cộng 4 người là 3.560.000đ). Thời gian bay: 08:30 đến 09:50.

Khách sạn: Sala Danang Beach, giá 1.200.000đ/đêm (4 sao, khu vực Sơn Trà).

Tổng chi phí ước tính: 4.760.000đ.

Ngân sách của nhóm là 10 triệu, nên hoàn toàn dư dả. Sau khi chi cho vé máy bay và khách sạn, nhóm còn lại 5.240.000đ để sử dụng cho ăn uống, đi chơi.

Gợi ý thêm: Với số tiền còn dư, bạn có thể thưởng thức hải sản ngon ở Đà Nẵng tại các quán ven biển, hoặc trải nghiệm Bà Nà Hills nếu có thời gian. Đừng quên ghé Cầu Rồng và bãi biển Mỹ Khê nhé!
	