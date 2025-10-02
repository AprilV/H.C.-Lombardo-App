#!/usr/bin/env python3
"""
Test script to run the data collector directly
"""
import sys
import os

# Add the apis directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'apis'))

try:
    from live_data_collector import LiveNFLDataCollector
    
    print("✅ Import successful")
    
    # Create collector instance
    collector = LiveNFLDataCollector()
    print("✅ Collector instance created")
    
    # Test database initialization
    collector.init_database()
    print("✅ Database initialized")
    
    # Test ESPN API connection
    print("🏈 Testing teams data collection...")
    teams_result = collector.collect_teams_data()
    print(f"✅ Teams collection result: {teams_result}")
    
    # Test collecting games
    print("🏈 Testing games data collection...")
    games_result = collector.collect_games_data()
    print(f"✅ Games collection result: {games_result}")
    
    print("🎉 All tests passed! Data collector is working.")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()