from fastapi import FastAPI, Request
from main import handler as cloud_handler
import uvicorn
import json

app = FastAPI()

@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def catch_all(request: Request, path_name: str):
    # Mimic Yandex Cloud Function event structure
    query_params = dict(request.query_params)

    body = ""
    try:
        body_bytes = await request.body()
        body = body_bytes.decode("utf-8")
    except:
        pass

    event = {
        "path": f"/{path_name}",
        "httpMethod": request.method,
        "queryStringParameters": query_params,
        "body": body,
        "headers": dict(request.headers),
        "isBase64Encoded": False
    }

    # Context can be empty or mock
    context = {}

    print(f"Calling handler with path: /{path_name}")
    response = cloud_handler(event, context)

    # Return the response from the cloud handler
    # Yandex Cloud Function response format: {"statusCode": 200, "body": "...", "headers": {...}}
    status_code = response.get("statusCode", 200)
    response_body = response.get("body", "")
    headers = response.get("headers", {})

    # Try to parse body as JSON if it's a string, otherwise return as is
    try:
        if isinstance(response_body, str):
            content = json.loads(response_body)
            return content
    except:
        pass

    return response_body

if __name__ == "__main__":
    print("Starting Main.py Local Emulator...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
