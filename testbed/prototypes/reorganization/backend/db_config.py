"""
PostgreSQL Database Configuration
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection settings
DATABASE_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'postgres'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

# Or use connection URL
DATABASE_URL = os.getenv('DATABASE_URL', '')

def get_connection_string():
    """Get PostgreSQL connection string"""
    if DATABASE_URL:
        return DATABASE_URL
    
    return f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['dbname']}"
