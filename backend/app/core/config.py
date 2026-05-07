"""
智能会议助手 - 后端配置
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "智能会议助手"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8001

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./meeting_assistant.db"

    # JWT 配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时

    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB

    # AI / LLM 服务配置（DeepSeek，兼容 OpenAI 格式）
    LLM_API_KEY: str = ""
    LLM_API_BASE_URL: str = "https://api.deepseek.com"
    LLM_MODEL_NAME: str = "deepseek-chat"
    LLM_MAX_TOKENS: int = 4096
    LLM_TEMPERATURE: float = 0.7

    # WebSocket 配置
    WS_HEARTBEAT_INTERVAL: int = 30  # 秒

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# 确保上传目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
