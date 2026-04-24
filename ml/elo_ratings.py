"""
NFL Elo Rating System

Core Elo rating implementation used by elo_tracker.py and predict_elo.py.
Provides team rating storage, updates, and mean reversion between seasons.

Sprint 13: TA-068 — Created Apr 21, 2026
"""

import math


class EloRatingSystem:
    """Core Elo rating engine for NFL teams."""

    def __init__(self, base_elo=1500, k_factor=20, home_advantage=65, mean_reversion=0.33):
        self.base_elo = base_elo
        self.k_factor = k_factor
        self.home_advantage = home_advantage
        self.mean_reversion = mean_reversion
        self._ratings = {}

    def initialize_team(self, team: str):
        """Set a team to base_elo if not already tracked."""
        team = team.upper()
        if team not in self._ratings:
            self._ratings[team] = self.base_elo

    def get_rating(self, team: str) -> float:
        """Return current rating for a team, defaulting to base_elo."""
        return self._ratings.get(team.upper(), self.base_elo)

    def get_all_ratings(self) -> dict:
        """Return a copy of all current ratings."""
        return dict(self._ratings)

    def set_ratings(self, ratings: dict):
        """Bulk-load ratings from a dict (e.g. loaded from JSON)."""
        self._ratings = {t.upper(): float(r) for t, r in ratings.items()}

    def _expected_score(self, rating_a: float, rating_b: float) -> float:
        """Expected win probability for team A against team B."""
        return 1.0 / (1.0 + math.pow(10, (rating_b - rating_a) / 400.0))

    def update_ratings(
        self,
        home_team: str,
        away_team: str,
        home_score: int,
        away_score: int,
        is_playoff: bool = False,
        is_neutral: bool = False,
    ):
        """
        Update Elo ratings after a completed game.

        Returns:
            (new_home_rating, new_away_rating)
        """
        home_team = home_team.upper()
        away_team = away_team.upper()

        home_rating = self.get_rating(home_team)
        away_rating = self.get_rating(away_team)

        # Apply home field advantage unless neutral site
        home_adj = home_rating + (0 if is_neutral else self.home_advantage)

        expected_home = self._expected_score(home_adj, away_rating)
        expected_away = 1.0 - expected_home

        # Actual outcome: 1 = win, 0.5 = tie, 0 = loss
        if home_score > away_score:
            actual_home, actual_away = 1.0, 0.0
        elif home_score < away_score:
            actual_home, actual_away = 0.0, 1.0
        else:
            actual_home, actual_away = 0.5, 0.5

        # Playoff games use a larger K factor
        k = self.k_factor * 1.25 if is_playoff else self.k_factor

        new_home = home_rating + k * (actual_home - expected_home)
        new_away = away_rating + k * (actual_away - expected_away)

        self._ratings[home_team] = new_home
        self._ratings[away_team] = new_away

        return new_home, new_away

    def predict_game(self, home_team: str, away_team: str, is_neutral: bool = False):
        """Return (home_win_prob, away_win_prob) from current Elo ratings."""
        home_team = home_team.upper()
        away_team = away_team.upper()

        home_rating = self.get_rating(home_team)
        away_rating = self.get_rating(away_team)

        # Apply home edge for non-neutral games, matching update logic.
        home_adj = home_rating + (0 if is_neutral else self.home_advantage)

        home_win_prob = self._expected_score(home_adj, away_rating)
        away_win_prob = 1.0 - home_win_prob
        return home_win_prob, away_win_prob

    def predict_spread(self, home_team: str, away_team: str, is_neutral: bool = False):
        """Estimate point spread from Elo differential (home perspective)."""
        home_team = home_team.upper()
        away_team = away_team.upper()

        home_rating = self.get_rating(home_team)
        away_rating = self.get_rating(away_team)

        home_adj = home_rating + (0 if is_neutral else self.home_advantage)
        elo_diff = home_adj - away_rating

        # Common heuristic: ~25 Elo points ~= 1 point on spread.
        return elo_diff / 25.0

    def regress_to_mean(self):
        """Pull all ratings toward base_elo at season boundary."""
        for team in self._ratings:
            self._ratings[team] = (
                self._ratings[team] * (1.0 - self.mean_reversion)
                + self.base_elo * self.mean_reversion
            )
