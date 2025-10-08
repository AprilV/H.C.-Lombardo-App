"""
H.C. Lombardo - Log Viewer Utility
View and analyze application logs easily
"""
import os
import glob
from datetime import datetime, timedelta
import re

def get_log_files():
    """Get all log files sorted by date"""
    logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
    if not os.path.exists(logs_dir):
        return []
    
    log_files = glob.glob(os.path.join(logs_dir, 'hc_lombardo_*.log'))
    return sorted(log_files, reverse=True)  # Most recent first

def view_recent_logs(lines=50):
    """View the most recent log entries"""
    log_files = get_log_files()
    if not log_files:
        print("📄 No log files found")
        return
    
    latest_log = log_files[0]
    print(f"\n📄 Latest Log File: {os.path.basename(latest_log)}")
    print("=" * 60)
    
    try:
        with open(latest_log, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            
            for line in recent_lines:
                print(line.strip())
                
    except Exception as e:
        print(f"❌ Error reading log file: {e}")

def view_logs_by_component(component, lines=50):
    """View logs filtered by component (app, database, scraper, api)"""
    log_files = get_log_files()
    if not log_files:
        print("📄 No log files found")
        return
    
    latest_log = log_files[0]
    print(f"\n📄 {component.upper()} Logs from: {os.path.basename(latest_log)}")
    print("=" * 60)
    
    try:
        with open(latest_log, 'r', encoding='utf-8') as f:
            matching_lines = []
            for line in f:
                if f"| {component} |" in line:
                    matching_lines.append(line.strip())
            
            recent_lines = matching_lines[-lines:] if len(matching_lines) > lines else matching_lines
            
            if recent_lines:
                for line in recent_lines:
                    print(line)
            else:
                print(f"No {component} logs found")
                
    except Exception as e:
        print(f"❌ Error reading log file: {e}")

def view_error_logs():
    """View only error and warning logs"""
    log_files = get_log_files()
    if not log_files:
        print("📄 No log files found")
        return
    
    latest_log = log_files[0]
    print(f"\n⚠️  ERROR & WARNING Logs from: {os.path.basename(latest_log)}")
    print("=" * 60)
    
    try:
        with open(latest_log, 'r', encoding='utf-8') as f:
            for line in f:
                if "| ERROR |" in line or "| WARNING |" in line:
                    print(line.strip())
                    
    except Exception as e:
        print(f"❌ Error reading log file: {e}")

def show_log_stats():
    """Show statistics about recent logging activity"""
    log_files = get_log_files()
    if not log_files:
        print("📄 No log files found")
        return
    
    latest_log = log_files[0]
    print(f"\n📊 Log Statistics for: {os.path.basename(latest_log)}")
    print("=" * 60)
    
    try:
        stats = {
            'total_lines': 0,
            'info': 0,
            'warning': 0,
            'error': 0,
            'debug': 0,
            'components': {'app': 0, 'database': 0, 'scraper': 0, 'api': 0}
        }
        
        with open(latest_log, 'r', encoding='utf-8') as f:
            for line in f:
                stats['total_lines'] += 1
                
                if "| INFO |" in line:
                    stats['info'] += 1
                elif "| WARNING |" in line:
                    stats['warning'] += 1
                elif "| ERROR |" in line:
                    stats['error'] += 1
                elif "| DEBUG |" in line:
                    stats['debug'] += 1
                
                for component in stats['components']:
                    if f"| {component} |" in line:
                        stats['components'][component] += 1
        
        print(f"Total log entries: {stats['total_lines']}")
        print(f"INFO:     {stats['info']}")
        print(f"WARNING:  {stats['warning']}")
        print(f"ERROR:    {stats['error']}")
        print(f"DEBUG:    {stats['debug']}")
        print()
        print("By Component:")
        for component, count in stats['components'].items():
            print(f"  {component.upper()}: {count}")
            
    except Exception as e:
        print(f"❌ Error reading log file: {e}")

def show_menu():
    """Show the log viewer menu"""
    print("\n" + "=" * 60)
    print("H.C. LOMBARDO - LOG VIEWER")
    print("=" * 60)
    print("1. View recent logs (last 50 lines)")
    print("2. View app logs")
    print("3. View database logs")
    print("4. View scraper logs")
    print("5. View API logs")
    print("6. View errors & warnings only")
    print("7. Show log statistics")
    print("8. Exit")
    print("=" * 60)

if __name__ == "__main__":
    while True:
        show_menu()
        choice = input("Enter your choice (1-8): ").strip()
        
        if choice == '1':
            view_recent_logs()
        elif choice == '2':
            view_logs_by_component('app')
        elif choice == '3':
            view_logs_by_component('database')
        elif choice == '4':
            view_logs_by_component('scraper')
        elif choice == '5':
            view_logs_by_component('api')
        elif choice == '6':
            view_error_logs()
        elif choice == '7':
            show_log_stats()
        elif choice == '8':
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")