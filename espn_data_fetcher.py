"""
ESPN API Data Fetcher for NFL Statistics
Fetches live team data from ESPN's free public API
Updates PostgreSQL database with current season stats
"""
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
from datetime import datetime
from team_abbreviations import to_canonical_abbr

# Load environment variables
load_dotenv()

class ESPNDataFetcher:
    """Fetch and process NFL data from ESPN API"""
    
    BASE_URL = "http://site.api.espn.com/apis/site/v2/sports/football/nfl"
    MIN_EXPECTED_TEAMS = 28
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    @staticmethod
    def _safe_int(value, default=0):
        """Convert value to int safely."""
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _safe_float(value, default=0.0):
        """Convert value to float safely."""
        try:
            return float(value)
        except (TypeError, ValueError):
            return default
    
    def get_db_connection(self):
        """Get PostgreSQL database connection"""
        return psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'nfl_analytics'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '')
        )
    
    def fetch_teams(self):
        """Fetch all NFL teams from ESPN API"""
        try:
            url = f"{self.BASE_URL}/teams"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            teams = []
            
            if 'sports' in data:
                for sport in data['sports']:
                    for league in sport.get('leagues', []):
                        for team_data in league.get('teams', []):
                            team = team_data.get('team', {})
                            teams.append({
                                'id': team.get('id'),
                                'name': team.get('displayName'),
                                'abbreviation': team.get('abbreviation'),
                                'logo': team.get('logos', [{}])[0].get('href', '') if team.get('logos') else ''
                            })
            
            print(f"✅ Fetched {len(teams)} teams from ESPN API")
            return teams
            
        except Exception as e:
            print(f"❌ Error fetching teams: {e}")
            return []
    
    def fetch_team_stats(self, team_id):
        """Fetch specific team statistics"""
        try:
            # Get current season year
            current_year = datetime.now().year
            
            # Try current season
            url = f"{self.BASE_URL}/seasons/{current_year}/teams/{team_id}/statistics"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                stats = self.parse_team_stats(data)
                return stats
            
            return None
            
        except Exception as e:
            print(f"⚠️  Error fetching stats for team {team_id}: {e}")
            return None
    
    def parse_team_stats(self, data):
        """Parse team statistics from ESPN API response"""
        stats = {
            'ppg': 0.0,
            'pa': 0.0,
            'wins': 0,
            'losses': 0,
            'games_played': 0
        }
        
        try:
            # ESPN API structure varies, extract what we can
            if 'team' in data:
                team_data = data['team']
                
                # Get record
                if 'record' in team_data:
                    record = team_data['record']
                    stats['wins'] = int(record.get('wins', 0))
                    stats['losses'] = int(record.get('losses', 0))
                
                # Get statistics
                if 'statistics' in team_data:
                    for stat in team_data['statistics']:
                        name = stat.get('name', '').lower()
                        value = float(stat.get('value', 0))
                        
                        if 'pointspergame' in name or 'points per game' in name:
                            stats['ppg'] = value
                        elif 'pointsallowed' in name or 'points allowed' in name:
                            stats['pa'] = value
                
                stats['games_played'] = stats['wins'] + stats['losses']
        
        except Exception as e:
            print(f"⚠️  Error parsing stats: {e}")
        
        return stats
    
    def fetch_scoreboard_stats(self):
        """Fetch team stats from scoreboard/season data"""
        try:
            # Get scoreboard which includes season stats
            url = f"{self.BASE_URL}/scoreboard"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            team_stats = {}
            
            # Extract season information
            if 'leagues' in data:
                for league in data['leagues']:
                    season = league.get('season', {})
                    print(f"📅 Season: {season.get('year')}, Type: {season.get('type')}")
            
            # Get teams from recent games to extract current stats
            if 'events' in data:
                for event in data['events']:
                    for competition in event.get('competitions', []):
                        for competitor in competition.get('competitors', []):
                            team = competitor.get('team', {})
                            team_id = team.get('id')
                            
                            if team_id and team_id not in team_stats:
                                # Get team record
                                records = competitor.get('records', [])
                                wins, losses = 0, 0
                                
                                for record in records:
                                    if record.get('type') == 'total':
                                        summary = record.get('summary', '0-0')
                                        parts = summary.split('-')
                                        if len(parts) >= 2:
                                            wins = int(parts[0])
                                            losses = int(parts[1])
                                
                                # Get statistics
                                stats_list = competitor.get('statistics', [])
                                ppg = 0.0
                                pa = 0.0
                                
                                for stat in stats_list:
                                    name = stat.get('name', '').lower()
                                    value = float(stat.get('displayValue', 0))
                                    
                                    if 'avgpointspergame' in name.replace(' ', ''):
                                        ppg = value
                                    elif 'avgpointsallowedpergame' in name.replace(' ', ''):
                                        pa = value
                                
                                team_stats[team_id] = {
                                    'id': team_id,
                                    'name': team.get('displayName'),
                                    'abbreviation': team.get('abbreviation'),
                                    'wins': wins,
                                    'losses': losses,
                                    'ppg': ppg,
                                    'pa': pa
                                }
            
            print(f"✅ Extracted stats for {len(team_stats)} teams from scoreboard")
            return team_stats
            
        except Exception as e:
            print(f"❌ Error fetching scoreboard: {e}")
            return {}
    
    def update_database(self):
        """Fetch data from ESPN and update PostgreSQL database"""
        print("\n" + "="*70)
        print("ESPN API DATA UPDATE")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        # Fetch teams and stats
        teams = self.fetch_teams()
        team_stats = self.fetch_scoreboard_stats()
        
        if not teams:
            print("❌ Failed to fetch teams from ESPN API")
            return False
        
        # If scoreboard didn't give us stats, we'll use existing data as fallback
        if not team_stats:
            print("⚠️  No stats from scoreboard, keeping existing database data")
            return False
        
        conn = None
        cursor = None

        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            # Build candidate rows first so we can refuse partial/empty refreshes.
            candidate_rows = []
            for team in teams:
                team_id = team.get('id')
                stats = team_stats.get(team_id, {}) if team_id else {}

                abbreviation = to_canonical_abbr(
                    (stats.get('abbreviation') or team.get('abbreviation') or '').strip().upper()
                )
                if not abbreviation:
                    continue

                wins = self._safe_int(stats.get('wins'), 0)
                losses = self._safe_int(stats.get('losses'), 0)
                ppg = round(self._safe_float(stats.get('ppg'), 0.0), 1)
                pa = round(self._safe_float(stats.get('pa'), 0.0), 1)
                games_played = self._safe_int(stats.get('games_played'), wins + losses)
                if games_played <= 0 and (wins > 0 or losses > 0):
                    games_played = wins + losses

                candidate_rows.append((
                    stats.get('name') or team.get('name') or abbreviation,
                    abbreviation,
                    wins,
                    losses,
                    ppg,
                    pa,
                    games_played,
                ))

            if len(candidate_rows) < self.MIN_EXPECTED_TEAMS:
                print(
                    f"❌ Safety stop: parsed {len(candidate_rows)} teams "
                    f"(< {self.MIN_EXPECTED_TEAMS}); keeping existing data"
                )
                return False

            cursor.execute("SELECT id, abbreviation, name FROM teams")
            existing_rows = cursor.fetchall()

            existing_by_abbr = {}
            existing_by_name = {}
            for existing_id, existing_abbr, existing_name in existing_rows:
                canonical_abbr = to_canonical_abbr(existing_abbr)
                if canonical_abbr:
                    existing_by_abbr[canonical_abbr] = existing_id
                if existing_name:
                    existing_by_name[existing_name.strip().lower()] = existing_id

            updated_count = 0
            unmatched_count = 0

            for row in candidate_rows:
                team_id = existing_by_abbr.get(row[1]) or existing_by_name.get(row[0].strip().lower())

                if team_id is None:
                    unmatched_count += 1
                    continue

                cursor.execute(
                    """
                    UPDATE teams
                    SET name = %s,
                        abbreviation = %s,
                        wins = %s,
                        losses = %s,
                        ppg = %s,
                        pa = %s,
                        games_played = %s
                    WHERE id = %s
                    """,
                    (row[0], row[1], row[2], row[3], row[4], row[5], row[6], team_id),
                )
                updated_count += cursor.rowcount

            if updated_count < self.MIN_EXPECTED_TEAMS:
                conn.rollback()
                print(
                    f"❌ Safety rollback: only {updated_count} teams matched existing rows "
                    f"({unmatched_count} unmatched)"
                )
                return False

            cursor.execute("SELECT COUNT(*) FROM teams")
            total_count = cursor.fetchone()[0]

            if total_count < self.MIN_EXPECTED_TEAMS:
                conn.rollback()
                print(
                    f"❌ Safety rollback: teams table has {total_count} rows "
                    f"(< {self.MIN_EXPECTED_TEAMS})"
                )
                return False

            conn.commit()

            print(
                f"✅ Database updated: {len(candidate_rows)} processed "
                f"({updated_count} updated, {unmatched_count} unmatched), total={total_count}"
            )
            print("="*70 + "\n")
            return True

        except Exception as e:
            if conn:
                conn.rollback()
            print(f"❌ Database update failed: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def get_last_update_time(self):
        """Check when database was last updated"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Check if we have a metadata table
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'update_metadata'
                )
            """)
            
            if not cursor.fetchone()[0]:
                # Create metadata table
                cursor.execute("""
                    CREATE TABLE update_metadata (
                        id SERIAL PRIMARY KEY,
                        last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                cursor.execute("INSERT INTO update_metadata DEFAULT VALUES")
                conn.commit()
            
            cursor.execute("SELECT last_update FROM update_metadata ORDER BY id DESC LIMIT 1")
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
            
        except Exception as e:
            print(f"⚠️  Error checking last update: {e}")
            return None
    
    def record_update(self):
        """Record that an update occurred"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO update_metadata (last_update) 
                VALUES (CURRENT_TIMESTAMP)
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️  Error recording update: {e}")


def main():
    """Run data update"""
    fetcher = ESPNDataFetcher()
    success = fetcher.update_database()
    
    if success:
        fetcher.record_update()
        print("✅ Data update complete!")
    else:
        print("❌ Data update failed!")


if __name__ == "__main__":
    main()
