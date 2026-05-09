from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
    )

    openai_api_key: str = ""
    model_name: str = "gpt-4o-mini"
    gemini_api: str = ""

    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-2"
    s3_bucket_name: str = "yss-jewelry-images"

    database_url: str = "postgresql://postgres:Pakistan%40786@localhost:5432/shopify"

    # Temp folder for reference images
    temp_folder: str = "./temp"


settings = Settings()

# Create temp folder on startup
temp_path = Path(settings.temp_folder)
temp_path.mkdir(exist_ok=True)
