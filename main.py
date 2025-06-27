import os
import uuid
import json
from yt_dlp import YoutubeDL


from env import ENV, PROXY_URL, BUCKET_NAME

STORAGE_PATH = "./downloads" if ENV == "development" else "/function/storage/storage"
ENV_PATH = "." if ENV == "development" else "/function/storage/env"

COOKIE_PATH = os.path.join(ENV_PATH, 'cookies.txt')
print("COOKIE_PATH", COOKIE_PATH)


# Helper function to build yt-dlp options
def get_yt_dlp_opts(download_path=None, fmt="18"):
    opts = {
        'proxy': PROXY_URL,
        'cookiefile': COOKIE_PATH,
        'cachedir': False,
        'noplaylist': True
    }
    if download_path:
        opts.update({
            'outtmpl': download_path,
            'format': fmt
        })
    return opts

def handler(event, context):
    print('event:', event)
    print('context:', context)

    path = event.get("path", "/")
    query = event.get("queryStringParameters") or {}
    url = query.get("url")
    fmt = query.get("format", "18")

    if not url:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing 'url' parameter"})
        }

    try:
        if path == "/download":
            return handle_download(url, fmt)
        elif path == "/info":
            return handle_info(url)
        else:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Not found"})
            }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def handle_download(url, fmt):
    video_id = str(uuid.uuid4())
    file_name = f"{video_id}.mp4"
    download_path = os.path.join(STORAGE_PATH, file_name)

    ydl_opts = get_yt_dlp_opts(download_path=download_path, fmt=fmt)

    print("Starting downloading...")
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    public_url = f"https://storage.yandexcloud.net/{BUCKET_NAME}/{file_name}"
    return {
        "statusCode": 200,
        "body": json.dumps({"url": public_url})
    }

def handle_info(url):
    ydl_opts = get_yt_dlp_opts()

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    print("Returning full video info...")
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(info, default=str)
    }
