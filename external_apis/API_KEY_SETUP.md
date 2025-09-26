# 🔑 API Key Setup Guide

## 🎯 Quick Setup - Choose Your Method:

### Method 1: Direct Config Update (Simplest)

1. **Open** `external_apis\api_config.py`
2. **Find** line 14: `self.api_sports_nfl_key = os.getenv("API_SPORTS_NFL_KEY", "your_api_key_here")`
3. **Replace** `"your_api_key_here"` with your actual API key:

```python
self.api_sports_nfl_key = os.getenv("API_SPORTS_NFL_KEY", "YOUR_ACTUAL_API_KEY_HERE")
```

### Method 2: Environment Variable (Most Secure)

**PowerShell:**
```powershell
$env:API_SPORTS_NFL_KEY = "YOUR_ACTUAL_API_KEY_HERE"
python external_apis\nfl_data_integration.py
```

**Command Prompt:**
```cmd
set API_SPORTS_NFL_KEY=YOUR_ACTUAL_API_KEY_HERE
python external_apis\nfl_data_integration.py
```

### Method 3: Batch File (Provided)

1. **Edit** `setup_api_key.bat`
2. **Replace** `your_actual_api_key_here` with your real key
3. **Run** the batch file

---

## 🏈 Getting Your API-SPORTS NFL API Key

### Step 1: Sign Up
1. Go to [API-SPORTS](https://rapidapi.com/api-sports/api/american-football/)
2. Create RapidAPI account
3. Subscribe to American Football API

### Step 2: Find Your Key
1. Go to your RapidAPI dashboard
2. Navigate to "My Apps"
3. Copy your API key (starts with something like "1234567890abcdef...")

### Step 3: Test Setup
```bash
python launcher.py
# Choose option 12: Test NFL External API
```

---

## ✅ Verification

After setting up your API key, you should see:

**Before Setup:**
```
⚠️  Warning: API-SPORTS NFL API key not set
   Option 1: Set environment variable: API_SPORTS_NFL_KEY
   Option 2: Update api_config.py with your actual key
   Option 3: Run setup_api_key.bat
```

**After Setup:**
```
✅ API key configured successfully
🔄 Making API request to API-SPORTS...
📊 Retrieved live NFL data!
```

---

## 🧪 Test Your Configuration

### Quick Test Command:
```bash
cd "c:\IS330\H.C. Lombardo App"
python external_apis\nfl_data_integration.py
```

### Expected Output (with valid key):
```
🏈 NFL External API Integration Test
=====================================
API Key Status: ✅ Valid
📊 Testing get_team_stats()...
✅ Live data retrieved from API-SPORTS
   Team: [Real Team Name]
   Record: [Real Season Record]
```

### Expected Output (without key):
```
⚠️  Warning: API-SPORTS NFL API key not set
✅ Mock data retrieved for testing
   Team: Kansas City Chiefs
   Record: 14-3
```

---

## 🔒 Security Best Practices

### ✅ Do This:
- Use environment variables for production
- Keep API keys out of version control
- Rotate keys regularly

### ❌ Don't Do This:
- Commit API keys to Git
- Share keys in screenshots
- Use the same key across multiple projects

---

## 🚨 Troubleshooting

### Problem: "API key not working"
**Solution:** Check that your key:
- Is from RapidAPI (not API-SPORTS directly)
- Has American Football API subscription
- Hasn't exceeded rate limits

### Problem: "Import errors"
**Solution:**
```bash
pip install requests python-dotenv
```

### Problem: "Permission errors"
**Solution:** Run PowerShell as Administrator

---

## 🎯 Current Status

**Your config is now set to accept:**
- ✅ Environment variable: `API_SPORTS_NFL_KEY`
- ✅ Direct config update: Replace `"your_api_key_here"`
- ✅ Batch file setup: `setup_api_key.bat`

**Mock data fallback ensures everything works without an API key!** 🔄