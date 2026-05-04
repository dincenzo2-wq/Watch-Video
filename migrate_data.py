import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

WEB_BASE_URL = os.getenv("WEB_BASE_URL")
WEB_API_KEY = os.getenv("WEB_API_KEY")
HEADERS = {"Authorization": f"Bearer {WEB_API_KEY}", "Content-Type": "application/json"}

import sys

# Fix encoding for Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def migrate_data():
    print(f"Starting migration on {WEB_BASE_URL}...")
    
    # 1. Fetch all places
    url = f"{WEB_BASE_URL}/api/places?limit=100"
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        print(f"Error fetching data: {res.text}")
        return
    
    places = res.json()
    count = 0
    
    for item in places:
        needs_update = False
        updates = {}
        
        for field in ["category", "type", "concept"]:
            val = item.get(field)
            if val and val.startswith("[") and val.endswith("]"):
                try:
                    # Try to parse as JSON
                    arr = json.loads(val)
                    if isinstance(arr, list):
                        new_val = ", ".join(arr)
                        updates[field] = new_val
                        needs_update = True
                except:
                    pass
        
        if needs_update:
            update_url = f"{WEB_BASE_URL}/api/places/{item['id']}"
            put_res = requests.put(update_url, json=updates, headers=HEADERS)
            if put_res.status_code == 200:
                print(f"✅ Fixed {field} for: {item.get('name') or item['id']}")
                count += 1
            else:
                print(f"❌ Failed to fix {item['id']}: {put_res.status_code}")
                
    print(f"\n✨ Done! Fixed {count} items.")

if __name__ == "__main__":
    migrate_data()
