#!/usr/bin/env python3
"""
NFL Betting API - Simplified Homepage Demo
FastAPI with HTML homepage (no database dependencies)
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="NFL Betting API",
    description="REST API for NFL betting predictions and database operations",
    version="1.0.0"
)

# Homepage route
@app.get("/", response_class=HTMLResponse)
async def homepage():
    """
    HTML homepage with navigation menu to all API endpoints
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NFL Betting Line API</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                line-height: 1.6;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            h1 {
                text-align: center;
                font-size: 3rem;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
                background: linear-gradient(45deg, #FFD700, #FFA500);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            .subtitle {
                text-align: center;
                font-size: 1.2rem;
                margin-bottom: 40px;
                opacity: 0.9;
            }
            .nav-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }
            .nav-card {
                background: rgba(255, 255, 255, 0.15);
                border-radius: 15px;
                padding: 25px;
                text-decoration: none;
                color: white;
                transition: all 0.3s ease;
                border: 1px solid rgba(255, 255, 255, 0.2);
                backdrop-filter: blur(5px);
            }
            .nav-card:hover {
                transform: translateY(-5px);
                background: rgba(255, 255, 255, 0.25);
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
                color: #FFD700;
            }
            .nav-card h3 {
                margin-top: 0;
                font-size: 1.3rem;
                color: #FFD700;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .nav-card p {
                margin-bottom: 0;
                opacity: 0.9;
                font-size: 0.95rem;
            }
            .icon {
                font-size: 1.5rem;
            }
            .footer {
                text-align: center;
                margin-top: 40px;
                opacity: 0.7;
                font-size: 0.9rem;
            }
            .api-status {
                display: inline-block;
                background: #28a745;
                color: white;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: bold;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="api-status">🟢 API Active</div>
            <h1>🏈 NFL Betting Line API</h1>
            <p class="subtitle">Professional REST API for NFL betting predictions and database operations</p>
            
            <div class="nav-grid">
                <a href="/docs" class="nav-card">
                    <h3><span class="icon">📚</span> Swagger UI</h3>
                    <p>Interactive API documentation with request/response examples and testing interface</p>
                </a>
                
                <a href="/redoc" class="nav-card">
                    <h3><span class="icon">📖</span> ReDoc UI</h3>
                    <p>Beautiful API documentation with detailed schemas and comprehensive endpoint descriptions</p>
                </a>
                
                <a href="/teams" class="nav-card">
                    <h3><span class="icon">🏟️</span> Teams API</h3>
                    <p>Access all 32 NFL teams with conference, division, and performance statistics</p>
                </a>
                
                <a href="/games" class="nav-card">
                    <h3><span class="icon">⚡</span> Games API</h3>
                    <p>Retrieve game schedules, scores, and matchup data for current and past seasons</p>
                </a>
                
                <a href="/predict" class="nav-card">
                    <h3><span class="icon">🎯</span> Predictions API</h3>
                    <p>Generate betting line predictions using advanced algorithms and team analytics</p>
                </a>
                
                <a href="/health" class="nav-card">
                    <h3><span class="icon">💚</span> Health Check</h3>
                    <p>API status and system health monitoring endpoint</p>
                </a>
            </div>
            
            <div class="footer">
                <p>🚀 Built with FastAPI • Powered by NFL Database • Version 1.0.0</p>
                <p>📡 Real-time NFL data integration with betting line predictions</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "NFL Betting API is running"}

@app.get("/teams")
async def get_teams():
    """Demo teams endpoint"""
    return {"message": "Teams endpoint - database integration needed"}

@app.get("/games")
async def get_games():
    """Demo games endpoint"""
    return {"message": "Games endpoint - database integration needed"}

@app.get("/predict")
async def predict():
    """Demo predictions endpoint"""
    return {"message": "Predictions endpoint - ML model integration needed"}

if __name__ == "__main__":
    print("🏈 Starting NFL Betting API with HTML Homepage...")
    print("📍 Homepage: http://localhost:8001/")
    print("📚 Docs: http://localhost:8001/docs")
    print("📖 ReDoc: http://localhost:8001/redoc")
    print("🛑 Press Ctrl+C to stop")
    
    uvicorn.run(app, host="127.0.0.1", port=8001)