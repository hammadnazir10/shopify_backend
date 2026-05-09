"""Application settings loaded from environment / .env."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
    )

    # ---- LLM ----
    openai_api_key: str = Field(default="", description="OpenAI API key")
    model_name: str = Field(default="gpt-4o-mini", description="Chat model used for design briefs")
    llm_temperature: float = Field(default=0.7, ge=0.0, le=2.0)

    # ---- Image generation ----
    gemini_api: str = Field(default="", description="Google Gemini API key")
    imagen_text_model: str = "imagen-4.0-generate-001"
    imagen_reference_model: str = "gemini-2.5-flash-image"
    image_output_size: tuple[int, int] = (1080, 1080)

    # ---- AWS S3 ----
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-2"
    s3_bucket_name: str = "yss-jewelry-images"

    # ---- Database ----
    database_url: str = "postgresql://postgres:Pakistan%40786@localhost:5432/shopify"

    # ---- Local storage ----
    temp_folder: str = "./temp"

    # ---- Upload limits ----
    max_upload_bytes: int = 10 * 1024 * 1024
    allowed_image_mime_types: tuple[str, ...] = (
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
    )

    @property
    def temp_path(self) -> Path:
        path = Path(self.temp_folder)
        path.mkdir(parents=True, exist_ok=True)
        return path


settings = Settings()
settings.temp_path  # eagerly create the temp directory
