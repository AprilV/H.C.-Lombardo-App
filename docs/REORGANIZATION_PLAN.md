# PROJECT REORGANIZATION PLAN
**Date:** October 9, 2025  
**Author:** April V  
**Goal:** Make dr.foster.md and key files easy to find

## Problems:
1. ❌ dr.foster.md buried in 20+ files
2. ❌ No clear backend/ folder (but frontend/ exists)
3. ❌ Test files mixed with production files
4. ❌ Documentation files scattered
5. ❌ Hard to navigate in VS Code explorer

## Proposed New Structure:

```
H.C Lombardo App/
├── 📄 dr.foster.md                    ← TOP LEVEL (Easy to find!)
├── 📄 README.md                       ← Project overview
├── 📄 BEST_PRACTICES.md               ← Development standards
├── 📄 .env                            ← Config (hidden by default)
├── 📄 .env.example
├── 📄 .gitignore
│
├── 📁 docs/                           ← All documentation
│   ├── PORT_MANAGEMENT_GUIDE.md
│   ├── PORT_SUMMARY_FOR_DR_FOSTER.md
│   ├── PRODUCTION_DEPLOYMENT.md
│   └── SCALABLE_DESIGN.md
│
├── 📁 backend/                        ← Python backend code
│   ├── api_server.py
│   ├── api_server_v2.py
│   ├── app.py
│   ├── db_config.py
│   ├── port_manager.py
│   ├── logging_config.py
│   ├── nfl_database_loader.py
│   ├── espn_data_fetcher.py
│   ├── scrape_teamrankings.py
│   ├── debug_scraper.py
│   ├── check_database.py
│   └── SCALABLE_DESIGN.py
│
├── 📁 frontend/                       ← React application
│   └── (existing React files)
│
├── 📁 tests/                          ← All test files
│   ├── test_apis.py
│   ├── test_db_direct.py
│   ├── test_espn_api.py
│   ├── test_espn_standings.py
│   ├── test_ml_model.py
│   ├── test_name_matching.py
│   ├── test_scoreboard.py
│   └── test_standings.py
│
├── 📁 utilities/                      ← Helper scripts
│   ├── log_viewer.py
│   └── quick_logs.py
│
├── 📁 templates/                      ← HTML templates
├── 📁 logs/                           ← Application logs
├── 📁 testbed/                        ← Testing environment
└── 📁 __pycache__/                    ← Python cache (auto-generated)
```

## Benefits:

✅ **dr.foster.md at top level** - First thing Dr. Foster sees!  
✅ **backend/ folder** - Matches frontend/ structure  
✅ **docs/ folder** - All documentation in one place  
✅ **tests/ folder** - Separate from production code  
✅ **utilities/ folder** - Helper tools organized  
✅ **Clean root** - Only 3-4 important files at top  

## VS Code Explorer View Will Look Like:

```
▼ H.C LOMBARDO APP
  📄 dr.foster.md              ← Easy to find!
  📄 README.md
  📄 BEST_PRACTICES.md
  ▶ .vscode/
  ▼ backend/                   ← All Python code
  ▼ docs/                      ← All documentation
  ▼ frontend/                  ← React app
  ▼ tests/                     ← All tests
  ▼ utilities/                 ← Tools
  ▶ logs/
  ▶ testbed/
```

## Implementation Steps:

1. ✅ Create new directories (backend/, docs/, tests/, utilities/)
2. Move files to appropriate locations
3. Update import statements in Python files
4. Test that everything still works
5. Update .gitignore if needed
6. Commit changes

## Next Steps:

**Ask April:** 
- Should we execute this reorganization now?
- Any changes to the proposed structure?
- Should we do this in testbed first? (Best practice!)

**Testing Plan:**
1. Create new structure in testbed
2. Test that imports still work
3. Test that API still runs
4. Test that frontend still connects
5. Only then apply to production
