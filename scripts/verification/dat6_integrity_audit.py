#!/usr/bin/env python3
"""DAT-6 integrity audit for season-level data completeness and consistency."""

import argparse
import os
import pathlib
import sys
from datetime import datetime, UTC

import psycopg2


ROOT_DIR = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
  sys.path.insert(0, str(ROOT_DIR))

from team_abbreviations import sql_to_canonical_case


def load_env_if_available():
    try:
        from dotenv import load_dotenv
        load_dotenv('.env')
    except ImportError:
        pass


def get_connection():
    return psycopg2.connect(
        dbname=os.getenv('DB_NAME', 'nfl_analytics'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', ''),
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
    )


def resolve_default_season(cur):
    cur.execute(
        """
        SELECT COALESCE(MAX(season), EXTRACT(YEAR FROM NOW())::int)
        FROM hcl.games
        """
    )
    return cur.fetchone()[0]


def query_single(cur, sql, params=()):
    cur.execute(sql, params)
    return cur.fetchone()[0]


def main():
    parser = argparse.ArgumentParser(description='Run DAT-6 integrity audit')
    parser.add_argument('--season', type=int, default=None, help='Season to audit')
    args = parser.parse_args()

    load_env_if_available()

    conn = get_connection()
    cur = conn.cursor()

    season = args.season
    if season is None:
        season = resolve_default_season(cur)

    cur.execute('SELECT current_database()')
    db_name = cur.fetchone()[0]

    cur.execute(
        """
        SELECT
          COUNT(*) AS total_games,
          COUNT(*) FILTER (WHERE home_score IS NOT NULL AND away_score IS NOT NULL) AS completed_games,
          COUNT(*) FILTER (WHERE home_score IS NULL OR away_score IS NULL) AS missing_score_games,
          COUNT(*) FILTER (WHERE COALESCE(is_postseason, FALSE) = TRUE) AS postseason_games
        FROM hcl.games
        WHERE season = %s
        """,
        (season,),
    )
    total_games, completed_games, missing_score_games_count, postseason_games = cur.fetchone()

    tgs_total = query_single(
        cur,
        'SELECT COUNT(*) FROM hcl.team_game_stats WHERE season = %s',
        (season,),
    )

    tgs_epa_null = query_single(
        cur,
        """
        SELECT COUNT(*)
        FROM hcl.team_game_stats
        WHERE season = %s
          AND epa_per_play IS NULL
        """,
        (season,),
    )

    tgs_epa_null_completed = query_single(
        cur,
        """
        SELECT COUNT(*)
        FROM hcl.team_game_stats
        WHERE season = %s
          AND epa_per_play IS NULL
          AND game_id IN (
            SELECT game_id
            FROM hcl.games
            WHERE season = %s
              AND home_score IS NOT NULL
              AND away_score IS NOT NULL
          )
        """,
        (season, season),
    )

    cur.execute(
        """
        WITH teams_in_games AS (
          SELECT DISTINCT home_team AS team FROM hcl.games WHERE season = %s
          UNION
          SELECT DISTINCT away_team AS team FROM hcl.games WHERE season = %s
        )
        SELECT ARRAY_AGG(g.team ORDER BY g.team)
        FROM teams_in_games g
        LEFT JOIN public.teams t ON t.abbreviation = g.team
        WHERE t.abbreviation IS NULL
        """,
        (season, season),
    )
    games_teams_missing_in_public_raw = cur.fetchone()[0] or []

    cur.execute(
        """
        WITH teams_in_games AS (
          SELECT DISTINCT home_team AS team FROM hcl.games WHERE season = %s
          UNION
          SELECT DISTINCT away_team AS team FROM hcl.games WHERE season = %s
        )
        SELECT ARRAY_AGG(t.abbreviation ORDER BY t.abbreviation)
        FROM public.teams t
        LEFT JOIN teams_in_games g ON g.team = t.abbreviation
        WHERE g.team IS NULL
        """,
        (season, season),
    )
    public_teams_missing_in_games_raw = cur.fetchone()[0] or []

    game_home_team_canonical_sql = sql_to_canonical_case('home_team')
    game_away_team_canonical_sql = sql_to_canonical_case('away_team')
    public_team_canonical_sql = sql_to_canonical_case('abbreviation')

    cur.execute(
        f"""
        WITH teams_in_games AS (
          SELECT DISTINCT {game_home_team_canonical_sql} AS team FROM hcl.games WHERE season = %s
          UNION
          SELECT DISTINCT {game_away_team_canonical_sql} AS team FROM hcl.games WHERE season = %s
        ), teams_in_public AS (
          SELECT DISTINCT {public_team_canonical_sql} AS team
          FROM public.teams
        )
        SELECT ARRAY_AGG(g.team ORDER BY g.team)
        FROM teams_in_games g
        LEFT JOIN teams_in_public p ON p.team = g.team
        WHERE p.team IS NULL
        """,
        (season, season),
    )
    games_teams_missing_in_public_canonical = cur.fetchone()[0] or []

    cur.execute(
        f"""
        WITH teams_in_games AS (
          SELECT DISTINCT {game_home_team_canonical_sql} AS team FROM hcl.games WHERE season = %s
          UNION
          SELECT DISTINCT {game_away_team_canonical_sql} AS team FROM hcl.games WHERE season = %s
        ), teams_in_public AS (
          SELECT DISTINCT {public_team_canonical_sql} AS team
          FROM public.teams
        )
        SELECT ARRAY_AGG(p.team ORDER BY p.team)
        FROM teams_in_public p
        LEFT JOIN teams_in_games g ON g.team = p.team
        WHERE g.team IS NULL
        """,
        (season, season),
    )
    public_teams_missing_in_games_canonical = cur.fetchone()[0] or []

    expected_tgs_completed = completed_games * 2
    actual_tgs_completed = query_single(
        cur,
        """
        SELECT COUNT(*)
        FROM hcl.team_game_stats
        WHERE season = %s
          AND game_id IN (
            SELECT game_id
            FROM hcl.games
            WHERE season = %s
              AND home_score IS NOT NULL
              AND away_score IS NOT NULL
          )
        """,
        (season, season),
    )

    cur.execute(
        """
        WITH completed_games AS (
          SELECT game_id
          FROM hcl.games
          WHERE season = %s
            AND home_score IS NOT NULL
            AND away_score IS NOT NULL
        ), counts AS (
          SELECT cg.game_id, COUNT(tgs.game_id) AS c
          FROM completed_games cg
          LEFT JOIN hcl.team_game_stats tgs
            ON tgs.game_id = cg.game_id
           AND tgs.season = %s
          GROUP BY cg.game_id
        )
        SELECT game_id, c
        FROM counts
        WHERE c <> 2
        ORDER BY game_id
        """,
        (season, season),
    )
    completed_games_with_tgs_gap = cur.fetchall()

    cur.execute(
        """
        SELECT week,
               COUNT(*) AS total,
               COUNT(*) FILTER (WHERE home_score IS NOT NULL AND away_score IS NOT NULL) AS completed,
               COUNT(*) FILTER (WHERE home_score IS NULL OR away_score IS NULL) AS missing
        FROM hcl.games
        WHERE season = %s
        GROUP BY week
        ORDER BY week
        """,
        (season,),
    )
    weekly_coverage = cur.fetchall()

    cur.execute(
        """
        SELECT week, game_id, game_date, away_team, home_team
        FROM hcl.games
        WHERE season = %s
          AND (home_score IS NULL OR away_score IS NULL)
        ORDER BY week, game_date, game_id
        """,
        (season,),
    )
    missing_score_games_rows = cur.fetchall()

    cur.close()
    conn.close()

    print('=== DAT-6 INTEGRITY AUDIT ===')
    print(f'timestamp={datetime.now(UTC).isoformat()}')
    print(f'database={db_name}')
    print(f'season={season}')
    print(f'games_total={total_games}')
    print(f'games_completed={completed_games}')
    print(f'games_missing_scores={missing_score_games_count}')
    print(f'games_postseason={postseason_games}')
    print(f'team_game_stats_total={tgs_total}')
    print(f'team_game_stats_epa_null={tgs_epa_null}')
    print(f'team_game_stats_epa_null_for_completed_games={tgs_epa_null_completed}')
    print(f'team_game_stats_expected_for_completed={expected_tgs_completed}')
    print(f'team_game_stats_actual_for_completed={actual_tgs_completed}')
    print(f'team_game_stats_missing_for_completed={expected_tgs_completed - actual_tgs_completed}')
    print('games_teams_missing_in_public_raw=' + ','.join(games_teams_missing_in_public_raw))
    print('public_teams_missing_in_games_raw=' + ','.join(public_teams_missing_in_games_raw))
    print('games_teams_missing_in_public_canonical=' + ','.join(games_teams_missing_in_public_canonical))
    print('public_teams_missing_in_games_canonical=' + ','.join(public_teams_missing_in_games_canonical))
    print('completed_games_with_tgs_gap=')
    for game_id, count_rows in completed_games_with_tgs_gap:
        print(f'  {game_id}: {count_rows}')
    print('weekly_coverage=')
    for week, total, completed, missing in weekly_coverage:
        print(f'  week={week} total={total} completed={completed} missing={missing}')
    print('missing_score_games=')
    for week, game_id, game_date, away, home in missing_score_games_rows:
        print(f'  week={week} game_id={game_id} date={game_date} away={away} home={home}')


if __name__ == '__main__':
    main()
