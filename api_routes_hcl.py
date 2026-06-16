"""
HCL Historical Data API Routes
Flask endpoints for team statistics and game history
"""

from flask import Blueprint, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
from dotenv import load_dotenv
from team_abbreviations import to_canonical_abbr, to_hcl_abbr, sql_to_canonical_case

load_dotenv()

# Database connection - Use environment variable for database name
# Defaults to production database (nfl_analytics)
def get_db_connection():
    """Connect to HCL historical data database"""
    db_name = os.getenv('DB_NAME', 'nfl_analytics')  # Default to production
    return psycopg2.connect(
        dbname=db_name,
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', ''),
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432')
    )

# Create blueprint
hcl_bp = Blueprint('hcl', __name__, url_prefix='/api/hcl')


def get_latest_completed_season(cur):
    """Return latest season with completed games, fallback to current year."""
    try:
        cur.execute(
            """
            SELECT COALESCE(MAX(season), EXTRACT(YEAR FROM NOW())::int) AS season
            FROM hcl.games
            WHERE home_score IS NOT NULL
              AND away_score IS NOT NULL
            """
        )
        row = cur.fetchone()
        if not row:
            return datetime.now().year
        if isinstance(row, dict):
            return row.get('season') or datetime.now().year
        return row[0] or datetime.now().year
    except Exception:
        return datetime.now().year


def resolve_request_season(cur):
    """Use explicit query param season when provided, else latest completed season."""
    season = request.args.get('season', type=int)
    if season is not None:
        return season
    return get_latest_completed_season(cur)


def view_exists(cur, qualified_view_name):
    """Return True when a database view exists and is addressable."""
    cur.execute("SELECT to_regclass(%s) AS relation_name", (qualified_view_name,))
    row = cur.fetchone()
    if not row:
        return False
    if isinstance(row, dict):
        return row.get('relation_name') is not None
    return row[0] is not None


def analytics_view_unavailable_payload(view_name, season=None):
    payload = {
        'success': True,
        'degraded': True,
        'warning': f'Analytics view {view_name} is not available in this environment'
    }
    if season is not None:
        payload['season'] = season
    return payload

