import time
import requests
from datetime import datetime, timedelta

# ==========================================
# 1. 텔레그램 설정
# ==========================================
BOT_TOKEN = "8939412377:AAG78_-cvqeFFSZNYG7N6wwVvFdsPvkzUzQ"
CHAT_ID = "8609558591"

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"텔레그램 전송 실패: {e}")

# ==========================================
# 2. 감시 대상 6대 핵심 휴양림
# ==========================================
TARGET_RESORTS = [
    {"name": "국립 유명산 자연휴양림 (가평)", "code": "0101"},
    {"name": "국립 산음 자연휴양림 (양평)", "code": "0102"},
    {"name": "국립 중미산 자연휴양림 (양평)", "code": "0103"},
    {"name": "국립 아세안자연휴양림 (양주)", "code": "0142"},
    {"name": "국립 용화산 자연휴양림 (춘천)", "code": "0104"},
    {"name": "국립 변산반도 자연휴양림 (부안)", "code": "0140"}
]

RESERVATION_URL = "https://www.foresttrip.go.kr/rep/or/orRsvt.do"

# 다가오는 토요일 날짜 계산
today = datetime.now()
days_until_saturday = (5 - today.weekday()) % 7
if days_until_saturday == 0:
    days_until_saturday = 7
target_saturday = today + timedelta(days=days_until_saturday)
TARGET_DATE = target_saturday.strftime("%Y%m%d")
formatted_date = target_saturday.strftime("%Y년 %m월 %d일 (토)")

def check_resort(hmpg_id, date_str=TARGET_DATE):
    url = "https://www.foresttrip.go.kr/rep/or/selectOrRsvtMonthList.do"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.foresttrip.go.kr/rep/or/orRsvt.do",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }
    data = {
        "hmpgId": hmpg_id,
        "searchDate": date_str,
        "dvcId": "01"
    }
    available_rooms = []
    try:
        res = requests.post(url, headers=headers, data=data, timeout=8)
        if res.status_code == 200:
            result = res.json()
            for room in result.get("rsvtList", []):
                if room.get("rsvtStatus") == "01":
                    available_rooms.append(room.get("fcltNm", "객실"))
    except Exception:
        pass
    return available_rooms

# ==========================================
# 3. 1회 순회 점검 실행
# ==========================================
now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"[{now_str}] 6대 휴양림 예약 현황 점검 시작 (대상일: {formatted_date})")

found_count = 0
for resort in TARGET_RESORTS:
    rooms = check_resort(resort["code"])
    if rooms:
        found_count += 1
        room_names = ", ".join(rooms)
        alert = (
            f"🚨 *[긴급 취소표 발생!]*\n\n"
            f"📍 *장소:* {resort['name']}\n"
            f"📅 *날짜:* {formatted_date}\n"
            f"🏠 *잔여 객실:* {room_names}\n\n"
            f"👉 [지금 즉시 예약하기]({RESERVATION_URL})"
        )
        print(f"🎉 {resort['name']} 취소표 발견: {room_names}")
        send_telegram(alert)
    time.sleep(1)

if found_count == 0:
    print("전체 매진 상태 확인 완료 (취소표 없음)")
