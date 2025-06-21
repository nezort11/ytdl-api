import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env

ENV = os.getenv("ENV", "production")
print("ENV", ENV)

BUCKET_NAME = os.getenv("BUCKET_NAME")
print("BUCKET_NAME", BUCKET_NAME)

PROXY_URL = os.getenv("PROXY_URL")
