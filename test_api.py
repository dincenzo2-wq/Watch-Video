import requests
import os
from dotenv import load_dotenv

load_dotenv()

WEB_BASE_URL = os.getenv("WEB_BASE_URL")
WEB_API_KEY = os.getenv("WEB_API_KEY")
HEADERS = {"Authorization": f"Bearer {WEB_API_KEY}", "Content-Type": "application/json"}

def test_api():
    url = f"{WEB_BASE_URL}/api/places?status=draft"
    print(f"Testing URL: {url}")
    try:
        res = requests.get(url, headers=HEADERS, timeout=30)
        print(f"Status Code: {res.status_code}")
        data = res.json()
        print(f"Found {len(data)} items.")
        if data:
            print("First item keys:", data[0].keys())
            print("First item linkSocial:", data[0].get("linkSocial"))
            print("First item tiktok_url:", data[0].get("tiktok_url"))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
