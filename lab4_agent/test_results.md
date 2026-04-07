# **UPDATE SYSTEM PROMPT**
Từ prompt ban đầu rất ngắn (chỉ có persona, trả lời tiếng Việt và danh sách tool), em đã bổ sung các rule và constraint sau để agent gọi tool ổn định hơn và giảm trả lời sai:

| Loại | Nội dung | Lý do |
|---|---|---|
| Rule | Nhận diện rõ 3 intent chính và gọi tool ngay khi đủ dữ liệu tối thiểu: tìm chuyến bay -> search_flights, tìm khách sạn -> search_hotels, tính ngân sách -> calculate_budget. | Tránh trả lời lan man hoặc hỏi dư khi đã có đủ input để gọi tool. |
| Rule | Nếu tool trả về không có dữ liệu hoặc lỗi, giữ nguyên thông báo lỗi của tool khi phản hồi. | Giảm nguy cơ model diễn giải sai hoặc làm mềm lỗi thành câu mơ hồ. |
| Rule | Chỉ hỏi thêm khi thiếu trường bắt buộc theo intent; không hỏi thêm trường tùy chọn nếu vẫn gọi được tool. | Cải thiện tốc độ hội thoại và tăng tỉ lệ pass các test cần gọi tool ngay. |
| Rule | Khi yêu cầu rẻ nhất/tốt nhất thì bắt buộc gọi tool rồi mới chọn theo tiêu chí: rẻ nhất theo giá thấp nhất, tốt nhất theo rating cao nhất trong tập phù hợp. | Đảm bảo quyết định dựa trên dữ liệu tool thay vì đoán. |
| Rule | Nếu user có ngân sách tổng cho chuyến đi, sau khi lấy dữ liệu flight/hotel thì bắt buộc gọi calculate_budget. | Chuẩn hóa bước kết luận đủ/vượt ngân sách bằng phép tính từ tool. |
| Rule | Khi user nêu số tiền bằng chữ (ví dụ một triệu rưỡi), chuẩn hóa về số trước khi tính. | Tăng độ bền cho input tự nhiên và giảm lỗi parse. |
| Rule | Với yêu cầu cụ thể + ngân sách (ví dụ khách sạn cụ thể), áp dụng quy trình gọi chuỗi: search_flights -> search_hotels -> calculate_budget -> đề xuất phương án thay thế nếu vượt ngân sách. | Khóa flow nhất quán cho bài toán tư vấn có ràng buộc ngân sách. |
| Constraint | Từ chối yêu cầu ngoài phạm vi du lịch/đặt vé/đặt phòng bằng câu từ chối thống nhất và lịch sự chuyển về đúng chủ đề. | Giữ guardrail an toàn, tránh trả lời lạc đề. |
| Constraint | Không bịa tên chuyến bay, khách sạn, giá tiền nếu chưa có kết quả tool. | Ngăn hallucination và giữ tính kiểm chứng. |
| Constraint | Nếu đã đủ dữ liệu tối thiểu thì không được hỏi thêm trước khi gọi tool; không âm thầm retry quá 2 lần. | Tăng tính quyết đoán khi gọi tool và tránh vòng lặp thất bại. |


## TEST CASE RESULT

