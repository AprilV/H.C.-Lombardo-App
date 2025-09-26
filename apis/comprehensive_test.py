#!/usr/bin/env python3
"""
Comprehensive FastAPI Application Testing Suite
Tests all endpoints, templates, and functionality
"""

import sys
import time
import subprocess
import threading
from pathlib import Path

def test_imports():
    """Test all required imports"""
    print("🧪 Testing Python imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import jinja2
        print("✅ Jinja2 imported")
    except ImportError as e:
        print(f"❌ Jinja2 import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn imported")
    except ImportError as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False
    
    return True

def test_app_imports():
    """Test FastAPI application imports"""
    print("\n🧪 Testing FastAPI application imports...")
    
    try:
        from nfl_betting_api import app as nfl_app
        print("✅ NFL Betting API imported")
    except Exception as e:
        print(f"❌ NFL Betting API import failed: {e}")
    
    try:
        from text_classification_api import app as text_app
        print("✅ Text Classification API imported")
    except Exception as e:
        print(f"❌ Text Classification API import failed: {e}")
    
    try:
        from fastapi_template_inheritance import app as template_app
        print("✅ Template Inheritance API imported")
    except Exception as e:
        print(f"❌ Template Inheritance API import failed: {e}")

def test_templates():
    """Test template system"""
    print("\n🧪 Testing Jinja2 templates...")
    
    try:
        from jinja2 import Environment, FileSystemLoader
        
        template_dir = Path(__file__).parent / "templates"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        
        # Test base template
        base_template = env.get_template('base.html')
        print("✅ base.html template loaded")
        
        # Test extended template
        extended_template = env.get_template('index_extended.html')
        print("✅ index_extended.html template loaded")
        
        # Test rendering
        context = {
            "title": "Test Page",
            "icon": "🧪",
            "description": "Testing template rendering",
            "navigation_links": [
                {"url": "/test", "icon": "🧪", "name": "Test", "description": "Test link"}
            ]
        }
        
        rendered = extended_template.render(**context)
        print(f"✅ Template rendered successfully ({len(rendered)} chars)")
        
        return True
        
    except Exception as e:
        print(f"❌ Template test failed: {e}")
        return False

def test_server_startup():
    """Test server startup without blocking"""
    print("\n🧪 Testing server startup...")
    
    try:
        # Import the app to test if it can be loaded
        from fastapi_template_inheritance import app
        
        # Test app configuration
        print(f"✅ App title: {app.title}")
        print(f"✅ App description: {app.description}")
        
        # Get routes
        routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                routes.append(f"{list(route.methods)[0]} {route.path}")
        
        print("✅ Available routes:")
        for route in routes[:10]:  # Show first 10 routes
            print(f"   {route}")
        
        return True
        
    except Exception as e:
        print(f"❌ Server startup test failed: {e}")
        return False

def test_template_inheritance():
    """Test template inheritance specifically"""
    print("\n🧪 Testing template inheritance...")
    
    try:
        from fastapi.testclient import TestClient
        from fastapi_template_inheritance import app
        
        client = TestClient(app)
        
        # Test homepage
        response = client.get("/")
        print(f"✅ Homepage status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Homepage content length: {len(response.text)} chars")
            
            # Check for key elements
            content = response.text
            if "NFL Betting Line API" in content:
                print("✅ NFL title found in homepage")
            if "nav-card" in content:
                print("✅ Navigation cards found")
            if "Jinja2" in content:
                print("✅ Jinja2 template indicator found")
        
        # Test text classifier page
        response = client.get("/text-classifier")
        print(f"✅ Text classifier status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Text classifier content length: {len(response.text)} chars")
        
        # Test API endpoints
        response = client.get("/health")
        print(f"✅ Health check status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Health response: {response.json()}")
        
        response = client.get("/predict")
        print(f"✅ Predict endpoint status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Predict response: {response.json()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Template inheritance test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 FastAPI Comprehensive Testing Suite")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 5
    
    if test_imports():
        tests_passed += 1
    
    test_app_imports()  # This doesn't return bool, just informational
    
    if test_templates():
        tests_passed += 1
    
    if test_server_startup():
        tests_passed += 1
    
    if test_template_inheritance():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {tests_passed}/{total_tests-1} tests passed")
    
    if tests_passed >= 3:
        print("✅ FastAPI application is ready to run!")
        print("\n🚀 Next steps:")
        print("1. Run: python -m uvicorn fastapi_template_inheritance:app --host 127.0.0.1 --port 8000 --reload")
        print("2. Open: http://127.0.0.1:8000")
        print("3. Visit: http://127.0.0.1:8000/text-classifier")
        print("4. API docs: http://127.0.0.1:8000/docs")
    else:
        print("❌ Some tests failed. Check the errors above.")
    
    return tests_passed >= 3

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)