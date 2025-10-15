"""
NFL STATS SYSTEM - GUIDING PRINCIPLES & DATA SOURCES
PERMANENT REFERENCE - READ THIS BEFORE ANY STATS WORK
Date Created: October 14, 2025
Author: April V. Sykes
"""

# ============================================================================
# CRITICAL RULES - NEVER VIOLATE THESE
# ============================================================================

## Rule 1: ALWAYS USE LIVE DATA
- ❌ NEVER embed static tables or hardcoded stats
- ✅ ALWAYS call external API/data source for stat lookups
- ✅ ALWAYS validate timestamp/freshness (same day or same game)
- ⚠️  If data is stale, re-fetch or flag error

## Rule 2: NEVER MAKE UP DATA
- ❌ NEVER fabricate stats if API fails
- ✅ Use fallback APIs in order of priority
- ✅ If all sources fail, return "data not available" error
- ✅ Include source citation: "source: API X, endpoint Y, fetched at Z"

## Rule 3: PARAMETERIZE ALL QUERIES
- ✅ Accept filters: team, player, stat type, season, game
- ✅ Build API requests dynamically (not hardcoded)
- ✅ Support any stat from stats_config.py
- ❌ Do not hardcode single stat queries

## Rule 4: CACHE WITH EXPIRATION
- ✅ Cache recent results briefly (5-15 minutes for live games)
- ✅ Expire cache rapidly during live games
- ❌ Do not use old cached results past validity period
- ✅ Include "cached_at" timestamp in responses

## Rule 5: SCHEMA AWARENESS
- ✅ Maintain internal reference of API schemas (fields, endpoints)
- ✅ Form correct requests based on schema
- ✅ Handle schema changes gracefully
- ✅ Document all API endpoints used

## Rule 6: ERROR & BOUNDARY HANDLING
- ✅ For future games: "data not available yet"
- ✅ For missing data: "stat not tracked for this team/player"
- ✅ For API errors: "temporary data unavailability"
- ❌ Never default to placeholder/dummy values

## Rule 7: TESTABLE & AUDITABLE
- ✅ Every output includes: source, endpoint, timestamp
- ✅ Log all API calls for auditing
- ✅ Provide data provenance trail
- ✅ Enable verification of non-static data usage

# ============================================================================
# DATA SOURCE PRIORITY (In Order)
# ============================================================================

## PRIMARY SOURCES (Use First)

### 1. TeamRankings.com (CURRENT IMPLEMENTATION)
**Status**: ✅ IMPLEMENTED in universal_stat_fetcher.py
**Coverage**: 226+ team stats, live updates
**URL Format**: https://www.teamrankings.com/nfl/stat/{stat-slug}
**Cost**: Free (web scraping)
**Limitations**: 
  - Rate limit: Be polite, 2 second delays between requests
  - No play-by-play data
  - No player stats
**Use For**: 
  - All 37 configured team stats
  - Historical season data
  - Game-by-game breakdowns

### 2. ESPN API (CURRENT IMPLEMENTATION)
**Status**: ✅ IMPLEMENTED in multi_source_data_fetcher.py
**Coverage**: Live standings, scores, basic stats
**Endpoint**: http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard
**Cost**: Free (unofficial API)
**Limitations**:
  - May not return all 32 teams
  - Limited advanced stats
  - No guaranteed SLA
**Use For**:
  - Live game scores
  - Current standings (wins/losses)
  - Team records

## SECONDARY SOURCES (Fallback)

### 3. Sportradar NFL API v7
**Status**: 🔴 NOT IMPLEMENTED - Requires API Key
**Coverage**: Comprehensive - play-by-play, rosters, injuries, advanced stats
**Endpoint**: https://api.sportradar.us/nfl/official/trial/v7/
**Cost**: Commercial/paid license required
**Real-time**: Yes (REST + Push feeds)
**Documentation**: https://developer.sportradar.com/docs/read/american_football/NFL_v7
**Use For**:
  - Official data when available
  - Play-by-play analysis
  - Injury reports
  - Next Gen Stats

### 4. SportsDataIO NFL API
**Status**: 🔴 NOT IMPLEMENTED - Requires API Key
**Coverage**: Real-time scores, stats, odds, projections
**Endpoint**: https://api.sportsdata.io/v3/nfl/
**Cost**: Paid/tiered ($0-$200+/month)
**Documentation**: https://sportsdata.io/developers/api-documentation/nfl
**Use For**:
  - Real-time game data
  - Player stats
  - Betting odds
  - Fantasy projections