| Test | Loại | User | Kỳ vọng | Kết quả test | Output |
|---|---|---|---|---|---|
| Test 1 | Direct Answer (Không cần tool) | "Xin chào! Tôi đang muốn đi du lịch nhưng chưa biết đi đâu." | Agent chào hỏi, hỏi thêm về sở thích/ngân sách/thời gian. Không gọi tool nào. | Pass | Không gọi tool; trả lời chào hỏi và hỏi thêm loại điểm đến + ngân sách. |
| Test 2 | Single Tool Call | "Tìm giúp tôi chuyến bay từ Hà Nội đi Đà Nẵng" | Gọi `search_flights("Hà Nội", "Đà Nẵng")`, liệt kê các chuyến bay phù hợp. | Pass | Có gọi `search_flights`; liệt kê đầy đủ các chuyến bay Hà Nội - Đà Nẵng. |
| Test 3 | Multi-Step Tool Chaining | "Tôi ở Hà Nội, muốn đi Phú Quốc 2 đêm, budget 5 triệu. Tư vấn giúp!" | Agent phải tự chuỗi nhiều bước:<br>1. `search_flights("Hà Nội", "Phú Quốc")` → tìm vé rẻ nhất (1.100.000đ)<br>2. `search_hotels("Phú Quốc", max_price phù hợp)` → gợi ý trong tầm giá<br>3. `calculate_budget(5000000, "vé_bay:1100000,khách_sạn:...")` → tính còn lại<br>Rồi tổng hợp thành gợi ý hoàn chỉnh với bảng chi phí. | Pass | Có gọi đủ 3 tool theo chuỗi; chọn vé 1.100.000đ, khách sạn Lahana Resort 800.000đ/đêm x2 và tính ngân sách còn lại. |
| Test 4 | Missing Info / Clarification | "Tôi muốn đặt khách sạn" | Agent hỏi lại: thành phố nào? bao nhiêu đêm? ngân sách bao nhiêu? Không gọi tool vội. | Pass | Không gọi tool; hỏi lại thành phố và mức giá tối đa/đêm. |
| Test 5 | Guardrail / Refusal | "Giải giúp tôi bài tập lập trình Python về linked list" | Từ chối lịch sự, nói rằng chỉ hỗ trợ về du lịch. | Pass | Từ chối đúng mẫu: "Tôi chỉ hỗ trợ thông tin về du lịch" và mời quay lại chủ đề du lịch. |
| Test 6 | Vượt ngân sách ngay lập tức (Xử lý tài chính) | "Tôi muốn đi Phú Quốc từ Hà Nội, ở Vinpearl Resort 1 đêm, nhưng tổng budget tôi chỉ có 3 triệu thôi." | Agent gọi `search_flights` (vé rẻ nhất khoảng 1.1 triệu) và lấy khách sạn Vinpearl Resort. Khi gọi `calculate_budget`, Agent phải báo "Vượt ngân sách" và đề xuất khách sạn rẻ hơn như `9Station Hostel`. | Pass | Có gọi `search_flights`, `search_hotels`, `calculate_budget`; báo vượt ngân sách 1.600.000đ và đề xuất Lahana Resort thay cho Vinpearl Resort. |
| Test 7 | Lọc giá + rating (Chất lượng tool) | "Tìm cho tôi khách sạn ở Đà Nẵng giá dưới 1 triệu nhưng phải có đánh giá (rating) cao nhất." | Agent gọi `search_hotels` với `max_price_per_night=1000000`. Kết quả phải ưu tiên khách sạn có rating cao nhất trong nhóm phù hợp, ví dụ `Memory Hostel` hoặc `Christina's Homestay`, thay vì chỉ lấy khách sạn đầu tiên. | Pass | Có gọi `search_hotels` với max price; trả danh sách đúng và ưu tiên `Fivitel Danang` (rating 4.7 cao nhất). |
| Test 8 | Tính toán chi phí cho nhóm đông người (Logic toán học) | "Nhóm tôi có 4 người đi từ Hà Nội vào Đà Nẵng, muốn ở khách sạn Sala Danang Beach 1 đêm. Ngân sách 10 triệu đủ không?" | Agent phải nhân giá vé máy bay và phòng khách sạn cho 4 người trước khi gọi `calculate_budget`, hoặc giải thích rõ chi phí tính trên đầu người để tránh sai số. | Pass | Có gọi `search_flights`, `search_hotels`, `calculate_budget`; nhân vé máy bay cho 4 người và kết luận ngân sách đủ. |
| Test 9 | Guardrail | "Bạn thấy tôi có đẹp trai không?" | Agent từ chối lịch sự và khẳng định chỉ hỗ trợ du lịch/đặt vé. | Pass | Từ chối đúng phạm vi: chỉ hỗ trợ du lịch, vé máy bay và khách sạn. |
| Test 10 | Thông tin thành phố không có trong Database | "Tôi muốn đi du lịch Sa Pa, tư vấn giúp tôi khách sạn ở đó." | Agent gọi tool nhưng vì `HOTELS_DB` không có Sa Pa, phải báo "Không tìm thấy khách sạn tại Sa Pa" | Pass | Đã gọi `search_hotels` với city `Sa Pa` và phản hồi không có dữ liệu khách sạn phù hợp cho Sa Pa. |
| Test 11 | Yêu cầu mập mờ về ngân sách | "Tìm cho tôi chuyến bay rẻ nhất từ Hồ Chí Minh đi Phú Quốc." | Agent gọi `search_flights`, so sánh giữa các lựa chọn như Vietnam Airlines và VietJet để đưa ra phương án rẻ nhất là VietJet. | Pass | Có gọi `search_flights` đúng thành phố Hồ Chí Minh và trả ra chuyến rẻ nhất của VietJet Air với giá 650.000đ. |
| Test 12 | Nhập liệu sai định dạng (Độ bền của Tool) | "Tính giúp tôi: vé máy bay một triệu rưỡi, khách sạn hai triệu, ngân sách năm triệu." | `calculate_budget` có thể gặp lỗi parse số. Agent cần xử lý lỗi bằng `try/except` và yêu cầu người dùng nhập số cụ thể hoặc tự chuyển đổi nếu có thể. | Pass | Có gọi `calculate_budget` với 1.500.000đ, 2.000.000đ và 5.000.000đ, rồi tính ra còn lại 1.500.000đ. |

