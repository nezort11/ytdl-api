import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env

PROXY_URL = os.getenv("PROXY_URL")
