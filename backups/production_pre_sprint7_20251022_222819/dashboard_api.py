"""
Auto-Updating Dashboard API
Provides real-time data endpoints for dr.foster dashboard
"""

from flask import Flask, jsonify, Blueprint
from datetime import datetime
import psycopg2
from db_config import DATABASE_CONFIG
import requests
import os

# Create Blueprint for dashboard endpoints
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

def get_db_connection():
    """Get PostgreSQL database connection"""
    try:
        return psycopg2.connect(**DATABASE_CONFIG)
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

@dashboard_bp.route('/stats', methods=['GET'])
def get_dashboard_stats():
    """Get overview statistics"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = conn.cursor()
        
        # Get team count
        cursor.execute("SELECT COUNT(*) FROM teams")
        team_count = cursor.fetchone()[0]
        
        # Get last update time
        cursor.execute("SELECT MAX(last_updated) FROM teams")
        last_update = cursor.fetchone()[0]
        
        # Get update metadata
        cursor.execute("SELECT MAX(last_update) FROM update_metadata")
        last_refresh = cursor.fetchone()[0]
        
        # Calculate current week (simple estimation based on date)
        # NFL 2025 season started Sep 4, 2025 (typical Thursday after Labor Day)
        from datetime import date
        season_start = date(2025, 9, 4)
        today = date.today()
        days_since_start = (today - season_start).days
        
        # Week calculation: If before season start, show Week 1
        # Otherwise calculate week (1-18 for regular season)
        if days_since_start < 0:
            current_week = 1  # Preseason/not started yet
        else:
            current_week = min(18, max(1, (days_since_start // 7) + 1))
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": {
                "current_week": current_week,
                "total_teams": team_count,
                "last_update": last_update.isoformat() if last_update else None,
                "last_refresh": last_refresh.isoformat() if last_refresh else None,
                "conferences": 2,
                "divisions": 8,
                "timestamp": datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@dashboard_bp.route('/database', methods=['GET'])
def get_database_info():
    """Get live database schema information"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        # Get details for each table
        table_details = []
        total_columns = 0
        total_records = 0
        
        for table_name in tables:
            # Get column count
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
            """)
            column_count = cursor.fetchone()[0]
            
            # Get record count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            record_count = cursor.fetchone()[0]
            
            total_columns += column_count
            total_records += record_count
            
            table_details.append({
                "name": table_name,
                "columns": column_count,
                "records": record_count
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": {
                "total_tables": len(tables),
                "total_columns": total_columns,
                "total_records": total_records,
                "tables": table_details,
                "database_name": DATABASE_CONFIG.get('database', 'postgres'),
                "timestamp": datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@dashboard_bp.route('/analytics', methods=['GET'])
def get_analytics_data():
    """Get real-time NFL analytics data"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = conn.cursor()
        
        # Get conference breakdown
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN abbreviation IN ('BUF', 'MIA', 'NE', 'NYJ', 'BAL', 'CIN', 'CLE', 'PIT', 
                                         'HOU', 'IND', 'JAX', 'TEN', 'DEN', 'KC', 'LV', 'LAC') 
                    THEN 'AFC'
                    ELSE 'NFC'
                END as conference,
                COUNT(*) as team_count,
                SUM(wins) as total_wins,
                SUM(losses) as total_losses,
                CAST(AVG(ppg) AS NUMERIC(10,1)) as avg_ppg
            FROM teams
            GROUP BY conference
        """)
        conference_data = cursor.fetchall()
        
        # Get division breakdown
        divisions = {
            'AFC East': ['BUF', 'MIA', 'NE', 'NYJ'],
            'AFC North': ['BAL', 'CIN', 'CLE', 'PIT'],
            'AFC South': ['HOU', 'IND', 'JAX', 'TEN'],
            'AFC West': ['DEN', 'KC', 'LV', 'LAC'],
            'NFC East': ['DAL', 'NYG', 'PHI', 'WAS'],
            'NFC North': ['CHI', 'DET', 'GB', 'MIN'],
            'NFC South': ['ATL', 'CAR', 'NO', 'TB'],
            'NFC West': ['ARI', 'LAR', 'SF', 'SEA']
        }
        
        division_stats = []
        for div_name, teams in divisions.items():
            team_list = "', '".join(teams)
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as team_count,
                    SUM(wins) as total_wins,
                    CAST(AVG(ppg) AS NUMERIC(10,1)) as avg_ppg
                FROM teams
                WHERE abbreviation IN ('{team_list}')
            """)
            result = cursor.fetchone()
            division_stats.append({
                "division": div_name,
                "teams": result[0],
                "total_wins": result[1],
                "avg_ppg": float(result[2]) if result[2] else 0
            })
        
        # Get top teams by PPG
        cursor.execute("""
            SELECT name, abbreviation, wins, losses, ppg
            FROM teams
            ORDER BY ppg DESC
            LIMIT 5
        """)
        top_teams = []
        for row in cursor.fetchall():
            top_teams.append({
                "name": row[0],
                "abbreviation": row[1],
                "wins": row[2],
                "losses": row[3],
                "ppg": float(row[4])
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": {
                "conferences": [
                    {
                        "name": row[0],
                        "teams": row[1],
                        "wins": row[2],
                        "losses": row[3],
                        "avg_ppg": float(row[4])
                    }
                    for row in conference_data
                ],
                "divisions": division_stats,
                "top_teams": top_teams,
                "timestamp": datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@dashboard_bp.route('/github', methods=['GET'])
def get_github_commits():
    """Get latest GitHub commits"""
    try:
        # GitHub API endpoint
        repo_owner = "AprilV"
        repo_name = "H.C.-Lombardo-App"
        api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits"
        
        # Make request with headers
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "HC-Lombardo-Dashboard"
        }
        
        response = requests.get(api_url, headers=headers, params={"per_page": 5})
        
        if response.status_code == 200:
            commits = response.json()
            commit_list = []
            
            for commit in commits:
                commit_list.append({
                    "sha": commit['sha'][:7],
                    "message": commit['commit']['message'].split('\n')[0],
                    "author": commit['commit']['author']['name'],
                    "date": commit['commit']['author']['date'],
                    "url": commit['html_url']
                })
            
            return jsonify({
                "success": True,
                "data": {
                    "commits": commit_list,
                    "repo_url": f"https://github.com/{repo_owner}/{repo_name}",
                    "timestamp": datetime.now().isoformat()
                }
            })
        else:
            return jsonify({
                "success": False,
                "error": f"GitHub API returned status {response.status_code}"
            }), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@dashboard_bp.route('/status', methods=['GET'])
def get_system_status():
    """Get system health status"""
    try:
        # Check database
        db_status = "online"
        db_message = "Connected"
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
                conn.close()
            else:
                db_status = "offline"
                db_message = "Connection failed"
        except Exception as e:
            db_status = "offline"
            db_message = str(e)
        
        # Check API
        api_status = "online"
        api_message = "Running"
        
        # Overall status
        overall_status = "healthy" if db_status == "online" else "degraded"
        
        return jsonify({
            "success": True,
            "data": {
                "overall": overall_status,
                "database": {
                    "status": db_status,
                    "message": db_message
                },
                "api": {
                    "status": api_status,
                    "message": api_message
                },
                "timestamp": datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Export blueprint
def register_dashboard_routes(app):
    """Register dashboard routes with Flask app"""
    app.register_blueprint(dashboard_bp)
