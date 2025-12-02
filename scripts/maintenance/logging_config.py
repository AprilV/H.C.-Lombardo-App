"""
H.C. Lombardo NFL Analytics - Logging Configuration
Comprehensive logging system for all app activities
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Set up comprehensive logging for the application"""
    
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Generate log filename with date
    today = datetime.now().strftime('%Y%m%d')
    log_file = os.path.join(logs_dir, f'hc_lombardo_{today}.log')
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            # File handler with rotation (10MB max, keep 5 files)
            RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            ),
            # Console handler for immediate feedback
            logging.StreamHandler()
        ]
    )
    
    # Create specific loggers for different components
    app_logger = logging.getLogger('app')
    database_logger = logging.getLogger('database')
    scraper_logger = logging.getLogger('scraper')
    api_logger = logging.getLogger('api')
    
    return {
        'app': app_logger,
        'database': database_logger,
        'scraper': scraper_logger,
        'api': api_logger
    }

def log_activity(logger_name, level, message, **kwargs):
    """
    Log activity with additional context
    
    Args:
        logger_name: Name of the logger ('app', 'database', 'scraper', 'api')
        level: Logging level ('info', 'warning', 'error', 'debug')
        message: Main log message
        **kwargs: Additional context (user_action, data_count, etc.)
    """
    logger = logging.getLogger(logger_name)
    
    # Add context to message if provided
    if kwargs:
        context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        full_message = f"{message} | {context}"
    else:
        full_message = message
    
    # Log at appropriate level
    if level.lower() == 'info':
        logger.info(full_message)
    elif level.lower() == 'warning':
        logger.warning(full_message)
    elif level.lower() == 'error':
        logger.error(full_message)
    elif level.lower() == 'debug':
        logger.debug(full_message)
    else:
        logger.info(full_message)

if __name__ == "__main__":
    # Test the logging system
    loggers = setup_logging()
    
    log_activity('app', 'info', 'Logging system initialized', component='logging_config')
    log_activity('database', 'info', 'Test database connection', action='test')
    log_activity('scraper', 'info', 'Test scraper log', teams_processed=32)
    log_activity('api', 'info', 'Test API log', endpoint='test', status='success')
    
    print("✅ Logging system test complete! Check logs/ directory")