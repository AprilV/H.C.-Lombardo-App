"""
NFL Elo Rating Tracker

Maintains Elo ratings across all historical games and seasons.
Builds a complete rating history for all teams.

Usage:
    python ml/elo_tracker.py --rebuild     # Rebuild from historical data
    python ml/elo_tracker.py --current     # Show current ratings

Sprint 10: Elo System Implementation
Date: December 19, 2025
"""

import psycopg2
import pandas as pd
import numpy as np
import os
import json
import argparse
from datetime import datetime
from dotenv import load_dotenv
from elo_ratings import EloRatingSystem

load_dotenv()

class EloTracker:
    """Track and maintain Elo ratings across all NFL games"""
    
    # NFL team abbreviations (standardized)
    NFL_TEAMS = [
        'ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE',
        'DAL', 'DEN', 'DET', 'GB', 'HOU', 'IND', 'JAX', 'KC',
        'LAC', 'LAR', 'LV', 'MIA', 'MIN', 'NE', 'NO', 'NYG',
        'NYJ', 'PHI', 'PIT', 'SEA', 'SF', 'TB', 'TEN', 'WAS'
    ]
    
    # Team abbreviation mapping (handle variations)
    TEAM_MAPPING = {
        'LA': 'LAR',      # LA Rams
        'OAK': 'LV',      # Oakland -> Las Vegas
        'SD': 'LAC',      # San Diego -> LA Chargers
        'STL': 'LAR',     # St. Louis -> LA Rams
    }
    
    def __init__(self):
        self.db_config = {
            'dbname': os.getenv('DB_NAME', 'nfl_analytics'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', ''),
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432')
        }
        
        self.elo = EloRatingSystem()
        self.ratings_by_date = {}  # Store ratings at each date
        
    def normalize_team(self, team: str) -> str:
        """Normalize team abbreviation"""
        team = team.upper().strip()
        return self.TEAM_MAPPING.get(team, team)
    
    def initialize_all_teams(self):
        """Initialize Elo ratings for all NFL teams"""
        for team in self.NFL_TEAMS:
            self.elo.initialize_team(team)
        print(f"✅ Initialized {len(self.NFL_TEAMS)} NFL teams at Elo {self.elo.base_elo}")
    
    def load_historical_games(self, start_season: int = 2002, end_season: int = 2024):
        """
        Load all historical games from database
        
        Args:
            start_season: First season to include
            end_season: Last season to include
        
        Returns:
            DataFrame of games sorted by date
        """
        print(f"\n📊 Loading historical games ({start_season}-{end_season})...")
        
        conn = psycopg2.connect(**self.db_config)
        
        query = """
        SELECT 
            game_id,
            season,
            week,
            game_date,
            home_team,
            away_team,
            home_score,
            away_score
        FROM hcl.games
        WHERE season >= %s 
          AND season <= %s
          AND home_score IS NOT NULL
          AND away_score IS NOT NULL
        ORDER BY game_date, game_id
        """
        
        df = pd.read_sql(query, conn, params=(start_season, end_season))
        conn.close()
        
        # Normalize team names
        df['home_team'] = df['home_team'].apply(self.normalize_team)
        df['away_team'] = df['away_team'].apply(self.normalize_team)
        
        print(f"✅ Loaded {len(df)} games")
        return df
    
    def process_historical_games(self, games_df: pd.DataFrame):
        """
        Process all historical games to build Elo ratings
        
        Args:
            games_df: DataFrame of games sorted by date
        """
        print("\n⚙️  Processing historical games...")
        
        current_season = None
        games_processed = 0
        
        for idx, game in games_df.iterrows():
            # Check for new season (apply mean reversion)
            if current_season is None:
                current_season = game['season']
                print(f"\n📅 Starting season {current_season}")
            elif game['season'] != current_season:
                print(f"\n🔄 Season {current_season} → {game['season']}")
                print(f"   Applying mean reversion ({self.elo.mean_reversion:.1%} toward {self.elo.base_elo})")
                self.elo.regress_to_mean()
                current_season = game['season']
            
            # Determine if playoff game (week > 18)
            is_playoff = game['week'] > 18 if pd.notna(game['week']) else False
            
            # Neutral site detection (Super Bowl, international games)
            # For now, assume all regular season games have home field advantage
            is_neutral = False
            
            # Update Elo ratings
            home_team = game['home_team']
            away_team = game['away_team']
            home_score = int(game['home_score'])
            away_score = int(game['away_score'])
            
            # Store pre-game ratings
            pre_home = self.elo.get_rating(home_team)
            pre_away = self.elo.get_rating(away_team)
            
            # Update ratings
            post_home, post_away = self.elo.update_ratings(
                home_team, away_team, home_score, away_score,
                is_playoff=is_playoff, is_neutral=is_neutral
            )
            
            # Store ratings snapshot
            game_date = game['game_date'].strftime('%Y-%m-%d') if pd.notna(game['game_date']) else 'unknown'
            if game_date not in self.ratings_by_date:
                self.ratings_by_date[game_date] = {}
            
            self.ratings_by_date[game_date][home_team] = post_home
            self.ratings_by_date[game_date][away_team] = post_away
            
            games_processed += 1
            
            # Progress indicator
            if games_processed % 500 == 0:
                print(f"   Processed {games_processed} games...")
        
        print(f"\n✅ Processed {games_processed} total games")
    
    def save_current_ratings(self, filepath: str = 'ml/models/elo_ratings_current.json'):
        """Save current Elo ratings to file"""
        ratings_data = {
            'last_updated': datetime.now().isoformat(),
            'ratings': self.elo.get_all_ratings(),
            'system_params': {
                'base_elo': self.elo.base_elo,
                'k_factor': self.elo.k_factor,
                'home_advantage': self.elo.home_advantage,
                'mean_reversion': self.elo.mean_reversion
            }
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(ratings_data, f, indent=2)
        
        print(f"\n💾 Saved current ratings to {filepath}")
    
    def load_current_ratings(self, filepath: str = 'ml/models/elo_ratings_current.json'):
        """Load Elo ratings from file"""
        if not os.path.exists(filepath):
            print(f"⚠️  No saved ratings found at {filepath}")
            return False
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.elo.set_ratings(data['ratings'])
        print(f"✅ Loaded ratings from {filepath}")
        print(f"   Last updated: {data['last_updated']}")
        return True
    
    def display_current_ratings(self, top_n: int = 32):
        """Display current Elo ratings sorted by rating"""
        ratings = self.elo.get_all_ratings()
        sorted_teams = sorted(ratings.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\n{'='*60}")
        print(f"{'CURRENT NFL ELO RATINGS':^60}")
        print(f"{'='*60}")
        print(f"{'Rank':<6} {'Team':<8} {'Rating':<10} {'vs Avg':<10}")
        print(f"{'-'*60}")
        
        for rank, (team, rating) in enumerate(sorted_teams[:top_n], 1):
            diff = rating - self.elo.base_elo
            sign = '+' if diff >= 0 else ''
            print(f"{rank:<6} {team:<8} {rating:>7.1f}    {sign}{diff:>6.1f}")
        
        print(f"{'='*60}\n")
    
    def rebuild_from_scratch(self, start_season: int = 2002):
        """
        Rebuild Elo ratings from scratch
        
        Args:
            start_season: First season to include (default: 2002 - realignment)
        """
        print("\n🔄 REBUILDING ELO RATINGS FROM SCRATCH")
        print(f"   Starting from {start_season} season")
        
        # Initialize all teams
        self.initialize_all_teams()
        
        # Load historical games
        games_df = self.load_historical_games(start_season=start_season)
        
        # Process all games
        self.process_historical_games(games_df)
        
        # Save current state
        self.save_current_ratings()
        
        # Display results
        self.display_current_ratings()
        
        print("\n✅ Elo rating system rebuilt successfully!")
    
    def get_rating_at_date(self, team: str, date: str) -> float:
        """
        Get a team's Elo rating at a specific date
        
        Args:
            team: Team abbreviation
            date: Date string (YYYY-MM-DD)
        
        Returns:
            Elo rating (or base_elo if no data)
        """
        team = self.normalize_team(team)
        
        if date in self.ratings_by_date and team in self.ratings_by_date[date]:
            return self.ratings_by_date[date][team]
        
        # Find most recent date before target
        available_dates = sorted(self.ratings_by_date.keys())
        for past_date in reversed(available_dates):
            if past_date <= date and team in self.ratings_by_date[past_date]:
                return self.ratings_by_date[past_date][team]
        
        return self.elo.base_elo


def main():
    parser = argparse.ArgumentParser(description='NFL Elo Rating Tracker')
    parser.add_argument('--rebuild', action='store_true', 
                       help='Rebuild Elo ratings from historical data')
    parser.add_argument('--current', action='store_true',
                       help='Show current Elo ratings')
    parser.add_argument('--start-season', type=int, default=2002,
                       help='Starting season for rebuild (default: 2002)')
    
    args = parser.parse_args()
    
    tracker = EloTracker()
    
    if args.rebuild:
        tracker.rebuild_from_scratch(start_season=args.start_season)
    elif args.current:
        if tracker.load_current_ratings():
            tracker.display_current_ratings()
        else:
            print("❌ No ratings found. Run with --rebuild first.")
    else:
        print("Usage:")
        print("  python ml/elo_tracker.py --rebuild         # Rebuild from history")
        print("  python ml/elo_tracker.py --current         # Show current ratings")
        print("  python ml/elo_tracker.py --rebuild --start-season 2010")


if __name__ == '__main__':
    main()
