"""
Configuration settings for 68GB Game API Crawler
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "68GB Game API Crawler"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./game_data.db"
    
    # 68GB Game settings
    GAME_URL: str = "https://68gbvn25.biz/"
    CRAWL_INTERVAL: int = 30  # seconds
    MAX_RETRIES: int = 3
    REQUEST_TIMEOUT: int = 30
    
    # Selenium settings
    HEADLESS_BROWSER: bool = True
    BROWSER_TIMEOUT: int = 30
    
    # API settings
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list = ["*"]
    
    # Notification settings
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None
    EMAIL_SMTP_SERVER: Optional[str] = None
    EMAIL_SMTP_PORT: int = 587
    EMAIL_USERNAME: Optional[str] = None
    EMAIL_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None
    EMAIL_TO: Optional[str] = None
    
    # Webhook settings
    WEBHOOK_URL: Optional[str] = None
    WEBHOOK_SECRET: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()

# Game specific settings
GAME_TYPES = {
    "tai_xiu": {
        "name": "Tài Xỉu",
        "endpoint": "/tai-xiu",
        "md5_field": "result_md5"
    },
    "ban_do": {
        "name": "Bàn Đỏ", 
        "endpoint": "/ban-do",
        "md5_field": "result_md5"
    }
}

# Database table names
TABLE_NAMES = {
    "game_results": "game_results",
    "game_sessions": "game_sessions", 
    "notifications": "notifications",
    "api_logs": "api_logs"
}
