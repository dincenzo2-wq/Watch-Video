import requests

APP_KEY = "m9sugup87hekz3d"
APP_SECRET = "bkzjbiikhirweaf"
AUTH_CODE = "QmYurMLq4b8AAAAAAAAAGOYvnFkDUPrz8I0hawYd-ghA"

def exchange_code():
    url = "https://api.dropbox.com/oauth2/token"
    data = {
        "code": AUTH_CODE,
        "grant_type": "authorization_code",
        "client_id": APP_KEY,
        "client_secret": APP_SECRET
    }
    res = requests.post(url, data=data)
    print(res.json())

if __name__ == "__main__":
    exchange_code()