# **Có một số test case em chưa chạy được vì hết token, mong rằng sẽ sớm có chương trình hỗ trợ :> **

# **CONSOLE LOG**

(venv) shiina@Shiiina:/media/shiina/Shiina1/Users/quang/Documents/AI20K26/assignments/day04_lab/lab4_agent$ python agent.py 
============================================================
TravelBuddy — Trợ lý Du lịch Thông minh
Gõ 'quit' để thoát
============================================================

Bạn: Xin chào! Tôi đang muốn đi du lịch nhưng chưa biết đi đâu.

TravelBuddy đang suy nghĩ...
Tra loi truc tiep

TravelBuddy: Xin chào! Du lịch thú vị lắm! Bạn có dự định đi vào thời gian nào và thích khám phá kiểu gì? Một số điểm đến nổi bật có thể kể đến: 

- **Nha Trang**: Nắng vàng, biển xanh, hải sản tươi ngon.
- **Đà Lạt**: Khí hậu mát mẻ, hoa cỏ quanh năm.
- **Phú Quốc**: Bãi biển đẹp, nhiều hoạt động khám phá.
- **Hội An**: Phố cổ lung linh, ẩm thực đa dạng.

Hãy cho tôi biết thêm sở thích hoặc tiêu chí để mình tư vấn điểm đến phù hợp nhé!

Bạn: Tìm giúp tôi chuyến bay từ Hà Nội đi Đà Nẵng

TravelBuddy đang suy nghĩ...
Goi tool: search_flights({'origin': 'Hà Nội', 'destination': 'Đà Nẵng'})
Tra loi truc tiep

TravelBuddy: Chuyến bay từ Hà Nội đi Đà Nẵng bạn có thể chọn như sau:

1. **Vietnam Airlines**
   - Khởi hành: 06:00 → Đến: 07:20
   - Hạng: economy
   - Giá: 1.450.000đ

2. **Vietnam Airlines**
   - Khởi hành: 14:00 → Đến: 15:20
   - Hạng: business
   - Giá: 2.800.000đ

3. **VietJet Air**
   - Khởi hành: 08:30 → Đến: 09:50
   - Hạng: economy
   - Giá: 890.000đ

4. **Bamboo Airways**
   - Khởi hành: 11:00 → Đến: 12:20
   - Hạng: economy
   - Giá: 1.200.000đ

Gợi ý của mình: Nếu bạn muốn tiết kiệm chi phí, có thể chọn chuyến của VietJet Air với giá 890.000đ.

Bạn: Tôi ở Hà Nội, muốn đi Phú Quốc 2 đêm, budget 5 triệu. Tư vấn giúp!

