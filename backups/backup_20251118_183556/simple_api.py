"""
Simple API Server for Dashboard Testing
"""
from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
CORS(app)

def get_db_connection():
    return psycopg2.connect(
        dbname='nfl_analytics',
        user='postgres',
        password='aprilv120',
        host='localhost',
        port='5432'
    )

@app.route('/api/teams/count')
def teams_count():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM teams")
        count = cursor.fetchone()[0]
        conn.close()
        return jsonify({'count': count, 'status': 'success'})
    except Exception as e:
        return jsonify({'count': 0, 'status': 'error', 'message': str(e)})

@app.route('/api/teams')
def teams():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, abbreviation, conference, division FROM teams ORDER BY name")
        rows = cursor.fetchall()
        teams_list = []
        for row in rows:
            teams_list.append({
                'id': row[0],
                'name': row[1],
                'abbreviation': row[2],
                'conference': row[3],
                'division': row[4]
            })
        conn.close()
        return jsonify(teams_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    return jsonify({'message': 'H.C. Lombardo API', 'status': 'online'})

if __name__ == '__main__':
    print("="*60)
    print("🚀 H.C. LOMBARDO API SERVER")
    print("="*60)
    print("✅ Starting on: http://127.0.0.1:5000")
    print("✅ Endpoint: http://127.0.0.1:5000/api/teams/count")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=False)
