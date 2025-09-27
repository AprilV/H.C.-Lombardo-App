"""
H.C. Lombardo NFL Dashboard - Educational Version with Official Logos
Built by April V. Sykes
Technical Implementation by GitHub Copilot
Professional NFL Analytics Dashboard with FastAPI
Self-contained with embedded HTML, CSS, and JavaScript
Educational Use Only - NFL Logos © NFL
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
from datetime import datetime
import sqlite3

# Initialize FastAPI app
app = FastAPI(title="H.C. Lombardo NFL Dashboard", version="3.0.0")

# Mock NFL Data Function with Official Logos
def get_nfl_data():
    return {
        'last_updated': datetime.now().strftime("%B %d, %Y at %I:%M %p"),
        'top_offense': [
            ("Kansas City Chiefs", "29.2", "2024", "https://a.espncdn.com/i/teamlogos/nfl/500/kc.png"),
            ("Buffalo Bills", "28.8", "2024", "https://a.espncdn.com/i/teamlogos/nfl/500/buf.png"), 
            ("Baltimore Ravens", "28.4", "2024", "https://a.espncdn.com/i/teamlogos/nfl/500/bal.png"),
            ("Detroit Lions", "27.1", "2024", "https://a.espncdn.com/i/teamlogos/nfl/500/det.png"),
            ("Dallas Cowboys", "26.1", "2024", "https://a.espncdn.com/i/teamlogos/nfl/500/dal.png"),
            ("San Francisco 49ers", "25.8", "2024", "https://a.espncdn.com/i/teamlogos/nfl/500/sf.png"),
            ("Miami Dolphins", "25.4", "2024", "https://a.espncdn.com/i/teamlogos/nfl/500/mia.png"),
            ("Philadelphia Eagles", "24.9", "2024", "https://a.espncdn.com/i/teamlogos/nfl/500/phi.png"),
            ("Cincinnati Bengals", "24.8", "2024", "https://a.espncdn.com/i/teamlogos/nfl/500/cin.png"),
            ("Los Angeles Chargers", "24.7", "2024", "https://a.espncdn.com/i/teamlogos/nfl/500/lac.png")
        ],
        'top_defense': [
            ("Baltimore Ravens", "16.5", "2024", "https://a.espncdn.com/i/teamlogos/nfl/500/bal.png"),
            ("San Francisco 49ers", "16.9", "2024", "https://a.espncdn.com/i/teamlogos/nfl/500/sf.png"),
            ("Kansas City Chiefs", "17.3", "2024", "https://a.espncdn.com/i/teamlogos/nfl/500/kc.png"),
            ("New England Patriots", "17.8", "2024", "https://a.espncdn.com/i/teamlogos/nfl/500/ne.png"),
            ("Buffalo Bills", "18.5", "2024", "https://a.espncdn.com/i/teamlogos/nfl/500/buf.png"),
            ("Pittsburgh Steelers", "19.3", "2024", "https://a.espncdn.com/i/teamlogos/nfl/500/pit.png"),
            ("Philadelphia Eagles", "19.8", "2024", "https://a.espncdn.com/i/teamlogos/nfl/500/phi.png"),
            ("Dallas Cowboys", "20.1", "2024", "https://a.espncdn.com/i/teamlogos/nfl/500/dal.png"),
            ("Los Angeles Chargers", "20.3", "2024", "https://a.espncdn.com/i/teamlogos/nfl/500/lac.png"),
            ("Detroit Lions", "20.8", "2024", "https://a.espncdn.com/i/teamlogos/nfl/500/det.png")
        ]
    }

@app.get("/", response_class=HTMLResponse)
async def dashboard_home():
    """Main Dashboard Homepage with Sidebar"""
    
    # Get NFL data
    data = get_nfl_data()
    
    # Generate table rows
    def generate_offense_rows():
        rows = ""
        for i, (team, ppg, season, logo_url) in enumerate(data['top_offense'][:10], 1):
            rows += f"""
            <tr class="{'row-gold' if i <= 3 else ''}">
                <td class="rank">#{i}</td>
                <td class="team-name">
                    <img src="{logo_url}" alt="{team} logo" class="team-logo" onerror="this.style.display='none'">
                    {team}
                </td>
                <td class="stat-value">{ppg}</td>
                <td class="season">{season}</td>
            </tr>
            """
        return rows
    
    def generate_defense_rows():
        rows = ""
        for i, (team, ppg_allowed, season, logo_url) in enumerate(data['top_defense'][:10], 1):
            rows += f"""
            <tr class="{'row-gold' if i <= 3 else ''}">
                <td class="rank">#{i}</td>
                <td class="team-name">
                    <img src="{logo_url}" alt="{team} logo" class="team-logo" onerror="this.style.display='none'">
                    {team}
                </td>
                <td class="stat-value">{ppg_allowed}</td>
                <td class="season">{season}</td>
            </tr>
            """
        return rows
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>H.C. Lombardo NFL Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
        }}
        
        /* HAMBURGER MENU */
        .menu-btn {{
            position: fixed;
            top: 20px;
            left: 20px;
            z-index: 2000;
            background: #FFD700;
            color: #000;
            font-size: 2rem;
            font-weight: 900;
            padding: 15px;
            border: 3px solid #FFA500;
            border-radius: 12px;
            cursor: pointer;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
            transition: all 0.3s ease;
            width: 60px;
            height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .menu-btn:hover {{
            background: #FFA500;
            transform: scale(1.1);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.6);
        }}
        
        /* SIDEBAR */
        .sidebar {{
            position: fixed;
            left: -320px;
            top: 0;
            width: 320px;
            height: 100vh;
            background: linear-gradient(180deg, #000000 0%, #1a1a1a 100%);
            border-right: 3px solid #FFD700;
            transition: left 0.4s ease;
            z-index: 1500;
            box-shadow: 5px 0 20px rgba(0, 0, 0, 0.5);
        }}
        
        .sidebar.open {{ left: 0; }}
        
        .sidebar-header {{
            padding: 30px 25px 25px 25px;
            border-bottom: 2px solid #FFD700;
            background: linear-gradient(45deg, #FFD700, #FFA500);
            color: #000;
        }}
        
        .sidebar-header h1 {{
            font-size: 1.6rem;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .sidebar-nav {{
            padding: 25px 0;
        }}
        
        .nav-item {{
            display: block;
            color: #fff;
            text-decoration: none;
            padding: 18px 25px;
            margin: 5px 15px;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.05);
            border-left: 4px solid transparent;
            transition: all 0.3s ease;
            font-size: 1rem;
            font-weight: 500;
        }}
        
        .nav-item:hover {{
            background: rgba(255, 215, 0, 0.15);
            border-left-color: #FFD700;
            transform: translateX(8px);
            color: #FFD700;
        }}
        
        .nav-item span {{
            margin-right: 12px;
            font-size: 1.2rem;
        }}
        
        /* OVERLAY */
        .overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.6);
            z-index: 1000;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
        }}
        
        .overlay.active {{
            opacity: 1;
            visibility: visible;
        }}
        
        /* MAIN CONTENT */
        .main-content {{
            padding: 100px 30px 30px 30px;
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .dashboard-header {{
            text-align: center;
            margin-bottom: 40px;
            background: rgba(255, 255, 255, 0.1);
            padding: 40px 30px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }}
        
        .dashboard-header h1 {{
            font-size: 3rem;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #FFD700, #FFA500);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
        }}
        
        .nfl-logo {{
            width: 50px;
            height: 50px;
            object-fit: contain;
        }}
        
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }}
        
        .data-section {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .section-header {{
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 20px;
            text-align: center;
            color: #FFD700;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }}
        
        .section-logo {{
            width: 32px;
            height: 32px;
            object-fit: contain;
        }}
        
        .data-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        .data-table th {{
            background: rgba(0, 0, 0, 0.3);
            color: #FFD700;
            padding: 15px 12px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #FFD700;
        }}
        
        .data-table td {{
            padding: 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .data-table tr:hover {{
            background: rgba(255, 215, 0, 0.1);
        }}
        
        .row-gold {{
            background: rgba(255, 215, 0, 0.15) !important;
        }}
        
        .rank {{
            font-weight: bold;
            color: #FFD700;
            text-align: center;
            width: 60px;
        }}
        
        .team-name {{
            font-weight: 600;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        .team-logo {{
            width: 32px;
            height: 32px;
            object-fit: contain;
            border-radius: 4px;
            background: white;
            padding: 2px;
        }}
        
        .stat-value {{
            font-weight: bold;
            color: #00ff88;
            text-align: center;
        }}
        
        .season {{
            color: #87CEEB;
            text-align: center;
        }}
        
        .dashboard-footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
        }}
        
        .last-updated {{
            font-size: 1.1rem;
            color: #FFD700;
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <!-- HAMBURGER MENU BUTTON -->
    <button class="menu-btn" onclick="toggleSidebar()">☰</button>
    
    <!-- OVERLAY -->
    <div class="overlay" id="overlay" onclick="closeSidebar()"></div>
    
    <!-- SIDEBAR NAVIGATION -->
    <nav class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <h1>H.C. Lombardo</h1>
            <p>NFL Analytics Dashboard</p>
        </div>
        
        <div class="sidebar-nav">
            <a href="/" class="nav-item">
                <span>🏠</span>Dashboard Home
            </a>
            <a href="/teams" class="nav-item">
                <span>🏈</span>NFL Teams
            </a>
            <a href="/predictions" class="nav-item">
                <span>🎯</span>Predictions
            </a>
            <a href="/api-info" class="nav-item">
                <span>📚</span>API Info
            </a>
        </div>
    </nav>
    
    <!-- MAIN DASHBOARD CONTENT -->
    <div class="main-content">
        <!-- Dashboard Header -->
        <div class="dashboard-header">
            <h1>
                <img src="https://a.espncdn.com/combiner/i?img=/i/teamlogos/leagues/500/nfl.png" alt="NFL Logo" class="nfl-logo" onerror="this.style.display='none'">
                H.C. Lombardo Dashboard
            </h1>
            <p>Professional Analytics & Team Performance Data</p>
            <p style="font-size: 0.8rem; opacity: 0.7; margin-top: 10px;">Educational Use - Official Data</p>
        </div>
        
        <!-- Dashboard Grid -->
        <div class="dashboard-grid">
            <!-- TOP OFFENSIVE TEAMS -->
            <div class="data-section">
                <div class="section-header">
                    <img src="https://a.espncdn.com/combiner/i?img=/i/teamlogos/leagues/500/nfl.png" alt="NFL Logo" class="section-logo" onerror="this.style.display='none'">
                    Top 10 Offensive Teams
                </div>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Team</th>
                            <th>PPG</th>
                            <th>Season</th>
                        </tr>
                    </thead>
                    <tbody>
                        {generate_offense_rows()}
                    </tbody>
                </table>
            </div>
            
            <!-- TOP DEFENSIVE TEAMS -->
            <div class="data-section">
                <div class="section-header">
                    <img src="https://a.espncdn.com/combiner/i?img=/i/teamlogos/leagues/500/nfl.png" alt="NFL Logo" class="section-logo" onerror="this.style.display='none'">
                    Top 10 Defensive Teams
                </div>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Team</th>
                            <th>PA/G</th>
                            <th>Season</th>
                        </tr>
                    </thead>
                    <tbody>
                        {generate_defense_rows()}
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Dashboard Footer -->
        <div class="dashboard-footer">
            <div class="last-updated">
                📊 Last Updated: {data['last_updated']}
            </div>
            <p>🚀 H.C. Lombardo Dashboard - Built by April V. Sykes, Owner & Developer © 2025</p>
            <p style="font-size: 0.85rem; margin-top: 8px; opacity: 0.8;">
                🤖 Technical Implementation by GitHub Copilot | Educational Use Only
            </p>
        </div>
    </div>
    
    <!-- SIDEBAR JAVASCRIPT -->
    <script>
        console.log('🚀 H.C. Lombardo NFL Dashboard Loaded!');
        
        function toggleSidebar() {{
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('overlay');
            const isOpen = sidebar.classList.contains('open');
            
            if (isOpen) {{
                closeSidebar();
            }} else {{
                openSidebar();
            }}
        }}
        
        function openSidebar() {{
            document.getElementById('sidebar').classList.add('open');
            document.getElementById('overlay').classList.add('active');
        }}
        
        function closeSidebar() {{
            document.getElementById('sidebar').classList.remove('open');
            document.getElementById('overlay').classList.remove('active');
        }}
    </script>
</body>
</html>
    """
    
    return html_content