@hcl_bp.route('/teams', methods=['GET'])
def get_teams():
    """
    Get list of all NFL teams with basic season stats
    
    Query params:
        season: Season year (default: latest completed season)
    
    Returns:
        JSON array of teams with abbreviation, name, wins, losses, PPG, yards
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        season = resolve_request_season(cur)

        stats_team_key_sql = sql_to_canonical_case('tgs.team')
        teams_key_sql = sql_to_canonical_case('t.abbreviation')

        # Anchor on public.teams to guarantee full-team coverage even in partial season data.
        query = f"""
            WITH season_stats AS (
                SELECT
                    {stats_team_key_sql} AS team,
                    COUNT(*) AS games_played,
                    SUM(CASE WHEN tgs.result = 'W' THEN 1 ELSE 0 END) AS wins,
                    SUM(CASE WHEN tgs.result = 'L' THEN 1 ELSE 0 END) AS losses,
                    SUM(CASE WHEN tgs.result = 'T' THEN 1 ELSE 0 END) AS ties,
                    ROUND(AVG(tgs.points)::numeric, 1) AS ppg,
                    ROUND(AVG(tgs.total_yards)::numeric, 1) AS yards_per_game,
                    ROUND(AVG(tgs.yards_per_play)::numeric, 2) AS yards_per_play,
                    ROUND(AVG(tgs.completion_pct)::numeric, 1) AS completion_pct,
                    SUM(tgs.turnovers) AS total_turnovers
                FROM hcl.team_game_stats tgs
                WHERE tgs.season = %s
                GROUP BY {stats_team_key_sql}
            )
            SELECT
                {teams_key_sql} AS team,
                t.name AS team_name,
                COALESCE(ss.games_played, 0) AS games_played,
                COALESCE(ss.wins, 0) AS wins,
                COALESCE(ss.losses, 0) AS losses,
                COALESCE(ss.ties, 0) AS ties,
                COALESCE(ss.ppg, 0) AS ppg,
                COALESCE(ss.yards_per_game, 0) AS yards_per_game,
                COALESCE(ss.yards_per_play, 0) AS yards_per_play,
                COALESCE(ss.completion_pct, 0) AS completion_pct,
                COALESCE(ss.total_turnovers, 0) AS total_turnovers
            FROM public.teams t
            LEFT JOIN season_stats ss
                ON {teams_key_sql} = ss.team
            ORDER BY wins DESC, ppg DESC, team ASC
        """
        
        cur.execute(query, (season,))
        teams = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(teams),
            'season': season,
            'teams': teams
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@hcl_bp.route('/teams/<team_abbr>', methods=['GET'])
def get_team_details(team_abbr):
    """
    Get detailed season statistics for a specific team
    
    Args:
        team_abbr: Team abbreviation (e.g. 'BAL', 'KC')
    
    Query params:
        season: Filter by season (default: latest completed season)
    
    Returns:
        JSON with team stats, home/away splits, recent form
    """
    try:
        requested_team_abbr = to_canonical_abbr(team_abbr)
        db_team_abbr = to_hcl_abbr(requested_team_abbr)
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        season = resolve_request_season(cur)
        
        # Get season stats from team_game_stats - ALL AVAILABLE STATS
        query = """
            SELECT 
                team,
                season,
                COUNT(*) as games_played,
                SUM(CASE WHEN result = 'W' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN result = 'L' THEN 1 ELSE 0 END) as losses,
                SUM(CASE WHEN result = 'T' THEN 1 ELSE 0 END) as ties,
                
                -- Scoring
                ROUND(AVG(points)::numeric, 1) as ppg,
                SUM(points) as total_points,
                ROUND(AVG(touchdowns)::numeric, 1) as touchdowns_per_game,
                ROUND(AVG(field_goals_made)::numeric, 1) as fg_per_game,
                ROUND(AVG(field_goals_att)::numeric, 1) as fg_att_per_game,
                
                -- Offensive Stats
                ROUND(AVG(total_yards)::numeric, 1) as total_yards_per_game,
                ROUND(AVG(passing_yards)::numeric, 1) as passing_yards_per_game,
                ROUND(AVG(rushing_yards)::numeric, 1) as rushing_yards_per_game,
                ROUND(AVG(plays)::numeric, 1) as plays_per_game,
                ROUND(AVG(yards_per_play)::numeric, 2) as yards_per_play,
                
                -- Passing Stats
                ROUND(AVG(completions)::numeric, 1) as completions_per_game,
                ROUND(AVG(passing_att)::numeric, 1) as passing_att_per_game,
                ROUND(AVG(completion_pct)::numeric, 1) as completion_pct,
                ROUND(AVG(passing_tds)::numeric, 1) as passing_tds_per_game,
                ROUND(AVG(interceptions)::numeric, 1) as interceptions_per_game,
                ROUND(AVG(sacks_taken)::numeric, 1) as sacks_taken_per_game,
                ROUND(AVG(sack_yards_lost)::numeric, 1) as sack_yards_lost_per_game,
                ROUND(AVG(qb_rating)::numeric, 1) as qb_rating,
                
                -- Rushing Stats
                ROUND(AVG(rushing_att)::numeric, 1) as rushing_att_per_game,
                ROUND(AVG(yards_per_carry)::numeric, 2) as yards_per_carry,
                ROUND(AVG(rushing_tds)::numeric, 1) as rushing_tds_per_game,
                
                -- Efficiency Metrics
                ROUND(AVG(third_down_pct)::numeric, 1) as third_down_pct,
                ROUND(AVG(fourth_down_pct)::numeric, 1) as fourth_down_pct,
                ROUND(AVG(red_zone_pct)::numeric, 1) as red_zone_pct,
                
                -- Special Teams
                ROUND(AVG(punt_count)::numeric, 1) as punts_per_game,
                ROUND(AVG(punt_avg_yards)::numeric, 1) as punt_avg_yards,
                ROUND(AVG(kickoff_return_yards)::numeric, 1) as kickoff_return_yards_per_game,
                ROUND(AVG(punt_return_yards)::numeric, 1) as punt_return_yards_per_game,
                
                -- Defense/Turnovers
                SUM(turnovers) as total_turnovers,
                ROUND(AVG(turnovers)::numeric, 1) as turnovers_per_game,
                ROUND(AVG(fumbles_lost)::numeric, 1) as fumbles_lost_per_game,
                ROUND(AVG(penalties)::numeric, 1) as penalties_per_game,
                ROUND(AVG(penalty_yards)::numeric, 1) as penalty_yards_per_game,
                
                -- Time of Possession
                ROUND(AVG(time_of_possession_pct)::numeric, 1) as time_of_possession_pct,
                
                -- Advanced Metrics
                ROUND(AVG(drives)::numeric, 1) as drives_per_game,
                ROUND(AVG(early_down_success_rate)::numeric, 1) as early_down_success_rate,
                ROUND(AVG(starting_field_pos_yds)::numeric, 1) as starting_field_pos_yds,
                
                -- EPA (Expected Points Added) Metrics
                ROUND(AVG(epa_per_play)::numeric, 3) as epa_per_play,
                ROUND(AVG(pass_epa)::numeric, 3) as pass_epa,
                ROUND(AVG(rush_epa)::numeric, 3) as rush_epa,
                ROUND(AVG(success_rate)::numeric, 1) as success_rate,
                ROUND(AVG(explosive_play_pct)::numeric, 1) as explosive_play_pct,
                ROUND(AVG(stuff_rate)::numeric, 1) as stuff_rate,
                
                -- Home/Away splits
                ROUND(AVG(CASE WHEN is_home THEN points END)::numeric, 1) as ppg_home,
                ROUND(AVG(CASE WHEN NOT is_home THEN points END)::numeric, 1) as ppg_away,
                SUM(CASE WHEN is_home AND result = 'W' THEN 1 ELSE 0 END) as home_wins,
                SUM(CASE WHEN NOT is_home AND result = 'W' THEN 1 ELSE 0 END) as away_wins
            FROM hcl.team_game_stats
            WHERE team = %s AND season = %s
            GROUP BY team, season
        """
        
        cur.execute(query, (db_team_abbr, season))
        team_stats = cur.fetchone()
        
        if not team_stats:
            cur.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': f'Team {requested_team_abbr} not found for season {season}'
            }), 404

        team_stats['team'] = to_canonical_abbr(team_stats['team'])
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'team': team_stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@hcl_bp.route('/teams/<team_abbr>/games', methods=['GET'])
def get_team_games(team_abbr):
    """
    Get full season schedule for a specific team (both completed and upcoming games)
    
    Args:
        team_abbr: Team abbreviation (e.g. 'BAL', 'KC')
    
    Query params:
        season: Filter by season (default: latest completed season)
        limit: Max games to return (default: 20)
    
    Returns:
        JSON array of games with stats for completed games, schedule info for upcoming
    """
    try:
        requested_team_abbr = to_canonical_abbr(team_abbr)
        db_team_abbr = to_hcl_abbr(requested_team_abbr)
        limit = request.args.get('limit', default=18, type=int)  # Changed default to 18 for full season
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        season = resolve_request_season(cur)
        
        # Query to get all scheduled games (from hcl.games) and join with stats where available
        query = """
            SELECT 
                g.game_id,
                g.season,
                g.week,
                g.game_date,
                CASE WHEN g.home_team = %s THEN g.home_team ELSE g.away_team END as team,
                CASE WHEN g.home_team = %s THEN g.away_team ELSE g.home_team END as opponent,
                CASE WHEN g.home_team = %s THEN TRUE ELSE FALSE END as is_home,
                -- Scores (NULL for upcoming games)
                g.home_score,
                g.away_score,
                CASE WHEN g.home_team = %s THEN g.home_score ELSE g.away_score END as team_points,
                -- Result (NULL for upcoming games)
                tgs.result,
                -- Team stats (NULL for upcoming games)
                tgs.total_yards,
                tgs.passing_yards,
                tgs.rushing_yards,
                ROUND(tgs.yards_per_play::numeric, 2) as yards_per_play,
                ROUND(tgs.completion_pct::numeric, 1) as completion_pct,
                tgs.turnovers,
                ROUND(tgs.third_down_pct::numeric, 1) as third_down_pct,
                -- EPA stats (NULL for upcoming games)
                ROUND(tgs.epa_per_play::numeric, 3) as epa_per_play,
                ROUND(tgs.pass_epa::numeric, 3) as pass_epa,
                ROUND(tgs.rush_epa::numeric, 3) as rush_epa,
                ROUND(tgs.success_rate::numeric, 1) as success_rate,
                ROUND(tgs.explosive_play_pct::numeric, 1) as explosive_play_pct,
                -- Betting lines
                g.spread_line,
                g.total_line,
                g.home_moneyline,
                g.away_moneyline,
                -- Weather
                g.roof,
                g.temp,
                g.wind,
                -- Context
                CASE WHEN g.home_team = %s THEN g.home_rest ELSE g.away_rest END as rest_days,
                g.is_divisional_game,
                g.referee
            FROM hcl.games g
            LEFT JOIN hcl.team_game_stats tgs ON g.game_id = tgs.game_id AND tgs.team = %s
            WHERE (g.home_team = %s OR g.away_team = %s) AND g.season = %s
            ORDER BY g.week ASC
            LIMIT %s
        """
        
        cur.execute(
            query,
            (
                db_team_abbr,
                db_team_abbr,
                db_team_abbr,
                db_team_abbr,
                db_team_abbr,
                db_team_abbr,
                db_team_abbr,
                db_team_abbr,
                season,
                limit,
            ),
        )
        games = cur.fetchall()

        for game in games:
            game['team'] = to_canonical_abbr(game['team'])
            game['opponent'] = to_canonical_abbr(game['opponent'])
        
        cur.close()
        conn.close()
        
        if not games:
            return jsonify({
                'success': False,
                'error': f'No games found for team {requested_team_abbr} in season {season}'
            }), 404
        
        return jsonify({
            'success': True,
            'count': len(games),
            'team': requested_team_abbr,
            'season': season,
            'games': games
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@hcl_bp.route('/teams/<team_abbr>/sos', methods=['GET'])
def get_team_strength_of_schedule(team_abbr):
    """
    Get weighted strength of schedule for a team in a season.

    SOS definition:
      - Played SOS: opponents' current-season win% excluding games vs the requested team.
      - Projected SOS: opponents' prior-season win% when current season has no completed team games.
      - Final SOS is weighted by times played/scheduled (division opponents count twice).
    """
    try:
        requested_team_abbr = to_canonical_abbr(team_abbr)
        db_team_abbr = to_hcl_abbr(requested_team_abbr)

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        season = resolve_request_season(cur)

        def get_opponent_counts(target_season, completed_only):
            completed_clause = ""
            if completed_only:
                completed_clause = """
                  AND g.home_score IS NOT NULL
                  AND g.away_score IS NOT NULL
                """

            cur.execute(
                f"""
                SELECT
                    CASE
                        WHEN g.home_team = %s THEN g.away_team
                        ELSE g.home_team
                    END AS opponent,
                    COUNT(*) AS played
                FROM hcl.games g
                WHERE g.season = %s
                  AND (g.home_team = %s OR g.away_team = %s)
                  {completed_clause}
                GROUP BY opponent
                """,
                (db_team_abbr, target_season, db_team_abbr, db_team_abbr),
            )
            return cur.fetchall() or []

        def get_opponent_record(target_season, opponent_abbr, exclude_team_abbr=None):
            exclusion_clause = ""
            params = [
                opponent_abbr,
                opponent_abbr,
                opponent_abbr,
                opponent_abbr,
                opponent_abbr,
                opponent_abbr,
                target_season,
                opponent_abbr,
                opponent_abbr,
            ]

            if exclude_team_abbr is not None:
                exclusion_clause = """
                  AND NOT (
                      (g.home_team = %s AND g.away_team = %s)
                      OR
                      (g.away_team = %s AND g.home_team = %s)
                  )
                """
                params.extend([
                    exclude_team_abbr,
                    opponent_abbr,
                    exclude_team_abbr,
                    opponent_abbr,
                ])

            cur.execute(
                f"""
                SELECT
                    SUM(
                        CASE
                            WHEN (g.home_team = %s AND g.home_score > g.away_score)
                              OR (g.away_team = %s AND g.away_score > g.home_score)
                            THEN 1 ELSE 0
                        END
                    ) AS wins,
                    SUM(
                        CASE
                            WHEN (g.home_team = %s AND g.home_score < g.away_score)
                              OR (g.away_team = %s AND g.away_score < g.home_score)
                            THEN 1 ELSE 0
                        END
                    ) AS losses,
                    SUM(
                        CASE
                            WHEN (g.home_team = %s OR g.away_team = %s)
                              AND g.home_score = g.away_score
                            THEN 1 ELSE 0
                        END
                    ) AS ties
                FROM hcl.games g
                WHERE g.season = %s
                  AND g.home_score IS NOT NULL
                  AND g.away_score IS NOT NULL
                  AND (g.home_team = %s OR g.away_team = %s)
                  {exclusion_clause}
                """,
                tuple(params),
            )

            row = cur.fetchone() or {}
            wins = int((row.get('wins') or 0))
            losses = int((row.get('losses') or 0))
            ties = int((row.get('ties') or 0))
            games_for_pct = wins + losses + ties
            win_pct = (wins + (0.5 * ties)) / games_for_pct if games_for_pct > 0 else None
            return wins, losses, ties, win_pct

        def build_weighted_sos(opponent_rows, record_season, exclude_self):
            weighted_win_pct_total = 0.0
            games_counted = 0
            weighted_wins = 0
            weighted_losses = 0
            skipped_opponents = []
            breakdown = []

            for row in opponent_rows:
                opponent = row.get('opponent')
                played = int(row.get('played') or 0)

                if not opponent or played <= 0:
                    continue

                wins, losses, ties, win_pct = get_opponent_record(
                    record_season,
                    opponent,
                    db_team_abbr if exclude_self else None,
                )

                canonical_opp = to_canonical_abbr(opponent)
                if win_pct is None:
                    skipped_opponents.append(canonical_opp)
                    breakdown.append({
                        'opponent': canonical_opp,
                        'win_pct': None,
                        'played': played,
                    })
                    continue

                weighted_win_pct_total += win_pct * played
                games_counted += played
                weighted_wins += wins * played
                weighted_losses += losses * played
                breakdown.append({
                    'opponent': canonical_opp,
                    'win_pct': round(win_pct, 3),
                    'played': played,
                })

            breakdown.sort(key=lambda item: (-item['played'], item['opponent']))
            sos_value = round(weighted_win_pct_total / games_counted, 3) if games_counted > 0 else None

            return {
                'sos': sos_value,
                'opponents_record': f'{weighted_wins}-{weighted_losses}',
                'games_counted': games_counted,
                'opponent_breakdown': breakdown,
                'skipped': sorted(set(skipped_opponents)),
            }

        completed_opponents = get_opponent_counts(season, completed_only=True)
        has_completed_games = len(completed_opponents) > 0

        sos_type = 'played' if has_completed_games else 'projected'
        based_on_season = season if has_completed_games else season - 1
        opponents = completed_opponents if has_completed_games else get_opponent_counts(season, completed_only=False)

        if not opponents:
            cur.close()
            conn.close()
            return jsonify({
                'success': True,
                'season': season,
                'team': requested_team_abbr,
                'sos_type': sos_type,
                'based_on_season': based_on_season,
                'sos': None,
                'opponents_record': '0-0',
                'games_counted': 0,
                'opponent_breakdown': [],
                'note': f'No opponents found for {requested_team_abbr} in {season}.'
            })

        sos_data = build_weighted_sos(
            opponents,
            based_on_season,
            exclude_self=has_completed_games,
        )

        payload = {
            'success': True,
            'season': season,
            'team': requested_team_abbr,
            'sos_type': sos_type,
            'based_on_season': based_on_season,
            'sos': sos_data['sos'],
            'opponents_record': sos_data['opponents_record'],
            'games_counted': sos_data['games_counted'],
            'opponent_breakdown': sos_data['opponent_breakdown'],
        }

        notes = []
        if sos_type == 'projected':
            notes.append(f"Based on opponents' {based_on_season} records (season not yet played).")

        if sos_data['skipped']:
            notes.append(
                f"Skipped opponents with missing {based_on_season} data: {', '.join(sos_data['skipped'])}."
            )

        if sos_data['sos'] is None:
            if sos_type == 'played':
                notes.append('SOS is not yet available because opponents have no non-head-to-head completed games.')
            else:
                notes.append('Projected SOS unavailable because prior-season records were not found for scheduled opponents.')

        if notes:
            payload['note'] = ' '.join(notes)

        cur.close()
        conn.close()
        return jsonify(payload)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@hcl_bp.route('/games/<game_id>', methods=['GET'])
def get_game_details(game_id):
    """
    Get complete game details including betting lines and weather
    
    Args:
        game_id: Game ID (format: YYYY_WW_AWAY_HOME)
    
    Returns:
        JSON with complete game info, team stats, betting lines, weather
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get game info with betting/weather
        query = """
            SELECT 
                g.game_id,
                g.season,
                g.week,
                g.game_date,
                g.home_team,
                g.away_team,
                g.home_score,
                g.away_score,
                g.stadium,
                -- Betting lines
                g.spread_line,
                g.total_line,
                g.home_moneyline,
                g.away_moneyline,
                g.home_spread_odds,
                g.away_spread_odds,
                g.over_odds,
                g.under_odds,
                -- Weather
                g.roof,
                g.surface,
                g.temp,
                g.wind,
                -- Context
                g.away_rest,
                g.home_rest,
                g.is_divisional_game,
                g.overtime,
                g.referee,
                g.away_coach,
                g.home_coach,
                g.away_qb_name,
                g.home_qb_name
            FROM hcl.games g
            WHERE g.game_id = %s
        """
        
        cur.execute(query, (game_id,))
        game = cur.fetchone()
        
        if not game:
            cur.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': f'Game {game_id} not found'
            }), 404
        
        # Get team stats for this game
        cur.execute("""
            SELECT 
                team,
                is_home,
                points,
                total_yards,
                passing_yards,
                rushing_yards,
                turnovers,
                ROUND(yards_per_play::numeric, 2) as yards_per_play,
                ROUND(completion_pct::numeric, 1) as completion_pct,
                ROUND(third_down_pct::numeric, 1) as third_down_pct,
                result
            FROM hcl.team_game_stats
            WHERE game_id = %s
            ORDER BY is_home DESC
        """, (game_id,))
        
        team_stats = cur.fetchall()

        game['home_team'] = to_canonical_abbr(game['home_team'])
        game['away_team'] = to_canonical_abbr(game['away_team'])
        for stat_row in team_stats:
            stat_row['team'] = to_canonical_abbr(stat_row['team'])
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'game': game,
            'team_stats': team_stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@hcl_bp.route('/games/week/<int:season>/<int:week>', methods=['GET'])
