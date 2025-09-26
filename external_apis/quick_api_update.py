#!/usr/bin/env python3
"""
Quick API Key Update Tool
One-click way to update your API key
"""

import os
import sys

def read_current_config():
    """Read the current api_config.py file"""
    config_path = "api_config.py"
    
    if not os.path.exists(config_path):
        print(f"❌ Config file not found: {config_path}")
        return None
    
    with open(config_path, 'r') as f:
        lines = f.readlines()
    
    return lines

def find_api_key_line(lines):
    """Find the line with the API key"""
    for i, line in enumerate(lines):
        if 'self.api_sports_nfl_key' in line and 'os.getenv' in line:
            return i, line.strip()
    return None, None

def update_api_key(lines, line_num, new_key):
    """Update the API key in the config"""
    # Create the new line
    new_line = f'        self.api_sports_nfl_key = os.getenv("API_SPORTS_NFL_KEY", "{new_key}")\n'
    lines[line_num] = new_line
    return lines

def write_updated_config(lines):
    """Write the updated configuration back to file"""
    with open("api_config.py", 'w') as f:
        f.writelines(lines)

def test_new_config():
    """Test the new configuration"""
    try:
        # Reload the module
        if 'api_config' in sys.modules:
            del sys.modules['api_config']
        
        from api_config import APIKeys
        keys = APIKeys()
        
        print(f"\n🧪 Testing new configuration...")
        print(f"📍 API Key: {keys.get_api_sports_key()[:10]}...")
        print(f"✅ Valid: {'Yes' if keys.is_api_key_valid() else 'No'}")
        
        return keys.is_api_key_valid()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    print("🔧 Quick API Key Update Tool")
    print("=" * 35)
    
    # Read current config
    print("📖 Reading current configuration...")
    lines = read_current_config()
    if not lines:
        return
    
    # Find API key line
    line_num, current_line = find_api_key_line(lines)
    if line_num is None:
        print("❌ Could not find API key configuration line")
        return
    
    print(f"🔍 Found configuration on line {line_num + 1}:")
    print(f"   {current_line}")
    
    # Check current status
    current_key = current_line.split('"')[3] if current_line.count('"') >= 4 else "unknown"
    print(f"📍 Current key: {current_key}")
    
    if current_key != "your_api_key_here":
        print("ℹ️  API key appears to already be set!")
        choice = input("Update anyway? (y/n): ").lower().strip()
        if choice != 'y':
            print("⏭️ Cancelled")
            return
    
    # Get new API key
    print("\n🔑 Enter your new API key:")
    print("💡 Get it from: https://rapidapi.com/api-sports/api/american-football/")
    new_key = input("API Key: ").strip()
    
    if not new_key:
        print("❌ No API key entered. Cancelled.")
        return
    
    if len(new_key) < 10:
        print("⚠️  Warning: API key seems very short. Continue anyway?")
        choice = input("Continue? (y/n): ").lower().strip()
        if choice != 'y':
            print("⏭️ Cancelled")
            return
    
    # Update the configuration
    print(f"\n🔄 Updating configuration...")
    updated_lines = update_api_key(lines, line_num, new_key)
    
    # Write back to file
    write_updated_config(updated_lines)
    print("✅ Configuration file updated!")
    
    # Test the new configuration
    if test_new_config():
        print("\n🎉 SUCCESS! Your API key is configured and valid.")
        print("🌐 You should now get live NFL data instead of mock data.")
        
        print("\n🧪 Test command:")
        print("   python nfl_data_integration.py")
        
    else:
        print("\n⚠️  Configuration updated but validation failed.")
        print("💡 The API key might be invalid or there might be an issue.")
        print("🔄 You can still test with: python nfl_data_integration.py")

if __name__ == "__main__":
    main()