### 5. MySportsFeeds
**Status**: 🔴 NOT IMPLEMENTED - Requires API Key
**Coverage**: Standings, boxscores, play-by-play
**Endpoint**: https://api.mysportsfeeds.com/v2.1/pull/nfl/
**Cost**: Affordable, developer-friendly
**Documentation**: https://www.mysportsfeeds.com/data-feeds/api-docs/
**Use For**:
  - Historical data
  - Boxscore details
  - Affordable live data

### 6. EntitySport NFL API
**Status**: 🔴 NOT IMPLEMENTED
**Coverage**: Live scores, historical, team/player data
**Documentation**: https://entitysport.com/
**Use For**: Alternative live scores

### 7. Goalserve NFL API
**Status**: 🔴 NOT IMPLEMENTED
**Coverage**: Live scores, in-game stats, historical from 2010+
**Documentation**: https://www.goalserve.com/
**Use For**: Historical data analysis

## TERTIARY SOURCES (Emergency Fallback)

### 8. Stats Perform / STATS API
**Status**: 🔴 NOT IMPLEMENTED - Enterprise
**Coverage**: Industry-grade live + historical
**Cost**: Commercial/enterprise pricing
**Use For**: High-reliability production systems

### 9. OddsMatrix NFL Data Feed
**Status**: 🔴 NOT IMPLEMENTED
**Coverage**: Game analytics, play-by-play, odds
**Documentation**: https://oddsmatrix.com/
**Use For**: Betting analytics focus

# ============================================================================
# FALLBACK LOGIC IMPLEMENTATION
# ============================================================================

## Template for Live Data Fetching

```python
def get_nfl_stat_with_fallback(stat_type, season, team=None, player=None):
    """
    Fetch NFL stat with multi-source fallback
    ALWAYS uses live data, NEVER static values
    """
    import time
    from datetime import datetime
    
    # Log the request
    log_request = {
        'timestamp': datetime.now().isoformat(),
        'stat_type': stat_type,
        'season': season,
        'team': team,
        'player': player
    }
    
    # 1. Try PRIMARY: TeamRankings (if team stat)
    if not player and stat_type in AVAILABLE_STATS:
        try:
            category, stat_key = parse_stat_type(stat_type)
            data = fetch_stat_from_teamrankings(category, stat_key)
            
            if data and is_fresh(data):
                return {
                    'data': data,
                    'source': 'TeamRankings.com',
                    'endpoint': f'/nfl/stat/{stat_key}',
                    'fetched_at': datetime.now().isoformat(),
                    'cache_ttl': 300  # 5 minutes
                }
        except Exception as e:
            log_error(f"TeamRankings failed: {e}")
    
    # 2. Try SECONDARY: ESPN API (if standings/scores)
    if stat_type in ['wins', 'losses', 'record']:
        try:
            data = fetch_espn_standings()
            
            if data and is_fresh(data):
                return {
                    'data': data,
                    'source': 'ESPN API',
                    'endpoint': '/apis/site/v2/sports/football/nfl/scoreboard',
                    'fetched_at': datetime.now().isoformat(),
                    'cache_ttl': 180  # 3 minutes during live games
                }
        except Exception as e:
            log_error(f"ESPN failed: {e}")
    
    # 3. Try TERTIARY: Sportradar (if API key available)
    if SPORTRADAR_API_KEY:
        try:
            data = fetch_sportradar_stat(stat_type, season, team, player)
            
            if data and is_fresh(data):
                return {
                    'data': data,
                    'source': 'Sportradar NFL API v7',
                    'endpoint': '/nfl/official/trial/v7/...',
                    'fetched_at': datetime.now().isoformat(),
                    'cache_ttl': 60  # 1 minute for premium source
                }
        except Exception as e:
            log_error(f"Sportradar failed: {e}")
    
    # 4. ALL SOURCES FAILED
    return {
        'error': 'No live data available',
        'message': f"Could not fetch {stat_type} for {team or 'all teams'}",
        'attempted_sources': ['TeamRankings', 'ESPN', 'Sportradar'],
        'timestamp': datetime.now().isoformat(),
        'recommendation': 'Check API status or try again in 30 seconds'
    }

def is_fresh(data, max_age_seconds=300):
    """Validate data freshness"""
    if 'timestamp' not in data:
        return False
    
    data_time = datetime.fromisoformat(data['timestamp'])
    age = (datetime.now() - data_time).total_seconds()
    
    return age < max_age_seconds
```