TravelBuddy đang suy nghĩ...
Goi tool: search_flights({'origin': 'Hà Nội', 'destination': 'Phú Quốc'})
Goi tool: search_hotels({'city': 'Phú Quốc'})
Goi tool: calculate_budget({'total_budget': 5000000, 'expenses': 'vé_máy_bay:1100000,khách_sạn:1600000'})
Tra loi truc tiep

TravelBuddy: Chuyến bay: 
- Lựa chọn rẻ nhất: VietJet Air, khởi hành 16:00 từ Hà Nội và đến Phú Quốc lúc 18:15. Giá vé 1.100.000đ.

Khách sạn: 
- Lahana Resort ⭐⭐⭐ ở Dương Đông với giá 800.000đ/đêm. Tổng chi cho 2 đêm là 1.600.000đ.

Tổng chi phí ước tính: 
- Vé máy bay: 1.100.000đ
- Khách sạn: 1.600.000đ
- Tổng chi phí: 2.700.000đ
- Ngân sách của bạn: 5.000.000đ
- Còn lại: 2.300.000đ

Gợi ý thêm: 
- Bạn vẫn còn một khoản dư 2.300.000đ để chi tiêu cho ăn uống, tham quan hay các hoạt động vui chơi khác ở Phú Quốc.

Bạn: Tôi muốn đặt khách sạn

TravelBuddy đang suy nghĩ...
Tra loi truc tiep

TravelBuddy: Bạn muốn đặt khách sạn tại thành phố nào? Nếu có ngân sách cụ thể cho mỗi đêm, bạn cũng có thể chia sẻ để mình tìm được chỗ phù hợp hơn nhé!

Bạn: Giải giúp tôi bài tập lập trình Python về linked list

TravelBuddy đang suy nghĩ...
Tra loi truc tiep

TravelBuddy: Xin lỗi, tôi chỉ hỗ trợ thông tin về du lịch. Nếu bạn cần tư vấn về các chuyến đi, đặt vé máy bay hay đặt phòng khách sạn, hãy cho tôi biết chi tiết để tôi có thể giúp bạn tốt nhất.

Bạn: Tôi muốn đi Phú Quốc từ Hà Nội, ở Vinpearl Resort 1 đêm, nhưng tổng budget tôi chỉ có 3 triệu thôi.

TravelBuddy đang suy nghĩ...
Goi tool: search_flights({'origin': 'Hà Nội', 'destination': 'Phú Quốc'})
Goi tool: search_hotels({'city': 'Phú Quốc'})
Goi tool: calculate_budget({'total_budget': 3000000, 'expenses': 'vé_máy_bay:1100000,khách_sạn:3500000'})
Tra loi truc tiep

TravelBuddy: Chuyến đi của bạn đang vượt ngân sách 1.600.000đ. Bạn cần điều chỉnh lại các lựa chọn như sau:

Chuyến bay:
- Lựa chọn rẻ nhất: VietJet Air với giá 1.100.000đ.

Khách sạn:
- Vinpearl Resort có giá 3.500.000đ/đêm, vượt quá ngân sách. Bạn có thể cân nhắc ở khách sạn khác có giá hợp lý hơn như:
  - Lahana Resort: 800.000đ/đêm (Vẫn có thể tiết kiệm được nhiều so với Vinpearl).

Tổng chi phí ước tính với Lahana Resort:
- Chuyến bay: 1.100.000đ
- Khách sạn: 800.000đ
- Tổng cộng: 1.900.000đ

Gợi ý thêm: Bạn nên cân nhắc chọn Lahana Resort để tận dụng ngân sách tốt nhất. Còn lại, bạn sẽ có một khoản tiền dư để chi tiêu cho các hoạt động khác ở Phú Quốc.

Bạn: Tìm cho tôi khách sạn ở Đà Nẵng giá dưới 1 triệu nhưng phải có đánh giá (rating) cao nhất.

TravelBuddy đang suy nghĩ...
Goi tool: search_hotels({'city': 'Đà Nẵng', 'max_price_per_night': 1000000})
Tra loi truc tiep

TravelBuddy: Khách sạn ở Đà Nẵng có giá dưới 1 triệu và có đánh giá cao nhất là:

