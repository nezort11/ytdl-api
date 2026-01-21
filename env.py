import os
from dotenv import load_dotenv

# Path to .env in the S3 mount for production
S3_ENV_PATH = "/function/storage/env/.env"

if os.path.exists(S3_ENV_PATH):
    print(f"Loading env from S3: {S3_ENV_PATH}")
    load_dotenv(S3_ENV_PATH)
else:
    load_dotenv()  # Load variables from local .env

# ENV is set to production using terraform env var
ENV = os.getenv("ENV", "development")
print("ENV", ENV)

BUCKET_NAME = os.getenv("BUCKET_NAME")
print("BUCKET_NAME", BUCKET_NAME)

PROXY_URL = os.getenv("PROXY_URL")