# ============================================================================
# CURRENT SYSTEM STATUS
# ============================================================================

## ✅ IMPLEMENTED

1. **TeamRankings Integration**
   - File: universal_stat_fetcher.py
   - Stats: 37 configured (20 offense, 11 defense, 6 special teams)
   - Coverage: All 32 teams
   - Status: ✅ Working, tested Oct 14, 2025

2. **ESPN Integration**
   - File: multi_source_data_fetcher.py
   - Stats: Standings (wins, losses, ties, games_played)
   - Coverage: ~30 teams (inconsistent)
   - Status: ✅ Working, but unreliable for full coverage
   - **Note**: Now handles ties! (W-L-T format, e.g., "5-2-1")

3. **Stats Configuration**
   - File: stats_config.py
   - Stats: 37 team stats
   - Extensibility: ✅ Add new stats by editing config only

4. **Database Schema**
   - Table: teams
   - Columns: id, name, abbreviation, wins, losses, ties, ppg, pa, games_played, stats (JSONB)
   - Status: ✅ Updated Oct 14, 2025 to include ties column

## 🔴 NOT IMPLEMENTED

1. **Premium API Integration**
   - Sportradar, SportsDataIO, MySportsFeeds
   - Reason: Requires API keys/payment
   - Priority: HIGH for production deployment

2. **Player Stats**
   - Current: Team stats only
   - Needed: Individual player performance
   - Reason: TeamRankings doesn't provide player data

3. **Play-by-Play Data**
   - Current: Game-level stats only
   - Needed: Drive-by-drive, play-by-play
   - Reason: Requires premium API (Sportradar)

4. **Caching Layer**
   - Current: No caching
   - Needed: Redis/memcached for performance
   - Priority: MEDIUM

5. **Data Validation**
   - Current: Basic freshness checks
   - Needed: Comprehensive validation pipeline
   - Priority: HIGH

# ============================================================================
# MIGRATION PATH TO PREMIUM APIs
# ============================================================================

## When to Upgrade

### Triggers for Sportradar/SportsDataIO:
- ⚠️  TeamRankings rate limiting issues
- ⚠️  Need real-time (< 1 minute delay) updates
- ⚠️  Need player-level stats
- ⚠️  Need play-by-play data
- ⚠️  Production deployment with SLA requirements

### Cost Analysis:
- **SportsDataIO Trial**: 1,000 API calls free
- **SportsDataIO Bronze**: $50/month (10,000 calls)
- **SportsDataIO Silver**: $100/month (50,000 calls)
- **Sportradar Trial**: Limited trial available
- **Sportradar Production**: Custom pricing (likely $500+/month)

## Integration Steps:

1. **Get API Key**
   ```bash
   # Sign up at https://sportsdata.io/ or https://developer.sportradar.com/
   # Store in environment variable
   export SPORTSDATA_API_KEY="your-key-here"
   ```

2. **Add to stats_config.py**
   ```python
   API_KEYS = {
       'sportsdata': os.getenv('SPORTSDATA_API_KEY'),
       'sportradar': os.getenv('SPORTRADAR_API_KEY'),
       'mysportsfeeds': os.getenv('MYSPORTSFEEDS_API_KEY')
   }
   ```

3. **Create API Client**
   ```python
   # File: sportsdata_client.py
   def fetch_team_stats_sportsdata(season, team=None):
       headers = {'Ocp-Apim-Subscription-Key': API_KEYS['sportsdata']}
       url = f"https://api.sportsdata.io/v3/nfl/stats/json/TeamSeasonStats/{season}"
       response = requests.get(url, headers=headers)
       return response.json()
   ```

4. **Update Fallback Chain**
   - Add premium API as primary source
   - Keep TeamRankings as free fallback
   - Update get_nfl_stat_with_fallback()

# ============================================================================
# TESTING & VALIDATION
# ============================================================================

## Required Tests Before Declaring Success:

1. **Freshness Test**
   ```python
   # Verify data is from today
   data = fetch_stat_from_teamrankings('offense', 'points_per_game')
   assert is_today(data['timestamp'])
   ```

2. **Coverage Test**
   ```python
   # Verify all 32 teams
   data = fetch_stat_from_teamrankings('offense', 'points_per_game')
   assert len(data) == 32
   assert all(team in ALL_32_TEAMS.values() for team in data.keys())
   ```

