-- Insert Week 14-16 team game stats
-- Generated from local database

INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_14_CHI_GB', 2025, 14, 'CHI', 'GB', false, 317, 177, 140, 1, 21, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_14_CHI_GB', 2025, 14, 'GB', 'CHI', true, 337, 220, 118, 1, 28, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_14_CIN_BUF', 2025, 14, 'BUF', 'CIN', true, 418, 235, 186, 1, 39, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_14_CIN_BUF', 2025, 14, 'CIN', 'BUF', false, 338, 276, 62, 2, 34, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_14_DAL_DET', 2025, 14, 'DAL', 'DET', false, 419, 328, 91, 3, 30, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_14_DAL_DET', 2025, 14, 'DET', 'DAL', true, 408, 299, 111, 0, 44, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_14_DEN_LV', 2025, 14, 'DEN', 'LV', false, 356, 204, 152, 0, 24, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_14_DEN_LV', 2025, 14, 'LV', 'DEN', true, 229, 189, 40, 0, 17, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_14_HOU_KC', 2025, 14, 'HOU', 'KC', false, 268, 186, 82, 0, 17, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_14_HOU_KC', 2025, 14, 'KC', 'HOU', true, 274, 148, 126, 3, 10, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_14_IND_JAX', 2025, 14, 'IND', 'JAX', false, 285, 196, 90, 3, 19, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_14_IND_JAX', 2025, 14, 'JAX', 'IND', true, 350, 247, 104, 1, 36, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_14_LA_ARI', 2025, 14, 'ARI', 'LA', true, 314, 263, 51, 1, 17, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_14_LA_ARI', 2025, 14, 'LA', 'ARI', false, 530, 281, 253, 0, 45, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_14_MIA_NYJ', 2025, 14, 'MIA', 'NYJ', false, 358, 119, 241, 0, 34, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_14_MIA_NYJ', 2025, 14, 'NYJ', 'MIA', true, 207, 142, 65, 3, 10, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_14_NO_TB', 2025, 14, 'NO', 'TB', false, 260, 121, 142, 1, 24, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_14_NO_TB', 2025, 14, 'TB', 'NO', true, 301, 122, 179, 1, 20, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_14_PHI_LAC', 2025, 14, 'LAC', 'PHI', true, 275, 106, 169, 2, 22, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_14_PHI_LAC', 2025, 14, 'PHI', 'LAC', false, 365, 231, 135, 4, 19, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_14_PIT_BAL', 2025, 14, 'BAL', 'PIT', true, 420, 203, 217, 1, 22, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_14_PIT_BAL', 2025, 14, 'PIT', 'BAL', false, 318, 284, 35, 0, 27, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_14_SEA_ATL', 2025, 14, 'ATL', 'SEA', true, 274, 154, 120, 3, 9, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_14_SEA_ATL', 2025, 14, 'SEA', 'ATL', false, 365, 236, 129, 1, 37, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_14_TEN_CLE', 2025, 14, 'CLE', 'TEN', true, 412, 351, 61, 2, 29, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_14_TEN_CLE', 2025, 14, 'TEN', 'CLE', false, 292, 108, 184, 1, 31, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_14_WAS_MIN', 2025, 14, 'MIN', 'WAS', true, 313, 151, 166, 0, 31, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_14_WAS_MIN', 2025, 14, 'WAS', 'MIN', false, 206, 99, 107, 3, 0, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_ARI_HOU', 2025, 15, 'ARI', 'HOU', false, 307, 235, 72, 2, 20, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_ARI_HOU', 2025, 15, 'HOU', 'ARI', true, 399, 256, 143, 0, 40, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_ATL_TB', 2025, 15, 'ATL', 'TB', false, 476, 365, 111, 1, 26, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_ATL_TB', 2025, 15, 'TB', 'ATL', true, 340, 252, 88, 1, 28, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_BAL_CIN', 2025, 15, 'BAL', 'CIN', false, 317, 128, 192, 1, 24, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_BAL_CIN', 2025, 15, 'CIN', 'BAL', true, 298, 198, 100, 2, 0, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_BUF_NE', 2025, 15, 'BUF', 'NE', false, 349, 181, 171, 0, 35, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_BUF_NE', 2025, 15, 'NE', 'BUF', true, 385, 139, 246, 1, 31, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_CAR_NO', 2025, 15, 'CAR', 'NO', false, 281, 154, 127, 1, 17, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_CAR_NO', 2025, 15, 'NO', 'CAR', true, 337, 256, 82, 0, 20, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_CLE_CHI', 2025, 15, 'CHI', 'CLE', true, 361, 219, 143, 0, 31, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_CLE_CHI', 2025, 15, 'CLE', 'CHI', false, 192, 142, 50, 3, 3, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_DET_LA', 2025, 15, 'DET', 'LA', false, 396, 326, 70, 0, 34, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_DET_LA', 2025, 15, 'LA', 'DET', true, 519, 360, 159, 1, 41, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_GB_DEN', 2025, 15, 'DEN', 'GB', true, 391, 302, 91, 1, 34, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_GB_DEN', 2025, 15, 'GB', 'DEN', false, 362, 247, 115, 2, 26, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_IND_SEA', 2025, 15, 'IND', 'SEA', false, 220, 118, 102, 1, 16, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_IND_SEA', 2025, 15, 'SEA', 'IND', true, 314, 264, 51, 0, 18, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_LAC_KC', 2025, 15, 'KC', 'LAC', true, 239, 190, 49, 2, 13, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_LAC_KC', 2025, 15, 'LAC', 'KC', false, 295, 201, 95, 1, 16, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_LV_PHI', 2025, 15, 'LV', 'PHI', false, 75, 29, 46, 1, 0, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_LV_PHI', 2025, 15, 'PHI', 'LV', true, 387, 204, 183, 0, 31, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_MIA_PIT', 2025, 15, 'MIA', 'PIT', false, 285, 222, 63, 1, 15, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_MIA_PIT', 2025, 15, 'PIT', 'MIA', true, 336, 201, 135, 0, 28, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_MIN_DAL', 2025, 15, 'DAL', 'MIN', true, 423, 285, 138, 0, 23, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_MIN_DAL', 2025, 15, 'MIN', 'DAL', false, 327, 250, 78, 1, 34, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_NYJ_JAX', 2025, 15, 'JAX', 'NYJ', true, 438, 330, 110, 1, 48, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_NYJ_JAX', 2025, 15, 'NYJ', 'JAX', false, 284, 154, 130, 3, 20, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_TEN_SF', 2025, 15, 'SF', 'TEN', true, 430, 292, 138, 1, 34, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_TEN_SF', 2025, 15, 'TEN', 'SF', false, 306, 170, 136, 0, 24, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_WAS_NYG', 2025, 15, 'NYG', 'WAS', true, 384, 238, 146, 1, 21, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_15_WAS_NYG', 2025, 15, 'WAS', 'NYG', false, 340, 195, 148, 2, 29, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_16_BUF_CLE', 2025, 16, 'BUF', 'CLE', false, 259, 95, 166, 0, 23, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_16_BUF_CLE', 2025, 16, 'CLE', 'BUF', true, 294, 134, 160, 2, 20, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_16_CIN_MIA', 2025, 16, 'CIN', 'MIA', false, 407, 302, 105, 0, 45, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_16_CIN_MIA', 2025, 16, 'MIA', 'CIN', true, 389, 260, 129, 3, 21, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_16_GB_CHI', 2025, 16, 'CHI', 'GB', true, 400, 250, 150, 0, 22, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_16_GB_CHI', 2025, 16, 'GB', 'CHI', false, 384, 192, 194, 1, 16, 'T')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_16_KC_TEN', 2025, 16, 'KC', 'TEN', false, 133, 82, 51, 0, 9, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_16_KC_TEN', 2025, 16, 'TEN', 'KC', true, 376, 212, 166, 0, 26, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_16_LA_SEA', 2025, 16, 'LA', 'SEA', false, 581, 457, 124, 0, 36, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_16_LA_SEA', 2025, 16, 'SEA', 'LA', true, 421, 248, 173, 3, 38, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_16_LAC_DAL', 2025, 16, 'DAL', 'LAC', true, 340, 249, 91, 1, 17, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_16_LAC_DAL', 2025, 16, 'LAC', 'DAL', false, 452, 300, 154, 0, 34, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_16_MIN_NYG', 2025, 16, 'MIN', 'NYG', false, 240, 126, 117, 2, 16, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_16_MIN_NYG', 2025, 16, 'NYG', 'MIN', true, 141, 13, 128, 1, 13, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_16_NYJ_NO', 2025, 16, 'NO', 'NYJ', true, 412, 328, 84, 1, 28, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_16_NYJ_NO', 2025, 16, 'NYJ', 'NO', false, 195, 131, 64, 2, 6, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_16_PHI_WAS', 2025, 16, 'PHI', 'WAS', false, 387, 178, 211, 1, 29, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_16_PHI_WAS', 2025, 16, 'WAS', 'PHI', true, 222, 130, 93, 1, 16, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_16_TB_CAR', 2025, 16, 'CAR', 'TB', true, 275, 174, 102, 0, 23, 'W')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
INSERT INTO hcl.team_game_stats 
(game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
VALUES ('2025_16_TB_CAR', 2025, 16, 'TB', 'CAR', false, 296, 127, 170, 1, 20, 'L')
ON CONFLICT (game_id, team) DO UPDATE SET
    total_yards = EXCLUDED.total_yards,
    passing_yards = EXCLUDED.passing_yards,
    rushing_yards = EXCLUDED.rushing_yards,
    turnovers = EXCLUDED.turnovers,
    points = EXCLUDED.points,
    result = EXCLUDED.result;
