#!/usr/bin/env python3
"""
HC in Lombardo — MVP team-game loader (nflverse PBP -> Postgres)
- Pulls seasons you specify from nflverse/nflfastR parquet
- Aggregates to the 47 columns we agreed on
- UPSERTs into hcl.team_game_stats

Usage:
  pip install pandas pyarrow SQLAlchemy psycopg2-binary python-dotenv requests
  export DATABASE_URL=postgresql+psycopg2://USER:PASS@HOST:PORT/DB
  python hcl_ingest_team_game_mvp.py --seasons 2023 2024 2025

Author: Professional betting analytics implementation
Date: October 22, 2025
"""

import argparse
import io
import os
from typing import List

import pandas as pd
import numpy as np
import requests
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from dotenv import load_dotenv

NFLVERSE_PBP_URL = "https://github.com/nflverse/nflfastR-data/raw/master/data/play_by_play_{season}.parquet"

UPSERT_SQL = """
INSERT INTO hcl.team_game_stats (
  game_id, season, week, team_id, opponent_id, is_home,
  points_for, points_against,
  plays, yards_total, yards_pass, yards_rush, pass_attempts, rush_attempts,
  sacks, interceptions, fumbles_lost,
  epa_total, epa_per_play, success_plays, success_rate,
  drives, plays_per_drive, turnovers, penalty_yards, starting_field_pos_yds,
  rush_epa_per_play, pass_epa_per_play, early_down_success_rate,
  red_zone_trips, red_zone_td_rate, third_down_att, third_down_conv, fourth_down_att, fourth_down_conv,
  source_tag, updated_at
) VALUES (
  :game_id, :season, :week, :team_id, :opponent_id, :is_home,
  :points_for, :points_against,
  :plays, :yards_total, :yards_pass, :yards_rush, :pass_attempts, :rush_attempts,
  :sacks, :interceptions, :fumbles_lost,
  :epa_total, :epa_per_play, :success_plays, :success_rate,
  :drives, :plays_per_drive, :turnovers, :penalty_yards, :starting_field_pos_yds,
  :rush_epa_per_play, :pass_epa_per_play, :early_down_success_rate,
  :red_zone_trips, :red_zone_td_rate, :third_down_att, :third_down_conv, :fourth_down_att, :fourth_down_conv,
  'nflverse_pbp_mvp', NOW()
)
ON CONFLICT (game_id, team_id) DO UPDATE SET
  season               = EXCLUDED.season,
  week                 = EXCLUDED.week,
  opponent_id          = EXCLUDED.opponent_id,
  is_home              = EXCLUDED.is_home,
  points_for           = EXCLUDED.points_for,
  points_against       = EXCLUDED.points_against,
  plays                = EXCLUDED.plays,
  yards_total          = EXCLUDED.yards_total,
  yards_pass           = EXCLUDED.yards_pass,
  yards_rush           = EXCLUDED.yards_rush,
  pass_attempts        = EXCLUDED.pass_attempts,
  rush_attempts        = EXCLUDED.rush_attempts,
  sacks                = EXCLUDED.sacks,
  interceptions        = EXCLUDED.interceptions,
  fumbles_lost         = EXCLUDED.fumbles_lost,
  epa_total            = EXCLUDED.epa_total,
  epa_per_play         = EXCLUDED.epa_per_play,
  success_plays        = EXCLUDED.success_plays,
  success_rate         = EXCLUDED.success_rate,
  drives               = EXCLUDED.drives,
  plays_per_drive      = EXCLUDED.plays_per_drive,
  turnovers            = EXCLUDED.turnovers,
  penalty_yards        = EXCLUDED.penalty_yards,
  starting_field_pos_yds = EXCLUDED.starting_field_pos_yds,
  rush_epa_per_play    = EXCLUDED.rush_epa_per_play,
  pass_epa_per_play    = EXCLUDED.pass_epa_per_play,
  early_down_success_rate = EXCLUDED.early_down_success_rate,
  red_zone_trips       = EXCLUDED.red_zone_trips,
  red_zone_td_rate     = EXCLUDED.red_zone_td_rate,
  third_down_att       = EXCLUDED.third_down_att,
  third_down_conv      = EXCLUDED.third_down_conv,
  fourth_down_att      = EXCLUDED.fourth_down_att,
  fourth_down_conv     = EXCLUDED.fourth_down_conv,
  source_tag           = EXCLUDED.source_tag,
  updated_at           = NOW();
"""

