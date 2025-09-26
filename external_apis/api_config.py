#!/usr/bin/env python3
"""
API Configuration
Configuration file for external API keys and settings
"""

import os
from typing import Dict

class APIKeys:
    """Centralized API key management"""
    
    def __init__(self):
        # API-SPORTS NFL API
        # Option 1: Set via environment variable (recommended)
        # Option 2: Replace "PASTE_YOUR_API_KEY_HERE" with your actual key below
        self.api_sports_nfl_key = os.getenv("API_SPORTS_NFL_KEY", "PASTE_YOUR_API_KEY_HERE")
        
        # Other potential API keys
        self.rapidapi_key = os.getenv("RAPIDAPI_KEY", "YOUR_RAPIDAPI_KEY_HERE")
        self.sports_data_io_key = os.getenv("SPORTS_DATA_IO_KEY", "YOUR_SPORTS_DATA_IO_KEY")
        
        # Validate keys
        self.validate_keys()
    
    def validate_keys(self):
        """Check if API keys are properly set"""
        if self.api_sports_nfl_key == "YOUR_API_KEY_HERE" or self.api_sports_nfl_key == "your_api_key_here":
            print("⚠️  Warning: API-SPORTS NFL API key not set")
            print("   Option 1: Set environment variable: API_SPORTS_NFL_KEY")
            print("   Option 2: Update api_config.py with your actual key")
            print("   Option 3: Run setup_api_key.bat")
    
    def get_api_sports_key(self) -> str:
        """Get API-SPORTS NFL API key"""
        return self.api_sports_nfl_key
    
    def is_api_key_valid(self, service: str = "api_sports") -> bool:
        """Check if API key is set and not default"""
        if service == "api_sports":
            return (self.api_sports_nfl_key != "YOUR_API_KEY_HERE" and 
                   self.api_sports_nfl_key != "your_api_key_here")
        return False
    
    def get_headers(self, service: str = "api_sports") -> Dict[str, str]:
        """Get headers for API requests"""
        if service == "api_sports":
            return {
                "X-RapidAPI-Key": self.api_sports_nfl_key,
                "X-RapidAPI-Host": "v1.american-football.api-sports.io"
            }
        return {}

# API Endpoints and Configuration
API_ENDPOINTS = {
    "api_sports_nfl": {
        "base_url": "https://v1.american-football.api-sports.io",
        "endpoints": {
            "teams": "teams",
            "games": "games", 
            "standings": "standings",
            "team_statistics": "teams/statistics",
            "game_statistics": "games/statistics",
            "odds": "odds",
            "predictions": "predictions"
        },
        "rate_limit": 100,  # requests per day for free tier
        "rate_limit_window": 86400  # 24 hours in seconds
    }
}

# Default request settings
REQUEST_SETTINGS = {
    "timeout": 30,
    "max_retries": 3,
    "backoff_factor": 1,
    "rate_limit_delay": 1  # seconds between requests
}

def get_api_config() -> APIKeys:
    """Get API configuration instance"""
    return APIKeys()

def setup_environment_variables():
    """Instructions for setting up environment variables"""
    instructions = """
    🔧 Setting up API Keys:
    
    1. Get your free API key from RapidAPI:
       https://rapidapi.com/api-sports/api/american-football/
    
    2. Set environment variables:
       
       Windows (Command Prompt):
       set API_SPORTS_NFL_KEY=your_actual_api_key_here
       
       Windows (PowerShell):
       $env:API_SPORTS_NFL_KEY="your_actual_api_key_here"
       
       Linux/Mac:
       export API_SPORTS_NFL_KEY=your_actual_api_key_here
    
    3. Or update the key directly in this file:
       api_sports_nfl_key = "your_actual_api_key_here"
    
    4. Restart your Python session after setting environment variables
    """
    return instructions

if __name__ == "__main__":
    print("API Configuration Setup")
    print("=" * 30)
    
    config = get_api_config()
    
    if not config.is_api_key_valid():
        print(setup_environment_variables())
    else:
        print("✅ API keys are configured!")
        print(f"API-SPORTS NFL Key: {config.api_sports_nfl_key[:10]}...") 