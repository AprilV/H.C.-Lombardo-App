"""
H.C. Lombardo App Logging Configuration
Professional logging setup for the H.C. Lombardo application
"""

import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime
from .settings import settings

def setup_logging():
    """Configure logging for the H.C. Lombardo application"""
    
    # Ensure logs directory exists
    settings.LOGS_DIR.mkdir(exist_ok=True)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s | Line %(lineno)-4d | %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s'
    )
    
    # Create handlers
    
    # 1. Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # 2. Main Application Log File
    app_log_file = settings.LOGS_DIR / f"hc-lombardo-{datetime.now().strftime('%Y-%m-%d')}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        app_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # 3. Error Log File
    error_log_file = settings.LOGS_DIR / f"hc-lombardo-errors-{datetime.now().strftime('%Y-%m-%d')}.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    
    # 4. API Access Log
    api_log_file = settings.LOGS_DIR / f"hc-lombardo-api-{datetime.now().strftime('%Y-%m-%d')}.log"
    api_handler = logging.handlers.RotatingFileHandler(
        api_log_file,
        maxBytes=20*1024*1024,  # 20MB
        backupCount=7,
        encoding='utf-8'
    )
    api_handler.setLevel(logging.INFO)
    api_handler.setFormatter(simple_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    
    # Configure specific loggers
    
    # H.C. Lombardo App Logger
    app_logger = logging.getLogger('hc_lombardo')
    app_logger.setLevel(logging.DEBUG)
    
    # API Logger
    api_logger = logging.getLogger('hc_lombardo.api')
    api_logger.addHandler(api_handler)
    api_logger.setLevel(logging.INFO)
    
    # Uvicorn Logger Configuration
    uvicorn_access = logging.getLogger('uvicorn.access')
    uvicorn_access.addHandler(api_handler)
    
    # FastAPI Logger
    fastapi_logger = logging.getLogger('fastapi')
    fastapi_logger.setLevel(logging.INFO)
    
    # Suppress verbose third-party logs in production
    if not settings.DEBUG:
        logging.getLogger('transformers').setLevel(logging.WARNING)
        logging.getLogger('torch').setLevel(logging.WARNING)
        logging.getLogger('httpx').setLevel(logging.WARNING)
    
    # Log startup message
    app_logger.info("="*80)
    app_logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} - Logging System Initialized")
    app_logger.info(f"📁 Log Directory: {settings.LOGS_DIR}")
    app_logger.info(f"📊 Log Level: {settings.LOG_LEVEL}")
    app_logger.info(f"🔧 Debug Mode: {settings.DEBUG}")
    app_logger.info("="*80)

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    return logging.getLogger(f'hc_lombardo.{name}')

# Convenience loggers for different components
nfl_logger = get_logger('nfl')
text_logger = get_logger('text') 
api_logger = get_logger('api')
template_logger = get_logger('templates')
test_logger = get_logger('tests')