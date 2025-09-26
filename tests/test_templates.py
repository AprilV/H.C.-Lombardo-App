#!/usr/bin/env python3
"""
Quick Template Testing Script
Tests Jinja2 template functionality without running the full server
"""

from jinja2 import Environment, FileSystemLoader
from pathlib import Path

def test_templates():
    """Test template rendering functionality"""
    
    # Setup Jinja2 environment
    template_dir = Path(__file__).parent / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    
    print(f"🔍 Template directory: {template_dir}")
    print(f"📁 Template files found: {list(template_dir.glob('*.html'))}")
    
    # Test base template
    try:
        base_template = env.get_template('base.html')
        print("✅ base.html loaded successfully")
    except Exception as e:
        print(f"❌ Error loading base.html: {e}")
        return
    
    # Test extended template
    try:
        extended_template = env.get_template('index_extended.html')
        print("✅ index_extended.html loaded successfully")
    except Exception as e:
        print(f"❌ Error loading index_extended.html: {e}")
        return
    
    # Test rendering with context data
    context = {
        "title": "Template Test",
        "icon": "🧪", 
        "description": "Testing Jinja2 template inheritance",
        "gradient_from": "#ff7e5f",
        "gradient_to": "#feb47b",
        "navigation_links": [
            {
                "url": "/test",
                "icon": "🧪",
                "name": "Test Link",
                "description": "This is a test navigation link"
            }
        ],
        "features": ["Template inheritance", "Dynamic content", "CSS styling"],
        "footer_text": "Template Test Complete"
    }
    
    try:
        rendered = extended_template.render(**context)
        print("✅ Template rendered successfully")
        print(f"📄 Rendered HTML length: {len(rendered)} characters")
        
        # Save rendered output for inspection
        output_file = Path(__file__).parent / "template_test_output.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(rendered)
        print(f"💾 Rendered HTML saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Template rendering error: {e}")
        return False

def main():
    print("🧪 Testing Jinja2 Template System")
    print("=" * 40)
    
    if test_templates():
        print("\n✅ All template tests passed!")
        print("🚀 Ready to run FastAPI with template inheritance")
        print("\nNext steps:")
        print("1. Run: python fastapi_template_inheritance.py")
        print("2. Open: http://localhost:8000")
    else:
        print("\n❌ Template tests failed")
        print("🔧 Check template files and fix any issues")

if __name__ == "__main__":
    main()