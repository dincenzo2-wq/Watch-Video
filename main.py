import os
import time
import json
import requests
import yt_dlp
from google import genai
import sys
from pathlib import Path
from dotenv import load_dotenv

# 0. Fix encoding for Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# 1. Khởi tạo
load_dotenv()

# ===== CẤU HÌNH HỆ THỐNG =====
WEB_BASE_URL = os.getenv("WEB_BASE_URL")
WEB_API_KEY = os.getenv("WEB_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.1-flash-lite-preview" # Model mới nhất cho phân tích video

client = genai.Client(api_key=GEMINI_API_KEY)

# Bộ nhớ tạm để bỏ qua các ID lỗi
BLACKLIST = set() 
HEADERS = {"Authorization": f"Bearer {WEB_API_KEY}", "Content-Type": "application/json"}

# Thư mục tải video
PROJECT_DIR = Path(__file__).resolve().parent
DOWNLOAD_DIR = PROJECT_DIR / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Danh sách mở rộng (Khớp với Metadata của Web)
CATEGORIES = ['Lưu Trú', 'Sức Khỏe', 'Giải Trí', 'Ăn Uống', 'Du Lịch', 'Shopping']
TYPES = ['Nhà Sách', 'Hẹn Hò', 'Giày Dép', 'Thể Thao', 'Khách Sạn', 'Homestay', 'Check In', 'Game', 'Nước Hoa', 'Khu Vui Chơi', 'Đồ Điện Tử', 'Gym', 'Music', 'Rạp Chiếu Phim', 'Nhà Hàng', 'Quán Ăn', 'Quán Nước', 'Trekking', 'Quà Tặng', 'Quần Áo', 'Hoa', 'Tinh Dầu']
CONCEPTS = ['Pizza', 'Kem', 'Dimsum', 'Món Thái', 'Ramen', 'Đồ Chay', 'Bò', 'Cơm', 'Mì', 'Gà', 'Lẩu Nướng', 'Món Trung', 'Món Hàn', 'Món Nhật', 'Nhậu Nhẹt', 'Hải Sản', 'Chè', 'Ăn Vặt', 'Ăn No', 'Món Việt', 'Món Âu', 'Rooftop', 'Coffee In Bed', 'Accoustic', 'Glamping', 'Chó Mèo', 'Bar']
DISTRICTS = ['Quận 1', 'Quận 2', 'Quận 3', 'Quận 4', 'Quận 5', 'Quận 6', 'Quận 7', 'Quận 8', 'Quận 9', 'Quận 10', 'Quận 11', 'Quận 12', 'Bình Thạnh', 'Phú Nhuận', 'Gò Vấp', 'Tân Bình', 'Tân Phú', 'Bình Tân', 'Thủ Đức']

# ===== HÀM XỬ LÝ =====

def fetch_one_item():
    # Sử dụng status=all để lấy cả bản nháp (draft)
    url = f"{WEB_BASE_URL}/api/places?status=all&limit=100"
    try:
        res = requests.get(url, headers=HEADERS, timeout=30)
        if res.status_code == 200:
            data = res.json()
            if not data or not isinstance(data, list):
                return None
            
            # Lọc các bản nháp chưa được xử lý
            draft_items = [i for i in data if str(i.get("status")).lower() == "draft" and i["id"] not in BLACKLIST]
            
            print(f"📊 Tổng số địa điểm: {len(data)} | Bản nháp chờ xử lý: {len(draft_items)}")
            
            if draft_items:
                return draft_items[0]
        else:
            print(f"⚠️ Fetch Error: Status {res.status_code}")
    except Exception as e:
        print(f"⚠️ Fetch Exception: {e}")
    return None

def analyze_video_with_gemini(video_path: Path):
    """Gửi video cho AI phân tích"""
    try:
        video_file = client.files.upload(file=str(video_path))
        while video_file.state == "PROCESSING":
            time.sleep(5)
            video_file = client.files.get(name=video_file.name)
        
        prompt = f"""
        Phân tích video TikTok này và trả về JSON thông tin địa điểm.
        QUY TẮC: 
        1. KHÔNG TỰ DỊCH TIẾNG ANH.
        2. category, type, concept: CHỈ CHỌN TRONG LIST DƯỚI ĐÂY (Có thể chọn nhiều, trả về mảng):
           - category: {CATEGORIES}
           - type: {TYPES}
           - concept: {CONCEPTS}
        3. district: CHỈ CHỌN TRONG: {DISTRICTS}
        4. desc: Mô tả ngắn gọn sự đặc sắc của nơi này (tối đa 2 câu).
        
        JSON format: {{
            "place_name": "", 
            "address": "", 
            "desc": "",
            "category": [], 
            "type": [], 
            "concept": [],
            "district": "",
            "city": "Hồ Chí Minh",
            "province": "Hồ Chí Minh"
        }}
        """
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[video_file, prompt],
            config={
                "response_mime_type": "application/json"
            }
        )
        client.files.delete(name=video_file.name)
        return response.text
    except Exception as e:
        raise Exception(f"AI Error: {e}")

