from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
    )

    openai_api_key: str = ""
    model_name: str = "gpt-4o-mini"
    gemini_api: str = ""


settings = Settings()
