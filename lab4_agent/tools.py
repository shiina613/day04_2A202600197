from langchain_core.tools import tool

#---------------------------------------
# MOCK DATA - Dữ liệu giả lập hệ thống du lịch
# Lưu ý: Giá cả có logic (VD: cuối tuần đắt hơn, hạng cao hơn đắt hơn)
# Sinh viên cần đọc hiểu data để debug test cases.
#---------------------------------------
FLIGHTS_DB = {
    ("Hà Nội", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "07:20", "price": 1_450_000, "class": "economy"},
        {"airline": "Vietnam Airlines", "departure": "14:00", "arrival": "15:20", "price": 2_800_000, "class": "business"},
        {"airline": "VietJet Air", "departure": "08:30", "arrival": "09:50", "price": 890_000, "class": "economy"},
        {"airline": "Bamboo Airways", "departure": "11:00", "arrival": "12:20", "price": 1_200_000, "class": "economy"},
    ],
    ("Hà Nội", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "07:00", "arrival": "09:15", "price": 2_100_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "10:00", "arrival": "12:15", "price": 1_350_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "16:00", "arrival": "18:15", "price": 1_100_000, "class": "economy"},
    ],
    ("Hà Nội", "Hồ Chí Minh"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "08:10", "price": 1_600_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "07:30", "arrival": "09:40", "price": 950_000, "class": "economy"},
        {"airline": "Bamboo Airways", "departure": "12:00", "arrival": "14:10", "price": 1_300_000, "class": "economy"},
        {"airline": "Vietnam Airlines", "departure": "18:00", "arrival": "20:10", "price": 3_200_000, "class": "business"},
    ],
    ("Hồ Chí Minh", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "09:00", "arrival": "10:20", "price": 1_300_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "13:00", "arrival": "14:20", "price": 780_000, "class": "economy"},
    ],
    ("Hồ Chí Minh", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "08:00", "arrival": "09:00", "price": 1_100_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "15:00", "arrival": "16:00", "price": 650_000, "class": "economy"},
    ],
}

HOTELS_DB = {
    "Đà Nẵng": [
        {"name": "Mường Thanh Luxury", "stars": 5, "price_per_night": 1_800_000, "area": "Mỹ Khê", "rating": 4.5},
        {"name": "Sala Danang Beach", "stars": 4, "price_per_night": 1_200_000, "area": "Sơn Trà", "rating": 4.1},
        {"name": "Memory Hostel", "stars": 2, "price_per_night": 250_000, "area": "Hải Châu", "rating": 4.6},
        {"name": "Christina's Homestay", "stars": 2, "price_per_night": 350_000, "area": "An Thượng", "rating": 4.3},
        {"name": "Fivitel Danang", "stars": 3, "price_per_night": 650_000, "area": "Mỹ Khê", "rating": 4.7},
    ],
    "Phú Quốc": [
        {"name": "Vinpearl Resort", "stars": 5, "price_per_night": 3_500_000, "area": "Bãi Dài", "rating": 4.4},
        {"name": "Sol by Meliá", "stars": 4, "price_per_night": 1_500_000, "area": "Bãi Trường", "rating": 4.2},
        {"name": "Lahana Resort", "stars": 3, "price_per_night": 800_000, "area": "Dương Đông", "rating": 4.0},
        {"name": "9Station Hostel", "stars": 2, "price_per_night": 200_000, "area": "Dương Đông", "rating": 4.5},
    ],
    "Hồ Chí Minh": [
        {"name": "Rex Hotel", "stars": 5, "price_per_night": 2_800_000, "area": "Quận 1", "rating": 4.3},
        {"name": "Liberty Central", "stars": 4, "price_per_night": 1_400_000, "area": "Quận 1", "rating": 4.1},
        {"name": "Cochin Zen Hotel", "stars": 3, "price_per_night": 550_000, "area": "Quận 3", "rating": 4.4},
        {"name": "The Common Room", "stars": 2, "price_per_night": 180_000, "area": "Quận 1", "rating": 4.6},
    ],
}


@tool
def search_flights(origin: str, destination: str) -> str:
    """
    Tìm kiếm các chuyến bay giữa hai thành phố.
    Tham số:
    - origin: thành phố khởi hành (VD: "Hà Nội", "Hồ Chí Minh")
    - destination: thành phố đến (VD: "Đà Nẵng", "Hồ Chí Minh")
    Trả về danh sách chuyến bay với hãng, giờ bay, giá vé.
    Nếu không tìm thấy tuyến bay, trả về thông báo không có chuyến.
    """
    
    # Tra cứu FLIGHTS_DB với key (origin, destination)
    key = (origin, destination)
    flights = FLIGHTS_DB.get(key)
    
    # Nếu không tìm thấy, thử tra ngược (destination, origin)
    if not flights:
        key = (destination, origin)
        flights = FLIGHTS_DB.get(key)
    
    # Nếu vẫn không tìm thấy, trả về thông báo
    if not flights:
        return f"Không tìm thấy chuyến bay từ {origin} đến {destination}."
    
    # Format danh sách chuyến bay dễ đọc
    result = f"Chuyến bay từ {origin} đến {destination}:\n"
    for i, flight in enumerate(flights, 1):
        # Format giá tiền có dấu chấm phân cách (1.450.000đ)
        price_formatted = f"{flight['price']:,}".replace(",", ".")
        result += f"{i}. {flight['airline']}\n"
        result += f"   Khởi hành: {flight['departure']} → Đến: {flight['arrival']}\n"
        result += f"   Hạng: {flight['class']} | Giá: {price_formatted}đ\n"
    
    return result

