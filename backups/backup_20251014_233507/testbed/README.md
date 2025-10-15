# H.C. Lombardo - Testbed

## Purpose
This folder is for **testing new features** before implementing them in the main app.

## Guidelines
- ✅ Test new APIs here
- ✅ Experiment with new features
- ✅ Try different data sources
- ✅ Prototype UI changes
- ❌ Don't connect to production database
- ❌ Don't commit broken code

## Structure
```
testbed/
├── README.md           (this file)
├── test_*.py          (individual test scripts)
├── experiments/       (experimental features)
└── prototypes/        (UI/feature prototypes)
```

## Testing Workflow
1. **Create test file** - `test_new_feature.py`
2. **Experiment freely** - Try new ideas without breaking main app
3. **Document findings** - Add notes about what works
4. **Implement in main** - Once tested and working, move to main app
5. **Clean up** - Archive or delete test files

## Current Tests
- `experiments/test_espn_api.py` - ESPN API endpoint testing (scoreboard + teams)

## Main App Features (Production)
See `dr.foster.md` in root for complete documentation.

**Current Production Stack:**
- PostgreSQL 18 database (nfl_analytics)
- Flask web dashboard
- TeamRankings.com live data scraper
- 24-hour automatic refresh
- All 32 NFL teams with logos
- Professional UI with glassmorphism

**When to Use Testbed:**
- Testing new data sources before replacing TeamRankings
- Experimenting with alternative UI designs
- Trying different database queries
- Validating API endpoints before integration
- Prototyping new features without risk

## Notes
- This folder is excluded from production deployment
- Tests use separate test database when needed
- Feel free to break things here! 🧪
