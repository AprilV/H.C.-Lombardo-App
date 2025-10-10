"""
Enhanced API Server with Intelligent Port Management
====================================================
Automatically finds available ports and handles conflicts gracefully.
"""

from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
from datetime import datetime
import sys
from port_manager import PortManager
from logging_config import log_activity

# Initialize port manager
port_manager = PortManager()

# Create Flask app
app = Flask(__name__)

# Configure CORS for multiple possible React ports
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001",  # Backup port
            "http://127.0.0.1:3001"
        ]
    }
})

# Database connection
def get_db_connection():
    """Get PostgreSQL database connection"""
    return psycopg2.connect(
        dbname='nfl_analytics',
        user='postgres',
        password='aprilv120',
        host='localhost',
        port='5432'
    )

# Routes
@app.route('/')
def home():
    """API home endpoint"""
    assigned_port = port_manager.config['reserved_ports'].get('flask_api', 'unknown')
    return jsonify({
        'message': 'H.C. Lombardo NFL Analytics API',
        'version': '2.0',
        'port': assigned_port,
        'endpoints': {
            '/health': 'Health check',
            '/port-status': 'Port management status',
            '/api/teams': 'All NFL teams',
            '/api/teams/count': 'Team count',
            '/api/teams/<abbr>': 'Team by abbreviation'
        }
    })

@app.route('/health')
def health():
    """Health check endpoint with database test"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM teams")
        count = cursor.fetchone()[0]
        conn.close()
        
        assigned_port = port_manager.config['reserved_ports'].get('flask_api', 'unknown')
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'teams': count,
            'port': assigned_port,
            'cors': 'enabled',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/port-status')
def port_status():
    """Get current port allocation status"""
    status = port_manager.get_port_status()
    conflicts = port_manager.diagnose_port_conflicts()
    
    return jsonify({
        'port_range': status,
        'conflicts': conflicts,
        'reserved_ports': port_manager.config['reserved_ports'],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/teams')
def get_teams():
    """Get all NFL teams"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, abbreviation, wins, losses, ppg, pa, games_played
            FROM teams
            ORDER BY ppg DESC
        """)
        
        teams = []
        for row in cursor.fetchall():
            teams.append({
                'name': row[0],
                'abbreviation': row[1],
                'wins': row[2],
                'losses': row[3],
                'ppg': row[4],
                'pa': row[5],
                'games_played': row[6]
            })
        
        conn.close()
        log_activity('api', 'info', f'Retrieved {len(teams)} teams')
        return jsonify(teams)
        
    except Exception as e:
        log_activity('api', 'error', f'Error fetching teams: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/teams/count')
def get_team_count():
    """Get total number of teams"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM teams")
        count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({'count': count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/teams/<abbr>')
def get_team(abbr):
    """Get team by abbreviation"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, abbreviation, wins, losses, ppg, pa, games_played
            FROM teams
            WHERE abbreviation = %s
        """, (abbr.upper(),))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return jsonify({
                'name': row[0],
                'abbreviation': row[1],
                'wins': row[2],
                'losses': row[3],
                'ppg': row[4],
                'pa': row[5],
                'games_played': row[6]
            })
        else:
            return jsonify({'error': 'Team not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def main():
    """Main startup with intelligent port management"""
    print("\n" + "="*70)
    print("H.C. LOMBARDO NFL ANALYTICS API - PRODUCTION")
    print("="*70)
    
    # Diagnose port conflicts
    conflicts = port_manager.diagnose_port_conflicts()
    if conflicts:
        print("\n⚠️  PORT CONFLICTS DETECTED:")
        for conflict in conflicts:
            severity_symbol = "🔴" if conflict['severity'] == 'critical' else "🟡"
            print(f"  {severity_symbol} {conflict['service']} (port {conflict['port']})")
        print("\n🔧 Attempting automatic resolution...\n")
    
    # Get available port
    try:
        port = port_manager.get_port_for_service('flask_api')
        print(f"✓ Flask API assigned to port: {port}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    # Test database connection
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM teams")
        count = cursor.fetchone()[0]
        conn.close()
        print(f"✓ Database connected: {count} teams found")
    except Exception as e:
        print(f"⚠️  Database connection warning: {e}")
    
    # Display CORS info
    print(f"✓ CORS Enabled for: http://localhost:3000, http://127.0.0.1:3000")
    
    # Show port range status
    status = port_manager.get_port_status()
    print(f"\n📊 Port Range Status:")
    print(f"   Range: {status['range']}")
    print(f"   Available: {status['available']}/{status['total_ports']}")
    print(f"   In Use: {status['in_use']}/{status['total_ports']}")
    
    print("\n" + "="*70)
    log_activity('api', 'info', f'Starting Flask server on port {port}')
    print(f"🚀 Starting Flask server on http://127.0.0.1:{port}")
    print("="*70 + "\n")
    
    # Start Flask app
    app.run(
        host='127.0.0.1',
        port=port,
        debug=False
    )

if __name__ == '__main__':
    main()
