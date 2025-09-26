# H.C. Lombardo App - Config Module

This folder contains configuration files for the H.C. Lombardo application.

## Files

- `settings.py` - Main application settings and configuration
- `logging_config.py` - Logging configuration and setup
- `__init__.py` - Makes this a Python package

## Usage

```python
from config.settings import settings
from config.logging_config import setup_logging, get_logger

# Initialize logging
setup_logging()

# Get application logger
logger = get_logger('main')
logger.info("H.C. Lombardo App starting...")

# Use settings
print(f"App Name: {settings.APP_NAME}")
print(f"Static Directory: {settings.STATIC_DIR}")
```