def update_to_web(video_id, analysis_result):
    """Đẩy dữ liệu JSON lên Web"""
    url = f"{WEB_BASE_URL}/api/places/{video_id}"
    
    try:
        # Xử lý JSON linh hoạt (loại bỏ markdown block nếu có)
        clean_json = analysis_result.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json.replace("```json", "").replace("```", "").strip()
        
        raw = json.loads(clean_json)
        data = raw[0] if isinstance(raw, list) else raw
        
        # Hàm helper xử lý cả list và string từ Gemini
        def ensure_list(val):
            if isinstance(val, list): return val
            if isinstance(val, str): return [v.strip() for v in val.split(",") if v.strip()]
            return []

        # Lọc và Chuẩn hóa Tag thành chuỗi cách nhau bởi dấu phẩy (D1 format)
        clean_cat = ", ".join([c for c in ensure_list(data.get("category")) if c in CATEGORIES])
        clean_typ = ", ".join([t for t in ensure_list(data.get("type")) if t in TYPES])
        clean_con = ", ".join([cp for cp in ensure_list(data.get("concept")) if cp in CONCEPTS])

        # Khớp chính xác với Schema của D1 (Database)
        payload = {
            "name": str(data.get("place_name") or "Review"),
            "desc": str(data.get("desc") or ""),
            "address": str(data.get("address") or "Đang cập nhật"),
            "category": clean_cat,
            "type": clean_typ,
            "concept": clean_con,
            "district": str(data.get("district") or ""),
            "city": str(data.get("city") or "Hồ Chí Minh"),
            "province": str(data.get("province") or "Hồ Chí Minh"),
            "status": "published", 
            "processed": 1         
        }

        # Sử dụng PATCH theo tài liệu của bạn
        res = requests.patch(url, json=payload, headers=HEADERS, timeout=30)
        if res.ok:
            print(f"📡 Web phản hồi (PATCH {url}): {res.status_code}")
            return True
        else:
            print(f"⚠️ PATCH {url} thất bại: {res.status_code} - {res.text}")
        
        return False
    except Exception as e:
        print(f"❌ Update Error: {e}")
        return False

# ===== LUỒNG VẬN HÀNH CHÍNH =====

def run_workflow():
    print("\n" + "—"*45)
    item = fetch_one_item()
    if not item: return "EMPTY"

    video_id = item["id"]
    tiktok_url = item.get("linkSocial") or item.get("tiktok_url")
    
    if not tiktok_url:
        print(f"⚠️ Không tìm thấy link video cho ID: {video_id}")
        BLACKLIST.add(video_id)
        return False
    video_path = DOWNLOAD_DIR / f"{video_id}.mp4"

    try:
        print(f"🎬 ID: {video_id} | Đang tải video từ: {tiktok_url}")
        ydl_opts = {
            "outtmpl": str(video_path),
            "quiet": True,
            "no_warnings": True,
            "impersonate": "chrome",
            "extractor_retries": 3,
            "socket_timeout": 30,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([tiktok_url])
        
        print(f"🧠 Gemini đang phân tích nội dung...")
        result = analyze_video_with_gemini(video_path)
        
        if result and update_to_web(video_id, result):
            print(f"✅ THÀNH CÔNG: {video_id}")
            return True

    except Exception as e:
        print(f"❌ THẤT BẠI: {e}")
        BLACKLIST.add(video_id)
        return False
    finally:
        # TỰ ĐỘNG XÓA VIDEO SAU KHI XỬ LÝ (Dù thành công hay lỗi)
        if video_path.exists():
            video_path.unlink()
            print(f"🗑️ Đã xóa video: {video_id}.mp4")

def main():
    print("🚀 BOT AUTO CONTENT (BẢN KHÔNG ẢNH): KHỞI CHẠY")
    try:
        while True:
            status = run_workflow()
            
            if status == "EMPTY":
                print("\n🏁 HOÀN TẤT: Không còn video nào chờ xử lý.")
                if os.getenv("GITHUB_ACTIONS") == "true":
                    print("🚀 Đang chạy trên GitHub Actions: Tự động thoát để hoàn tất Workflow.")
                    break
                print("⏳ Nghỉ 5 phút trước khi kiểm tra lại...")
                time.sleep(300) # Nghỉ 5 phút thay vì thoát hẳn để run.bat tiếp tục
                continue
            
            if status is True:
                print("⏳ Nghỉ 2 phút bảo vệ API...")
                time.sleep(120)
            else:
                print("⚠️ Lỗi nhẹ, thử lại sau 30 giây...")
                time.sleep(30)
                continue
    except KeyboardInterrupt:
        print("\n🛑 Đã dừng Bot theo yêu cầu.")
        sys.exit(0)
    except Exception as e:
        print(f"🔥 LỖI HỆ THỐNG NGHIÊM TRỌNG: {e}")
        time.sleep(10)
        sys.exit(1) # Thoát với mã lỗi để run.bat biết và restart

if __name__ == "__main__":
    main()