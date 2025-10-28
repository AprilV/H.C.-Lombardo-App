"""
Complete Production-Ready Flask API Test with Port Manager
===========================================================
Tests the full production API with database connectivity and port management.
"""

from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from port_manager import PortManager

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
            "http://localhost:3001",
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
        'message': 'H.C. Lombardo NFL Analytics API - TESTBED',
        'version': '2.0',
        'port': assigned_port,
        'endpoints': {
            '/health': 'Health check with database test',
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
        return jsonify(teams)
        
    except Exception as e:
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

def run_comprehensive_test():
    """Run all endpoint tests without starting server"""
    print("\n" + "=" * 70)
    print("COMPREHENSIVE API TEST - TESTBED")
    print("=" * 70)
    
    # Check port assignment
    try:
        port = port_manager.get_port_for_service('flask_api')
        print(f"✅ Port Manager: Flask assigned to port {port}")
    except Exception as e:
        print(f"❌ Port Manager failed: {e}")
        return False
    
    # Check for conflicts
    conflicts = port_manager.diagnose_port_conflicts()
    if conflicts:
        print(f"\n⚠️  Detected {len(conflicts)} port conflicts:")
        for conflict in conflicts:
            severity = "🔴" if conflict['severity'] == 'critical' else "🟡"
            print(f"   {severity} {conflict['service']} on port {conflict['port']}")
    else:
        print("✅ No port conflicts detected")
    
    # Test database connection
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM teams")
        count = cursor.fetchone()[0]
        conn.close()
        print(f"✅ Database: Connected ({count} teams)")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    # Test all endpoints
    print("\n📝 Testing API Endpoints:")
    with app.test_client() as client:
        # Test 1: Home
        response = client.get('/')
        if response.status_code == 200:
            data = response.get_json()
            print(f"✅ / (Home): {data['message']}")
        else:
            print(f"❌ / (Home) failed: {response.status_code}")
            return False
        
        # Test 2: Health
        response = client.get('/health')
        if response.status_code == 200:
            data = response.get_json()
            print(f"✅ /health: {data['status']} - {data['teams']} teams")
        else:
            print(f"❌ /health failed: {response.status_code}")
            return False
        
        # Test 3: Port Status
        response = client.get('/port-status')
        if response.status_code == 200:
            data = response.get_json()
            status = data['port_range']
            print(f"✅ /port-status: {status['available']}/{status['total_ports']} ports available")
        else:
            print(f"❌ /port-status failed: {response.status_code}")
            return False
        
        # Test 4: Teams
        response = client.get('/api/teams')
        if response.status_code == 200:
            teams = response.get_json()
            print(f"✅ /api/teams: Retrieved {len(teams)} teams")
            if teams:
                print(f"   Sample: {teams[0]['name']} - W:{teams[0]['wins']} L:{teams[0]['losses']}")
        else:
            print(f"❌ /api/teams failed: {response.status_code}")
            return False
        
        # Test 5: Team Count
        response = client.get('/api/teams/count')
        if response.status_code == 200:
            data = response.get_json()
            print(f"✅ /api/teams/count: {data['count']} teams")
        else:
            print(f"❌ /api/teams/count failed: {response.status_code}")
            return False
        
        # Test 6: Specific Team
        response = client.get('/api/teams/DET')
        if response.status_code == 200:
            team = response.get_json()
            print(f"✅ /api/teams/DET: {team['name']} ({team['wins']}-{team['losses']})")
        else:
            print(f"❌ /api/teams/DET failed: {response.status_code}")
            return False
    
    # Port range status
    status = port_manager.get_port_status()
    print(f"\n📊 Port Range Analysis:")
    print(f"   Range: {status['range']}")
    print(f"   Total: {status['total_ports']} ports")
    print(f"   Available: {status['available']} ports")
    print(f"   In Use: {status['in_use']} ports")
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED - READY FOR PRODUCTION")
    print("=" * 70)
    
    return True

def run_live_server():
    """Run the actual server for manual testing"""
    print("\n" + "=" * 70)
    print("STARTING LIVE TEST SERVER")
    print("=" * 70)
    
    # Get port
    try:
        port = port_manager.get_port_for_service('flask_api')
        print(f"✓ Flask API assigned to port: {port}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    # Test database
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM teams")
        count = cursor.fetchone()[0]
        conn.close()
        print(f"✓ Database connected: {count} teams")
    except Exception as e:
        print(f"⚠️  Database warning: {e}")
    
    print("\n" + "=" * 70)
    print(f"🚀 Server running at: http://127.0.0.1:{port}")
    print("\nTest these endpoints:")
    print(f"   http://127.0.0.1:{port}/")
    print(f"   http://127.0.0.1:{port}/health")
    print(f"   http://127.0.0.1:{port}/port-status")
    print(f"   http://127.0.0.1:{port}/api/teams")
    print("\nPress Ctrl+C to stop")
    print("=" * 70 + "\n")
    
    app.run(host='127.0.0.1', port=port, debug=False)

if __name__ == '__main__':
    if '--live' in sys.argv:
        run_live_server()
    else:
        success = run_comprehensive_test()
        sys.exit(0 if success else 1)
