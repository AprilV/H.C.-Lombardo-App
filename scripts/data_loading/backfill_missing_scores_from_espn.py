#!/usr/bin/env python3
"""Backfill missing final scores in hcl.games from ESPN scoreboard API."""

import argparse
import json
import os
import pathlib
import sys
from collections import defaultdict
from urllib.request import Request, urlopen

import psycopg2

ROOT_DIR = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from team_abbreviations import to_hcl_abbr


ESPN_SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"


def load_env_if_available():
    try:
        from dotenv import load_dotenv

        load_dotenv(".env")
    except ImportError:
        pass


def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "nfl_analytics"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
    )


def get_missing_games(cur, season):
    cur.execute(
        """
        SELECT game_id, week, home_team, away_team
        FROM hcl.games
        WHERE season = %s
          AND (home_score IS NULL OR away_score IS NULL)
        ORDER BY week, game_id
        """,
        (season,),
    )
    return cur.fetchall()


def fetch_week_scoreboard(season, week):
    url = f"{ESPN_SCOREBOARD_URL}?dates={season}&seasontype=2&week={week}"
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def parse_completed_games(scoreboard_data):
    parsed = {}
    for event in scoreboard_data.get("events", []):
        competitions = event.get("competitions", [])
        if not competitions:
            continue

        comp = competitions[0]
        status = comp.get("status", {}).get("type", {})
        if not status.get("completed", False):
            continue

        home_team = None
        away_team = None
        home_score = None
        away_score = None

        for competitor in comp.get("competitors", []):
            team_abbr = competitor.get("team", {}).get("abbreviation")
            score_text = competitor.get("score")
            if team_abbr is None or score_text is None:
                continue
            if competitor.get("homeAway") == "home":
                home_team = to_hcl_abbr(team_abbr)
                home_score = int(score_text)
            elif competitor.get("homeAway") == "away":
                away_team = to_hcl_abbr(team_abbr)
                away_score = int(score_text)

        if home_team and away_team and home_score is not None and away_score is not None:
            parsed[(away_team, home_team)] = (away_score, home_score)

    return parsed


def resolve_default_season(cur):
    cur.execute(
        """
        SELECT COALESCE(MAX(season), EXTRACT(YEAR FROM NOW())::int)
        FROM hcl.games
        """
    )
    return cur.fetchone()[0]


def main():
    parser = argparse.ArgumentParser(description="Backfill missing scores from ESPN")
    parser.add_argument("--season", type=int, default=None, help="Season to backfill")
    parser.add_argument("--dry-run", action="store_true", help="Print planned updates only")
    args = parser.parse_args()

    load_env_if_available()
    conn = get_connection()
    cur = conn.cursor()

    season = args.season
    if season is None:
        season = resolve_default_season(cur)

    missing_games = get_missing_games(cur, season)
    if not missing_games:
        print(f"season={season}")
        print("missing_games_before=0")
        print("updates_applied=0")
        cur.close()
        conn.close()
        return

    missing_by_week = defaultdict(list)
    for game_id, week, home_team, away_team in missing_games:
        missing_by_week[week].append((game_id, away_team, home_team))

    updates = []
    unresolved = []

    for week in sorted(missing_by_week.keys()):
        scoreboard = fetch_week_scoreboard(season, week)
        completed_games = parse_completed_games(scoreboard)

        for game_id, away_team, home_team in missing_by_week[week]:
            key = (away_team, home_team)
            if key not in completed_games:
                unresolved.append((game_id, week, away_team, home_team))
                continue

            away_score, home_score = completed_games[key]
            updates.append((home_score, away_score, game_id, week, away_team, home_team))

    if not args.dry_run and updates:
        cur.executemany(
            """
            UPDATE hcl.games
            SET home_score = %s,
                away_score = %s,
                updated_at = NOW()
            WHERE game_id = %s
                            AND (home_score IS NULL OR away_score IS NULL)
            """,
            [(h, a, game_id) for h, a, game_id, _, _, _ in updates],
        )
        conn.commit()

    cur.execute(
        """
        SELECT COUNT(*)
        FROM hcl.games
        WHERE season = %s
          AND (home_score IS NULL OR away_score IS NULL)
        """,
        (season,),
    )
    missing_after = cur.fetchone()[0]

    print(f"season={season}")
    print(f"missing_games_before={len(missing_games)}")
    print(f"updates_matched={len(updates)}")
    print(f"updates_applied={0 if args.dry_run else len(updates)}")
    print(f"missing_games_after={missing_after}")

    if unresolved:
        print("unresolved_games=")
        for game_id, week, away_team, home_team in unresolved:
            print(f"  week={week} game_id={game_id} matchup={away_team}@{home_team}")

    if updates:
        print("sample_updates=")
        for home_score, away_score, game_id, week, away_team, home_team in updates[:10]:
            print(
                f"  week={week} game_id={game_id} matchup={away_team}@{home_team} "
                f"score={away_score}-{home_score}"
            )

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
