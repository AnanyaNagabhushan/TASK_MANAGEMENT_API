import os
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables from .env
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me")
    JWT_VERIFY_SUB = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

    API_TITLE = "Task Management API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

# Optional: print out to verify env vars loaded correctly (for debugging only)
if __name__ == "__main__":
    print("Loaded DATABASE_URL:", os.getenv("DATABASE_URL"))
    print("Loaded JWT_SECRET_KEY:", os.getenv("JWT_SECRET_KEY"))
