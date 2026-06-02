# Full Program Test Automation Status

Generated UTC: 2026-06-02T05:20:32.405282+00:00
Frontend base: https://staging.d2fwv8daemi5y2.amplifyapp.com
API base: https://9dkkj5n2rc.execute-api.us-east-2.amazonaws.com

## Totals
- route_inventory_count: 13
- route_pass: 1
- route_fail: 12
- api_inventory_count: 32
- api_pass: 25
- api_fail: 5
- api_skipped: 2

## Route Results
- route=/ ok=true status=200 error=None
- route=/admin ok=false status=404 error=None
- route=/analytics ok=false status=404 error=None
- route=/game-statistics ok=false status=404 error=None
- route=/historical-data ok=false status=404 error=None
- route=/matchup-analyzer ok=false status=404 error=None
- route=/ml-predictions ok=false status=404 error=None
- route=/ml-predictions-old ok=false status=404 error=None
- route=/ml-predictions-redesign ok=false status=404 error=None
- route=/model-performance ok=false status=404 error=None
- route=/settings ok=false status=404 error=None
- route=/team-comparison ok=false status=404 error=None
- route=/team-stats ok=false status=404 error=None

## API Results
- method=GET template=/api/elo/predict-week/${season}/${week} resolved=/api/elo/predict-week/2025/1 ok=true skipped=false status=200 skip_reason=None error=None
- method=GET template=/api/elo/ratings/current resolved=/api/elo/ratings/current ok=true skipped=false status=200 skip_reason=None error=None
- method=GET template=/api/hcl/analytics/betting?season=${season} resolved=/api/hcl/analytics/betting?season=2025 ok=false skipped=false status=500 skip_reason=None error=None
- method=GET template=/api/hcl/analytics/betting?season=${season}${selectedTeam ? resolved=None ok=false skipped=true status=None skip_reason=Template has unresolved dynamic variables error=None
- method=GET template=/api/hcl/analytics/referees?season=${season} resolved=/api/hcl/analytics/referees?season=2025 ok=false skipped=false status=500 skip_reason=None error=None
- method=GET template=/api/hcl/analytics/rest?season=${season} resolved=/api/hcl/analytics/rest?season=2025 ok=false skipped=false status=500 skip_reason=None error=None
- method=GET template=/api/hcl/analytics/summary?season=${season} resolved=/api/hcl/analytics/summary?season=2025 ok=false skipped=false status=500 skip_reason=None error=None
- method=GET template=/api/hcl/analytics/weather?season=${season} resolved=/api/hcl/analytics/weather?season=2025 ok=false skipped=false status=500 skip_reason=None error=None
- method=GET template=/api/hcl/teams/${abbr}/games?season=${season}&limit=50 resolved=/api/hcl/teams/KC/games?season=2025&limit=50 ok=true skipped=false status=200 skip_reason=None error=None
- method=GET template=/api/hcl/teams/${abbr}?season=${season} resolved=/api/hcl/teams/KC?season=2025 ok=true skipped=false status=200 skip_reason=None error=None
- method=GET template=/api/hcl/teams/${selectedTeam}?season=${selectedSeason} resolved=/api/hcl/teams/KC?season=2025 ok=true skipped=false status=200 skip_reason=None error=None
- method=GET template=/api/hcl/teams/${teamAbbr}/games?season=${season} resolved=/api/hcl/teams/KC/games?season=2025 ok=true skipped=false status=200 skip_reason=None error=None
- method=GET template=/api/hcl/teams/${teamAbbr}?season=${season} resolved=/api/hcl/teams/KC?season=2025 ok=true skipped=false status=200 skip_reason=None error=None
- method=GET template=/api/hcl/teams?season=${defaultSeason} resolved=/api/hcl/teams?season=2025 ok=true skipped=false status=200 skip_reason=None error=None
- method=GET template=/api/hcl/teams?season=${seasonA} resolved=/api/hcl/teams?season=2025 ok=true skipped=false status=200 skip_reason=None error=None
- method=GET template=/api/hcl/teams?season=${seasonB} resolved=/api/hcl/teams?season=2025 ok=true skipped=false status=200 skip_reason=None error=None
- method=GET template=/api/hcl/teams?season=${season} resolved=/api/hcl/teams?season=2025 ok=true skipped=false status=200 skip_reason=None error=None
- method=GET template=/api/hcl/teams?season=${selectedSeason} resolved=/api/hcl/teams?season=2025 ok=true skipped=false status=200 skip_reason=None error=None
- method=GET template=/api/live-scores resolved=/api/live-scores ok=true skipped=false status=200 skip_reason=None error=None
- method=GET template=/api/ml/available-weeks resolved=/api/ml/available-weeks ok=true skipped=false status=200 skip_reason=None error=None
- method=GET template=/api/ml/explain resolved=/api/ml/explain ok=true skipped=false status=200 skip_reason=None error=None
- method=GET template=/api/ml/model-info resolved=/api/ml/model-info ok=true skipped=false status=200 skip_reason=None error=None
- method=GET template=/api/ml/performance-stats?season=${season} resolved=/api/ml/performance-stats?season=2025 ok=true skipped=false status=200 skip_reason=None error=None
- method=GET template=/api/ml/predict-upcoming resolved=/api/ml/predict-upcoming ok=true skipped=false status=200 skip_reason=None error=None
- method=GET template=/api/ml/predict-week/${season}/${week} resolved=/api/ml/predict-week/2025/1 ok=true skipped=false status=200 skip_reason=None error=None
- method=GET template=/api/ml/season-ai-vs-vegas/${season} resolved=/api/ml/season-ai-vs-vegas/2025 ok=true skipped=false status=200 skip_reason=None error=None
- method=GET template=/api/ml/season-ai-vs-vegas/${selectedSeason} resolved=/api/ml/season-ai-vs-vegas/2025 ok=true skipped=false status=200 skip_reason=None error=None
- method=GET template=/api/predictions/combined/${season}/${week} resolved=/api/predictions/combined/2025/1 ok=true skipped=false status=200 skip_reason=None error=None
- method=GET template=/api/teams resolved=/api/teams ok=true skipped=false status=200 skip_reason=None error=None
- method=GET template=/api/teams/${abbreviation} resolved=/api/teams/KC ok=true skipped=false status=200 skip_reason=None error=None
- method=GET template=/health resolved=/health ok=true skipped=false status=200 skip_reason=None error=None
- method=POST template=/api/ml/update-results resolved=/api/ml/update-results ok=false skipped=true status=None skip_reason=Non-GET endpoint skipped to avoid side effects error=None
