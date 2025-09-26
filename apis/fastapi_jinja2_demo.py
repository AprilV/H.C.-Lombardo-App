#!/usr/bin/env python3
"""
FastAPI with Jinja2 Templates
Professional implementation using template engine
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

# Initialize FastAPI app
app = FastAPI(
    title="NFL Betting API",
    description="REST API for NFL betting predictions using Jinja2 templates",
    version="2.0.0"
)

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    """
    Homepage using Jinja2 template with dynamic content
    """
    
    # NFL API specific data
    context = {
        "request": request,
        "title": "NFL Betting Line API",
        "icon": "🏈",
        "description": "Professional REST API for NFL betting predictions and database operations",
        "status": "API Active",
        "gradient_start": "#667eea",
        "gradient_end": "#764ba2",
        "navigation_links": [
            {
                "url": "/docs",
                "icon": "📚",
                "title": "Swagger UI",
                "description": "Interactive API documentation with request/response examples and testing interface"
            },
            {
                "url": "/redoc", 
                "icon": "📖",
                "title": "ReDoc UI",
                "description": "Beautiful API documentation with detailed schemas and comprehensive descriptions"
            },
            {
                "url": "/teams",
                "icon": "🏟️", 
                "title": "Teams API",
                "description": "Access all 32 NFL teams with conference, division, and performance statistics"
            },
            {
                "url": "/games",
                "icon": "⚡",
                "title": "Games API", 
                "description": "Retrieve game schedules, scores, and matchup data for current and past seasons"
            },
            {
                "url": "/predict",
                "icon": "🎯",
                "title": "Predictions API",
                "description": "Generate betting line predictions using advanced algorithms and team analytics"
            },
            {
                "url": "/health",
                "icon": "💚",
                "title": "Health Check",
                "description": "API status and system health monitoring endpoint"
            }
        ],
        "footer_main": "🚀 Built with FastAPI & Jinja2 • Powered by NFL Database • Version 2.0.0",
        "footer_sub": "📡 Real-time NFL data integration with betting line predictions",
        "features": [
            "Jinja2 Templates",
            "Dynamic Rendering", 
            "Template Inheritance",
            "Professional Architecture",
            "Maintainable Code"
        ]
    }
    
    return templates.TemplateResponse("index.html", context)

@app.get("/text", response_class=HTMLResponse)
async def text_homepage(request: Request):
    """
    Alternative homepage for text classification theme
    """
    
    context = {
        "request": request,
        "title": "Text Classification API",
        "icon": "🤖",
        "description": "Advanced NLP API powered by HuggingFace Transformers for sentiment analysis",
        "status": "ML Models Ready",
        "gradient_start": "#74b9ff",
        "gradient_end": "#0984e3",
        "navigation_links": [
            {
                "url": "/docs",
                "icon": "📚",
                "title": "Swagger UI",
                "description": "Interactive API documentation with ML model testing interface"
            },
            {
                "url": "/redoc",
                "icon": "📖", 
                "title": "ReDoc UI",
                "description": "Comprehensive API documentation with model schemas and examples"
            },
            {
                "url": "/classify",
                "icon": "🎯",
                "title": "Text Classification",
                "description": "Classify individual text for sentiment analysis with confidence scores"
            },
            {
                "url": "/batch-classify",
                "icon": "📝",
                "title": "Batch Processing",
                "description": "Process multiple texts simultaneously for efficient bulk analysis"
            },
            {
                "url": "/models",
                "icon": "🧠",
                "title": "Available Models", 
                "description": "View supported HuggingFace transformer models and capabilities"
            },
            {
                "url": "/health",
                "icon": "💚",
                "title": "Health Check",
                "description": "API status and ML model health monitoring"
            }
        ],
        "footer_main": "🚀 Built with FastAPI & Jinja2 • Powered by HuggingFace • Version 2.0.0",
        "footer_sub": "🧠 Advanced NLP sentiment analysis and text classification",
        "features": [
            "Jinja2 Templates",
            "HuggingFace Models",
            "Batch Processing", 
            "Sentiment Analysis",
            "Professional UI"
        ]
    }
    
    return templates.TemplateResponse("index.html", context)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "message": "FastAPI with Jinja2 templates is running",
        "template_engine": "Jinja2",
        "version": "2.0.0"
    }

@app.get("/teams")
async def get_teams():
    """Demo teams endpoint"""
    return {
        "message": "Teams API endpoint",
        "note": "This would return NFL teams data from database",
        "template_powered": True
    }

@app.get("/games") 
async def get_games():
    """Demo games endpoint"""
    return {
        "message": "Games API endpoint", 
        "note": "This would return NFL games and schedules",
        "template_powered": True
    }

@app.get("/predict")
async def predict():
    """Demo predictions endpoint"""
    return {
        "message": "Predictions API endpoint",
        "note": "This would return ML betting predictions", 
        "template_powered": True
    }

@app.get("/classify")
async def classify():
    """Demo classification endpoint"""
    return {
        "message": "Text Classification endpoint",
        "note": "This would classify text using HuggingFace models",
        "template_powered": True
    }

@app.get("/models")
async def models():
    """Demo models endpoint"""
    return {
        "message": "Available Models endpoint",
        "models": ["distilbert", "bert", "roberta"],
        "template_powered": True
    }

if __name__ == "__main__":
    print("🚀 Starting FastAPI with Jinja2 Templates...")
    print("📍 NFL Homepage: http://localhost:8002/")
    print("📍 Text Homepage: http://localhost:8002/text")
    print("📚 Documentation: http://localhost:8002/docs")
    print("📖 ReDoc: http://localhost:8002/redoc")
    print("🛑 Press Ctrl+C to stop")
    
    uvicorn.run(app, host="127.0.0.1", port=8002)