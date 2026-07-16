from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_TITLE: str = "Backend Test API"
    APP_VERSION: str = "1.0.0"

    DATABASE_URL: str = "sqlite:///./test.db"

    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    OWNER_EMAIL: str = "owner@example.com"

    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"

    RATE_LIMIT: int = 5
    RATE_WINDOW: int = 60

    class Config:
        env_file = ".env"


settings = Settings()