@tool
def search_hotels(city: str, max_price_per_night: int = 99999999) -> str:
    """
    Tìm kiếm khách sạn tại một thành phố, có thể lọc theo giá tối đa mỗi
    đêm.
    Tham số:
    - city: tên thành phố (VD: 'Đà Nẵng', 'Phú Quốc', 'Hồ Chí Minh')
    - max_price_per_night: giá tối đa mỗi đêm (VNĐ), mặc định không giới
    hạn
    Trả về danh sách khách sạn phù hợp với tên, số sao, giá, khu vực,
    rating.
    """
    
    # Tra cứu HOTELS_DB[city]
    hotels = HOTELS_DB.get(city)
    
    # Nếu không có thành phố
    if not hotels:
        return f"Không tìm thấy khách sạn tại {city}."
    
    # Lọc theo max_price_per_night
    filtered_hotels = [h for h in hotels if h['price_per_night'] <= max_price_per_night]
    
    # Nếu không có khách sạn phù hợp
    if not filtered_hotels:
        price_formatted = f"{max_price_per_night:,}".replace(",", ".")
        return f"Không tìm thấy khách sạn tại {city} với giá dưới {price_formatted}đ/đêm. Hãy thử tăng ngân sách."
    
    # Sắp xếp theo rating giảm dần
    filtered_hotels.sort(key=lambda h: h['rating'], reverse=True)
    
    # Format đẹp
    result = f"Khách sạn tại {city}:\n"
    for i, hotel in enumerate(filtered_hotels, 1):
        price_formatted = f"{hotel['price_per_night']:,}".replace(",", ".")
        result += f"{i}. {hotel['name']}\n"
        result += f"   ⭐ {hotel['stars']} sao | Rating: {hotel['rating']}/5.0\n"
        result += f"   Khu vực: {hotel['area']} | Giá: {price_formatted}đ/đêm\n"
    
    return result


@tool
def calculate_budget(total_budget: int, expenses: str) -> str:
    """Tính toán ngân sách còn lại sau khi trừ các khoản chi phí.
    Tham số:
    - total_budget: tổng ngân sách ban đầu (VNĐ)
    - expenses: chuỗi mô tả các khoản chi, mỗi khoản cách nhau bởi dấu
    phẩy,
    định dạng 'tên_khoản:số_tiền' (VD:
    'vé_máy_bay:890000,khách_sạn:650000')
    Trả về bảng chi tiết các khoản chi và số tiền còn lại.
    Nếu vượt ngân sách, cảnh báo rõ ràng số tiền thiếu.
    """
    
    # Parse chuỗi expenses thành dict {tên: số_tiền}
    try:
        expense_items = expenses.split(',')
        expenses_dict = {}
        total_expenses = 0
        
        for item in expense_items:
            item = item.strip()
            if ':' not in item:
                return f"Lỗi định dạng: '{item}' không chứa ':'. Vui lòng sử dụng 'tên_khoản:số_tiền'."
            
            name, amount_str = item.split(':', 1)
            name = name.strip()
            amount_str = amount_str.strip()
            
            try:
                amount = int(amount_str)
                if amount < 0:
                    return f"Lỗi: số tiền '{name}' không được âm."
                expenses_dict[name] = amount
                total_expenses += amount
            except ValueError:
                return f"Lỗi: '{amount_str}' không phải là số nguyên hợp lệ cho khoản '{name}'."
        
        # Tính số tiền còn lại
        remaining = total_budget - total_expenses
        
        # Format bảng chi tiết
        result = "Bảng chi phí:\n"
        for name, amount in expenses_dict.items():
            amount_formatted = f"{amount:,}".replace(",", ".")
            result += f"- {name}: {amount_formatted}đ\n"
        
        result += "---\n"
        total_formatted = f"{total_expenses:,}".replace(",", ".")
        budget_formatted = f"{total_budget:,}".replace(",", ".")
        result += f"Tổng chi: {total_formatted}đ\n"
        result += f"Ngân sách: {budget_formatted}đ\n"
        
        # Nếu vượt ngân sách
        if remaining < 0:
            shortage_formatted = f"{abs(remaining):,}".replace(",", ".")
            result += f"⚠️  Vượt ngân sách {shortage_formatted}đ! Cần điều chỉnh."
        else:
            remaining_formatted = f"{remaining:,}".replace(",", ".")
            result += f"Còn lại: {remaining_formatted}đ"
        
        return result
        
    except Exception as e:
        return f"Lỗi khi xử lý expenses: {str(e)}"