3. **Fallback Test**
   ```python
   # Simulate primary source failure
   with mock_teamrankings_failure():
       data = get_nfl_stat_with_fallback('points_per_game')
       assert data['source'] == 'ESPN API'  # Should fallback
   ```

4. **Error Handling Test**
   ```python
   # All sources fail
   with mock_all_sources_failure():
       result = get_nfl_stat_with_fallback('points_per_game')
       assert 'error' in result
       assert result['error'] == 'No live data available'
   ```

5. **Audit Trail Test**
   ```python
   # Verify source citation
   data = fetch_stat_from_teamrankings('offense', 'points_per_game')
   assert 'source' in data
   assert 'endpoint' in data
   assert 'fetched_at' in data
   ```

# ============================================================================
# DROPDOWN SITE INVESTIGATION
# ============================================================================

## User mentioned: "there was a site with dropdown boxes"

### How to Find It:
1. Check browser history for sports stats sites visited
2. Look for sites with UI: Category dropdown → Stat dropdown → Load button
3. Common candidates:
   - TeamRankings.com (✅ We use this)
   - Pro-Football-Reference.com
   - StatMuse.com
   - NFL.com/stats
   - FantasyPros.com

### How to Reverse Engineer:
1. **Open browser DevTools (F12)**
2. **Go to Network tab**
3. **Change dropdown selection**
4. **Look for XHR/Fetch requests**
   - Copy request URL
   - Note query parameters
   - Save response format

5. **Document the API**
   ```python
   # Example discovered endpoint:
   DROPDOWN_SITE_API = {
       'base_url': 'https://discovered-site.com/api',
       'endpoints': {
           'team_stats': '/stats/teams',
           'player_stats': '/stats/players'
       },
       'params': {
           'season': 'int (2025)',
           'stat_type': 'string (passing_yards, rushing_yards, etc.)',
           'team': 'string (team abbreviation)'
       }
   }
   ```

### Integration Priority:
- 🔴 HIGH if it has stats not in TeamRankings
- 🟡 MEDIUM if it's more reliable than current sources
- 🟢 LOW if it duplicates existing coverage

# ============================================================================
# MAINTENANCE CHECKLIST
# ============================================================================

## Daily (During Season):
- [ ] Verify all 32 teams fetching successfully
- [ ] Check data freshness (< 5 minutes old)
- [ ] Monitor API error rates
- [ ] Review fallback usage frequency

## Weekly:
- [ ] Update stats_config.py if new stats available
- [ ] Test all 37 stats end-to-end
- [ ] Review and clear old cached data
- [ ] Check for API schema changes

## Monthly:
- [ ] Evaluate API costs vs usage
- [ ] Consider premium API upgrade if needed
- [ ] Update team name mappings (trades, rebrands)
- [ ] Performance optimization review

## Yearly (Off-season):
- [ ] Update for new season structure changes
- [ ] Review all API subscriptions
- [ ] Clean up deprecated endpoints
- [ ] Update documentation

# ============================================================================
# CRITICAL REMINDERS
# ============================================================================

## ❌ NEVER DO THIS:
1. Hardcode stats in arrays/dicts
2. Use static data files (CSV, JSON with stats)
3. Return cached data > 15 minutes old during live games
4. Fabricate data when API fails
5. Ignore timestamp validation
6. Skip source citation

## ✅ ALWAYS DO THIS:
1. Call live API for every stat request
2. Validate data freshness (timestamp check)
3. Use fallback chain (never single point of failure)
4. Include audit trail (source, endpoint, time)
5. Handle errors gracefully
6. Log all API calls for debugging
7. Test with real API calls (not mocks) before production

# ============================================================================
# CONTACT & ESCALATION
# ============================================================================

## When Stuck:
1. Check this document first
2. Review API documentation
3. Test with curl/Postman before coding
4. Ask user for clarification on requirements
5. Document what you tried and why it failed

## When Adding New Feature:
1. Does it violate any CRITICAL RULES? → STOP, redesign
2. Does it need a new API? → Document cost/coverage first
3. Does it change existing behavior? → Get user approval first
4. Can you test it end-to-end? → Don't merge until tested

---

**Last Updated**: October 14, 2025
**Status**: ✅ ACTIVE - REFERENCE FOR ALL NFL STATS WORK
**Next Review**: When adding new API source or after any data quality incident
