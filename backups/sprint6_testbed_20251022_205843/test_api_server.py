"""
Simple Flask server to test HCL API endpoints
Run this to test the team statistics APIs
"""

from flask import Flask
from api_routes_hcl import hcl_bp

app = Flask(__name__)

# Register HCL blueprint
app.register_blueprint(hcl_bp)

@app.route('/')
def index():
    return {
        'message': 'HCL API Test Server',
        'endpoints': [
            'GET /api/hcl/teams - List all teams',
            'GET /api/hcl/teams/<abbr> - Team details',
            'GET /api/hcl/teams/<abbr>/games - Team game history'
        ]
    }

if __name__ == '__main__':
    print("\n🏈 HCL API Test Server Starting...")
    print("=" * 50)
    print("\nAvailable endpoints:")
    print("  - http://localhost:5001/api/hcl/teams")
    print("  - http://localhost:5001/api/hcl/teams/BAL")
    print("  - http://localhost:5001/api/hcl/teams/BAL/games")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(debug=True, port=5001)
