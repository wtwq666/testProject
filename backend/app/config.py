"""环境变量配置，从 .env 读取"""
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # Kimi / 月之暗面
    KIMI_API_KEY: str = ""
    KIMI_MODEL: str = "moonshot-v1-8k"
    KIMI_BASE_URL: str = "https://api.moonshot.cn/v1"

    # 数据库
    DATABASE_URL: str = "sqlite:///./data/smart_data.db"
    SESSION_DB_URL: str = "sqlite:///./data/sessions.db"

    # 上下文窗口
    CONTEXT_WINDOW_SIZE: int = 10

    class Config:
        env_file = Path(__file__).resolve().parent.parent / ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
