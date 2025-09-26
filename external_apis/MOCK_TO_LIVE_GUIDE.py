#!/usr/bin/env python3
"""
📝 EXACT STEPS to Replace Mock Data with Live Data
==================================================

CURRENT STATUS: You're seeing this warning:
⚠️ Warning: API-SPORTS NFL API key not set
→ Using mock data (no API key configured)

TO FIX THIS AND GET LIVE DATA:
"""

def show_exact_fix():
    print("🎯 EXACT STEPS TO FIX:")
    print("=" * 30)
    
    print("\n📁 STEP 1: Open this file in VS Code or any text editor:")
    print("   external_apis\\api_config.py")
    
    print("\n🔍 STEP 2: Find this line (around line 17):")
    print("   self.api_sports_nfl_key = os.getenv(\"API_SPORTS_NFL_KEY\", \"your_api_key_here\")")
    print("                                                                ^^^^^^^^^^^^^^^^^^")
    print("                                                                REPLACE THIS PART")
    
    print("\n✏️ STEP 3: Replace 'your_api_key_here' with your actual API key:")
    print("   FROM: \"your_api_key_here\"")
    print("   TO:   \"your_actual_api_key_from_rapidapi\"")
    
    print("\n💾 STEP 4: Save the file")
    
    print("\n🧪 STEP 5: Test it works:")
    print("   python external_apis\\nfl_data_integration.py")
    
    print("\n✅ WHAT YOU'LL SEE AFTER FIX:")
    print("   🌐 NFL External API Integration Demo")
    print("   ✅ API key configured successfully")
    print("   📊 Live data from API-SPORTS!")

def show_file_example():
    print("\n📄 BEFORE AND AFTER EXAMPLE:")
    print("=" * 35)
    
    print("\n❌ BEFORE (causing mock data warning):")
    print("   self.api_sports_nfl_key = os.getenv(\"API_SPORTS_NFL_KEY\", \"your_api_key_here\")")
    
    print("\n✅ AFTER (will use live data):")
    print("   self.api_sports_nfl_key = os.getenv(\"API_SPORTS_NFL_KEY\", \"abc123def456ghi789\")")
    
    print("\n📝 YOUR API KEY LOOKS LIKE:")
    print("   • A string of letters and numbers")
    print("   • Usually 30-50 characters long")
    print("   • From your RapidAPI dashboard")
    print("   • Example: \"a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6\"")

def show_get_key_steps():
    print("\n🔑 HOW TO GET YOUR API KEY:")
    print("=" * 32)
    
    print("1. 🌐 Go to: https://rapidapi.com/api-sports/api/american-football/")
    print("2. 📝 Create free RapidAPI account")
    print("3. ✅ Subscribe to 'American Football API' (free tier available)")
    print("4. 📋 Go to your dashboard → 'My Apps' → Copy your API key")
    print("5. 📂 Paste it into the api_config.py file as shown above")

def main():
    print(__doc__)
    show_exact_fix()
    show_file_example() 
    show_get_key_steps()
    
    print("\n🎯 SUMMARY:")
    print("• You're currently using MOCK DATA (fake data for testing)")
    print("• To get LIVE NFL DATA, you need a real API key from RapidAPI")
    print("• Replace 'your_api_key_here' in api_config.py with your real key")
    print("• That's it! No other changes needed.")
    
    print("\n🔄 Current mock data is high quality and works for development!")
    print("🌐 Live data gives you real NFL stats and current betting lines.")

if __name__ == "__main__":
    main()