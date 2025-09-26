"""
🔑 EXACTLY WHERE TO PUT YOUR API KEY
====================================

In the file: external_apis\api_config.py

Look for LINE 14 that currently looks like this:

    self.api_sports_nfl_key = os.getenv("API_SPORTS_NFL_KEY", "your_api_key_here")
                                                              ^^^^^^^^^^^^^^^^^^
                                                              REPLACE THIS PART

Change it to:

    self.api_sports_nfl_key = os.getenv("API_SPORTS_NFL_KEY", "YOUR_ACTUAL_KEY_HERE")
                                                              ^^^^^^^^^^^^^^^^^^^^
                                                              PUT YOUR REAL KEY HERE

Example:
    self.api_sports_nfl_key = os.getenv("API_SPORTS_NFL_KEY", "abcd1234567890xyz")

✅ That's it! Your API key is now configured.

📝 The API key should look something like:
   - A long string of letters and numbers
   - Usually 32-64 characters
   - From your RapidAPI dashboard
   - Starts with letters/numbers (no special format)

🧪 Test it works:
   python external_apis\nfl_data_integration.py

⚠️  Keep your API key private!
   - Don't share it
   - Don't commit it to Git  
   - Don't post it online
"""

print(__doc__)