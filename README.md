# ytdl-api

Test youtube videos:

- https://www.youtube.com/watch?v=224plb3bCog

## Production

Edit `terraform.tfvars`

```sh
./deploy.sh
```

## Development

```sh
./.venv/bin/python ./dev.py
```

http://127.0.0.1:8000/download?url=https://www.youtube.com/watch?v=224plb3bCog

```
Starting uvicorn server...
INFO:     Started server process [2812]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
Inside download video endpoint
Started downloading...
[youtube] Extracting URL: https://www.youtube.com/watch?v=224plb3bCog
[youtube] 224plb3bCog: Downloading webpage
[youtube] 224plb3bCog: Downloading tv client config
[youtube] 224plb3bCog: Downloading player 91e7c654-main
[youtube] 224plb3bCog: Downloading tv player API JSON
[youtube] 224plb3bCog: Downloading ios player API JSON


ERROR: [youtube] 224plb3bCog: Sign in to confirm you’re not a bot. Use --cookies-from-browser or --cookies for the authentication. See  https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp  for how to manually pass cookies. Also see  https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies  for tips on effectively exporting YouTube cookies

ERROR:    Exception in ASGI application

yt_dlp.utils.ExtractorError: [youtube] 224plb3bCog: Sign in to confirm you’re not a bot. Use --cookies-from-browser or --cookies for the authentication. See  https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp  for how to manually pass cookies. Also see  https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies  for tips on effectively exporting YouTube cookies
```
