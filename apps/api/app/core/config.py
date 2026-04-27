from urllib.parse import quote

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = Field(default="development", alias="APP_ENV")
    app_name: str = Field(default="orbis", alias="APP_NAME")

    api_secret_key: str = Field(default="change_me_to_a_long_random_value", alias="API_SECRET_KEY")
    api_access_token_expire_minutes: int = Field(default=30, alias="API_ACCESS_TOKEN_EXPIRE_MINUTES")
    api_refresh_token_expire_days: int = Field(default=30, alias="API_REFRESH_TOKEN_EXPIRE_DAYS")

    api_rate_limit_requests: int = Field(default=30, alias="API_RATE_LIMIT_REQUESTS")
    api_rate_limit_window_seconds: int = Field(default=60, alias="API_RATE_LIMIT_WINDOW_SECONDS")
    api_key_header_name: str = Field(default="X-API-Key", alias="API_KEY_HEADER_NAME")

    postgres_db: str = Field(default="orbis", alias="POSTGRES_DB")
    postgres_user: str = Field(default="orbis", alias="POSTGRES_USER")
    postgres_password: str = Field(default="change_me", alias="POSTGRES_PASSWORD")
    postgres_host: str = Field(default="db", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL")
    openai_base_url: str = Field(default="https://api.openai.com/v1", alias="OPENAI_BASE_URL")
    openai_timeout_seconds: int = Field(default=60, alias="OPENAI_TIMEOUT_SECONDS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        quoted_user = quote(self.postgres_user, safe="")
        quoted_password = quote(self.postgres_password, safe="")
        return f"postgresql+psycopg://{quoted_user}:{quoted_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


settings = Settings()
