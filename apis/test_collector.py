#!/usr/bin/env python3

import sys
import traceback

try:
    from live_data_collector import LiveNFLDataCollector
    print("✅ LiveNFLDataCollector imported successfully")
    
    collector = LiveNFLDataCollector()
    print("✅ Collector instance created")
    
    # Test ESPN API first
    print("🔍 Testing database initialization...")
    print(f"Database path: {collector.db_path}")
    
    # Try data collection
    print("🔄 Starting data collection...")
    result = collector.collect_all_data()
    print("✅ Data collection completed")
    print("Result:", result)
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n🔍 Full traceback:")
    traceback.print_exc()