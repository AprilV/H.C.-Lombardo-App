"""
H.C. Lombardo App Configuration
Central configuration management for the H.C. Lombardo application
"""

import os
from pathlib import Path
from typing import Optional

# Base directory paths
BASE_DIR = Path(__file__).parent.parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = BASE_DIR / "backup"

class Settings:
    """Application settings and configuration"""
    
    # Application Info
    APP_NAME: str = "H.C. Lombardo App"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Professional H.C. Lombardo Application with FastAPI and Jinja2"
    
    # Server Configuration
    HOST: str = "127.0.0.1"
    PORT: int = 8001
    DEBUG: bool = True
    RELOAD: bool = True
    
    # Directory Paths
    STATIC_DIR: Path = STATIC_DIR
    TEMPLATES_DIR: Path = TEMPLATES_DIR
    LOGS_DIR: Path = LOGS_DIR
    DATA_DIR: Path = DATA_DIR
    BACKUP_DIR: Path = BACKUP_DIR
    
    # API Configuration
    API_TITLE: str = "H.C. Lombardo API"
    API_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    
    # Database Configuration
    NFL_DB_PATH: Path = BASE_DIR / "nfl_betting_database" / "sports_betting.db"
    TEXT_MODEL_PATH: Optional[Path] = None
    
    # Theme Configuration
    DEFAULT_THEME: str = "default"
    AVAILABLE_THEMES: list = ["default", "nfl", "text", "corporate", "dark"]
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Path = LOGS_DIR / "hc-lombardo.log"
    
    # Security Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "hc-lombardo-secret-key")
    ALLOWED_HOSTS: list = ["localhost", "127.0.0.1", "0.0.0.0"]
    
    # External API Settings
    EXTERNAL_API_TIMEOUT: int = 30
    RATE_LIMIT: int = 100  # requests per minute
    
    # Template Settings
    TEMPLATE_AUTO_RELOAD: bool = DEBUG
    TEMPLATE_CACHE_SIZE: int = 50
    
    # Static Files Settings
    STATIC_URL: str = "/static"
    STATIC_MAX_AGE: int = 3600  # 1 hour cache
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist"""
        directories = [
            cls.LOGS_DIR,
            cls.DATA_DIR,
            cls.BACKUP_DIR,
            cls.STATIC_DIR / "css",
            cls.STATIC_DIR / "js", 
            cls.STATIC_DIR / "images",
            cls.TEMPLATES_DIR / "components",
            cls.TEMPLATES_DIR / "pages"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        print(f"✅ Created directory structure for {cls.APP_NAME}")

class DevelopmentSettings(Settings):
    """Development-specific settings"""
    DEBUG: bool = True
    RELOAD: bool = True
    LOG_LEVEL: str = "DEBUG"
    TEMPLATE_AUTO_RELOAD: bool = True

class ProductionSettings(Settings):
    """Production-specific settings"""
    DEBUG: bool = False
    RELOAD: bool = False
    LOG_LEVEL: str = "INFO"
    TEMPLATE_AUTO_RELOAD: bool = False
    STATIC_MAX_AGE: int = 86400  # 24 hours cache

class TestingSettings(Settings):
    """Testing-specific settings"""
    DEBUG: bool = True
    LOG_LEVEL: str = "WARNING"
    NFL_DB_PATH: Path = BASE_DIR / "tests" / "test_data" / "test_sports_betting.db"

# Environment-based configuration
def get_settings() -> Settings:
    """Get settings based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()

# Global settings instance
settings = get_settings()

# Ensure directories exist
settings.create_directories()