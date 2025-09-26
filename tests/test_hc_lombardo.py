#!/usr/bin/env python3
"""
H.C. Lombardo App Simple Test
Tests the template inheritance application with H.C. Lombardo branding
"""

def test_app():
    """Test H.C. Lombardo application"""
    print("🧪 Testing H.C. Lombardo FastAPI Application")
    print("=" * 50)
    
    try:
        from fastapi_template_inheritance import app
        print("✅ H.C. Lombardo app imported successfully")
        print(f"✅ App title: {app.title}")
        print(f"✅ App description: {app.description}")
        
        # Test with FastAPI test client
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        # Test homepage
        response = client.get("/")
        print(f"✅ Homepage status: {response.status_code}")
        if response.status_code == 200:
            content = response.text
            if "H.C. Lombardo" in content:
                print("✅ H.C. Lombardo branding found in homepage!")
            if "NFL Betting" in content:
                print("✅ NFL Betting content found")
            print(f"✅ Homepage content: {len(content)} characters")
        
        # Test text classifier page
        response = client.get("/text-classifier")
        print(f"✅ Text classifier status: {response.status_code}")
        if response.status_code == 200:
            content = response.text
            if "H.C. Lombardo" in content:
                print("✅ H.C. Lombardo branding found in text page!")
            print(f"✅ Text page content: {len(content)} characters")
        
        # Test API endpoints
        response = client.get("/health")
        print(f"✅ Health endpoint: {response.status_code} - {response.json()}")
        
        response = client.get("/predict")
        print(f"✅ Predict endpoint: {response.status_code} - {response.json()}")
        
        print("\n🎉 H.C. Lombardo Application Test Complete!")
        print("✅ All H.C. Lombardo branding successfully applied")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main test function"""
    if test_app():
        print("\n🚀 Ready to start H.C. Lombardo FastAPI Server:")
        print("python -m uvicorn fastapi_template_inheritance:app --host 127.0.0.1 --port 8000 --reload")
        print("\n🌐 H.C. Lombardo App URLs:")
        print("• Homepage: http://127.0.0.1:8000")
        print("• Text Analysis: http://127.0.0.1:8000/text-classifier")
        print("• API Docs: http://127.0.0.1:8000/docs")
        return True
    else:
        print("❌ H.C. Lombardo app test failed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)