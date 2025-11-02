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
def get_yt_dlp_opts(download_path=None, fmt=None, playlistend=None):
    opts = {
        'proxy': PROXY_URL,
        'cookiefile': COOKIE_PATH,
        'cachedir': False,
        'noplaylist': False if playlistend else True,  # allow playlists
        # Optimize for speed
        'concurrent_fragment_downloads': 4,  # Download fragments in parallel
        'fragment_retries': 3,  # Retry failed fragments
        'retries': 3,  # Retry failed downloads
        'http_chunk_size': 10485760,  # 10MB chunks for better throughput
    }
    if download_path:
        # Use flexible format selector with fallbacks
        # Priority: format 18 (360p ~10MB) -> 480p or lower -> worst available
        # This keeps file sizes reasonable (10-30 MB typical) instead of downloading huge HD files
        if fmt and fmt not in ["best", "worst"]:
            # If specific format requested, try it with fallbacks
            format_selector = f"{fmt}/bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best[height<=480]/worst"
        else:
            # Default: prioritize format 18 (360p), fallback to 480p max, then worst
            format_selector = "18/bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best[height<=480]/worst"

        opts.update({
            'outtmpl': download_path,
            'format': format_selector,
            # Merge video+audio into single file if needed
            'merge_output_format': 'mp4',
        })
    if playlistend:
        opts['playlistend'] = playlistend
    return opts

def handler(event, context):
    print('event:', event)
    print('context:', context)

    path = event.get("path", "/")
    query = event.get("queryStringParameters") or {}
    url = query.get("url")
    fmt = query.get("format")  # Default None -> will use format 18 (360p) fallback

    if not url:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing 'url' parameter"})
        }

    try:
        if path == "/download":
            return handle_download(url, fmt)
        elif path == "/download-url":
            # New endpoint: returns direct download URL without downloading
            return handle_download_url(url, fmt)
        elif path == "/info":
            return handle_info(url)
        elif path == "/playlist":
            # Optional ?limit=5 query parameter
            limit = int(query.get("limit", 5))
            return handle_playlist(url, limit)
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

def handle_download_url(url, fmt):
    """
    New endpoint: Returns direct YouTube download URL without downloading the video.
    This avoids the 5-minute API Gateway timeout for large videos.

    The returned URL:
    - Is a direct download link from YouTube's servers
    - Expires after ~6 hours
    - Can be used by the bot to download directly (bypassing our gateway)
    """
    print(f"Getting direct download URL for: {url}, format: {fmt}")

    ydl_opts = get_yt_dlp_opts(fmt=fmt)

    with YoutubeDL(ydl_opts) as ydl:
        print("Extracting video info...")
        info = ydl.extract_info(url, download=False)

        if not info:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Video not found or unavailable"})
            }

        # Get the requested format or best available
        formats = info.get('formats', [])
        selected_format = None

        if fmt and fmt not in ["best", "worst"]:
            # Try to find exact format match
            for f in formats:
                if str(f.get('format_id')) == str(fmt):
                    selected_format = f
                    break

        if not selected_format:
            # Fallback: use yt-dlp's format selection logic
            # This gives us the format that yt-dlp would download
            requested_formats = info.get('requested_formats')
            if requested_formats:
                # For merged video+audio, we need both URLs
                # But for simplicity, return the video URL (usually contains audio)
                selected_format = requested_formats[0]
            else:
                # Single format (has both video and audio)
                selected_format = info

        if not selected_format or not selected_format.get('url'):
            return {
                "statusCode": 404,
                "body": json.dumps({
                    "error": "No suitable format found with direct URL",
                    "available_formats": [
                        {"format_id": f.get("format_id"), "ext": f.get("ext"), "quality": f.get("format_note")}
                        for f in formats[:10]  # Return first 10 formats as reference
                    ]
                })
            }

        direct_url = selected_format['url']

        print(f"Found direct URL: {direct_url[:100]}...")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "url": direct_url,
                "format_id": selected_format.get('format_id'),
                "ext": selected_format.get('ext', 'mp4'),
                "quality": selected_format.get('format_note'),
                "filesize": selected_format.get('filesize'),
                "expires_in_hours": 6,  # YouTube URLs typically expire in 6 hours
                "title": info.get('title'),
                "duration": info.get('duration')
            })
        }

def handle_download(url, fmt):
    video_id = str(uuid.uuid4())
    ext = "m4a" if fmt == "m4a" else "mp4"
    file_name = f"{str(uuid.uuid4())}.{ext}"
    download_path = os.path.join(STORAGE_PATH, file_name)

    ydl_opts = get_yt_dlp_opts(download_path=download_path, fmt=fmt)

    with YoutubeDL(ydl_opts) as ydl:
        print("Getting video info...")
        info = ydl.extract_info(url, download=False)
        print(json.dumps(info.get("formats", []), indent=2))

        print("Starting downloading...")
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

    # print("Scraping youtube video title...")
    # title = scrape_video_title(url)
    # print("Scraped youtube title:", title)
    # info["title"] = title

    print("Returning full video info...")
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(info, default=str)
    }

def handle_playlist(url, limit=5):
    """
    Extract playlist metadata and return the 'limit' most
    recently uploaded videos.
    """
    ydl_opts = get_yt_dlp_opts(playlistend=limit)

    print("Extracting playlist info...")
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    # `entries` is a list of video‐info dicts
    entries = info.get("entries") or []
    print("entries length:", len(entries))

    # Filter out any None entries and those without upload_date
    filtered = [e for e in entries if e and e.get("upload_date")]
    print("filtered entries length:", len(filtered))

    # Sort by upload_date descending (newest first)
    filtered.sort(key=lambda e: e["upload_date"], reverse=True)

    latest = filtered[:limit]
    print("latest entries length:", len(latest))

    # Only return a subset of fields per video
    result = []
    for e in latest:
        print("element:", e)
        result.append({
            "id": e.get("id"),
            "title": e.get("title"),
            "url": e.get("webpage_url"),
            "uploader": e.get("uploader"),
            "upload_date": e.get("upload_date"),
            "duration": e.get("duration"),
        })

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "playlist_id": info.get("id"),
            "title": info.get("title"),
            "entries_returned": len(result),
            "videos": result
        }, default=str)
    }
