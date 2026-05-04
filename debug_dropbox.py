import requests
import json

# Thay the bang thong tin cua sep
APP_KEY = "m9sugup87hekz3d"
APP_SECRET = "bkzjbiikhirweaf"
REFRESH_TOKEN = "mPd5-2m8NqwAAAAAAAAAAaQnYG84WFDUrfsblY_xK6N_Q8TfZvv99JXvV2aTzKqI"

def test_dropbox():
    print("Checking Dropbox connection...")
    
    # 1. Access Token
    token_url = "https://api.dropbox.com/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": APP_KEY,
        "client_secret": APP_SECRET
    }
    
    try:
        res = requests.post(token_url, data=data)
        token_data = res.json()
        if res.status_code != 200:
            print(f"Error getting Access Token: {token_data.get('error_description')}")
            return
        
        access_token = token_data["access_token"]
        print("Success: Access Token retrieved!")

        # 2. List files
        print("\nFiles list visible to this App:")
        list_url = "https://api.dropboxapi.com/2/files/list_folder"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        list_data = {"path": "", "recursive": True}
        
        res = requests.post(list_url, headers=headers, json=list_data)
        list_res = res.json()
        
        if res.status_code != 200:
            print(f"Error listing files: {list_res}")
            return
            
        entries = list_res.get("entries", [])
        if not entries:
            print("--- EMPTY (No files found) ---")
            print("Check if you put files in Apps/Zinh Tran/ folder.")
        else:
            for entry in entries:
                print(f"- {entry['name']} ({entry['path_display']})")

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    test_dropbox()
