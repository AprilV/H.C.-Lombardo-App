"""
SPRINT 6 TEST APPLICATION
Visual interface to test HCL historical data features

Runs on: http://localhost:5001
Database: nfl_analytics_test
Purpose: Visual verification before production integration
"""

from flask import Flask, render_template, jsonify
from api_routes_hcl import hcl_bp
import os

app = Flask(__name__, 
            template_folder='test_templates',
            static_folder='test_static')

# Register API blueprint
app.register_blueprint(hcl_bp)

@app.route('/')
def index():
    """Test dashboard - list all teams"""
    return render_template('test_index.html')

@app.route('/team/<team_abbr>')
def team_detail(team_abbr):
    """Team detail page"""
    return render_template('test_team_detail.html', team_abbr=team_abbr.upper())

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🏈 SPRINT 6 TEST APPLICATION")
    print("="*70)
    print("\nTest Environment:")
    print(f"  URL: http://localhost:5001")
    print(f"  Database: nfl_analytics_test")
    print(f"  Data: Week 7 2024 (15 games)")
    print("\nPages:")
    print(f"  Dashboard: http://localhost:5001")
    print(f"  Team Example: http://localhost:5001/team/BAL")
    print("\nAPI Endpoints:")
    print(f"  GET /api/hcl/teams")
    print(f"  GET /api/hcl/teams/<abbr>")
    print(f"  GET /api/hcl/teams/<abbr>/games")
    print("\nPress Ctrl+C to stop")
    print("="*70 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=5001)
