# Day 04 Lab - TravelBuddy Agent

## 1. Muc tieu
Project xay dung mot travel assistant su dung LLM + tool calling voi 3 cong cu:
- `search_flights`
- `search_hotels`
- `calculate_budget`

Agent duoc toi uu de:
- nhan dien dung intent,
- goi tool dung luc,
- chain tool de tinh ngan sach,
- xu ly cau hoi ngoai pham vi du lich.

## 2. Cau truc thu muc
```text
day04_lab/
├── README.md
├── venv/
└── lab4_agent/
	├── agent.py
	├── tools.py
	├── system_prompt.txt
	├── test_api.py
	└── test_results.md
```

## 3. Cai dat va chay
### 3.1 Tao va kich hoat virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3.2 Cai thu vien
```bash
pip install langgraph langchain-openai langchain-core python-dotenv openai
```

### 3.3 Cau hinh bien moi truong
Tao file `.env` (hoac cap nhat neu da co):
```env
OPENROUTER_API_KEY=your_openrouter_api_key
YOUR_SITE_URL=https://your-site.example
YOUR_SITE_NAME=TravelBuddyLab
```

`YOUR_SITE_URL` va `YOUR_SITE_NAME` la tuy chon.

### 3.4 Chay agent
```bash
cd lab4_agent
python agent.py
```

## 4. Prompt da cap nhat
Tu prompt ban dau rat ngan, prompt hien tai da bo sung:
- Rule nhan dien 3 intent chinh va goi tool ngay khi du thong tin toi thieu.
- Rule chi hoi them khi thieu truong bat buoc.
- Rule bat buoc goi tool khi can tim phuong an re nhat/tot nhat.
- Rule chain tool cho bai toan budget: `search_flights -> search_hotels -> calculate_budget`.
- Rule chuan hoa so tien dang chu (vi du: "mot trieu ruoi").
- Constraint tu choi request ngoai pham vi du lich.
- Constraint khong bịa du lieu neu chua co ket qua tool.
- Constraint xu ly loi/khong co du lieu tu tool va khong retry am tham qua 2 lan.

Chi tiet day du nam trong:
- `lab4_agent/test_results.md`
- `lab4_agent/system_prompt.txt`

## 5. Ket qua test
Da thuc hien 12 test case trong `lab4_agent/test_results.md`.

Tom tat:
- Pass: 12/12
- Bao gom cac nhom test: direct answer, single-tool, multi-tool chaining, guardrail, city-not-found, va budget parsing.

## 6. Ghi chu
- `venv/` da duoc ignore trong `.gitignore`.
- Du lieu flights/hotels la mock data trong `lab4_agent/tools.py`.