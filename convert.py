import requests

# API Key của sếp
IMGBB_API_KEY = "012c12a0313b028a4170521a52b78fd4"

def convert_link():
    print("🚀 MÁY CHUYỂN LINK VĨNH VIỄN ĐANG CHẠY...")
    print("------------------------------------------")
    print("Sếp chỉ cần dán link ảnh tạm (FB/TikTok) vào đây rồi nhấn Enter.")
    print("Gõ 'exit' để dừng tool.\n")

    while True:
        temp_url = input("🔗 https://scontent.fsgn2-5.fna.fbcdn.net/v/t39.30808-6/487824967_2052214548624296_3360867362527204002_n.jpg?_nc_cat=111&ccb=1-7&_nc_sid=e06c5d&_nc_eui2=AeFnOWv0b1m2uKdt03ADofnR_z6k2K-XsTH_PqTYr5exMbsaz5K3mXi6p_L-1rWcIsT2KPaY99jEDBJqfuMoRMkO&_nc_ohc=Qh0OvW_RF1cQ7kNvwHmic6j&_nc_oc=AdqSXE1cVWs-A4nmmS4yUfO3CNg5LiRoDOO7WdT04u9bgGxedjEBO9BHbpR5iyiznfk&_nc_zt=23&_nc_ht=scontent.fsgn2-5.fna&_nc_gid=GeIIYUHqlNPd-6oud7Is4w&_nc_ss=7a3a8&oh=00_Af3vWRb7DU1c_GNoNtVqAJyMW_bwFxAf5ojMW0GHLkygug&oe=69ED35C6 ").strip()
        
        if temp_url.lower() == 'exit':
            break
        if not temp_url:
            continue

        print("⏳ Đang xử lý...")
        try:
            # Tải và Đẩy lên ImgBB
            img_data = requests.get(temp_url, timeout=15).content
            res = requests.post(
                "https://api.imgbb.com/1/upload",
                params={"key": IMGBB_API_KEY},
                files={"image": img_data}
            )
            
            if res.ok:
                perm_link = res.json()["data"]["url"]
                print(f"✅ LINK VĨNH VIỄN CỦA SẾP ĐÂY:")
                print(f"{perm_link}") # Sếp bôi đen cái này copy là xong
                print("-" * 30)
            else:
                print(f"❌ Lỗi rồi sếp ơi: {res.text}")
        except Exception as e:
            print(f"⚠️ Có biến: {e}")

if __name__ == "__main__":
    convert_link()