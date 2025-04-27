import os
import uuid
import json
from yt_dlp import YoutubeDL

STORAGE_PATH = "/function/storage/storage"

# AWS Lambda compatible handler
def handler(event, context):
    print('event', event)
    event = event or {}
    query = event.get("queryStringParameters") or {}
    url = query.get("url")
    fmt = query.get("format", "18")  # default video format — 18 (mp4 360p)

    if not url:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing 'url' parameter"})
        }

    video_id = str(uuid.uuid4())
    file_name = f"{video_id}.mp4"
    file_path = os.path.join(STORAGE_PATH, file_name)

    ydl_opts = {
        'outtmpl': file_path,
        'format': fmt,
        # without ffmpeg - merge_output_format and ffmpeg_location
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        public_url = f"https://storage.yandexcloud.net/{os.environ['BUCKET_NAME']}/{file_name}"

        return {
            "statusCode": 200,
            "body": json.dumps({"url": public_url})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