@app.get("/teams", response_class=HTMLResponse)
async def teams_page():
    """NFL Teams Page with Official Logos - Educational Use"""
    
    data = get_nfl_data()
    
    # Generate team stats with official logos
    def generate_all_teams():
        teams_html = ""
        all_teams = [
            # AFC East
            ("Buffalo Bills", "13-4", "28.8 PPG", "18.5 PA", "AFC East", "https://a.espncdn.com/i/teamlogos/nfl/500/buf.png"),
            ("Miami Dolphins", "11-6", "25.4 PPG", "21.2 PA", "AFC East", "https://a.espncdn.com/i/teamlogos/nfl/500/mia.png"),
            ("New England Patriots", "8-9", "20.1 PPG", "17.8 PA", "AFC East", "https://a.espncdn.com/i/teamlogos/nfl/500/ne.png"),
            ("New York Jets", "7-10", "18.6 PPG", "20.7 PA", "AFC East", "https://a.espncdn.com/i/teamlogos/nfl/500/nyj.png"),
            
            # AFC North
            ("Baltimore Ravens", "13-4", "28.4 PPG", "16.5 PA", "AFC North", "https://a.espncdn.com/i/teamlogos/nfl/500/bal.png"),
            ("Cincinnati Bengals", "9-8", "24.8 PPG", "22.1 PA", "AFC North", "https://a.espncdn.com/i/teamlogos/nfl/500/cin.png"),
            ("Cleveland Browns", "7-10", "18.9 PPG", "24.5 PA", "AFC North", "https://a.espncdn.com/i/teamlogos/nfl/500/cle.png"),
            ("Pittsburgh Steelers", "9-8", "20.6 PPG", "19.3 PA", "AFC North", "https://a.espncdn.com/i/teamlogos/nfl/500/pit.png"),
            
            # AFC South
            ("Houston Texans", "10-7", "23.3 PPG", "20.9 PA", "AFC South", "https://a.espncdn.com/i/teamlogos/nfl/500/hou.png"),
            ("Indianapolis Colts", "9-8", "22.5 PPG", "21.8 PA", "AFC South", "https://a.espncdn.com/i/teamlogos/nfl/500/ind.png"),
            ("Jacksonville Jaguars", "9-8", "24.1 PPG", "24.8 PA", "AFC South", "https://a.espncdn.com/i/teamlogos/nfl/500/jax.png"),
            ("Tennessee Titans", "6-11", "16.5 PPG", "28.4 PA", "AFC South", "https://a.espncdn.com/i/teamlogos/nfl/500/ten.png"),
            
            # AFC West
            ("Kansas City Chiefs", "14-3", "29.2 PPG", "17.3 PA", "AFC West", "https://a.espncdn.com/i/teamlogos/nfl/500/kc.png"),
            ("Denver Broncos", "8-9", "21.3 PPG", "26.5 PA", "AFC West", "https://a.espncdn.com/i/teamlogos/nfl/500/den.png"),
            ("Las Vegas Raiders", "8-9", "21.8 PPG", "25.9 PA", "AFC West", "https://a.espncdn.com/i/teamlogos/nfl/500/lv.png"),
            ("Los Angeles Chargers", "10-7", "24.7 PPG", "20.3 PA", "AFC West", "https://a.espncdn.com/i/teamlogos/nfl/500/lac.png"),
            
            # NFC East
            ("Dallas Cowboys", "12-5", "26.1 PPG", "20.1 PA", "NFC East", "https://a.espncdn.com/i/teamlogos/nfl/500/dal.png"),
            ("Philadelphia Eagles", "11-6", "24.9 PPG", "19.8 PA", "NFC East", "https://a.espncdn.com/i/teamlogos/nfl/500/phi.png"),
            ("New York Giants", "6-11", "15.6 PPG", "27.5 PA", "NFC East", "https://a.espncdn.com/i/teamlogos/nfl/500/nyg.png"),
            ("Washington Commanders", "8-8-1", "21.0 PPG", "22.2 PA", "NFC East", "https://a.espncdn.com/i/teamlogos/nfl/500/wsh.png"),
            
            # NFC North
            ("Detroit Lions", "12-5", "27.1 PPG", "20.8 PA", "NFC North", "https://a.espncdn.com/i/teamlogos/nfl/500/det.png"),
            ("Green Bay Packers", "9-8", "23.0 PPG", "20.8 PA", "NFC North", "https://a.espncdn.com/i/teamlogos/nfl/500/gb.png"),
            ("Minnesota Vikings", "7-10", "21.8 PPG", "25.1 PA", "NFC North", "https://a.espncdn.com/i/teamlogos/nfl/500/min.png"),
            ("Chicago Bears", "7-10", "17.9 PPG", "27.3 PA", "NFC North", "https://a.espncdn.com/i/teamlogos/nfl/500/chi.png"),
            
            # NFC South
            ("Tampa Bay Buccaneers", "8-9", "20.2 PPG", "22.9 PA", "NFC South", "https://a.espncdn.com/i/teamlogos/nfl/500/tb.png"),
            ("New Orleans Saints", "9-8", "21.6 PPG", "22.8 PA", "NFC South", "https://a.espncdn.com/i/teamlogos/nfl/500/no.png"),
            ("Atlanta Falcons", "7-10", "21.8 PPG", "25.4 PA", "NFC South", "https://a.espncdn.com/i/teamlogos/nfl/500/atl.png"),
            ("Carolina Panthers", "7-10", "15.9 PPG", "25.3 PA", "NFC South", "https://a.espncdn.com/i/teamlogos/nfl/500/car.png"),
            
            # NFC West
            ("San Francisco 49ers", "12-5", "25.8 PPG", "16.9 PA", "NFC West", "https://a.espncdn.com/i/teamlogos/nfl/500/sf.png"),
            ("Seattle Seahawks", "9-8", "23.4 PPG", "22.1 PA", "NFC West", "https://a.espncdn.com/i/teamlogos/nfl/500/sea.png"),
            ("Los Angeles Rams", "10-7", "23.0 PPG", "22.0 PA", "NFC West", "https://a.espncdn.com/i/teamlogos/nfl/500/lar.png"),
            ("Arizona Cardinals", "4-13", "16.5 PPG", "28.6 PA", "NFC West", "https://a.espncdn.com/i/teamlogos/nfl/500/ari.png"),
        ]
        
        for i, (team, record, ppg, pa, division, logo_url) in enumerate(all_teams, 1):
            if i <= 5:
                row_class = "row-gold"
            elif i <= 10:
                row_class = "row-silver"
            elif i <= 15:
                row_class = "row-bronze"
            else:
                row_class = ""
            
            teams_html += f"""
            <tr class="{row_class}">
                <td class="rank">#{i}</td>
                <td class="team-name">
                    <img src="{logo_url}" alt="{team} logo" class="team-logo" onerror="this.style.display='none'">
                    {team}
                </td>
                <td class="stat-value">{record}</td>
                <td class="stat-value">{ppg}</td>
                <td class="stat-value">{pa}</td>
                <td class="division">{division}</td>
            </tr>
            """
        return teams_html
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>H.C. Lombardo NFL Teams</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; min-height: 100vh; }}
        
        /* HAMBURGER MENU */
        .menu-btn {{ position: fixed; top: 20px; left: 20px; z-index: 2000; background: #FFD700; color: #000; font-size: 2rem; font-weight: 900; padding: 15px; border: 3px solid #FFA500; border-radius: 12px; cursor: pointer; box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4); transition: all 0.3s ease; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; }}
        .menu-btn:hover {{ background: #FFA500; transform: scale(1.1); }}
        
        /* SIDEBAR */
        .sidebar {{ position: fixed; left: -320px; top: 0; width: 320px; height: 100vh; background: linear-gradient(180deg, #000000 0%, #1a1a1a 100%); border-right: 3px solid #FFD700; transition: left 0.4s ease; z-index: 1500; box-shadow: 5px 0 20px rgba(0, 0, 0, 0.5); }}
        .sidebar.open {{ left: 0; }}
        .sidebar-header {{ padding: 30px 25px 25px 25px; border-bottom: 2px solid #FFD700; background: linear-gradient(45deg, #FFD700, #FFA500); color: #000; }}
        .sidebar-header h1 {{ font-size: 1.6rem; font-weight: bold; margin-bottom: 5px; }}
        .sidebar-nav {{ padding: 25px 0; }}
        .nav-item {{ display: block; color: #fff; text-decoration: none; padding: 18px 25px; margin: 5px 15px; border-radius: 10px; background: rgba(255, 255, 255, 0.05); border-left: 4px solid transparent; transition: all 0.3s ease; font-size: 1rem; font-weight: 500; }}
        .nav-item:hover {{ background: rgba(255, 215, 0, 0.15); border-left-color: #FFD700; transform: translateX(8px); color: #FFD700; }}
        .nav-item span {{ margin-right: 12px; font-size: 1.2rem; }}
        
        /* OVERLAY */
        .overlay {{ position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0, 0, 0, 0.6); z-index: 1000; opacity: 0; visibility: hidden; transition: all 0.3s ease; }}
        .overlay.active {{ opacity: 1; visibility: visible; }}
        
        /* MAIN CONTENT */
        .main-content {{ padding: 100px 30px 30px 30px; max-width: 1400px; margin: 0 auto; }}
        .page-header {{ text-align: center; margin-bottom: 40px; background: rgba(255, 255, 255, 0.1); padding: 30px; border-radius: 20px; backdrop-filter: blur(10px); }}
        .page-header h1 {{ font-size: 3rem; margin-bottom: 10px; background: linear-gradient(45deg, #FFD700, #FFA500); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; display: flex; align-items: center; justify-content: center; gap: 15px; }}
        .nfl-logo {{ width: 50px; height: 50px; object-fit: contain; }}
        
        .teams-table {{ width: 100%; border-collapse: collapse; background: rgba(255, 255, 255, 0.05); border-radius: 15px; overflow: hidden; margin: 20px 0; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3); }}
        .teams-table th {{ background: linear-gradient(45deg, #000000, #1a1a1a); color: #FFD700; padding: 15px 12px; text-align: left; font-weight: 600; border-bottom: 2px solid #FFD700; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.5px; }}
        .teams-table td {{ padding: 12px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); transition: all 0.3s ease; }}
        .teams-table tr:hover {{ background: rgba(255, 215, 0, 0.1); transform: scale(1.01); }}
        .row-gold {{ background: rgba(255, 215, 0, 0.15) !important; }}
        .row-silver {{ background: rgba(192, 192, 192, 0.1) !important; }}
        .row-bronze {{ background: rgba(205, 127, 50, 0.1) !important; }}
        .rank {{ font-weight: bold; color: #FFD700; text-align: center; width: 60px; font-size: 1.1rem; }}
        .team-name {{ font-weight: 600; color: #fff; display: flex; align-items: center; gap: 12px; }}
        .team-logo {{ width: 32px; height: 32px; object-fit: contain; border-radius: 4px; background: white; padding: 2px; }}
        .stat-value {{ font-weight: bold; color: #00ff88; text-align: center; }}
        .division {{ color: #87CEEB; text-align: center; font-size: 0.9rem; }}
        .footer {{ text-align: center; margin-top: 40px; padding: 20px; background: rgba(255, 255, 255, 0.1); border-radius: 15px; }}
    </style>
</head>
<body>
    <!-- Hamburger Menu -->
    <button class="menu-btn" id="menuBtn">☰</button>
    
    <!-- Overlay -->
    <div class="overlay" id="overlay"></div>
    
    <!-- Sidebar -->
    <nav class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <h1>H.C. Lombardo</h1>
            <p>NFL Analytics Dashboard</p>
        </div>
        <div class="sidebar-nav">
            <a href="/" class="nav-item"><span>🏠</span>Dashboard Home</a>
            <a href="/teams" class="nav-item"><span>🏈</span>NFL Teams</a>
            <a href="/predictions" class="nav-item"><span>🎯</span>Predictions</a>
            <a href="/api-info" class="nav-item"><span>📚</span>API Info</a>
        </div>
    </nav>
    
    <!-- Main Content -->
    <div class="main-content">
        <div class="page-header">
            <h1>
                <img src="https://a.espncdn.com/combiner/i?img=/i/teamlogos/leagues/500/nfl.png" alt="NFL Logo" class="nfl-logo" onerror="this.style.display='none'">
                Teams
            </h1>
            <p>Complete team statistics with official team logos - Educational Use Only</p>
            <p style="font-size: 0.8rem; opacity: 0.7; margin-top: 10px;">
                *Official team logos used for educational purposes under fair use doctrine
            </p>
        </div>
        
        <table class="teams-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Team</th>
                    <th>Record</th>
                    <th>Points/Game</th>
                    <th>Points Against</th>
                    <th>Division</th>
                </tr>
            </thead>
            <tbody>
                {generate_all_teams()}
            </tbody>
        </table>
        
        <div class="footer">
            <p>📊 Last Updated: {data['last_updated']}</p>
            <p>🚀 H.C. Lombardo NFL Dashboard - Built by April V. Sykes, Owner & Developer © 2025</p>
            <p style="font-size: 0.85rem; margin-top: 8px; opacity: 0.8;">
                🤖 Technical Implementation by GitHub Copilot | Educational Use - NFL Logos © NFL
            </p>
        </div>
    </div>
    
    <script>
        function toggleSidebar() {{
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('overlay');
            const isOpen = sidebar.classList.contains('open');
            
            if (isOpen) {{
                sidebar.classList.remove('open');
                overlay.classList.remove('active');
            }} else {{
                sidebar.classList.add('open');
                overlay.classList.add('active');
            }}
        }}
        
        document.getElementById('menuBtn').addEventListener('click', toggleSidebar);
        document.getElementById('overlay').addEventListener('click', toggleSidebar);
        
        console.log('🏈 NFL Teams page with official logos loaded!');
    </script>
</body>
</html>
    """
    
    return html_content

@app.get("/predictions", response_class=HTMLResponse)
async def predictions_page():
    """NFL Predictions Page with Sidebar"""
    
    data = get_nfl_data()
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>H.C. Lombardo NFL Predictions</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; min-height: 100vh; }}
        
        /* HAMBURGER MENU */
        .menu-btn {{ position: fixed; top: 20px; left: 20px; z-index: 2000; background: #FFD700; color: #000; font-size: 2rem; font-weight: 900; padding: 15px; border: 3px solid #FFA500; border-radius: 12px; cursor: pointer; box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4); transition: all 0.3s ease; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; }}
        .menu-btn:hover {{ background: #FFA500; transform: scale(1.1); }}
        
        /* SIDEBAR */
        .sidebar {{ position: fixed; left: -320px; top: 0; width: 320px; height: 100vh; background: linear-gradient(180deg, #000000 0%, #1a1a1a 100%); border-right: 3px solid #FFD700; transition: left 0.4s ease; z-index: 1500; box-shadow: 5px 0 20px rgba(0, 0, 0, 0.5); }}
        .sidebar.open {{ left: 0; }}
        .sidebar-header {{ padding: 30px 25px 25px 25px; border-bottom: 2px solid #FFD700; background: linear-gradient(45deg, #FFD700, #FFA500); color: #000; }}
        .sidebar-header h1 {{ font-size: 1.6rem; font-weight: bold; margin-bottom: 5px; }}
        .sidebar-nav {{ padding: 25px 0; }}
        .nav-item {{ display: block; color: #fff; text-decoration: none; padding: 18px 25px; margin: 5px 15px; border-radius: 10px; background: rgba(255, 255, 255, 0.05); border-left: 4px solid transparent; transition: all 0.3s ease; font-size: 1rem; font-weight: 500; }}
        .nav-item:hover {{ background: rgba(255, 215, 0, 0.15); border-left-color: #FFD700; transform: translateX(8px); color: #FFD700; }}
        .nav-item span {{ margin-right: 12px; font-size: 1.2rem; }}
        
        /* OVERLAY */
        .overlay {{ position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0, 0, 0, 0.6); z-index: 1000; opacity: 0; visibility: hidden; transition: all 0.3s ease; }}
        .overlay.active {{ opacity: 1; visibility: visible; }}
        
        /* MAIN CONTENT */
        .main-content {{ padding: 100px 30px 30px 30px; max-width: 1400px; margin: 0 auto; }}
        .page-header {{ text-align: center; margin-bottom: 40px; background: rgba(255, 255, 255, 0.1); padding: 30px; border-radius: 20px; backdrop-filter: blur(10px); }}
        .page-header h1 {{ font-size: 3rem; margin-bottom: 10px; background: linear-gradient(45deg, #FFD700, #FFA500); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; display: flex; align-items: center; justify-content: center; gap: 15px; }}
        .nfl-logo {{ width: 50px; height: 50px; object-fit: contain; }}
        
        .predictions-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 25px; margin: 30px 0; }}
        .prediction-card {{ background: rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 25px; border: 1px solid rgba(255, 255, 255, 0.2); backdrop-filter: blur(10px); }}
        .game-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid rgba(255, 255, 255, 0.2); }}
        .game-title {{ display: flex; align-items: center; gap: 10px; }}
        .team-logos {{ display: flex; align-items: center; gap: 8px; }}
        .team-logo {{ width: 32px; height: 32px; object-fit: contain; border-radius: 4px; background: white; padding: 2px; }}
        .vs-text {{ margin: 0 8px; font-weight: bold; color: #FFD700; }}
        .confidence-badge {{ background: #28a745; color: white; padding: 8px 15px; border-radius: 20px; font-size: 0.9rem; font-weight: bold; }}
        .prediction-details div {{ margin-bottom: 12px; padding: 10px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.1); }}
        .footer {{ text-align: center; margin-top: 40px; padding: 20px; background: rgba(255, 255, 255, 0.1); border-radius: 15px; }}
    </style>
</head>
<body>
    <!-- Hamburger Menu -->
    <button class="menu-btn" id="menuBtn">☰</button>
    
    <!-- Overlay -->
    <div class="overlay" id="overlay"></div>
    
    <!-- Sidebar -->
    <nav class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <h1>H.C. Lombardo</h1>
            <p>NFL Analytics Dashboard</p>
        </div>
        <div class="sidebar-nav">
            <a href="/" class="nav-item"><span>🏠</span>Dashboard Home</a>
            <a href="/teams" class="nav-item"><span>🏈</span>NFL Teams</a>
            <a href="/predictions" class="nav-item"><span>🎯</span>Predictions</a>
            <a href="/api-info" class="nav-item"><span>📚</span>API Info</a>
        </div>
    </nav>
    
    <!-- Main Content -->
    <div class="main-content">
        <div class="page-header">
            <h1>
                <img src="https://a.espncdn.com/combiner/i?img=/i/teamlogos/leagues/500/nfl.png" alt="NFL Logo" class="nfl-logo" onerror="this.style.display='none'">
                Predictions
            </h1>
            <p>Advanced statistical analysis and betting predictions</p>
        </div>
        
        <div class="predictions-grid">
            <div class="prediction-card">
                <div class="game-header">
                    <div class="game-title">
                        <div class="team-logos">
                            <img src="https://a.espncdn.com/i/teamlogos/nfl/500/kc.png" alt="Chiefs logo" class="team-logo" onerror="this.style.display='none'">
                            <span class="vs-text">vs</span>
                            <img src="https://a.espncdn.com/i/teamlogos/nfl/500/buf.png" alt="Bills logo" class="team-logo" onerror="this.style.display='none'">
                        </div>
                        <h3>Chiefs vs Bills</h3>
                    </div>
                    <span class="confidence-badge">85% Confidence</span>
                </div>
                <div class="prediction-details">
                    <div><strong>Spread:</strong> Chiefs -3.5 ⭐</div>
                    <div><strong>Over/Under:</strong> 54.5 (OVER) 📈</div>
                    <div><strong>Moneyline:</strong> Chiefs -165 💰</div>
                    <div><strong>Score Prediction:</strong> Chiefs 31, Bills 24</div>
                </div>
            </div>
            
            <div class="prediction-card">
                <div class="game-header">
                    <div class="game-title">
                        <div class="team-logos">
                            <img src="https://a.espncdn.com/i/teamlogos/nfl/500/dal.png" alt="Cowboys logo" class="team-logo" onerror="this.style.display='none'">
                            <span class="vs-text">vs</span>
                            <img src="https://a.espncdn.com/i/teamlogos/nfl/500/sf.png" alt="49ers logo" class="team-logo" onerror="this.style.display='none'">
                        </div>
                        <h3>Cowboys vs 49ers</h3>
                    </div>
                    <span class="confidence-badge">78% Confidence</span>
                </div>
                <div class="prediction-details">
                    <div><strong>Spread:</strong> 49ers -6.5 ⭐</div>
                    <div><strong>Over/Under:</strong> 48.5 (UNDER) 📉</div>
                    <div><strong>Moneyline:</strong> 49ers -245 💰</div>
                    <div><strong>Score Prediction:</strong> 49ers 27, Cowboys 17</div>
                </div>
            </div>
            
            <div class="prediction-card">
                <div class="game-header">
                    <div class="game-title">
                        <div class="team-logos">
                            <img src="https://a.espncdn.com/i/teamlogos/nfl/500/bal.png" alt="Ravens logo" class="team-logo" onerror="this.style.display='none'">
                            <span class="vs-text">vs</span>
                            <img src="https://a.espncdn.com/i/teamlogos/nfl/500/pit.png" alt="Steelers logo" class="team-logo" onerror="this.style.display='none'">
                        </div>
                        <h3>Ravens vs Steelers</h3>
                    </div>
                    <span class="confidence-badge">82% Confidence</span>
                </div>
                <div class="prediction-details">
                    <div><strong>Spread:</strong> Ravens -4.5 ⭐</div>
                    <div><strong>Over/Under:</strong> 45.5 (OVER) 📈</div>
                    <div><strong>Moneyline:</strong> Ravens -185 💰</div>
                    <div><strong>Score Prediction:</strong> Ravens 28, Steelers 21</div>
                </div>
            </div>
            
            <div class="prediction-card">
                <div class="game-header">
                    <div class="game-title">
                        <div class="team-logos">
                            <img src="https://a.espncdn.com/i/teamlogos/nfl/500/det.png" alt="Lions logo" class="team-logo" onerror="this.style.display='none'">
                            <span class="vs-text">vs</span>
                            <img src="https://a.espncdn.com/i/teamlogos/nfl/500/gb.png" alt="Packers logo" class="team-logo" onerror="this.style.display='none'">
                        </div>
                        <h3>Lions vs Packers</h3>
                    </div>
                    <span class="confidence-badge">75% Confidence</span>
                </div>
                <div class="prediction-details">
                    <div><strong>Spread:</strong> Lions -3.0 ⭐</div>
                    <div><strong>Over/Under:</strong> 52.5 (OVER) 📈</div>
                    <div><strong>Moneyline:</strong> Lions -155 💰</div>
                    <div><strong>Score Prediction:</strong> Lions 31, Packers 24</div>
                </div>
            </div>
            
            <div class="prediction-card">
                <div class="game-header">
                    <div class="game-title">
                        <div class="team-logos">
                            <img src="https://a.espncdn.com/i/teamlogos/nfl/500/phi.png" alt="Eagles logo" class="team-logo" onerror="this.style.display='none'">
                            <span class="vs-text">vs</span>
                            <img src="https://a.espncdn.com/i/teamlogos/nfl/500/nyg.png" alt="Giants logo" class="team-logo" onerror="this.style.display='none'">
                        </div>
                        <h3>Eagles vs Giants</h3>
                    </div>
                    <span class="confidence-badge">88% Confidence</span>
                </div>
                <div class="prediction-details">
                    <div><strong>Spread:</strong> Eagles -9.5 ⭐</div>
                    <div><strong>Over/Under:</strong> 44.5 (UNDER) 📉</div>
                    <div><strong>Moneyline:</strong> Eagles -420 💰</div>
                    <div><strong>Score Prediction:</strong> Eagles 35, Giants 14</div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>📊 Last Updated: {data['last_updated']}</p>
            <p>🚀 H.C. Lombardo NFL Dashboard - Built by April V. Sykes, Owner & Developer © 2025</p>
            <p style="font-size: 0.85rem; margin-top: 8px; opacity: 0.8;">
                🤖 Technical Implementation by GitHub Copilot | Educational Use Only
            </p>
        </div>
    </div>
    
    <script>
        function toggleSidebar() {{
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('overlay');
            const isOpen = sidebar.classList.contains('open');
            
            if (isOpen) {{
                sidebar.classList.remove('open');
                overlay.classList.remove('active');
            }} else {{
                sidebar.classList.add('open');
                overlay.classList.add('active');
            }}
        }}
        
        document.getElementById('menuBtn').addEventListener('click', toggleSidebar);
        document.getElementById('overlay').addEventListener('click', toggleSidebar);
        
        console.log('🎯 NFL Predictions page loaded!');
    </script>
</body>
</html>
    """
    
    return html_content

@app.get("/api-info", response_class=HTMLResponse)
async def api_info_page():
    """API Information Page with Sidebar"""
    
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>H.C. Lombardo API Information</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; min-height: 100vh; }
        
        /* HAMBURGER MENU */
        .menu-btn { position: fixed; top: 20px; left: 20px; z-index: 2000; background: #FFD700; color: #000; font-size: 2rem; font-weight: 900; padding: 15px; border: 3px solid #FFA500; border-radius: 12px; cursor: pointer; box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4); transition: all 0.3s ease; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; }
        .menu-btn:hover { background: #FFA500; transform: scale(1.1); }
        
        /* SIDEBAR */
        .sidebar { position: fixed; left: -320px; top: 0; width: 320px; height: 100vh; background: linear-gradient(180deg, #000000 0%, #1a1a1a 100%); border-right: 3px solid #FFD700; transition: left 0.4s ease; z-index: 1500; box-shadow: 5px 0 20px rgba(0, 0, 0, 0.5); }
        .sidebar.open { left: 0; }
        .sidebar-header { padding: 30px 25px 25px 25px; border-bottom: 2px solid #FFD700; background: linear-gradient(45deg, #FFD700, #FFA500); color: #000; }
        .sidebar-header h1 { font-size: 1.6rem; font-weight: bold; margin-bottom: 5px; }
        .sidebar-nav { padding: 25px 0; }
        .nav-item { display: block; color: #fff; text-decoration: none; padding: 18px 25px; margin: 5px 15px; border-radius: 10px; background: rgba(255, 255, 255, 0.05); border-left: 4px solid transparent; transition: all 0.3s ease; font-size: 1rem; font-weight: 500; }
        .nav-item:hover { background: rgba(255, 215, 0, 0.15); border-left-color: #FFD700; transform: translateX(8px); color: #FFD700; }
        .nav-item span { margin-right: 12px; font-size: 1.2rem; }
        
        /* OVERLAY */
        .overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0, 0, 0, 0.6); z-index: 1000; opacity: 0; visibility: hidden; transition: all 0.3s ease; }
        .overlay.active { opacity: 1; visibility: visible; }
        
        /* MAIN CONTENT */
        .main-content { padding: 100px 30px 30px 30px; max-width: 1400px; margin: 0 auto; }
        .page-header { text-align: center; margin-bottom: 40px; background: rgba(255, 255, 255, 0.1); padding: 30px; border-radius: 20px; backdrop-filter: blur(10px); }
        .page-header h1 { font-size: 3rem; margin-bottom: 10px; background: linear-gradient(45deg, #FFD700, #FFA500); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; display: flex; align-items: center; justify-content: center; gap: 15px; }
        .nfl-logo { width: 50px; height: 50px; object-fit: contain; }
        
        .api-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 25px; margin: 30px 0; }
        .api-card { background: rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 25px; border: 1px solid rgba(255, 255, 255, 0.2); backdrop-filter: blur(10px); }
        .api-card h3 { color: #FFD700; margin-bottom: 15px; font-size: 1.3rem; }
        .api-link { display: inline-block; background: #28a745; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; margin-top: 15px; transition: background 0.3s ease; }
        .api-link:hover { background: #218838; }
        .footer { text-align: center; margin-top: 40px; padding: 20px; background: rgba(255, 255, 255, 0.1); border-radius: 15px; }
    </style>
</head>
<body>
    <!-- Hamburger Menu -->
    <button class="menu-btn" id="menuBtn">☰</button>
    
    <!-- Overlay -->
    <div class="overlay" id="overlay"></div>
    
    <!-- Sidebar -->
    <nav class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <h1>H.C. Lombardo</h1>
            <p>NFL Analytics Dashboard</p>
        </div>
        <div class="sidebar-nav">
            <a href="/" class="nav-item"><span>🏠</span>Dashboard Home</a>
            <a href="/teams" class="nav-item"><span>🏈</span>NFL Teams</a>
            <a href="/predictions" class="nav-item"><span>🎯</span>Predictions</a>
            <a href="/api-info" class="nav-item"><span>📚</span>API Info</a>
        </div>
    </nav>
    
    <!-- Main Content -->
    <div class="main-content">
        <div class="page-header">
            <h1>
                <img src="https://a.espncdn.com/combiner/i?img=/i/teamlogos/leagues/500/nfl.png" alt="NFL Logo" class="nfl-logo" onerror="this.style.display='none'">
                API Information
            </h1>
            <p>Explore our analytics APIs and documentation</p>
        </div>
        
        <div class="api-grid">
            <div class="api-card">
                <h3>🏈 Teams API</h3>
                <p>Get comprehensive NFL team data including statistics, rankings, and performance metrics.</p>
                <p><strong>Endpoint:</strong> <code>/api/teams</code></p>
                <a href="/api/teams" class="api-link">View JSON Data</a>
            </div>
            
            <div class="api-card">
                <h3>📊 FastAPI Docs</h3>
                <p>Interactive API documentation with Swagger UI. Test endpoints and view detailed schemas.</p>
                <p><strong>Features:</strong> Interactive testing, request/response examples</p>
                <a href="/docs" class="api-link">Open Swagger UI</a>
            </div>
            
            <div class="api-card">
                <h3>📖 ReDoc Documentation</h3>
                <p>Alternative API documentation with a clean, professional interface.</p>
                <p><strong>Features:</strong> Clean layout, comprehensive schemas</p>
                <a href="/redoc" class="api-link">Open ReDoc</a>
            </div>
            
            <div class="api-card">
                <h3>🔧 Health Check</h3>
                <p>Monitor API status and server health for system monitoring.</p>
                <p><strong>Endpoint:</strong> <code>/health</code></p>
                <a href="/health" class="api-link">Check Status</a>
            </div>
        </div>
        
        <div class="footer">
            <p>🚀 H.C. Lombardo NFL Dashboard - Built by April V. Sykes, Owner & Developer © 2025</p>
            <p style="font-size: 0.85rem; margin-top: 8px; opacity: 0.8;">
                🤖 Technical Implementation by GitHub Copilot | Educational Use Only
            </p>
        </div>
    </div>
    
    <script>
        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('overlay');
            const isOpen = sidebar.classList.contains('open');
            
            if (isOpen) {
                sidebar.classList.remove('open');
                overlay.classList.remove('active');
            } else {
                sidebar.classList.add('open');
                overlay.classList.add('active');
            }
        }
        
        document.getElementById('menuBtn').addEventListener('click', toggleSidebar);
        document.getElementById('overlay').addEventListener('click', toggleSidebar);
        
        console.log('📚 API Info page loaded!');
    </script>
</body>
</html>
    """
    
    return html_content

@app.get("/api/teams")
async def get_teams_api():
    """API endpoint for teams data"""
    teams_data = {
        "teams": [
            {"name": "Kansas City Chiefs", "record": "14-3", "ppg": "29.2", "pa": "17.3", "division": "AFC West"},
            {"name": "Buffalo Bills", "record": "13-4", "ppg": "28.8", "pa": "18.5", "division": "AFC East"},
            {"name": "Baltimore Ravens", "record": "13-4", "ppg": "28.4", "pa": "16.5", "division": "AFC North"},
            {"name": "Detroit Lions", "record": "12-5", "ppg": "27.1", "pa": "20.8", "division": "NFC North"},
            {"name": "Dallas Cowboys", "record": "12-5", "ppg": "26.1", "pa": "20.1", "division": "NFC East"},
        ],
        "last_updated": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
        "total_teams": 32
    }
    return JSONResponse(content=teams_data)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(content={
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "H.C. Lombardo NFL Dashboard",
        "version": "3.0.0",
        "educational_use": True,
        "developer": "April V. Sykes",
        "technical_implementation": "GitHub Copilot"
    })

if __name__ == "__main__":
    print("🚀 Starting H.C. Lombardo NFL Dashboard (Educational Use - Official Logos)...")
    print("🏈 Dashboard: http://localhost:8004")
    print("📚 API Docs: http://localhost:8004/docs")
    print("👨‍💻 Built by April V. Sykes | Technical Implementation by GitHub Copilot")
    
    uvicorn.run(app, host="127.0.0.1", port=8004)