#!/usr/bin/env python3
"""
Live API Verification Tool
Quick check to see if your API key is working
"""

def test_live_api():
    print("🧪 Testing Live API Configuration")
    print("=" * 40)
    
    try:
        from api_config import APIKeys
        keys = APIKeys()
        
        current_key = keys.get_api_sports_key()
        print(f"📍 Current Key: {current_key[:10]}..." if len(current_key) > 10 else f"📍 Current Key: {current_key}")
        
        if current_key == "PASTE_YOUR_API_KEY_HERE":
            print("❌ Status: Placeholder key detected")
            print("💡 Action: Replace 'PASTE_YOUR_API_KEY_HERE' with your real API key")
            return False
        
        elif current_key == "your_api_key_here":
            print("❌ Status: Old placeholder detected")
            print("💡 Action: Replace 'your_api_key_here' with your real API key")
            return False
            
        elif len(current_key) < 20:
            print("⚠️  Status: Key seems very short")
            print("💡 Action: Check if this is your complete API key")
            return False
            
        else:
            print("✅ Status: Real API key detected!")
            print("🌐 Testing actual API call...")
            
            # Test with actual API call
            from nfl_data_integration import get_team_stats
            result = get_team_stats(2024, 1)
            
            if "error" not in result and "API request failed" not in str(result):
                team_info = result.get("team_info", {})
                data_source = team_info.get("data_source", "unknown")
                
                if "live" in data_source.lower() or "api-sports" in data_source:
                    print("🎉 SUCCESS! Live data retrieved!")
                    print(f"   Team: {team_info.get('name', 'Unknown')}")
                    print(f"   Source: {data_source}")
                    return True
                else:
                    print("🔄 Getting mock data (API might have rate limits)")
                    return False
            else:
                print("❌ API call failed - likely authentication issue")
                print("💡 Check your API key and subscription status")
                return False
                
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def show_next_steps(success):
    """Show appropriate next steps"""
    print("\n" + "=" * 40)
    
    if success:
        print("🎯 YOU'RE ALL SET!")
        print("✅ Live NFL data is working")
        print("🚀 Try these commands:")
        print("   python launcher.py → Option 12 (Test NFL External API)")
        print("   python nfl_data_integration.py")
        
    else:
        print("🎯 NEXT STEPS:")
        print("1. 🌐 Get API key: https://rapidapi.com/api-sports/api/american-football/")
        print("2. 📝 Subscribe to American Football API (free tier available)")
        print("3. 🔑 Copy your API key from RapidAPI dashboard")
        print("4. ✏️ Replace 'PASTE_YOUR_API_KEY_HERE' in api_config.py")
        print("5. 🧪 Run this test again: python verify_live_api.py")
        
    print("\n📚 Full guide: GET_LIVE_API_STEPS.txt")

def main():
    print("🔍 Live API Verification")
    print("Checking if your API key is configured for live NFL data...\n")
    
    success = test_live_api()
    show_next_steps(success)

if __name__ == "__main__":
    main()