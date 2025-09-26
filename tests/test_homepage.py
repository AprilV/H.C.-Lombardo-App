#!/usr/bin/env python3
"""
Test FastAPI Homepage
Quick test to verify the HTML homepage routes work
"""

def test_nfl_api_homepage():
    """Test the NFL Betting API homepage"""
    print("🏈 Testing NFL Betting API Homepage")
    print("=" * 45)
    
    try:
        # Import the app
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__)))
        
        from nfl_betting_api import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/")
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Content Type: {response.headers.get('content-type')}")
        
        # Check if HTML content is returned
        if response.status_code == 200 and "text/html" in response.headers.get('content-type', ''):
            content = response.text
            
            # Check for key elements
            checks = [
                ("Title", "NFL Betting Line API" in content),
                ("Swagger Link", '"/docs"' in content),
                ("ReDoc Link", '"/redoc"' in content),
                ("Teams API", '"/teams"' in content),
                ("Games API", '"/games"' in content),
                ("CSS Styling", "<style>" in content and "background:" in content),
                ("Navigation Grid", "nav-grid" in content),
                ("Interactive Cards", "nav-card" in content)
            ]
            
            print("\n📋 Content Validation:")
            for check_name, passed in checks:
                status = "✅" if passed else "❌"
                print(f"   {status} {check_name}")
            
            all_passed = all(passed for _, passed in checks)
            
            if all_passed:
                print("\n🎉 NFL API Homepage Test: PASSED")
                print("   • HTML homepage working correctly")
                print("   • All required links present")
                print("   • CSS styling applied")
                return True
            else:
                print("\n⚠️ NFL API Homepage Test: PARTIAL")
                return False
                
        else:
            print(f"❌ HTTP {response.status_code}: {response.text[:100]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error testing NFL API: {e}")
        return False

def test_text_api_homepage():
    """Test the Text Classification API homepage"""
    print("\n🤖 Testing Text Classification API Homepage")
    print("=" * 50)
    
    try:
        from text_classification_api import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/")
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Content Type: {response.headers.get('content-type')}")
        
        if response.status_code == 200 and "text/html" in response.headers.get('content-type', ''):
            content = response.text
            
            checks = [
                ("Title", "Text Classification API" in content),
                ("Swagger Link", '"/docs"' in content),
                ("ReDoc Link", '"/redoc"' in content),
                ("Models API", '"/models"' in content),
                ("Health Check", '"/health"' in content),
                ("CSS Styling", "<style>" in content and "background:" in content),
                ("HuggingFace Reference", "HuggingFace" in content)
            ]
            
            print("\n📋 Content Validation:")
            for check_name, passed in checks:
                status = "✅" if passed else "❌"
                print(f"   {status} {check_name}")
            
            all_passed = all(passed for _, passed in checks)
            
            if all_passed:
                print("\n🎉 Text API Homepage Test: PASSED")
                return True
            else:
                print("\n⚠️ Text API Homepage Test: PARTIAL")
                return False
                
        else:
            print(f"❌ HTTP {response.status_code}: {response.text[:100]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Text API: {e}")
        return False

def main():
    """Test both API homepages"""
    print("🚀 FastAPI Homepage Testing")
    print("Testing HTML homepage routes with navigation")
    print("=" * 55)
    
    results = []
    
    # Test NFL API
    results.append(test_nfl_api_homepage())
    
    # Test Text API  
    results.append(test_text_api_homepage())
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 20)
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total} API homepages")
    
    if passed == total:
        print("🎉 All FastAPI homepages working perfectly!")
        print("\n🎯 Ready to serve:")
        print("   • NFL Betting API: http://localhost:8001/")
        print("   • Text Classification API: http://localhost:8000/")
    else:
        print(f"⚠️ {total - passed} API homepage(s) need attention")

if __name__ == "__main__":
    main()