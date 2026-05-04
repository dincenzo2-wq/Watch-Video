import yt_dlp
import os

def test_download():
    url = "https://vt.tiktok.com/ZS9NjxE4M/"
    print(f"Testing download for: {url}")
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'test_video.mp4',
        'quiet': False,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("Download successful!")
    except Exception as e:
        print(f"Download failed: {e}")

if __name__ == "__main__":
    test_download()