**Fivitel Danang**
- **3 sao** 
- **Rating:** 4.7/5.0
- **Khu vực:** Mỹ Khê
- **Giá:** 650.000đ/đêm

Đây là một lựa chọn tốt với mức giá phải chăng và đánh giá cao. Bạn thấy ổn không hay cần thêm thông tin gì khác nữa không?

Bạn: Nhóm tôi có 4 người đi từ Hà Nội vào Đà Nẵng, muốn ở khách sạn Sala Danang Beach 1 đêm. Ngân sách 10 triệu đủ không?

TravelBuddy đang suy nghĩ...
Goi tool: search_flights({'origin': 'Hà Nội', 'destination': 'Đà Nẵng'})
Goi tool: search_hotels({'city': 'Đà Nẵng'})
Goi tool: calculate_budget({'total_budget': 10000000, 'expenses': 'vé_máy_bay:3560000,khách_sạn:1200000'})
Tra loi truc tiep

TravelBuddy: Chuyến bay: 
- VietJet Air: Khởi hành 08:30 → Đến 09:50, giá 890.000đ (economy), tổng cho 4 người: 3.560.000đ.

Khách sạn: 
- Sala Danang Beach: 1.200.000đ/đêm.

Tổng chi phí ước tính: 
- Vé máy bay cho 4 người và khách sạn 1 đêm: 4.760.000đ.

Ngân sách của bạn là 10 triệu, còn lại 5.240.000đ sau khi trừ chi phí bay và khách sạn. Như vậy, ngân sách dư sức cho chuyến đi này! Bạn có thể thoải mái sử dụng số tiền còn lại cho những hoạt động khác tại Đà Nẵng nhé!

Bạn: Bạn thấy tôi có đẹp trai không?

TravelBuddy đang suy nghĩ...
Tra loi truc tiep

TravelBuddy: Tôi chỉ hỗ trợ thông tin về du lịch, các chuyến bay và khách sạn thôi! Nếu bạn cần tìm vé máy bay, đặt phòng khách sạn hay tính toán ngân sách cho chuyến đi, tôi sẵn sàng giúp ngay.

Bạn: Tôi muốn đi du lịch Sa Pa, tư vấn giúp tôi khách sạn ở đó.

TravelBuddy đang suy nghĩ...
Goi tool: search_hotels({'city': 'Sa Pa'})
Tra loi truc tiep

TravelBuddy: Rất tiếc, hiện tại tôi không lấy được thông tin khách sạn ở Sa Pa. Có thể bạn thử hỏi lại sau hoặc tìm kiếm trực tiếp qua các trang đặt phòng uy tín như Booking.com hay Agoda để biết thêm lựa chọn. Bạn có cần thêm thông tin gì khác không?

Bạn: Tìm cho tôi chuyến bay rẻ nhất từ Hồ Chí Minh đi Phú Quốc.

TravelBuddy đang suy nghĩ...
Goi tool: search_flights({'origin': 'Hồ Chí Minh', 'destination': 'Phú Quốc'})
Tra loi truc tiep

TravelBuddy: Chuyến bay rẻ nhất từ Hồ Chí Minh đến Phú Quốc là của hãng VietJet Air, khởi hành lúc 15:00 và đến nơi lúc 16:00, với giá là 650.000đ.

Bạn: Tính giúp tôi: vé máy bay một triệu rưỡi, khách sạn hai triệu, ngân sách năm triệu.

TravelBuddy đang suy nghĩ...
Goi tool: calculate_budget({'total_budget': 5000000, 'expenses': 'vé_máy_bay:1500000,khách_sạn:2000000'})
Tra loi truc tiep

TravelBuddy: Bạn còn lại 1.500.000 VNĐ sau khi trừ các chi phí cơ bản cho vé máy bay và khách sạn. Với số tiền còn lại, bạn có thể thoải mái chi tiêu cho những hoạt động khác như ăn uống, tham quan và mua sắm trong chuyến đi của mình. Chúc bạn có một kỳ nghỉ tuyệt vời!

Bạn: 