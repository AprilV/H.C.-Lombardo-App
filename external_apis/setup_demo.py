#!/usr/bin/env python3
"""
API Key Setup Demo
Quick demonstration of how to set up your API key
"""

print("🔑 API Key Setup Demo")
print("=" * 30)

print("\n📋 Current Methods Available:")
print("1. Environment Variable (Most Secure)")
print("2. Direct Config File Update")
print("3. Batch File Helper")

print("\n💡 Method 1: Environment Variable")
print("PowerShell Command:")
print('$env:API_SPORTS_NFL_KEY = "your_actual_api_key_here"')
print("\nCommand Prompt:")
print('set API_SPORTS_NFL_KEY=your_actual_api_key_here')

print("\n💡 Method 2: Direct Config Update")
print("Edit: external_apis\\api_config.py")
print("Find line 14, replace:")
print('FROM: "your_api_key_here"')
print('TO:   "YOUR_ACTUAL_API_KEY_HERE"')

print("\n💡 Method 3: Use the Batch File")
print("1. Edit setup_api_key.bat")
print("2. Replace 'your_actual_api_key_here' with your key")
print("3. Run the batch file")

print("\n🔍 Current Configuration Check:")
try:
    from api_config import APIKeys
    keys = APIKeys()
    
    if keys.is_api_key_valid():
        print("✅ API Key: CONFIGURED")
        print("🌐 Status: Ready for live data!")
    else:
        print("⚠️  API Key: NOT SET")
        print("🔄 Status: Using mock data")
        
        # Show exactly what needs to be done
        current_key = keys.get_api_sports_key()
        if current_key == "your_api_key_here":
            print(f"\n📝 To activate live data:")
            print(f"   Replace 'your_api_key_here' in api_config.py")
            print(f"   OR set environment variable API_SPORTS_NFL_KEY")
        
except Exception as e:
    print(f"❌ Configuration Error: {e}")

print("\n🧪 Test Command After Setup:")
print("python external_apis\\nfl_data_integration.py")

print("\n🎯 What You'll See:")
print("✅ With API Key: Live NFL data from API-SPORTS")
print("🔄 Without Key: Mock data for testing")

print("\n📚 More Info: external_apis\\API_KEY_SETUP.md")