def get_engine() -> Engine:
    """Get SQLAlchemy engine from DATABASE_URL environment variable."""
    load_dotenv()
    url = os.getenv("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL not set")
    return create_engine(url, pool_pre_ping=True)

def download_parquet(url: str) -> pd.DataFrame:
    """Download parquet file directly from nflverse GitHub."""
    r = requests.get(url, timeout=180)
    r.raise_for_status()
    return pd.read_parquet(io.BytesIO(r.content), engine="pyarrow")

def ensure_cols(df: pd.DataFrame, cols_defaults: dict):
    """Ensure columns exist with default values if missing."""
    for c, d in cols_defaults.items():
        if c not in df.columns:
            df[c] = d

def aggregate_team_game(pbp: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate play-by-play data to team-game level with all 47 MVP columns.
    
    Handles missing columns across different nflverse seasons gracefully.
    """
    # Use only offensive snaps with a defined posteam
    df = pbp.loc[pbp["posteam"].notna()].copy()

    # Soft-fills for expected columns across seasons
    ensure_cols(df, {
        "yards_gained": 0, "epa": 0.0, "success": 0,
        "rush_attempt": 0, "pass_attempt": 0,
        "sack": 0, "interception": 0, "fumble_lost": 0,
        "penalty": 0, "penalty_yards": 0,
        "down": np.nan, "yardline_100": np.nan,
        "third_down_converted": 0, "fourth_down_converted": 0,
        "third_down_attempt": 0,  # not always present
        "touchdown": 0,
        "drive": -1, "first_down": 0
    })

    # Volume splits
    df["rush_yards"] = np.where(df["rush_attempt"] == 1, df["yards_gained"], 0)
    df["pass_yards"] = np.where(df["pass_attempt"] == 1, df["yards_gained"], 0)

    # Third/Fourth down attempts (if no explicit flags, infer from 'down')
    missing_tda = "third_down_attempt" not in df or df["third_down_attempt"].isna().all()
    if missing_tda:
        df["third_down_attempt"] = (df["down"] == 3).astype(int)
    third_conv = np.where(df.get("third_down_converted", 0) == 1,
                          1,
                          np.where((df["down"] == 3) & (df["first_down"] == 1), 1, 0))
    fourth_conv = np.where(df.get("fourth_down_converted", 0) == 1,
                           1,
                           np.where((df["down"] == 4) & (df["first_down"] == 1), 1, 0))

    # Drives and starting field position (first play of each (game, posteam, drive))
    drv = df.sort_values(["game_id", "posteam", "drive", "play_id"]).copy()
    first_play_mask = drv.groupby(["game_id", "posteam", "drive"], dropna=False)["play_id"].transform("min") == drv["play_id"]
    drv_starts = drv.loc[first_play_mask, ["game_id", "posteam", "drive", "yardline_100"]].rename(
        columns={"posteam": "team_id"})
    avg_start = drv_starts.groupby(["game_id", "team_id"], dropna=False)["yardline_100"].mean().reset_index()
    avg_start = avg_start.rename(columns={"yardline_100": "starting_field_pos_yds"})

    # Red zone: any snap on a drive with yardline_100 <= 20
    drv["in_rz"] = (drv["yardline_100"] <= 20).astype(int)
    rz_drv = (
        drv.groupby(["game_id", "posteam", "drive"], dropna=False)["in_rz"].max().reset_index()
    )
    rz_drv["rz_trip"] = (rz_drv["in_rz"] == 1).astype(int)
    # TD on drive if any touchdown on that drive for posteam
    td_drv = (
        drv.groupby(["game_id", "posteam", "drive"], dropna=False)["touchdown"].max().reset_index()
    )
    rz_merged = rz_drv.merge(td_drv, on=["game_id", "posteam", "drive"], how="left")
    rz_team = (
        rz_merged.groupby(["game_id", "posteam"], dropna=False)
        .agg(red_zone_trips=("rz_trip", "sum"),
             red_zone_td=("touchdown", "sum"))
        .reset_index()
        .rename(columns={"posteam": "team_id"})
    )
    rz_team["red_zone_td_rate"] = np.where(rz_team["red_zone_trips"] > 0,
                                           rz_team["red_zone_td"] / rz_team["red_zone_trips"],
                                           0.0)

    # Base team-game aggregate (offense only)
    team = (
        df.groupby(["game_id", "season", "week", "posteam"], dropna=False)
          .agg(
              plays=("play_id", "count"),
              yards_total=("yards_gained", "sum"),
              yards_pass=("pass_yards", "sum"),
              yards_rush=("rush_yards", "sum"),
              pass_attempts=("pass_attempt", "sum"),
              rush_attempts=("rush_attempt", "sum"),
              sacks=("sack", "sum"),
              interceptions=("interception", "sum"),
              fumbles_lost=("fumble_lost", "sum"),
              success_plays=("success", "sum"),
              epa_total=("epa", "sum"),
              epa_per_play=("epa", "mean"),
              third_down_att=("third_down_attempt", "sum"),
              third_down_conv=(pd.Series(third_conv), "sum"),
              fourth_down_att=(lambda x: np.sum(df.loc[x.index, "down"] == 4)),
              fourth_down_conv=(pd.Series(fourth_conv), "sum"),
              penalty_yards=("penalty_yards", "sum"),
          )
          .reset_index()
          .rename(columns={"posteam": "team_id"})
    )

    # Drives per team-game (count distinct drive ids)
    drives = (df.groupby(["game_id", "posteam"], dropna=False)["drive"]
                .nunique()
                .reset_index()
                .rename(columns={"posteam": "team_id", "drive": "drives"}))
    team = team.merge(drives, on=["game_id", "team_id"], how="left")
    team["plays_per_drive"] = team["plays"] / team["drives"].replace({0: np.nan})

    # Rush/Pass EPA per play
    rush = (df[df["rush_attempt"] == 1]
            .groupby(["game_id", "posteam"], dropna=False)["epa"].mean()
            .reset_index()
            .rename(columns={"posteam": "team_id", "epa": "rush_epa_per_play"}))
    pas = (df[df["pass_attempt"] == 1]
           .groupby(["game_id", "posteam"], dropna=False)["epa"].mean()
           .reset_index()
           .rename(columns={"posteam": "team_id", "epa": "pass_epa_per_play"}))
    team = team.merge(rush, on=["game_id", "team_id"], how="left") \
               .merge(pas,  on=["game_id", "team_id"], how="left")

    # Early-down success rate (downs 1 or 2)
    ed = df[df["down"].isin([1, 2])]
    ed_sr = (ed.groupby(["game_id", "posteam"], dropna=False)
                .agg(eds_success=("success", "sum"),
                     eds_plays=("success", "count"))
                .reset_index()
                .rename(columns={"posteam": "team_id"}))
    ed_sr["early_down_success_rate"] = np.where(ed_sr["eds_plays"] > 0,
                                                ed_sr["eds_success"] / ed_sr["eds_plays"],
                                                0.0)
    team = team.merge(ed_sr[["game_id", "team_id", "early_down_success_rate"]],
                      on=["game_id", "team_id"], how="left")

    # Turnovers
    team["turnovers"] = team["interceptions"] + team["fumbles_lost"]

    # Add red-zone and avg starting field position
    team = team.merge(rz_team[["game_id", "team_id", "red_zone_trips", "red_zone_td_rate"]],
                      on=["game_id", "team_id"], how="left")
    team = team.merge(avg_start, on=["game_id", "team_id"], how="left")

    # Scores + opponent_id using max running scores
    score_cols = ["posteam_score", "defteam_score", "defteam"]
    for c in score_cols:
        if c not in df.columns:
            df[c] = np.nan

    scores = (df.groupby(["game_id", "season", "week", "posteam", "defteam"], dropna=False)
                .agg(pf=("posteam_score", "max"),
                     pa=("defteam_score", "max"))
                .reset_index()
                .rename(columns={"posteam": "team_id", "defteam": "opponent_id"}))

    team = team.merge(scores[["game_id", "season", "week", "team_id", "opponent_id", "pf", "pa"]],
                      on=["game_id", "team_id"], how="left")
    team = team.rename(columns={"pf": "points_for", "pa": "points_against"})

    # Clean types
    int_cols = [
        "week","plays","yards_total","yards_pass","yards_rush","pass_attempts",
        "rush_attempts","sacks","interceptions","fumbles_lost","success_plays",
        "drives","red_zone_trips","third_down_att","third_down_conv","fourth_down_att","fourth_down_conv",
        "points_for","points_against","penalty_yards","turnovers"
    ]
    for c in int_cols:
        team[c] = team[c].fillna(0).astype(int)

    # Rates and floats
    for c in ["epa_total","epa_per_play","plays_per_drive","rush_epa_per_play","pass_epa_per_play",
              "early_down_success_rate","red_zone_td_rate","starting_field_pos_yds"]:
        team[c] = team[c].astype(float)

    # Success rate overall
    team["success_rate"] = np.where(team["plays"] > 0,
                                    team["success_plays"] / team["plays"],
                                    0.0)

    # Final select / order
    keep = [
        "game_id","season","week","team_id","opponent_id",
        "points_for","points_against",
        "plays","yards_total","yards_pass","yards_rush","pass_attempts","rush_attempts",
        "sacks","interceptions","fumbles_lost",
        "epa_total","epa_per_play","success_plays","success_rate",
        "drives","plays_per_drive","turnovers","penalty_yards","starting_field_pos_yds",
        "rush_epa_per_play","pass_epa_per_play","early_down_success_rate",
        "red_zone_trips","red_zone_td_rate","third_down_att","third_down_conv","fourth_down_att","fourth_down_conv"
    ]
    team = team[keep].copy()

    return team

def attach_home_flag(team_df: pd.DataFrame, engine: Engine) -> pd.DataFrame:
    """
    Join to games table to determine is_home flag.
    Ensures season/week alignment is accurate.
    """
    with engine.begin() as cxn:
        g = pd.read_sql(text("SELECT game_id, home_team, away_team FROM hcl.games"), cxn)
    team_df = team_df.merge(g, on="game_id", how="left")
    team_df["is_home"] = (team_df["team_id"] == team_df["home_team"]).astype(bool)
    team_df.drop(columns=["home_team","away_team"], inplace=True)
    return team_df

def upsert(engine: Engine, df: pd.DataFrame):
    """UPSERT team-game stats into PostgreSQL."""
    rows = df.to_dict(orient="records")
    if not rows:
        return
    with engine.begin() as cxn:
        cxn.execute(text(UPSERT_SQL), rows)

def process_season(engine: Engine, season: int):
    """Download, aggregate, and upsert one season of data."""
    url = NFLVERSE_PBP_URL.format(season=season)
    print(f"[{season}] download {url}")
    pbp = download_parquet(url)
    
    # nflverse season/week are present; ensure ints
    pbp["season"] = pbp["season"].astype(int)
    pbp["week"] = pbp["week"].fillna(0).astype(int)

    team = aggregate_team_game(pbp)
    team = attach_home_flag(team, engine)

    # Basic sanity: drop rows without opponent_id
    team = team[team["opponent_id"].notna()].copy()

    print(f"[{season}] upserting {len(team):,} team-game rows")
    upsert(engine, team)

def main(seasons: List[int]):
    """Main entry point - process all seasons."""
    engine = get_engine()
    for s in seasons:
        process_season(engine, int(s))
    
    # Optional: refresh your rolling MV if you're using it
    with engine.begin() as cxn:
        try:
            cxn.execute(text("SELECT hcl.refresh_hcl_materialized();"))
        except Exception as e:
            print("Refresh materialized view skipped:", e)
    
    print("Done.")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seasons", nargs="+", required=True, 
                    help="Seasons to load, e.g. 2023 2024 2025")
    args = ap.parse_args()
    main([int(x) for x in args.seasons])
