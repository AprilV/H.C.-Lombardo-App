"""
Central Configuration for ALL NFL Stats from TeamRankings.com
Adding a new stat = just add one entry here, that's it!
"""

# ALL 37+ AVAILABLE NFL STATS
# Format: 'key': {'name': 'Display Name', 'url_slug': 'teamrankings-url', 'data_type': 'float|int|percentage'}

AVAILABLE_STATS = {
    'offense': {
        'points_per_game': {
            'name': 'Points Per Game',
            'url_slug': 'points-per-game',
            'data_type': 'float',
            'short_name': 'PPG'
        },
        'yards_per_game': {
            'name': 'Yards Per Game',
            'url_slug': 'yards-per-game',
            'data_type': 'float',
            'short_name': 'YPG'
        },
        'passing_yards_per_game': {
            'name': 'Passing Yards Per Game',
            'url_slug': 'passing-yards-per-game',
            'data_type': 'float',
            'short_name': 'Pass YPG'
        },
        'rushing_yards_per_game': {
            'name': 'Rushing Yards Per Game',
            'url_slug': 'rushing-yards-per-game',
            'data_type': 'float',
            'short_name': 'Rush YPG'
        },
        'first_downs_per_game': {
            'name': 'First Downs Per Game',
            'url_slug': 'first-downs-per-game',
            'data_type': 'float',
            'short_name': '1st Downs'
        },
        'third_down_conversions': {
            'name': 'Third Down Conversions',
            'url_slug': 'third-down-conversions-per-game',
            'data_type': 'float',
            'short_name': '3rd Conv'
        },
        'third_down_conversion_pct': {
            'name': 'Third Down Conversion %',
            'url_slug': 'third-down-conversion-pct',
            'data_type': 'percentage',
            'short_name': '3rd Down %'
        },
        'fourth_down_conversions': {
            'name': 'Fourth Down Conversions',
            'url_slug': 'fourth-down-conversions-per-game',
            'data_type': 'float',
            'short_name': '4th Conv'
        },
        'fourth_down_conversion_pct': {
            'name': 'Fourth Down Conversion %',
            'url_slug': 'fourth-down-conversion-pct',
            'data_type': 'percentage',
            'short_name': '4th Down %'
        },
        'red_zone_scoring_pct': {
            'name': 'Red Zone Scoring %',
            'url_slug': 'red-zone-scoring-pct',
            'data_type': 'percentage',
            'short_name': 'RZ %'
        },
        'touchdowns_per_game': {
            'name': 'Touchdowns Per Game',
            'url_slug': 'touchdowns-per-game',
            'data_type': 'float',
            'short_name': 'TD/G'
        },
        'passing_touchdowns': {
            'name': 'Passing Touchdowns',
            'url_slug': 'passing-touchdowns',
            'data_type': 'int',
            'short_name': 'Pass TD'
        },
        'rushing_touchdowns': {
            'name': 'Rushing Touchdowns',
            'url_slug': 'rushing-touchdowns',
            'data_type': 'int',
            'short_name': 'Rush TD'
        },
        'turnovers_per_game': {
            'name': 'Turnovers Per Game',
            'url_slug': 'turnovers-per-game',
            'data_type': 'float',
            'short_name': 'TO/G'
        },
        'giveaways': {
            'name': 'Giveaways',
            'url_slug': 'giveaways',
            'data_type': 'int',
            'short_name': 'Giveaways'
        },
        'fumbles_lost': {
            'name': 'Fumbles Lost',
            'url_slug': 'fumbles-lost',
            'data_type': 'int',
            'short_name': 'Fum Lost'
        },
        'interceptions_thrown': {
            'name': 'Interceptions Thrown',
            'url_slug': 'interceptions-thrown',
            'data_type': 'int',
            'short_name': 'INT'
        },
        'penalties_per_game': {
            'name': 'Penalties Per Game',
            'url_slug': 'penalties-per-game',
            'data_type': 'float',
            'short_name': 'Pen/G'
        },
        'penalty_yards_per_game': {
            'name': 'Penalty Yards Per Game',
            'url_slug': 'penalty-yards-per-game',
            'data_type': 'float',
            'short_name': 'Pen Yds'
        },
        'time_of_possession': {
            'name': 'Time of Possession',
            'url_slug': 'average-time-of-possession-net-of-ot',
            'data_type': 'string',
            'short_name': 'TOP'
        }
    },
    
    'defense': {
        'opponent_points_per_game': {
            'name': 'Opponent Points Per Game',
            'url_slug': 'opponent-points-per-game',
            'data_type': 'float',
            'short_name': 'Opp PPG'
        },
        'opponent_yards_per_game': {
            'name': 'Opponent Yards Per Game',
            'url_slug': 'opponent-yards-per-game',
            'data_type': 'float',
            'short_name': 'Opp YPG'
        },
        'opponent_passing_yards_per_game': {
            'name': 'Opponent Passing Yards Per Game',
            'url_slug': 'opponent-passing-yards-per-game',
            'data_type': 'float',
            'short_name': 'Opp Pass YPG'
        },
        'opponent_rushing_yards_per_game': {
            'name': 'Opponent Rushing Yards Per Game',
            'url_slug': 'opponent-rushing-yards-per-game',
            'data_type': 'float',
            'short_name': 'Opp Rush YPG'
        },
        'sacks_per_game': {
            'name': 'Sacks Per Game',
            'url_slug': 'sacks-per-game',
            'data_type': 'float',
            'short_name': 'Sacks'
        },
        'interceptions': {
            'name': 'Interceptions',
            'url_slug': 'interceptions',
            'data_type': 'int',
            'short_name': 'INT'
        },
        'forced_fumbles': {
            'name': 'Forced Fumbles',
            'url_slug': 'forced-fumbles',
            'data_type': 'int',
            'short_name': 'FF'
        },
        'takeaways': {
            'name': 'Takeaways',
            'url_slug': 'takeaways',
            'data_type': 'int',
            'short_name': 'Takeaways'
        },
        'opponent_third_down_conversion_pct': {
            'name': 'Opponent Third Down Conversion %',
            'url_slug': 'opponent-third-down-conversion-pct',
            'data_type': 'percentage',
            'short_name': 'Opp 3rd %'
        },
        'opponent_red_zone_scoring_pct': {
            'name': 'Opponent Red Zone Scoring %',
            'url_slug': 'opponent-red-zone-scoring-pct',
            'data_type': 'percentage',
            'short_name': 'Opp RZ %'
        },
        'tackles_for_loss_per_game': {
            'name': 'Tackles For Loss Per Game',
            'url_slug': 'tackles-for-loss-per-game',
            'data_type': 'float',
            'short_name': 'TFL/G'
        }
    },
    
    'special_teams': {
        'field_goal_pct': {
            'name': 'Field Goal %',
            'url_slug': 'field-goal-pct',
            'data_type': 'percentage',
            'short_name': 'FG%'
        },
        'extra_point_pct': {
            'name': 'Extra Point %',
            'url_slug': 'extra-point-conversion-pct',
            'data_type': 'percentage',
            'short_name': 'XP%'
        },
        'punt_average': {
            'name': 'Punt Average',
            'url_slug': 'punt-average',
            'data_type': 'float',
            'short_name': 'Punt Avg'
        },
        'punt_return_average': {
            'name': 'Punt Return Average',
            'url_slug': 'punt-return-average',
            'data_type': 'float',
            'short_name': 'PR Avg'
        },
        'kickoff_return_average': {
            'name': 'Kickoff Return Average',
            'url_slug': 'kickoff-return-average',
            'data_type': 'float',
            'short_name': 'KR Avg'
        },
        'touchbacks_per_game': {
            'name': 'Touchbacks Per Game',
            'url_slug': 'touchbacks-per-game',
            'data_type': 'float',
            'short_name': 'TB/G'
        }
    }
}

# Helper function to get total count
def get_total_stats_count():
    total = 0
    for category in AVAILABLE_STATS.values():
        total += len(category)
    return total

# Helper function to get stat by key
def get_stat_config(category, stat_key):
    """Get stat configuration by category and key"""
    return AVAILABLE_STATS.get(category, {}).get(stat_key)

# Helper function to get all stats in a category
def get_category_stats(category):
    """Get all stats in a category"""
    return AVAILABLE_STATS.get(category, {})

# Helper function for dropdown display
def get_stats_for_dropdown():
    """Format stats for frontend dropdown"""
    dropdown_data = []
    for category, stats in AVAILABLE_STATS.items():
        for stat_key, stat_config in stats.items():
            dropdown_data.append({
                'category': category,
                'key': stat_key,
                'name': stat_config['name'],
                'short_name': stat_config['short_name']
            })
    return dropdown_data

if __name__ == "__main__":
    print(f"Total stats configured: {get_total_stats_count()}")
    print(f"\nCategories:")
    for category, stats in AVAILABLE_STATS.items():
        print(f"  - {category}: {len(stats)} stats")
