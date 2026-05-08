"""Rebuild Elo ratings through a target season and emit evidence summary."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ML_DIR = PROJECT_ROOT / "ml"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(ML_DIR) not in sys.path:
    sys.path.insert(0, str(ML_DIR))

from elo_tracker import EloTracker  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="TA-020 Elo rebuild runner")
    parser.add_argument("--start-season", type=int, default=1999)
    parser.add_argument("--end-season", type=int, default=2025)
    parser.add_argument(
        "--ratings-out",
        default=str(PROJECT_ROOT / "ml" / "models" / "elo_ratings_current.json"),
    )
    parser.add_argument("--summary-out", required=False)
    parser.add_argument("--top-n", type=int, default=5)
    args = parser.parse_args()

    tracker = EloTracker()
    tracker.initialize_all_teams()

    games_df = tracker.load_historical_games(
        start_season=args.start_season,
        end_season=args.end_season,
    )

    tracker.process_historical_games(games_df)
    tracker.save_current_ratings(filepath=args.ratings_out)

    ratings = tracker.elo.get_all_ratings()
    sorted_ratings = sorted(ratings.items(), key=lambda item: item[1], reverse=True)
    top_n = [
        {"rank": idx + 1, "team": team, "elo": round(score, 1)}
        for idx, (team, score) in enumerate(sorted_ratings[: args.top_n])
    ]

    summary = {
        "task": "TA-020",
        "subtask": "s20_1",
        "start_season": args.start_season,
        "end_season": args.end_season,
        "games_loaded": int(len(games_df)),
        "season_min": int(games_df["season"].min()) if len(games_df) else None,
        "season_max": int(games_df["season"].max()) if len(games_df) else None,
        "ratings_count": len(ratings),
        "ratings_output": str(Path(args.ratings_out)),
        "top_teams": top_n,
    }

    print(f"games_loaded={summary['games_loaded']}")
    print(f"season_min={summary['season_min']}")
    print(f"season_max={summary['season_max']}")
    print(f"ratings_count={summary['ratings_count']}")
    print(f"ratings_output={summary['ratings_output']}")

    if args.summary_out:
        summary_path = Path(args.summary_out)
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(f"summary_out={summary_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
