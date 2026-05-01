#!/usr/bin/env python3
"""Sync public.teams standings fields from scored games in hcl.games."""

import argparse
import os
import pathlib
import sys
import psycopg2


ROOT_DIR = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
  sys.path.insert(0, str(ROOT_DIR))

from team_abbreviations import sql_to_canonical_case


def load_env_if_available():
    """Load .env when python-dotenv is installed."""
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
        port=os.getenv('DB_PORT', '5432')
    )


def resolve_default_season(cur):
    cur.execute(
        """
        SELECT COALESCE(MAX(season), EXTRACT(YEAR FROM NOW())::int)
        FROM hcl.games
        WHERE home_score IS NOT NULL
          AND away_score IS NOT NULL
        """
    )
    return cur.fetchone()[0]


def sync_standings(cur, season, include_postseason=False):
    home_team_canonical_sql = sql_to_canonical_case('home_team')
    away_team_canonical_sql = sql_to_canonical_case('away_team')

    update_sql = f"""
    WITH normalized_games AS (
      SELECT
        {home_team_canonical_sql} AS team,
        home_score::numeric AS pf,
        away_score::numeric AS pa,
        CASE
          WHEN home_score > away_score THEN 1
          WHEN home_score = away_score THEN 0
          ELSE -1
        END AS outcome
      FROM hcl.games
      WHERE season = %s
        AND home_score IS NOT NULL
        AND away_score IS NOT NULL
        AND (%s OR COALESCE(is_postseason, FALSE) = FALSE)

      UNION ALL

      SELECT
        {away_team_canonical_sql} AS team,
        away_score::numeric AS pf,
        home_score::numeric AS pa,
        CASE
          WHEN away_score > home_score THEN 1
          WHEN away_score = home_score THEN 0
          ELSE -1
        END AS outcome
      FROM hcl.games
      WHERE season = %s
        AND home_score IS NOT NULL
        AND away_score IS NOT NULL
        AND (%s OR COALESCE(is_postseason, FALSE) = FALSE)
    ), agg AS (
      SELECT
        team,
        COUNT(*)::int AS games_played,
        SUM(CASE WHEN outcome = 1 THEN 1 ELSE 0 END)::int AS wins,
        SUM(CASE WHEN outcome = -1 THEN 1 ELSE 0 END)::int AS losses,
        SUM(CASE WHEN outcome = 0 THEN 1 ELSE 0 END)::int AS ties,
        ROUND(AVG(pf)::numeric, 2)::real AS ppg,
        ROUND(AVG(pa)::numeric, 2)::real AS pa
      FROM normalized_games
      GROUP BY team
    )
    UPDATE public.teams t
    SET
      wins = a.wins,
      losses = a.losses,
      ties = a.ties,
      games_played = a.games_played,
      ppg = a.ppg,
      pa = a.pa,
      last_updated = NOW(),
      stats = COALESCE(t.stats, '{{}}'::jsonb) || jsonb_build_object(
        'source', 'hcl.games',
        'season', %s,
        'regular_season_only', %s,
        'note', 'Derived from completed scored games only'
      )
    FROM agg a
    WHERE t.abbreviation = a.team
    """

    cur.execute(
        update_sql,
        (
            season,
            include_postseason,
            season,
            include_postseason,
            season,
            not include_postseason,
        ),
    )
    return cur.rowcount


def print_summary(cur):
    cur.execute("SELECT COUNT(*) FROM public.teams")
    team_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM public.teams WHERE wins IS NOT NULL")
    with_wins = cur.fetchone()[0]

    cur.execute(
        """
        SELECT abbreviation, wins, losses, ties, games_played, ppg, pa
        FROM public.teams
        ORDER BY wins DESC, ppg DESC
        LIMIT 10
        """
    )
    top_rows = cur.fetchall()

    print(f"teams_total={team_count}")
    print(f"teams_with_wins={with_wins}")
    print("top_10_standings=")
    for row in top_rows:
        print(row)


def main():
    parser = argparse.ArgumentParser(
        description="Update public.teams standings from hcl.games scored results"
    )
    parser.add_argument(
        '--season',
        type=int,
        default=None,
        help='Season to process (default: latest completed season)'
    )
    parser.add_argument(
        '--include-postseason',
        action='store_true',
        help='Include postseason games (default: regular season only)'
    )
    args = parser.parse_args()

    load_env_if_available()

    conn = get_connection()
    cur = conn.cursor()

    season = args.season
    if season is None:
        season = resolve_default_season(cur)

    print(f"season={season}")
    print(f"include_postseason={args.include_postseason}")

    updated = sync_standings(cur, season, include_postseason=args.include_postseason)
    print(f"rows_updated={updated}")

    conn.commit()
    print_summary(cur)

    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
