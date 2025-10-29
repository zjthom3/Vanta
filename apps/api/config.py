from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")

    postgres_url: str = "postgresql+psycopg://vanta:vanta@localhost:5432/vanta"
    redis_url: str = "redis://localhost:6379/0"
    openai_api_key: str | None = None
    s3_endpoint: str = "http://localhost:9000"
    s3_bucket: str = "vanta"
    s3_access_key: str | None = None
    s3_secret_key: str | None = None


settings = Settings()
