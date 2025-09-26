#!/usr/bin/env python3
"""
H.C. Lombardo App - Project Launcher
Simple menu system to run different projects
"""

import os
import subprocess
import sys

def get_python_path():
    """Get the correct Python executable path"""
    return "C:/Users/april/AppData/Local/Microsoft/WindowsApps/python3.11.exe"

def run_script(folder, script_name):
    """Run a Python script in a specific folder"""
    current_dir = os.getcwd()
    try:
        os.chdir(folder)
        result = subprocess.run([get_python_path(), script_name], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"Error: {result.stderr}")
    finally:
        os.chdir(current_dir)

def show_menu():
    """Display the main menu"""
    print("=" * 60)
    print("H.C. LOMBARDO APP - PROJECT LAUNCHER")
    print("=" * 60)
    print()
    print("TEXT CLASSIFICATION PROJECTS:")
    print("1. Minimal Example (Quick Start)")
    print("2. Step-by-Step Tutorial (Learning)")
    print("3. BERT Example (Advanced)")
    print("4. Ultra Simple (Pipeline)")
    print()
    print("NFL BETTING DATABASE PROJECTS:")
    print("5. Setup Database (First Time)")
    print("6. Run Betting Predictor")
    print("7. Database Utilities Test")
    print()
    print("🆕 REST APIs:")
    print("8. Start Text Classification API")
    print("9. Start NFL Betting API")
    print("10. Start Both APIs")
    print("11. Test APIs with Client Examples")
    print()
    print("🌐 EXTERNAL API INTEGRATION:")
    print("12. Test NFL External API (API-SPORTS)")
    print("13. Configure API Keys")
    print()
    print("🗄️ DATABASE SCHEMA PROJECTS:")
    print("14. Create User Schema Database")
    print("15. Run NFL Database Analysis")
    print("16. Test All APIs")
    print()
    print("UTILITIES:")
    print("17. Show Project Structure")
    print("18. Exit")
    print()

def show_project_structure():
    """Display the project structure"""
    print("\nPROJECT STRUCTURE:")
    print("=" * 40)
    
    structure = """
H.C. Lombardo App/
├── text_classification/          # 🤖 HuggingFace ML Projects
│   ├── minimal_example.py        #   Quick start (25 lines)
│   ├── step_by_step_classification.py #   Detailed tutorial
│   ├── bert_step_by_step.py      #   BERT implementation  
│   ├── text_classification.py    #   RoBERTa sentiment
│   └── [8 more examples]         #   Various implementations
│
├── nfl_betting_database/         # 🏈 NFL Database System
│   ├── nfl_database_setup.py     #   Create database
│   ├── betting_predictor_example.py # Prediction demo
│   ├── nfl_database_utils.py     #   Database utilities
│   └── sports_betting.db         #   SQLite database
│
├── docs/                         # 📚 Documentation
│   ├── README.md                 #   Text classification docs
│   └── DATABASE_README.md        #   Database documentation
│
├── requirements.txt              # 📦 Dependencies
└── README.md                     # 📖 Main project info
    """
    print(structure)

def main():
    """Main launcher function"""
    while True:
        show_menu()
        try:
            choice = input("Enter your choice (1-15): ").strip()
            print()
            
            if choice == "1":
                print("🚀 Running Minimal Text Classification Example...")
                run_script("text_classification", "minimal_example.py")
                
            elif choice == "2":
                print("📚 Running Step-by-Step Tutorial...")
                run_script("text_classification", "step_by_step_classification.py")
                
            elif choice == "3":
                print("🧠 Running BERT Example...")
                run_script("text_classification", "bert_step_by_step.py")
                
            elif choice == "4":
                print("⚡ Running Ultra Simple Example...")
                run_script("text_classification", "ultra_simple.py")
                
            elif choice == "5":
                print("🏗️ Setting up NFL Database...")
                run_script("nfl_betting_database", "nfl_database_setup.py")
                
            elif choice == "6":
                print("🏈 Running NFL Betting Predictor...")
                run_script("nfl_betting_database", "betting_predictor_example.py")
                
            elif choice == "8":
                print("🌐 Starting Text Classification API...")
                run_script("apis", "text_classification_api.py")
                
            elif choice == "9":
                print("🏈 Starting NFL Betting API...")
                run_script("apis", "nfl_betting_api.py")
                
            elif choice == "10":
                print("🚀 Starting Both APIs...")
                run_script("apis", "start_apis.py")
                
            elif choice == "11":
                print("🧪 Testing APIs with Client Examples...")
                run_script("apis", "api_client_examples.py")
                
            elif choice == "12":
                print("🌐 Testing NFL External API Integration...")
                run_script("external_apis", "nfl_data_integration.py")
                
            elif choice == "13":
                print("🔧 Configuring API Keys...")
                run_script("external_apis", "api_config.py")
                
            elif choice == "14":
                print("🏗️ Creating User Schema Database...")
                run_script("nfl_betting_database", "user_schema_demo.py")
                
            elif choice == "15":
                print("📊 Running NFL Database Analysis...")
                run_script("nfl_betting_database", "nfl_analysis_tool.py")
                
            elif choice == "16":
                print("🧪 Testing All APIs...")
                run_script(".", "test_all_apis.py")
                
            elif choice == "17":
                show_project_structure()
                
            elif choice == "18":
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter a number from 1-18.")
            
            input("\nPress Enter to continue...")
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()