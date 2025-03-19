import os
import tempfile
from dotenv import load_dotenv
from pydantic import BaseSettings

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class S3DetailSettings(BaseSettings):
    bucket: str
    presigned_url_expiration: int = 300  # 5 minutes


class S3Settings(BaseSettings):
    private: S3DetailSettings
    public: S3DetailSettings


class AWSConfig(BaseSettings):
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION = os.getenv("AWS_REGION", "")
    AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET", "")
    AWS_S3_ENDPOINT = os.getenv("AWS_S3_ENDPOINT", "")
    s3: S3Settings = S3Settings()


class Settings(BaseSettings):
    PROJECT_NAME = os.getenv("PROJECT_NAME", "FASTAPI BASE")
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    API_PREFIX = ""
    BACKEND_CORS_ORIGINS = ["*"]
    DATABASE_URL = os.getenv("SQL_DATABASE_URL", "")
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24 * 7  # Token expired after 7 days
    SECURITY_ALGORITHM = "HS256"
    LOGGING_CONFIG_FILE = os.path.join(BASE_DIR, "logging.ini")

    # environment
    environment: str = os.getenv("ENVIRONMENT", "local")

    # aws s3 config
    aws: AWSConfig = AWSConfig()
    saved_documents = tempfile.TemporaryDirectory().name


settings = Settings()
