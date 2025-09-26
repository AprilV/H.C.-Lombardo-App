"""
FastAPI with Jinja2 Template Inheritance Demo
Advanced template architecture with base template and inheritance
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path
import os

app = FastAPI(title="H.C. Lombardo App", description="Professional H.C. Lombardo Application with FastAPI and Jinja2")

# Get the directory where this script is located
BASE_DIR = Path(__file__).parent.parent  # Go up one level to the main project directory
TEMPLATES_DIR = BASE_DIR / "templates"

print(f"🔍 BASE_DIR: {BASE_DIR}")
print(f"🔍 TEMPLATES_DIR: {TEMPLATES_DIR}")
print(f"🔍 Templates directory exists: {TEMPLATES_DIR.exists()}")
if TEMPLATES_DIR.exists():
    print(f"🔍 Files in templates: {list(TEMPLATES_DIR.glob('*.html'))}")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@app.get("/")
async def root():
    """Root route that just returns a simple message"""
    return {"message": "H.C. Lombardo API is running", "available_routes": ["/simple-test", "/working-sidebar", "/home", "/docs"]}

@app.get("/sidebar", response_class=HTMLResponse)
async def sidebar_demo():
    """Self-contained sidebar demo with inline HTML"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>H.C. Lombardo - Sidebar Navigation</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            position: relative;
        }
        
        /* Hamburger Menu - VERY VISIBLE */
        .menu-btn {
            position: fixed;
            top: 20px;
            left: 20px;
            z-index: 2000;
            background: #FFD700;
            color: #000;
            font-size: 2.5rem;
            font-weight: 900;
            padding: 20px;
            border: 4px solid #FFA500;
            border-radius: 15px;
            cursor: pointer;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
            transition: all 0.3s ease;
            width: 70px;
            height: 70px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .menu-btn:hover {
            background: #FFA500;
            transform: scale(1.2) rotate(90deg);
            box-shadow: 0 12px 35px rgba(0, 0, 0, 0.6);
        }
        
        /* Sidebar */
        .sidebar {
            position: fixed;
            left: -350px;
            top: 0;
            width: 350px;
            height: 100vh;
            background: linear-gradient(180deg, #000000 0%, #1a1a1a 100%);
            border-right: 3px solid #FFD700;
            transition: left 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            z-index: 1500;
            box-shadow: 5px 0 25px rgba(0, 0, 0, 0.5);
        }
        
        .sidebar.open { left: 0; }
        
        .sidebar-header {
            padding: 40px 30px 30px 30px;
            border-bottom: 2px solid #FFD700;
            background: linear-gradient(45deg, #FFD700, #FFA500);
            color: #000;
        }
        
        .sidebar-header h1 {
            font-size: 1.8rem;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .sidebar-header p {
            font-size: 1rem;
            opacity: 0.8;
        }
        
        .sidebar-nav {
            padding: 30px 0;
        }
        
        .nav-item {
            display: block;
            color: #fff;
            text-decoration: none;
            padding: 20px 30px;
            margin: 5px 20px;
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.05);
            border-left: 4px solid transparent;
            transition: all 0.3s ease;
            font-size: 1.1rem;
            font-weight: 500;
        }
        
        .nav-item:hover {
            background: rgba(255, 215, 0, 0.15);
            border-left-color: #FFD700;
            transform: translateX(10px);
            color: #FFD700;
        }
        
        .nav-item span {
            margin-right: 15px;
            font-size: 1.3rem;
        }
        
        /* Overlay */
        .overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.7);
            z-index: 1000;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
        }
        
        .overlay.active {
            opacity: 1;
            visibility: visible;
        }
        
        /* Main Content */
        .main-content {
            padding: 120px 40px 40px 40px;
            text-align: center;
        }
        
        .hero-card {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(20px);
            border-radius: 25px;
            padding: 60px 40px;
            max-width: 800px;
            margin: 0 auto;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }
        
        .hero-card h1 {
            font-size: 3rem;
            margin-bottom: 20px;
            background: linear-gradient(45deg, #FFD700, #FFA500);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .hero-card p {
            font-size: 1.3rem;
            margin-bottom: 30px;
            opacity: 0.9;
        }
        
        .status-badge {
            background: linear-gradient(45deg, #28a745, #20c997);
            color: white;
            padding: 15px 30px;
            border-radius: 30px;
            font-size: 1.1rem;
            font-weight: bold;
            display: inline-block;
            margin-bottom: 30px;
            box-shadow: 0 5px 15px rgba(40, 167, 69, 0.4);
        }
        
        .instruction {
            background: rgba(255, 215, 0, 0.1);
            border: 2px solid #FFD700;
            border-radius: 15px;
            padding: 25px;
            margin-top: 30px;
        }
        
        .instruction h3 {
            color: #FFD700;
            margin-bottom: 15px;
            font-size: 1.4rem;
        }
    </style>
</head>
<body>
    <!-- HAMBURGER MENU BUTTON -->
    <button class="menu-btn" onclick="toggleSidebar()">☰</button>
    
    <!-- OVERLAY -->
    <div class="overlay" id="overlay" onclick="closeSidebar()"></div>
    
    <!-- SIDEBAR -->
    <nav class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <h1>H.C. Lombardo</h1>
            <p>Professional Applications</p>
        </div>
        
        <div class="sidebar-nav">
            <a href="/" class="nav-item">
                <span>🏠</span>Home
            </a>
            <a href="/simple-test" class="nav-item">
                <span>🔧</span>Simple Test
            </a>
            <a href="/sidebar" class="nav-item">
                <span>📱</span>Sidebar Demo
            </a>
            <a href="/docs" class="nav-item">
                <span>📚</span>API Documentation
            </a>
            <a href="/redoc" class="nav-item">
                <span>📖</span>ReDoc
            </a>
        </div>
    </nav>
    
    <!-- MAIN CONTENT -->
    <div class="main-content">
        <div class="hero-card">
            <div class="status-badge">✅ SIDEBAR WORKING!</div>
            <h1>🚀 H.C. Lombardo</h1>
            <p>Professional Navigation System</p>
            
            <div class="instruction">
                <h3>🎯 How to Use the Sidebar:</h3>
                <p><strong>1.</strong> Click the bright GOLD hamburger button (☰) in the top-left corner</p>
                <p><strong>2.</strong> Watch the sidebar slide in from the left</p>
                <p><strong>3.</strong> Click any menu item to navigate</p>
                <p><strong>4.</strong> Click outside the sidebar to close it</p>
            </div>
        </div>
    </div>
    
    <script>
        console.log('🔥 H.C. Lombardo Sidebar Script Loaded!');
        
        function toggleSidebar() {
            console.log('🍔 Hamburger clicked!');
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('overlay');
            
            if (sidebar.classList.contains('open')) {
                closeSidebar();
            } else {
                openSidebar();
            }
        }
        
        function openSidebar() {
            console.log('📱 Opening sidebar...');
            document.getElementById('sidebar').classList.add('open');
            document.getElementById('overlay').classList.add('active');
        }
        
        function closeSidebar() {
            console.log('❌ Closing sidebar...');
            document.getElementById('sidebar').classList.remove('open');
            document.getElementById('overlay').classList.remove('active');
        }
        
        // Test that everything loaded properly
        document.addEventListener('DOMContentLoaded', function() {
            console.log('✅ DOM loaded, sidebar ready!');
            console.log('🍔 Menu button:', document.querySelector('.menu-btn'));
            console.log('📱 Sidebar:', document.getElementById('sidebar'));
        });
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

@app.get("/test")
async def test_route():
    """Simple test route"""
    return {"status": "working", "message": "Test route is functional"}

@app.get("/working-sidebar", response_class=HTMLResponse)
async def working_sidebar(request: Request):
    """Guaranteed working sidebar test"""
    try:
        context = {
            "request": request,
            "title": "H.C. Lombardo - WORKING Sidebar",
            "description": "This sidebar is guaranteed to work! Click the gold ☰ button."
        }
        return templates.TemplateResponse("working-sidebar.html", context)
    except Exception as e:
        print(f"❌ Error: {e}")
        return HTMLResponse(f"<h1>Error</h1><p>{str(e)}</p>")

@app.get("/simple-test", response_class=HTMLResponse)
async def simple_test():
    """Simple HTML test without templates"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Simple Test</title>
        <style>
            body { 
                font-family: Arial; 
                padding: 20px; 
                background: #333; 
                color: white; 
                text-align: center;
            }
            .big-button {
                background: #FFD700;
                color: black;
                font-size: 2rem;
                padding: 20px 40px;
                border: none;
                border-radius: 10px;
                cursor: pointer;
                margin: 20px;
                display: inline-block;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
        <h1>🔧 H.C. Lombardo Simple Test</h1>
        <p>If you can see this, the server and routes are working!</p>
        <a href="/sidebar" class="big-button">🎯 GUARANTEED SIDEBAR</a>
        <a href="/working-sidebar" class="big-button">✅ WORKING SIDEBAR</a>
        <a href="/home" class="big-button">Test Home Page</a>
        <a href="/sidebar-test" class="big-button">Test Sidebar</a>
        <a href="/" class="big-button">Main Homepage</a>
    </body>
    </html>
    """)

@app.get("/home", response_class=HTMLResponse)
async def homepage_with_sidebar(request: Request):
    """
    Simplified homepage that definitely shows the sidebar
    """
    try:
        context = {
            "request": request,
            "title": "H.C. Lombardo - NFL Betting (With Sidebar)",
            "icon": "🏈",
            "description": "Professional NFL betting line prediction and analysis by H.C. Lombardo",
            "current_page": "home"
        }
        print(f"🔍 Attempting to load base.html template...")
        return templates.TemplateResponse("base.html", context)
    except Exception as e:
        print(f"❌ Error loading template: {e}")
        return HTMLResponse(f"<h1>Template Error</h1><p>{str(e)}</p><p>Templates dir: {TEMPLATES_DIR}</p>")

@app.get("/sidebar-test", response_class=HTMLResponse) 
async def sidebar_test(request: Request):
    """Test route to verify sidebar visibility with dedicated template"""
    try:
        return templates.TemplateResponse("sidebar-test.html", {"request": request})
    except Exception as e:
        print(f"❌ Error loading sidebar-test.html: {e}")
        return HTMLResponse(f"<h1>Sidebar Test Error</h1><p>{str(e)}</p>")

@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    """
    NFL Betting API Homepage using template inheritance
    """
    context = {
        "request": request,
        "title": "H.C. Lombardo - NFL Betting",
        "icon": "🏈",
        "description": "Professional NFL betting line prediction and analysis by H.C. Lombardo",
        "gradient_from": "#1e3c72",
        "gradient_to": "#2a5298", 
        "features": [
            "🎯 NFL Game Predictions by H.C. Lombardo",
            "📊 Real-time Betting Lines",
            "🏆 Team Performance Analysis",
            "📈 Statistical Modeling",
            "🔄 Live Data Updates"
        ],
        "navigation_links": [
            {
                "url": "/docs",
                "icon": "📚",
                "name": "API Documentation",
                "description": "Interactive Swagger UI documentation for all endpoints"
            },
            {
                "url": "/redoc",
                "icon": "📖",
                "name": "ReDoc",
                "description": "Alternative API documentation with detailed schemas"
            },
            {
                "url": "/predict",
                "icon": "🎯",
                "name": "Betting Predictions",
                "description": "Get NFL game predictions and betting recommendations"
            },
            {
                "url": "/teams",
                "icon": "🏈",
                "name": "Team Stats",
                "description": "Comprehensive NFL team statistics and performance metrics"
            }
        ],
        "footer_text": "🏈 H.C. Lombardo NFL Betting",
        "footer_sub": "Advanced prediction system with real-time data",
        "current_page": "home"
    }
    return templates.TemplateResponse("base.html", context)

@app.get("/text-classifier", response_class=HTMLResponse)
async def text_classifier_page(request: Request):
    """
    Text Classification API page using same template inheritance
    """
    context = {
        "request": request,
        "title": "H.C. Lombardo - Text Analysis",
        "icon": "🤖",
        "description": "Advanced machine learning text analysis and classification by H.C. Lombardo",
        "gradient_from": "#667eea",
        "gradient_to": "#764ba2",
        "features": [
            "🧠 H.C. Lombardo Machine Learning Models",
            "📝 Text Sentiment Analysis", 
            "🏷️ Multi-class Classification",
            "⚡ Real-time Processing",
            "📊 Confidence Scoring"
        ],
        "navigation_links": [
            {
                "url": "/docs",
                "icon": "📚", 
                "name": "API Documentation",
                "description": "Complete API reference with examples"
            },
            {
                "url": "/classify",
                "icon": "🎯",
                "name": "Text Classification",
                "description": "Analyze and classify text content"
            },
            {
                "url": "/sentiment",
                "icon": "😊",
                "name": "Sentiment Analysis", 
                "description": "Determine emotional tone of text"
            },
            {
                "url": "/health",
                "icon": "💚",
                "name": "Health Check",
                "description": "API status and system health monitoring"
            }
        ],
        "footer_text": "🤖 H.C. Lombardo Text Analysis",
        "footer_sub": "Powered by advanced machine learning algorithms",
        "current_page": "text"
    }
    return templates.TemplateResponse("index_extended.html", context)

@app.get("/base-demo", response_class=HTMLResponse)
async def base_template_demo(request: Request):
    """
    Demo using just the base template without extension
    """
    context = {
        "request": request,
        "title": "H.C. Lombardo - Base Template Demo",
        "description": "H.C. Lombardo application using base.html template directly",
        "current_page": "base"
    }
    return templates.TemplateResponse("base.html", context)

@app.get("/debug", response_class=HTMLResponse)
async def debug_page(request: Request):
    """Debug page to check template rendering"""
    context = {
        "request": request,
        "title": "H.C. Lombardo - Debug",
        "icon": "🔧",
        "description": "Debug template rendering",
        "current_page": "debug"
    }
    return templates.TemplateResponse("base.html", context)

# Basic API endpoints for demonstration
@app.get("/predict", response_class=HTMLResponse)
async def predict_page(request: Request):
    """NFL Prediction Page"""
    context = {
        "request": request,
        "title": "H.C. Lombardo - NFL Predictions",
        "icon": "🎯",
        "description": "NFL betting predictions and analysis by H.C. Lombardo",
        "gradient_from": "#ff6b6b",
        "gradient_to": "#ee5a24",
        "current_page": "predict"
    }
    return templates.TemplateResponse("pages/predictions.html", context)

@app.get("/teams", response_class=HTMLResponse)
async def teams_page(request: Request):
    """NFL Teams Statistics Page"""
    context = {
        "request": request,
        "title": "H.C. Lombardo - NFL Team Stats",
        "icon": "🏈",
        "description": "Comprehensive NFL team statistics and analysis by H.C. Lombardo",
        "gradient_from": "#00d2d3",
        "gradient_to": "#54a0ff",
        "current_page": "teams"
    }
    return templates.TemplateResponse("pages/teams.html", context)

# JSON API endpoints
@app.get("/api/predict")
async def predict_game():
    return {"prediction": "Chiefs vs Bills - Chiefs -3.5", "confidence": 0.72}

@app.get("/api/teams")
async def get_teams():
    return {"teams": ["Chiefs", "Bills", "Cowboys", "49ers"], "total": 32}

@app.get("/classify")
async def classify_text():
    return {"classification": "positive", "confidence": 0.85}

@app.get("/sentiment")
async def analyze_sentiment():
    return {"sentiment": "positive", "score": 0.82}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-20T10:30:00Z"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting H.C. Lombardo FastAPI Application...")
    print("📁 Template directory:", BASE_DIR / "templates")
    print("🌐 H.C. Lombardo Homepage: http://localhost:8000")
    print("🏈 NFL Betting: http://localhost:8000")
    print("🤖 Text Analysis: http://localhost:8000/text-classifier")  
    print("📚 API Docs: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)