def get_week_games(season, week):
    """
    Get all games for a specific week with betting lines
    
    Args:
        season: Season year
        week: Week number
    
    Returns:
        JSON array of games with scores, betting lines, weather
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                game_id,
                season,
                week,
                game_date,
                away_team,
                home_team,
                away_score,
                home_score,
                spread_line,
                total_line,
                home_moneyline,
                away_moneyline,
                roof,
                temp,
                wind,
                is_divisional_game,
                referee
            FROM hcl.games
            WHERE season = %s AND week = %s
            ORDER BY game_date, game_id
        """
        
        cur.execute(query, (season, week))
        games = cur.fetchall()

        for game in games:
            game['home_team'] = to_canonical_abbr(game['home_team'])
            game['away_team'] = to_canonical_abbr(game['away_team'])
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'season': season,
            'week': week,
            'count': len(games),
            'games': games
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# FEATURE ENGINEERING VIEW ENDPOINTS
# ============================================================================

@hcl_bp.route('/analytics/betting', methods=['GET'])
def get_betting_performance():
    """
    Get team betting performance (ATS records, O/U trends)
    
    Query params:
        season: Filter by season (default: latest completed season)
        team: Filter by specific team (optional)
    
    Returns:
        JSON with ATS records, over/under performance, favorite/underdog splits
    """
    try:
        team = request.args.get('team', type=str)
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        season = resolve_request_season(cur)

        if not view_exists(cur, 'hcl.v_team_betting_performance'):
            cur.close()
            conn.close()
            fallback = analytics_view_unavailable_payload('hcl.v_team_betting_performance', season)
            fallback.update({
                'count': 0,
                'teams': []
            })
            return jsonify(fallback)
        
        query = """
            SELECT 
                team,
                season,
                total_games,
                ats_wins,
                ats_losses,
                ats_pushes,
                ats_win_pct,
                games_over,
                games_under,
                games_push,
                over_pct,
                games_as_favorite,
                wins_as_favorite,
                games_as_underdog,
                wins_as_underdog
            FROM hcl.v_team_betting_performance
            WHERE season = %s
        """
        
        params = [season]
        
        if team:
            query += " AND team = %s"
            params.append(to_hcl_abbr(team))
        
        query += " ORDER BY ats_win_pct DESC"
        
        cur.execute(query, params)
        results = cur.fetchall()

        for row in results:
            row['team'] = to_canonical_abbr(row['team'])
        
        cur.close()
        conn.close()
        
        if not results:
            return jsonify({
                'success': False,
                'error': f'No betting data found for season {season}'
            }), 404
        
        return jsonify({
            'success': True,
            'season': season,
            'count': len(results),
            'teams': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@hcl_bp.route('/analytics/weather', methods=['GET'])
def get_weather_impact():
    """
    Get weather impact on scoring and performance
    
    Query params:
        season: Filter by season (optional)
        roof: Filter by roof type (outdoors/dome/closed/open) (optional)
    
    Returns:
        JSON with scoring averages by weather conditions
    """
    try:
        season = request.args.get('season', type=int)
        roof = request.args.get('roof', type=str)
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        if not view_exists(cur, 'hcl.v_weather_impact_analysis'):
            cur.close()
            conn.close()
            fallback = analytics_view_unavailable_payload('hcl.v_weather_impact_analysis', season)
            fallback.update({
                'count': 0,
                'conditions': []
            })
            return jsonify(fallback)
        
        query = """
            SELECT 
                roof,
                surface,
                temp_range,
                wind_range,
                season,
                total_games,
                avg_total_points,
                avg_home_score,
                avg_away_score,
                avg_total_yards,
                avg_passing_yards,
                avg_rushing_yards,
                avg_completion_pct,
                avg_yards_per_play,
                highest_scoring_game,
                lowest_scoring_game,
                games_over,
                games_under,
                over_pct
            FROM hcl.v_weather_impact_analysis
            WHERE 1=1
        """
        
        params = []
        
        if season:
            query += " AND season = %s"
            params.append(season)
        
        if roof:
            query += " AND roof = %s"
            params.append(roof.lower())
        
        query += " ORDER BY avg_total_points DESC"
        
        cur.execute(query, params)
        results = cur.fetchall()
        
        cur.close()
        conn.close()
        
        if not results:
            return jsonify({
                'success': False,
                'error': 'No weather data found'
            }), 404
        
        return jsonify({
            'success': True,
            'count': len(results),
            'conditions': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@hcl_bp.route('/analytics/rest', methods=['GET'])
def get_rest_advantage():
    """
    Get team performance by days of rest
    
    Query params:
        season: Filter by season (default: latest completed season)
    
    Returns:
        JSON with win rates and performance by rest days
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        season = resolve_request_season(cur)

        if not view_exists(cur, 'hcl.v_rest_advantage'):
            cur.close()
            conn.close()
            fallback = analytics_view_unavailable_payload('hcl.v_rest_advantage', season)
            fallback.update({
                'count': 0,
                'rest_categories': []
            })
            return jsonify(fallback)
        
        query = """
            SELECT 
                rest_days,
                rest_category,
                season,
                total_games,
                wins,
                losses,
                ties,
                win_pct,
                avg_points_scored,
                avg_total_yards,
                avg_passing_yards,
                avg_rushing_yards,
                avg_turnovers,
                avg_yards_per_play,
                home_games,
                away_games,
                home_win_pct,
                away_win_pct
            FROM hcl.v_rest_advantage
            WHERE season = %s
            ORDER BY rest_days
        """
        
        cur.execute(query, (season,))
        results = cur.fetchall()
        
        cur.close()
        conn.close()
        
        if not results:
            return jsonify({
                'success': False,
                'error': f'No rest data found for season {season}'
            }), 404
        
        return jsonify({
            'success': True,
            'season': season,
            'count': len(results),
            'rest_categories': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@hcl_bp.route('/analytics/referees', methods=['GET'])
def get_referee_tendencies():
    """
    Get referee officiating patterns and tendencies
    
    Query params:
        season: Filter by season (default: latest completed season)
        referee: Filter by specific referee name (optional)
    
    Returns:
        JSON with referee stats, home bias, scoring averages
    """
    try:
        referee = request.args.get('referee', type=str)
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        season = resolve_request_season(cur)

        if not view_exists(cur, 'hcl.v_referee_tendencies'):
            cur.close()
            conn.close()
            fallback = analytics_view_unavailable_payload('hcl.v_referee_tendencies', season)
            fallback.update({
                'count': 0,
                'referees': []
            })
            return jsonify(fallback)
        
        query = """
            SELECT 
                referee,
                season,
                total_games,
                home_wins,
                away_wins,
                ties,
                home_win_pct,
                avg_total_points,
                avg_home_score,
                avg_away_score,
                avg_point_differential,
                highest_scoring_game,
                lowest_scoring_game,
                overtime_games,
                overtime_pct,
                avg_turnovers_per_game,
                divisional_games,
                games_over,
                games_under,
                over_pct
            FROM hcl.v_referee_tendencies
            WHERE season = %s
        """
        
        params = [season]
        
        if referee:
            query += " AND referee ILIKE %s"
            params.append(f"%{referee}%")
        
        query += " ORDER BY total_games DESC"
        
        cur.execute(query, params)
        results = cur.fetchall()
        
        cur.close()
        conn.close()
        
        if not results:
            return jsonify({
                'success': False,
                'error': f'No referee data found for season {season}'
            }), 404
        
        return jsonify({
            'success': True,
            'season': season,
            'count': len(results),
            'referees': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@hcl_bp.route('/analytics/summary', methods=['GET'])
def get_analytics_summary():
    """
    Get summary statistics from all analytical views
    
    Query params:
        season: Filter by season (default: latest completed season)
    
    Returns:
        JSON with key insights from betting, weather, rest, and referee data
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        season = resolve_request_season(cur)

        required_views = [
            'hcl.v_team_betting_performance',
            'hcl.v_weather_impact_analysis',
            'hcl.v_rest_advantage',
            'hcl.v_referee_tendencies'
        ]
        missing_views = [view for view in required_views if not view_exists(cur, view)]
        if missing_views:
            cur.close()
            conn.close()
            return jsonify({
                'success': True,
                'degraded': True,
                'season': season,
                'warning': 'One or more analytics views are unavailable in this environment',
                'missing_views': missing_views,
                'summary': {
                    'best_ats_team': None,
                    'weather_impact': [],
                    'best_rest_advantage': None,
                    'most_games_referee': None
                }
            })
        
        # Best ATS team
        cur.execute("""
            SELECT team, ats_wins, ats_losses, ats_win_pct
            FROM hcl.v_team_betting_performance
            WHERE season = %s
            ORDER BY ats_win_pct DESC
            LIMIT 1
        """, (season,))
        best_ats = cur.fetchone()
        if best_ats:
            best_ats['team'] = to_canonical_abbr(best_ats['team'])
        
        # Weather impact summary
        cur.execute("""
            SELECT roof, 
                   ROUND(AVG(avg_total_points)::numeric, 1) as avg_ppg,
                   COUNT(*) as conditions
            FROM hcl.v_weather_impact_analysis
            WHERE season = %s
            GROUP BY roof
            ORDER BY avg_ppg DESC
        """, (season,))
        weather_summary = cur.fetchall()
        
        # Rest advantage summary
        cur.execute("""
            SELECT rest_category,
                   SUM(total_games) as games,
                   ROUND(AVG(win_pct)::numeric, 1) as avg_win_pct
            FROM hcl.v_rest_advantage
            WHERE season = %s
            GROUP BY rest_category
            ORDER BY avg_win_pct DESC
            LIMIT 1
        """, (season,))
        best_rest = cur.fetchone()
        
        # Top referee
        cur.execute("""
            SELECT referee, total_games, home_win_pct
            FROM hcl.v_referee_tendencies
            WHERE season = %s
            ORDER BY total_games DESC
            LIMIT 1
        """, (season,))
        top_referee = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'season': season,
            'summary': {
                'best_ats_team': best_ats,
                'weather_impact': weather_summary,
                'best_rest_advantage': best_rest,
                'most_games_referee': top_referee
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
