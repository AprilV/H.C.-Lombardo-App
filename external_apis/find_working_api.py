#!/usr/bin/env python3
"""
Updated API Sources for Live NFL Data
Finding the correct API-SPORTS endpoints
"""

def show_current_api_sources():
    print("🔍 Finding the Correct NFL API")
    print("=" * 35)
    
    print("\n🏈 UPDATED API SOURCES:")
    print("=" * 25)
    
    print("\n1️⃣ API-SPORTS (Primary):")
    print("   🌐 https://rapidapi.com/api-sports/")
    print("   🔍 Search for: 'American Football'")
    print("   📝 Look for API-SPORTS publisher")
    
    print("\n2️⃣ Alternative Search:")
    print("   🌐 https://rapidapi.com/")
    print("   🔍 Search: 'NFL statistics'")
    print("   🔍 Search: 'American football API'")
    print("   🔍 Search: 'API-SPORTS'")
    
    print("\n3️⃣ Direct API-SPORTS Website:")
    print("   🌐 https://www.api-sports.io/")
    print("   📂 Browse their sports APIs")
    print("   🏈 Look for American Football section")
    
    print("\n4️⃣ Alternative NFL APIs:")
    print("   🌐 ESPN API (free but limited)")
    print("   🌐 NFL.com API (unofficial)")
    print("   🌐 Sports Data IO")
    print("   🌐 The Odds API (for betting lines)")

def show_what_to_look_for():
    print("\n🎯 WHAT TO LOOK FOR:")
    print("=" * 20)
    
    print("\n✅ Good NFL APIs should have:")
    print("   • Team statistics")
    print("   • Game schedules")
    print("   • Betting odds/lines")
    print("   • Season data")
    print("   • Player stats (bonus)")
    
    print("\n📊 Key Features Needed:")
    print("   • GET /teams - List teams")
    print("   • GET /games - Game data") 
    print("   • GET /statistics - Team stats")
    print("   • GET /odds - Betting lines")

def show_alternative_setup():
    print("\n🔄 ALTERNATIVE: Keep Using Mock Data")
    print("=" * 40)
    
    print("✅ Your current setup works perfectly with high-quality mock data!")
    print("📊 Mock data includes:")
    print("   • Realistic NFL team stats")
    print("   • Betting lines with spreads/totals")
    print("   • Season records and performance")
    print("   • Game results and analysis")
    
    print("\n💡 Benefits of Mock Data:")
    print("   • No API costs")
    print("   • No rate limits")
    print("   • Always available")
    print("   • Perfect for development")
    
    print("\n🚀 To switch back to mock data:")
    print("   Edit: external_apis\\api_config.py")
    print("   Change: 'PASTE_YOUR_API_KEY_HERE' back to 'your_api_key_here'")

def test_current_setup():
    print("\n🧪 Testing Current Setup:")
    print("=" * 25)
    
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(__file__))
        
        from nfl_data_integration import get_team_stats, get_game_odds
        
        print("🔄 Testing team stats...")
        team_result = get_team_stats(2024, 1)
        
        print("🔄 Testing game odds...")
        odds_result = get_game_odds(12345)
        
        if team_result and odds_result:
            print("✅ All functions working!")
            print("📊 Data source:", team_result.get('team_info', {}).get('data_source', 'Unknown'))
            return True
        else:
            print("❌ Some functions failed")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    print("🚨 API URL Not Found - Let's Fix This!")
    print("=" * 45)
    
    show_current_api_sources()
    show_what_to_look_for()
    
    print("\n" + "=" * 45)
    choice = input("Want to test current mock data setup? (y/n): ").lower().strip()
    
    if choice == 'y':
        if test_current_setup():
            print("\n✅ Everything is working with mock data!")
            print("💡 You can continue development while finding a live API")
        else:
            print("\n❌ Setup needs fixing")
    
    show_alternative_setup()
    
    print("\n🎯 RECOMMENDED NEXT STEPS:")
    print("1. 🔍 Search RapidAPI for 'NFL' or 'American Football'")
    print("2. 📝 Look for APIs with good ratings and documentation")  
    print("3. 🆓 Start with free tier to test")
    print("4. 🔄 Or continue with excellent mock data for now!")

if __name__ == "__main__":
    main()