"""
H.C. Lombardo - Simple Log Analysis
Quick log viewing without interaction
"""
import os
import sys
from datetime import datetime

def get_latest_log():
    """Get the most recent log file"""
    logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
    today = datetime.now().strftime('%Y%m%d')
    log_file = os.path.join(logs_dir, f'hc_lombardo_{today}.log')
    
    if os.path.exists(log_file):
        return log_file
    return None

def show_recent_activity(lines=20):
    """Show recent log activity"""
    log_file = get_latest_log()
    if not log_file:
        print("📄 No log file found for today")
        return
    
    print(f"\n📄 Recent Activity (last {lines} lines)")
    print("=" * 80)
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            recent = all_lines[-lines:] if len(all_lines) > lines else all_lines
            
            for line in recent:
                line = line.strip()
                if line:
                    # Color code by log level
                    if "| ERROR |" in line:
                        print(f"🔴 {line}")
                    elif "| WARNING |" in line:
                        print(f"🟡 {line}")
                    elif "| INFO |" in line:
                        print(f"🟢 {line}")
                    else:
                        print(f"⚪ {line}")
                        
    except Exception as e:
        print(f"❌ Error reading log: {e}")

def show_stats():
    """Show quick statistics"""
    log_file = get_latest_log()
    if not log_file:
        print("📄 No log file found for today")
        return
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        total = len(lines)
        info = sum(1 for line in lines if "| INFO |" in line)
        warning = sum(1 for line in lines if "| WARNING |" in line)
        error = sum(1 for line in lines if "| ERROR |" in line)
        
        print(f"\n📊 Today's Log Stats")
        print("=" * 30)
        print(f"Total entries: {total}")
        print(f"🟢 INFO:      {info}")
        print(f"🟡 WARNING:   {warning}")
        print(f"🔴 ERROR:     {error}")
        
    except Exception as e:
        print(f"❌ Error reading log: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "stats":
            show_stats()
        elif sys.argv[1] == "errors":
            # Show only errors and warnings
            log_file = get_latest_log()
            if log_file:
                print("\n⚠️  Errors & Warnings Today")
                print("=" * 50)
                with open(log_file, 'r') as f:
                    for line in f:
                        if "| ERROR |" in line or "| WARNING |" in line:
                            print(line.strip())
        else:
            lines = int(sys.argv[1]) if sys.argv[1].isdigit() else 20
            show_recent_activity(lines)
    else:
        show_recent_activity()
        show_stats()