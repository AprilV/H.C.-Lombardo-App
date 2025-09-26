#!/usr/bin/env python3
"""
API Key Configuration Helper
Quick way to set up your API key for live NFL data
"""

import os

def check_current_config():
    """Check current API key configuration"""
    print("🔍 Current API Configuration:")
    print("=" * 40)
    
    try:
        from api_config import APIKeys
        keys = APIKeys()
        
        current_key = keys.get_api_sports_key()
        is_valid = keys.is_api_key_valid()
        
        print(f"📍 Current Key: {current_key[:10]}..." if len(current_key) > 10 else f"📍 Current Key: {current_key}")
        print(f"✅ Valid: {'Yes' if is_valid else 'No'}")
        print(f"🔄 Status: {'Live Data' if is_valid else 'Mock Data'}")
        
        return current_key, is_valid
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, False

def show_setup_options():
    """Show different ways to set up the API key"""
    print("\n🛠️ Setup Options:")
    print("=" * 25)
    
    print("\n1️⃣ DIRECT FILE EDIT (Simplest)")
    print("   File: external_apis\\api_config.py")
    print("   Line 17: Replace 'your_api_key_here' with your actual key")
    print("   Example: \"abcd1234567890efgh\"")
    
    print("\n2️⃣ ENVIRONMENT VARIABLE (Most Secure)")
    print("   PowerShell: $env:API_SPORTS_NFL_KEY = \"your_key_here\"")
    print("   Command: set API_SPORTS_NFL_KEY=your_key_here")
    
    print("\n3️⃣ TEMPORARY TEST (For this session)")
    print("   Enter your key below to test without saving")

def test_with_temp_key():
    """Test API with temporary key without saving to file"""
    print("\n🧪 Temporary API Key Test:")
    print("=" * 30)
    
    temp_key = input("Enter your API key (or press Enter to skip): ").strip()
    
    if not temp_key:
        print("⏭️ Skipped temporary test")
        return
    
    # Set temporary environment variable
    os.environ["API_SPORTS_NFL_KEY"] = temp_key
    
    try:
        print(f"🔄 Testing with key: {temp_key[:8]}...")
        
        # Import after setting env var
        from api_config import APIKeys
        from nfl_data_integration import get_team_stats
        
        keys = APIKeys()
        if keys.is_api_key_valid():
            print("✅ API key format looks valid!")
            print("🌐 Testing live data request...")
            
            # Test actual API call
            result = get_team_stats(2024, 1)
            
            if "error" not in result:
                print("🎉 SUCCESS! Live data retrieved:")
                team_info = result.get("team_info", {})
                print(f"   Team: {team_info.get('name', 'Unknown')}")
                print(f"   Data Source: {team_info.get('data_source', 'Unknown')}")
            else:
                print(f"❌ API Error: {result.get('error', 'Unknown error')}")
                print("💡 This might be a rate limit or subscription issue")
                
        else:
            print("❌ Invalid API key format")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        # Clean up temp env var
        if "API_SPORTS_NFL_KEY" in os.environ:
            del os.environ["API_SPORTS_NFL_KEY"]

def show_api_info():
    """Show information about getting an API key"""
    print("\n📚 Getting Your API Key:")
    print("=" * 30)
    print("1. Go to: https://rapidapi.com/api-sports/api/american-football/")
    print("2. Create RapidAPI account (free)")
    print("3. Subscribe to American Football API")
    print("4. Copy your API key from dashboard")
    print("5. Use one of the setup options above")
    
    print("\n💰 API Pricing (as of 2024):")
    print("   • Free Tier: 100 requests/day")
    print("   • Basic: $10/month for 1000 requests/day") 
    print("   • Pro: $25/month for 10,000 requests/day")

def main():
    """Main configuration helper"""
    print("🔑 API Key Configuration Helper")
    print("🏈 For Live NFL Data from API-SPORTS")
    print("=" * 50)
    
    # Check current config
    current_key, is_valid = check_current_config()
    
    if is_valid:
        print("\n🎉 You're all set! Your API key is working.")
        print("🌐 You should be getting live NFL data.")
        return
    
    # Show setup options
    show_setup_options()
    
    # Option for temporary test
    print("\n" + "=" * 50)
    choice = input("Test with temporary key? (y/n): ").lower().strip()
    
    if choice == 'y':
        test_with_temp_key()
    
    # Show API info
    show_api_info()
    
    print("\n🎯 Next Steps:")
    print("1. Get your API key from RapidAPI")
    print("2. Choose a setup method above")
    print("3. Test: python nfl_data_integration.py")
    print("4. You should see live data instead of mock data!")

if __name__ == "__main__":
    main()