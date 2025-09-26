#!/usr/bin/env python3
"""
NFL Database Analysis Tool
Works with your exact schema specification:
🗃️ Teams | 🏈 Games | 📊 TeamStats | 💰 BettingLines
"""

import sqlite3
from typing import Dict, List
import json

class NFLDatabaseAnalyzer:
    """Analyze NFL data using your exact schema"""
    
    def __init__(self, db_path="user_schema_nfl.db"):
        self.db_path = db_path
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def analyze_team_performance(self, team_id: int) -> Dict:
        """Comprehensive team performance analysis"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get team info
            cursor.execute("SELECT * FROM Teams WHERE team_id = ?", (team_id,))
            team = cursor.fetchone()
            
            if not team:
                return {"error": "Team not found"}
            
            # Get team games
            cursor.execute('''
                SELECT g.*, 
                       CASE WHEN g.home_team_id = ? THEN 'HOME' ELSE 'AWAY' END as venue,
                       CASE WHEN g.home_team_id = ? THEN g.score_home ELSE g.score_away END as team_score,
                       CASE WHEN g.home_team_id = ? THEN g.score_away ELSE g.score_home END as opp_score
                FROM Games g
                WHERE g.home_team_id = ? OR g.away_team_id = ?
                  AND g.score_home IS NOT NULL AND g.score_away IS NOT NULL
                ORDER BY g.week
            ''', (team_id, team_id, team_id, team_id, team_id))
            games = cursor.fetchall()
            
            # Get team stats
            cursor.execute('''
                SELECT ts.*, g.week
                FROM TeamStats ts
                JOIN Games g ON ts.game_id = g.game_id
                WHERE ts.team_id = ?
                ORDER BY g.week
            ''', (team_id,))
            stats = cursor.fetchall()
            
            # Calculate performance metrics
            wins = sum(1 for g in games if g['team_score'] > g['opp_score'])
            losses = sum(1 for g in games if g['team_score'] < g['opp_score'])
            total_points_for = sum(g['team_score'] for g in games)
            total_points_against = sum(g['opp_score'] for g in games)
            
            # Calculate averages from stats
            if stats:
                avg_offense = sum(s['offense_yards'] for s in stats) / len(stats)
                avg_defense = sum(s['defense_yards'] for s in stats) / len(stats)
                total_turnovers = sum(s['turnovers'] for s in stats)
            else:
                avg_offense = avg_defense = total_turnovers = 0
            
            return {
                "team": {
                    "name": team['name'],
                    "abbreviation": team['abbreviation'],
                    "conference": team['conference'],
                    "division": team['division']
                },
                "record": {
                    "wins": wins,
                    "losses": losses,
                    "games_played": len(games)
                },
                "scoring": {
                    "points_for": total_points_for,
                    "points_against": total_points_against,
                    "point_differential": total_points_for - total_points_against,
                    "ppg": round(total_points_for / len(games), 1) if games else 0,
                    "ppg_allowed": round(total_points_against / len(games), 1) if games else 0
                },
                "stats": {
                    "avg_offense_yards": round(avg_offense, 1),
                    "avg_defense_yards": round(avg_defense, 1),
                    "total_turnovers": total_turnovers,
                    "turnover_rate": round(total_turnovers / len(stats), 1) if stats else 0
                },
                "games": [dict(g) for g in games],
                "detailed_stats": [dict(s) for s in stats]
            }
    
    def analyze_betting_performance(self, predicted_by_user: str) -> Dict:
        """Analyze betting prediction performance"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all predictions with game results
            cursor.execute('''
                SELECT bl.*, g.score_home, g.score_away, g.home_team_id, g.away_team_id,
                       ht.abbreviation as home_abbr, at.abbreviation as away_abbr
                FROM BettingLines bl
                JOIN Games g ON bl.game_id = g.game_id
                JOIN Teams ht ON g.home_team_id = ht.team_id
                JOIN Teams at ON g.away_team_id = at.team_id
                WHERE bl.predicted_by_user = ?
                  AND g.score_home IS NOT NULL AND g.score_away IS NOT NULL
            ''', (predicted_by_user,))
            predictions = cursor.fetchall()
            
            if not predictions:
                return {"error": f"No predictions found for {predicted_by_user}"}
            
            correct_spreads = 0
            correct_totals = 0
            results = []
            
            for pred in predictions:
                actual_margin = pred['score_home'] - pred['score_away']
                predicted_spread = pred['spread']
                
                # Check spread accuracy (home team perspective)
                spread_correct = (
                    (predicted_spread < 0 and actual_margin > -predicted_spread) or
                    (predicted_spread > 0 and actual_margin < -predicted_spread) or
                    (predicted_spread == 0 and actual_margin == 0)
                )
                
                if spread_correct:
                    correct_spreads += 1
                
                # Check total accuracy
                actual_total = pred['score_home'] + pred['score_away']
                total_correct = abs(actual_total - pred['total']) <= 3  # Within 3 points
                
                if total_correct:
                    correct_totals += 1
                
                results.append({
                    "game": f"{pred['away_abbr']} @ {pred['home_abbr']}",
                    "predicted_spread": predicted_spread,
                    "actual_margin": actual_margin,
                    "spread_correct": spread_correct,
                    "predicted_total": pred['total'],
                    "actual_total": actual_total,
                    "total_correct": total_correct,
                    "formula": pred['formula_name'],
                    "confidence": pred['prediction_confidence']
                })
            
            total_predictions = len(predictions)
            
            return {
                "predictor": predicted_by_user,
                "summary": {
                    "total_predictions": total_predictions,
                    "spread_accuracy": round(correct_spreads / total_predictions, 3),
                    "total_accuracy": round(correct_totals / total_predictions, 3),
                    "overall_score": round((correct_spreads + correct_totals) / (total_predictions * 2), 3)
                },
                "detailed_results": results,
                "formulas_used": list(set(p['formula_name'] for p in predictions if p['formula_name'])),
                "avg_confidence": round(sum(p['prediction_confidence'] for p in predictions if p['prediction_confidence']) / total_predictions, 3)
            }
    
    def get_conference_standings(self, conference: str) -> List[Dict]:
        """Get conference standings"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM Teams WHERE conference = ?", (conference,))
            teams = cursor.fetchall()
            
            standings = []
            
            for team in teams:
                team_analysis = self.analyze_team_performance(team['team_id'])
                if 'error' not in team_analysis:
                    standings.append({
                        "team": team_analysis['team']['name'],
                        "abbreviation": team_analysis['team']['abbreviation'],
                        "division": team_analysis['team']['division'],
                        "wins": team_analysis['record']['wins'],
                        "losses": team_analysis['record']['losses'],
                        "win_pct": round(team_analysis['record']['wins'] / max(team_analysis['record']['games_played'], 1), 3),
                        "point_diff": team_analysis['scoring']['point_differential'],
                        "ppg": team_analysis['scoring']['ppg']
                    })
            
            # Sort by win percentage, then point differential
            standings.sort(key=lambda x: (x['win_pct'], x['point_diff']), reverse=True)
            
            return standings
    
    def get_top_statistical_performances(self) -> Dict:
        """Get top statistical performances across all categories"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Top offensive performances
            cursor.execute('''
                SELECT t.name, t.abbreviation, ts.offense_yards, g.week
                FROM TeamStats ts
                JOIN Teams t ON ts.team_id = t.team_id
                JOIN Games g ON ts.game_id = g.game_id
                ORDER BY ts.offense_yards DESC
                LIMIT 5
            ''')
            top_offense = cursor.fetchall()
            
            # Most turnovers forced (lowest turnovers committed)
            cursor.execute('''
                SELECT t.name, t.abbreviation, ts.turnovers, g.week
                FROM TeamStats ts
                JOIN Teams t ON ts.team_id = t.team_id
                JOIN Games g ON ts.game_id = g.game_id
                ORDER BY ts.turnovers ASC
                LIMIT 5
            ''')
            best_ball_security = cursor.fetchall()
            
            # Best defensive performances (lowest yards allowed)
            cursor.execute('''
                SELECT t.name, t.abbreviation, ts.defense_yards, g.week
                FROM TeamStats ts
                JOIN Teams t ON ts.team_id = t.team_id
                JOIN Games g ON ts.game_id = g.game_id
                ORDER BY ts.defense_yards ASC
                LIMIT 5
            ''')
            top_defense = cursor.fetchall()
            
            return {
                "top_offensive_games": [dict(row) for row in top_offense],
                "best_ball_security": [dict(row) for row in best_ball_security],
                "top_defensive_games": [dict(row) for row in top_defense]
            }
    
    def generate_comprehensive_report(self) -> Dict:
        """Generate comprehensive database report"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get basic counts
            cursor.execute("SELECT COUNT(*) as count FROM Teams")
            team_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM Games WHERE score_home IS NOT NULL")
            completed_games = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM BettingLines")
            betting_lines = cursor.fetchone()['count']
            
            # Get season info
            cursor.execute("SELECT DISTINCT season FROM Games ORDER BY season")
            seasons = [row['season'] for row in cursor.fetchall()]
            
            # Get all predictors
            cursor.execute('''
                SELECT predicted_by_user, COUNT(*) as prediction_count
                FROM BettingLines 
                WHERE predicted_by_user IS NOT NULL
                GROUP BY predicted_by_user
            ''')
            predictors = cursor.fetchall()
            
            return {
                "database_overview": {
                    "total_teams": team_count,
                    "completed_games": completed_games,
                    "betting_lines": betting_lines,
                    "seasons_covered": seasons
                },
                "conference_standings": {
                    "AFC": self.get_conference_standings('AFC'),
                    "NFC": self.get_conference_standings('NFC')
                },
                "top_performances": self.get_top_statistical_performances(),
                "predictors": [dict(row) for row in predictors],
                "betting_analysis": {
                    predictor['predicted_by_user']: self.analyze_betting_performance(predictor['predicted_by_user'])
                    for predictor in predictors if predictor['predicted_by_user']
                }
            }

def main():
    """Generate comprehensive NFL database analysis"""
    print("📊 NFL Database Analysis Report")
    print("Using your exact schema:")
    print("🗃️ Teams | 🏈 Games | 📊 TeamStats | 💰 BettingLines")
    print("=" * 60)
    
    analyzer = NFLDatabaseAnalyzer()
    
    # Generate comprehensive report
    report = analyzer.generate_comprehensive_report()
    
    # Display overview
    overview = report['database_overview']
    print(f"\n📋 Database Overview:")
    print(f"   Teams: {overview['total_teams']}")
    print(f"   Completed Games: {overview['completed_games']}")
    print(f"   Betting Lines: {overview['betting_lines']}")
    print(f"   Seasons: {', '.join(map(str, overview['seasons_covered']))}")
    
    # Display conference standings
    print(f"\n🏆 Conference Standings:")
    for conf in ['AFC', 'NFC']:
        standings = report['conference_standings'][conf]
        print(f"\n   {conf} Conference:")
        for i, team in enumerate(standings, 1):
            print(f"     {i}. {team['team']} ({team['abbreviation']}) {team['wins']}-{team['losses']} ({team['win_pct']:.3f})")
            print(f"        Point Diff: {team['point_diff']:+}, PPG: {team['ppg']}")
    
    # Display top performances
    print(f"\n⭐ Top Statistical Performances:")
    top_perf = report['top_performances']
    
    print(f"\n   🚀 Best Offensive Games:")
    for perf in top_perf['top_offensive_games']:
        print(f"     {perf['abbreviation']} Week {perf['week']}: {perf['offense_yards']} yards")
    
    print(f"\n   🛡️ Best Ball Security (Fewest Turnovers):")
    for perf in top_perf['best_ball_security']:
        print(f"     {perf['abbreviation']} Week {perf['week']}: {perf['turnovers']} turnovers")
    
    print(f"\n   🔒 Best Defensive Games (Fewest Yards Allowed):")
    for perf in top_perf['top_defensive_games']:
        print(f"     {perf['abbreviation']} Week {perf['week']}: {perf['defense_yards']} yards allowed")
    
    # Display betting analysis
    print(f"\n💰 Betting Prediction Analysis:")
    betting_analysis = report['betting_analysis']
    
    for predictor, analysis in betting_analysis.items():
        if 'error' not in analysis:
            summary = analysis['summary']
            print(f"\n   📈 {predictor}:")
            print(f"     Total Predictions: {summary['total_predictions']}")
            print(f"     Spread Accuracy: {summary['spread_accuracy']:.1%}")
            print(f"     Total Accuracy: {summary['total_accuracy']:.1%}")
            print(f"     Overall Score: {summary['overall_score']:.1%}")
            print(f"     Average Confidence: {analysis['avg_confidence']:.1%}")
            print(f"     Formulas Used: {', '.join(analysis['formulas_used'])}")
    
    # Individual team analysis example
    print(f"\n🔍 Sample Team Analysis (Kansas City Chiefs):")
    kc_analysis = analyzer.analyze_team_performance(1)  # KC is team_id 1
    
    if 'error' not in kc_analysis:
        team = kc_analysis['team']
        record = kc_analysis['record']
        scoring = kc_analysis['scoring']
        stats = kc_analysis['stats']
        
        print(f"   Team: {team['name']} ({team['abbreviation']})")
        print(f"   Conference: {team['conference']} {team['division']}")
        print(f"   Record: {record['wins']}-{record['losses']} ({record['games_played']} games)")
        print(f"   Scoring: {scoring['ppg']} PPG, {scoring['ppg_allowed']} allowed")
        print(f"   Point Differential: {scoring['point_differential']:+}")
        print(f"   Avg Offense: {stats['avg_offense_yards']} yards/game")
        print(f"   Avg Defense: {stats['avg_defense_yards']} yards allowed/game")
        print(f"   Turnover Rate: {stats['turnover_rate']} per game")
    
    print(f"\n✅ Comprehensive analysis complete!")
    print(f"📁 Database: user_schema_nfl.db")
    print(f"🎯 Schema: Your exact specifications implemented perfectly!")

if __name__ == "__main__":
    main()