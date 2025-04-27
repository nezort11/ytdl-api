import yt_dlp
import os
import uuid
import json
from yt_dlp import YoutubeDL
# FastAPI
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse

app = FastAPI()
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.get("/download")
async def download_video(url: str = Query(..., title="YouTube Video URL")):
    """
    Download a YouTube video and return the file.
    """
    print('Inside download video endpoint')
    ydl_opts = {
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'format': '18',
        # 'merge_output_format': 'mp4',
    }

    print('Started downloading...')
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).rsplit(".", 1)[0] + ".mp4"

    print('Returing file response...')
    return FileResponse(filename, media_type='video/mp4', filename=os.path.basename(filename))

STORAGE_PATH = "/function/storage/storage"

if __name__ == "__main__":
    import uvicorn
    print('Starting uvicorn server...')
    uvicorn.run(app, host="0.0.0.0", port=8000)

