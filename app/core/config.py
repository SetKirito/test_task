import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_TITLE: str = "Backend Test API"
    APP_VERSION: str = "1.0.0"


settings = Settings()
