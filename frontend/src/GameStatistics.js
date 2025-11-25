import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './GameStatistics.css';

const API_URL = '';

// All available statistics organized by category for à la carte selection
const STAT_CATEGORIES = {
  'Record': [
    { key: 'games_played', label: 'Games Played', format: 'int' },
    { key: 'wins', label: 'Wins', format: 'int' },
    { key: 'losses', label: 'Losses', format: 'int' },
    { key: 'home_wins', label: 'Home Wins', format: 'int' },
    { key: 'away_wins', label: 'Away Wins', format: 'int' },
  ],
  'Scoring': [
    { key: 'ppg', label: 'Points Per Game', format: 'decimal' },
    { key: 'total_points', label: 'Total Points', format: 'int' },
    { key: 'ppg_home', label: 'PPG (Home)', format: 'decimal' },
    { key: 'ppg_away', label: 'PPG (Away)', format: 'decimal' },
    { key: 'touchdowns_per_game', label: 'TDs/Game', format: 'decimal' },
    { key: 'fg_per_game', label: 'FGs/Game', format: 'decimal' },
    { key: 'fg_att_per_game', label: 'FG Attempts/Game', format: 'decimal' },
  ],
  'Offense': [
    { key: 'total_yards_per_game', label: 'Total Yards/Game', format: 'decimal' },
    { key: 'passing_yards_per_game', label: 'Passing Yards/Game', format: 'decimal' },
    { key: 'rushing_yards_per_game', label: 'Rushing Yards/Game', format: 'decimal' },
    { key: 'plays_per_game', label: 'Plays/Game', format: 'decimal' },
    { key: 'yards_per_play', label: 'Yards Per Play', format: 'decimal' },
  ],
  'Passing': [
    { key: 'completions_per_game', label: 'Completions/Game', format: 'decimal' },
    { key: 'passing_att_per_game', label: 'Pass Attempts/Game', format: 'decimal' },
    { key: 'completion_pct', label: 'Completion %', format: 'percent' },
    { key: 'passing_tds_per_game', label: 'Pass TDs/Game', format: 'decimal' },
    { key: 'interceptions_per_game', label: 'INTs/Game', format: 'decimal' },
    { key: 'sacks_taken_per_game', label: 'Sacks Taken/Game', format: 'decimal' },
    { key: 'sack_yards_lost_per_game', label: 'Sack Yards Lost/Game', format: 'decimal' },
    { key: 'qb_rating', label: 'QB Rating', format: 'decimal' },
  ],
  'Rushing': [
    { key: 'rushing_att_per_game', label: 'Rush Attempts/Game', format: 'decimal' },
    { key: 'yards_per_carry', label: 'Yards Per Carry', format: 'decimal' },
    { key: 'rushing_tds_per_game', label: 'Rush TDs/Game', format: 'decimal' },
  ],
  'Efficiency': [
    { key: 'third_down_pct', label: 'Third Down %', format: 'percent' },
    { key: 'fourth_down_pct', label: 'Fourth Down %', format: 'percent' },
    { key: 'red_zone_pct', label: 'Red Zone %', format: 'percent' },
    { key: 'time_of_possession_pct', label: 'Time of Possession %', format: 'percent' },
    { key: 'early_down_success_rate', label: 'Early Down Success %', format: 'percent' },
  ],
  'Special Teams': [
    { key: 'punts_per_game', label: 'Punts/Game', format: 'decimal' },
    { key: 'punt_avg_yards', label: 'Punt Average', format: 'decimal' },
    { key: 'kickoff_return_yards_per_game', label: 'KR Yards/Game', format: 'decimal' },
    { key: 'punt_return_yards_per_game', label: 'PR Yards/Game', format: 'decimal' },
  ],
  'Turnovers': [
    { key: 'total_turnovers', label: 'Total Turnovers', format: 'int' },
    { key: 'turnovers_per_game', label: 'Turnovers/Game', format: 'decimal' },
    { key: 'fumbles_lost_per_game', label: 'Fumbles Lost/Game', format: 'decimal' },
  ],
  'Penalties': [
    { key: 'penalties_per_game', label: 'Penalties/Game', format: 'decimal' },
    { key: 'penalty_yards_per_game', label: 'Penalty Yards/Game', format: 'decimal' },
  ],
  'Advanced': [
    { key: 'drives_per_game', label: 'Drives/Game', format: 'decimal' },
    { key: 'starting_field_pos_yds', label: 'Avg Starting Field Position', format: 'decimal' },
  ],
};

function GameStatistics() {
  // Team A state
  const [seasonA, setSeasonA] = useState('2025');
  const [teamAList, setTeamAList] = useState([]);
  const [selectedTeamA, setSelectedTeamA] = useState('');
  const [teamAData, setTeamAData] = useState(null);
  
  // Team B state
  const [seasonB, setSeasonB] = useState('2025');
  const [teamBList, setTeamBList] = useState([]);
  const [selectedTeamB, setSelectedTeamB] = useState('');
  const [teamBData, setTeamBData] = useState(null);
  
  // À la carte stat selection - start with most common stats selected
  const [selectedStats, setSelectedStats] = useState(new Set([
    'ppg', 'total_yards_per_game', 'passing_yards_per_game', 'rushing_yards_per_game',
    'completion_pct', 'qb_rating', 'third_down_pct', 'turnovers_per_game'
  ]));
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showStatPicker, setShowStatPicker] = useState(false);
  const [viewMode, setViewMode] = useState('average'); // 'average' or 'schedule'
  
  // Weekly schedule state
  const [teamASchedule, setTeamASchedule] = useState([]);
  const [teamBSchedule, setTeamBSchedule] = useState([]);
  const [expandedGameA, setExpandedGameA] = useState(null);
  const [expandedGameB, setExpandedGameB] = useState(null);
  const [scheduleFilter, setScheduleFilter] = useState('all'); // 'all', 'division', 'home', 'away'
  
  const navigate = useNavigate();

  // Generate season years (1999-2025)
  const seasons = [];
  for (let year = 2025; year >= 1999; year--) {
    seasons.push(year);
  }

  // Load Team A teams when season changes
  useEffect(() => {
    if (seasonA) {
      loadTeamsA();
    }
  }, [seasonA]);

  // Load Team B teams when season changes
  useEffect(() => {
    if (seasonB) {
      loadTeamsB();
    }
  }, [seasonB]);

  // Load Team A data when selected
  useEffect(() => {
    if (selectedTeamA && seasonA) {
      loadTeamData('A', selectedTeamA, seasonA);
      if (viewMode === 'schedule') {
        loadTeamSchedule('A', selectedTeamA, seasonA);
      }
    }
  }, [selectedTeamA, seasonA, viewMode]);

  // Load Team B data when selected
  useEffect(() => {
    if (selectedTeamB && seasonB) {
      loadTeamData('B', selectedTeamB, seasonB);
      if (viewMode === 'schedule') {
        loadTeamSchedule('B', selectedTeamB, seasonB);
      }
    }
  }, [selectedTeamB, seasonB, viewMode]);

  const loadTeamsA = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/hcl/teams?season=${seasonA}`);
      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to load teams');
      }
      
      setTeamAList(data.teams);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadTeamsB = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/hcl/teams?season=${seasonB}`);
      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to load teams');
      }
      
      setTeamBList(data.teams);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadTeamData = async (team, abbr, season) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/hcl/teams/${abbr}?season=${season}`);
      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to load team data');
      }
      
      if (team === 'A') {
        setTeamAData(data.team);
      } else {
        setTeamBData(data.team);
      }
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadTeamSchedule = async (team, abbr, season) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/hcl/teams/${abbr}/games?season=${season}&limit=50`);
      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to load schedule');
      }
      
      // Sort by week ascending
      const sortedGames = data.games.sort((a, b) => a.week - b.week);
      
      if (team === 'A') {
        setTeamASchedule(sortedGames);
      } else {
        setTeamBSchedule(sortedGames);
      }
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getTeamLogo = (teamAbbr) => {
    return `https://a.espncdn.com/i/teamlogos/nfl/500/${teamAbbr}.png`;
  };

  const formatStatValue = (value, format) => {
    if (value === null || value === undefined) return 'N/A';
    
    switch (format) {
      case 'int':
        return Math.round(value);
      case 'percent':
        return `${parseFloat(value).toFixed(1)}%`;
      case 'decimal':
        return parseFloat(value).toFixed(1);
      default:
        return value;
    }
  };

  const formatGameDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const getFilteredSchedule = (schedule) => {
    if (!schedule) return [];
    
    switch (scheduleFilter) {
      case 'division':
        return schedule.filter(game => game.is_divisional_game);
      case 'home':
        return schedule.filter(game => game.is_home);
      case 'away':
        return schedule.filter(game => !game.is_home);
      default:
        return schedule;
    }
  };

  const getDivisionStats = (schedule) => {
    if (!schedule || schedule.length === 0) return { wins: 0, losses: 0, total: 0 };
    
    const divGames = schedule.filter(game => game.is_divisional_game && game.result);
    const wins = divGames.filter(game => game.result === 'W').length;
    const losses = divGames.filter(game => game.result === 'L').length;
    
    return { wins, losses, total: divGames.length };
  };

  const getCommonOpponents = () => {
    if (!teamASchedule.length || !teamBSchedule.length) return [];
    
    const opponentsA = new Set(teamASchedule.map(g => g.opponent));
    const opponentsB = new Set(teamBSchedule.map(g => g.opponent));
    
    return [...opponentsA].filter(opp => opponentsB.has(opp));
  };

  const getHeadToHead = () => {
    if (!teamAData || !teamBData) return null;
    
    const teamAPlaysB = teamASchedule.find(g => g.opponent === teamBData.team);
    const teamBPlaysA = teamBSchedule.find(g => g.opponent === teamAData.team);
    
    return teamAPlaysB || teamBPlaysA || null;
  };

  const toggleStat = (statKey) => {
    setSelectedStats(prev => {
      const newSet = new Set(prev);
      if (newSet.has(statKey)) {
        newSet.delete(statKey);
      } else {
        newSet.add(statKey);
      }
      return newSet;
    });
  };

  const selectAllInCategory = (category) => {
    setSelectedStats(prev => {
      const newSet = new Set(prev);
      STAT_CATEGORIES[category].forEach(stat => newSet.add(stat.key));
      return newSet;
    });
  };

  const clearAllInCategory = (category) => {
    setSelectedStats(prev => {
      const newSet = new Set(prev);
      STAT_CATEGORIES[category].forEach(stat => newSet.delete(stat.key));
      return newSet;
    });
  };

  const selectAll = () => {
    const allStats = new Set();
    Object.values(STAT_CATEGORIES).forEach(category => {
      category.forEach(stat => allStats.add(stat.key));
    });
    setSelectedStats(allStats);
  };

  const clearAll = () => {
    setSelectedStats(new Set());
  };

  if (loading && !teamAList.length) {
    return (
      <div className="game-statistics">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  return (
    <div className="game-statistics">
      {/* Header */}
      <div className="stats-header">
        <h1>📊 Historical Stats - À La Carte</h1>
        <p className="subtitle">Pick your stats, compare any teams from any seasons (1999-2025)</p>
      </div>

      {error && (
        <div className="error-banner">
          ⚠️ {error}
        </div>
      )}

      {/* Stat Picker Toggle Button */}
      <div className="stat-picker-toggle">
        <button 
          className="toggle-picker-btn"
          onClick={() => setShowStatPicker(!showStatPicker)}
        >
          {showStatPicker ? '✖ Hide' : '⚙️ Customize'} Stats ({selectedStats.size} selected)
        </button>
      </div>

      {/* View Mode Toggle */}
      <div className="view-mode-toggle">
        <button 
          className={`view-mode-btn ${viewMode === 'average' ? 'active' : ''}`}
          onClick={() => setViewMode('average')}
        >
          📊 Season Average
        </button>
        <button 
          className={`view-mode-btn ${viewMode === 'schedule' ? 'active' : ''}`}
          onClick={() => setViewMode('schedule')}
        >
          📅 Weekly Schedule
        </button>
      </div>

      {/* Stat Picker Panel */}
      {showStatPicker && (
        <div className="stat-picker-panel">
          <div className="picker-header">
            <h3>Choose Your Stats</h3>
            <div className="picker-actions">
              <button onClick={selectAll} className="action-btn">Select All</button>
              <button onClick={clearAll} className="action-btn">Clear All</button>
            </div>
          </div>
          
          <div className="stat-categories-grid">
            {Object.entries(STAT_CATEGORIES).map(([category, stats]) => (
              <div key={category} className="stat-category-picker">
                <div className="category-picker-header">
                  <h4>{category}</h4>
                  <div className="category-picker-actions">
                    <button 
                      onClick={() => selectAllInCategory(category)}
                      className="mini-btn"
                    >
                      All
                    </button>
                    <button 
                      onClick={() => clearAllInCategory(category)}
                      className="mini-btn"
                    >
                      None
                    </button>
                  </div>
                </div>
                <div className="stat-checkboxes">
                  {stats.map(stat => (
                    <label key={stat.key} className="stat-checkbox-label">
                      <input
                        type="checkbox"
                        checked={selectedStats.has(stat.key)}
                        onChange={() => toggleStat(stat.key)}
                      />
                      <span>{stat.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Conditional rendering based on view mode */}
      {viewMode === 'average' && (
        /* Two-Team Comparison Layout - Season Average View */
        <div className="comparison-container">
          {/* Team A Card */}
          <div className="team-card team-a-card">
          <div className="team-card-header">
            <h2>Team A</h2>
          </div>
          
          {/* Team A Season Selector */}
          <div className="team-season-selector">
            <label htmlFor="seasonA-select">📅 Season:</label>
            <select
              id="seasonA-select"
              value={seasonA}
              onChange={(e) => {
                setSeasonA(e.target.value);
                setSelectedTeamA('');
                setTeamAData(null);
              }}
              className="season-dropdown-small"
            >
              {seasons.map(year => (
                <option key={year} value={year}>
                  {year}
                </option>
              ))}
            </select>
          </div>
          
          <div className="team-selector">
            <label htmlFor="teamA-select">Select Team:</label>
            <select
              id="teamA-select"
              value={selectedTeamA}
              onChange={(e) => setSelectedTeamA(e.target.value)}
              className="team-dropdown"
            >
              <option value="">-- Choose Team --</option>
              {teamAList.map(team => (
                <option key={team.team} value={team.team}>
                  {team.team} ({team.wins || 0}-{team.losses || 0}{(team.ties || 0) > 0 ? `-${team.ties}` : ''})
                </option>
              ))}
            </select>
          </div>

          {teamAData && (
            <>
              <div className="team-logo-display">
                <img 
                  src={getTeamLogo(teamAData.team)} 
                  alt={teamAData.team}
                  className="team-logo"
                  onError={(e) => { e.target.style.display = 'none'; }}
                />
                <div className="team-record-badge">
                  {teamAData.wins}-{teamAData.losses}{(teamAData.ties || 0) > 0 ? `-${teamAData.ties}` : ''}
                </div>
              </div>

              <div className="stats-display">
                {Object.entries(STAT_CATEGORIES).map(([category, stats]) => {
                  const visibleStats = stats.filter(stat => selectedStats.has(stat.key));
                  if (visibleStats.length === 0) return null;

                  return (
                    <div key={category} className="stat-category">
                      <h4 className="category-title">{category}</h4>
                      <div className="stat-rows">
                        {visibleStats.map(stat => (
                          <div key={stat.key} className="stat-row">
                            <span className="stat-label">{stat.label}</span>
                            <span className="stat-value">
                              {formatStatValue(teamAData[stat.key], stat.format)}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            </>
          )}

          {!teamAData && selectedTeamA && (
            <div className="no-data-message">
              <p>Loading team data...</p>
            </div>
          )}

          {!selectedTeamA && (
            <div className="no-data-message">
              <p>Select a team to view statistics</p>
            </div>
          )}
        </div>

        {/* Team B Card */}
        <div className="team-card team-b-card">
          <div className="team-card-header">
            <h2>Team B</h2>
          </div>
          
          {/* Team B Season Selector */}
          <div className="team-season-selector">
            <label htmlFor="seasonB-select">📅 Season:</label>
            <select
              id="seasonB-select"
              value={seasonB}
              onChange={(e) => {
                setSeasonB(e.target.value);
                setSelectedTeamB('');
                setTeamBData(null);
              }}
              className="season-dropdown-small"
            >
              {seasons.map(year => (
                <option key={year} value={year}>
                  {year}
                </option>
              ))}
            </select>
          </div>
          
          <div className="team-selector">
            <label htmlFor="teamB-select">Select Team:</label>
            <select
              id="teamB-select"
              value={selectedTeamB}
              onChange={(e) => setSelectedTeamB(e.target.value)}
              className="team-dropdown"
            >
              <option value="">-- Choose Team --</option>
              {teamBList.map(team => (
                <option key={team.team} value={team.team}>
                  {team.team} ({team.wins || 0}-{team.losses || 0}{(team.ties || 0) > 0 ? `-${team.ties}` : ''})
                </option>
              ))}
            </select>
          </div>

          {teamBData && (
            <>
              <div className="team-logo-display">
                <img 
                  src={getTeamLogo(teamBData.team)} 
                  alt={teamBData.team}
                  className="team-logo"
                  onError={(e) => { e.target.style.display = 'none'; }}
                />
                <div className="team-record-badge">
                  {teamBData.wins}-{teamBData.losses}{(teamBData.ties || 0) > 0 ? `-${teamBData.ties}` : ''}
                </div>
              </div>

              <div className="stats-display">
                {Object.entries(STAT_CATEGORIES).map(([category, stats]) => {
                  const visibleStats = stats.filter(stat => selectedStats.has(stat.key));
                  if (visibleStats.length === 0) return null;

                  return (
                    <div key={category} className="stat-category">
                      <h4 className="category-title">{category}</h4>
                      <div className="stat-rows">
                        {visibleStats.map(stat => (
                          <div key={stat.key} className="stat-row">
                            <span className="stat-label">{stat.label}</span>
                            <span className="stat-value">
                              {formatStatValue(teamBData[stat.key], stat.format)}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            </>
          )}

          {!teamBData && selectedTeamB && (
            <div className="no-data-message">
              <p>Loading team data...</p>
            </div>
          )}

          {!selectedTeamB && (
            <div className="no-data-message">
              <p>Select a team to view statistics</p>
            </div>
          )}
        </div>
      </div>
      )}

      {viewMode === 'schedule' && (
        /* Weekly Schedule View */
        <div className="schedule-view-container">
          {/* Schedule Filters */}
          {(selectedTeamA || selectedTeamB) && (
            <div className="schedule-filters">
              <button 
                className={`filter-btn ${scheduleFilter === 'all' ? 'active' : ''}`}
                onClick={() => setScheduleFilter('all')}
              >
                All Games
              </button>
              <button 
                className={`filter-btn ${scheduleFilter === 'division' ? 'active' : ''}`}
                onClick={() => setScheduleFilter('division')}
              >
                🏆 Division Only
              </button>
              <button 
                className={`filter-btn ${scheduleFilter === 'home' ? 'active' : ''}`}
                onClick={() => setScheduleFilter('home')}
              >
                🏠 Home
              </button>
              <button 
                className={`filter-btn ${scheduleFilter === 'away' ? 'active' : ''}`}
                onClick={() => setScheduleFilter('away')}
              >
                ✈️ Away
              </button>
            </div>
          )}

          {/* Head-to-Head Alert */}
          {selectedTeamA && selectedTeamB && getHeadToHead() && (
            <div className="head-to-head-alert">
              <h4>📌 Head-to-Head Matchup</h4>
              <p>
                {teamAData.team} vs {teamBData.team} - Week {getHeadToHead().week}
                {getHeadToHead().result && ` (${getHeadToHead().result === 'W' ? teamAData.team : teamBData.team} won ${getHeadToHead().team_points}-${getHeadToHead().home_score === getHeadToHead().team_points ? getHeadToHead().away_score : getHeadToHead().home_score})`}
              </p>
            </div>
          )}

          <div className="comparison-container">
            {/* Team A Schedule */}
            <div className="team-schedule-card team-a-card">
              <div className="team-card-header">
                <h2>Team A Schedule</h2>
              </div>
              
              {/* Team A Season Selector */}
              <div className="team-season-selector">
                <label htmlFor="seasonA-select-sched">📅 Season:</label>
                <select
                  id="seasonA-select-sched"
                  value={seasonA}
                  onChange={(e) => {
                    setSeasonA(e.target.value);
                    setSelectedTeamA('');
                    setTeamAData(null);
                    setTeamASchedule([]);
                  }}
                  className="season-dropdown-small"
                >
                  {seasons.map(year => (
                    <option key={year} value={year}>
                      {year}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="team-selector">
                <label htmlFor="teamA-select-sched">Select Team:</label>
                <select
                  id="teamA-select-sched"
                  value={selectedTeamA}
                  onChange={(e) => setSelectedTeamA(e.target.value)}
                  className="team-dropdown"
                >
                  <option value="">-- Choose Team --</option>
                  {teamAList.map(team => (
                    <option key={team.team} value={team.team}>
                      {team.team} ({team.wins || 0}-{team.losses || 0}{(team.ties || 0) > 0 ? `-${team.ties}` : ''})
                    </option>
                  ))}
                </select>
              </div>

              {selectedTeamA && teamAData && (
                <>
                  <div className="team-logo-display">
                    <img 
                      src={getTeamLogo(teamAData.team)} 
                      alt={teamAData.team}
                      className="team-logo"
                    />
                    <h3>{teamAData.team}</h3>
                    <div className="team-record-badge">
                      {teamAData.wins}-{teamAData.losses}{(teamAData.ties || 0) > 0 ? `-${teamAData.ties}` : ''}
                    </div>
                  </div>

                  {/* Division Stats Widget */}
                  {teamASchedule.length > 0 && (
                    <div className="division-stats-widget">
                      <h4>Division Record</h4>
                      <div className="division-record">
                        {getDivisionStats(teamASchedule).wins}-{getDivisionStats(teamASchedule).losses}
                        <span className="division-games-total">
                          ({getDivisionStats(teamASchedule).total} games)
                        </span>
                      </div>
                    </div>
                  )}

                  {/* Schedule Table */}
                  <div className="schedule-table">
                    {getFilteredSchedule(teamASchedule).length === 0 ? (
                      <div className="no-games-message">
                        No games match the selected filter
                      </div>
                    ) : (
                      getFilteredSchedule(teamASchedule).map((game) => {
                        const isCommonOpp = getCommonOpponents().includes(game.opponent);
                        return (
                          <div 
                            key={game.game_id} 
                            className={`schedule-game-row ${game.is_divisional_game ? 'division-game' : ''} ${game.result === 'W' ? 'win' : game.result === 'L' ? 'loss' : 'upcoming'}`}
                          >
                            <div 
                              className="game-row-header"
                              onClick={() => setExpandedGameA(expandedGameA === game.game_id ? null : game.game_id)}
                            >
                              <div className="game-week">
                                Week {game.week}
                                {game.is_divisional_game && <span className="division-badge">🏆</span>}
                                {isCommonOpp && <span className="common-opp-badge">⚡</span>}
                              </div>
                              <div className="game-date">{formatGameDate(game.game_date)}</div>
                              <div className="game-matchup">
                                <img src={getTeamLogo(game.opponent)} alt={game.opponent} className="opponent-logo-small" />
                                {game.is_home ? 'vs' : '@'} {game.opponent}
                              </div>
                              <div className="game-result">
                                {game.result ? (
                                  <span className={`result-badge ${game.result === 'W' ? 'win-badge' : 'loss-badge'}`}>
                                    {game.result} {game.team_points}-{game.is_home ? game.away_score : game.home_score}
                                  </span>
                                ) : (
                                  <span className="upcoming-badge">TBD</span>
                                )}
                              </div>
                              <div className="expand-icon">{expandedGameA === game.game_id ? '▼' : '▶'}</div>
                            </div>
                            
                            {expandedGameA === game.game_id && (
                              <div className="game-row-details">
                                <div className="game-stats-grid">
                                  <div className="stat-item">
                                    <span className="stat-label">Total Yards</span>
                                    <span className="stat-value">{game.total_yards || 'N/A'}</span>
                                  </div>
                                  <div className="stat-item">
                                    <span className="stat-label">Pass Yards</span>
                                    <span className="stat-value">{game.passing_yards || 'N/A'}</span>
                                  </div>
                                  <div className="stat-item">
                                    <span className="stat-label">Rush Yards</span>
                                    <span className="stat-value">{game.rushing_yards || 'N/A'}</span>
                                  </div>
                                  <div className="stat-item">
                                    <span className="stat-label">Completion %</span>
                                    <span className="stat-value">{game.completion_pct ? `${game.completion_pct}%` : 'N/A'}</span>
                                  </div>
                                  <div className="stat-item">
                                    <span className="stat-label">Yards/Play</span>
                                    <span className="stat-value">{game.yards_per_play || 'N/A'}</span>
                                  </div>
                                  <div className="stat-item">
                                    <span className="stat-label">Third Down %</span>
                                    <span className="stat-value">{game.third_down_pct ? `${game.third_down_pct}%` : 'N/A'}</span>
                                  </div>
                                  <div className="stat-item">
                                    <span className="stat-label">Turnovers</span>
                                    <span className="stat-value">{game.turnovers !== null ? game.turnovers : 'N/A'}</span>
                                  </div>
                                  <div className="stat-item">
                                    <span className="stat-label">Rest Days</span>
                                    <span className="stat-value">{game.rest_days || 'N/A'}</span>
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>
                        );
                      })
                    )}
                  </div>
                </>
              )}

              {!selectedTeamA && (
                <div className="no-data-message">
                  <p>Select a team to view schedule</p>
                </div>
              )}
            </div>

            {/* Team B Schedule */}
            <div className="team-schedule-card team-b-card">
              <div className="team-card-header">
                <h2>Team B Schedule</h2>
              </div>
              
              {/* Team B Season Selector */}
              <div className="team-season-selector">
                <label htmlFor="seasonB-select-sched">📅 Season:</label>
                <select
                  id="seasonB-select-sched"
                  value={seasonB}
                  onChange={(e) => {
                    setSeasonB(e.target.value);
                    setSelectedTeamB('');
                    setTeamBData(null);
                    setTeamBSchedule([]);
                  }}
                  className="season-dropdown-small"
                >
                  {seasons.map(year => (
                    <option key={year} value={year}>
                      {year}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="team-selector">
                <label htmlFor="teamB-select-sched">Select Team:</label>
                <select
                  id="teamB-select-sched"
                  value={selectedTeamB}
                  onChange={(e) => setSelectedTeamB(e.target.value)}
                  className="team-dropdown"
                >
                  <option value="">-- Choose Team --</option>
                  {teamBList.map(team => (
                    <option key={team.team} value={team.team}>
                      {team.team} ({team.wins || 0}-{team.losses || 0}{(team.ties || 0) > 0 ? `-${team.ties}` : ''})
                    </option>
                  ))}
                </select>
              </div>

              {selectedTeamB && teamBData && (
                <>
                  <div className="team-logo-display">
                    <img 
                      src={getTeamLogo(teamBData.team)} 
                      alt={teamBData.team}
                      className="team-logo"
                    />
                    <h3>{teamBData.team}</h3>
                    <div className="team-record-badge">
                      {teamBData.wins}-{teamBData.losses}{(teamBData.ties || 0) > 0 ? `-${teamBData.ties}` : ''}
                    </div>
                  </div>

                  {/* Division Stats Widget */}
                  {teamBSchedule.length > 0 && (
                    <div className="division-stats-widget">
                      <h4>Division Record</h4>
                      <div className="division-record">
                        {getDivisionStats(teamBSchedule).wins}-{getDivisionStats(teamBSchedule).losses}
                        <span className="division-games-total">
                          ({getDivisionStats(teamBSchedule).total} games)
                        </span>
                      </div>
                    </div>
                  )}

                  {/* Schedule Table */}
                  <div className="schedule-table">
                    {getFilteredSchedule(teamBSchedule).length === 0 ? (
                      <div className="no-games-message">
                        No games match the selected filter
                      </div>
                    ) : (
                      getFilteredSchedule(teamBSchedule).map((game) => {
                        const isCommonOpp = getCommonOpponents().includes(game.opponent);
                        return (
                          <div 
                            key={game.game_id} 
                            className={`schedule-game-row ${game.is_divisional_game ? 'division-game' : ''} ${game.result === 'W' ? 'win' : game.result === 'L' ? 'loss' : 'upcoming'}`}
                          >
                            <div 
                              className="game-row-header"
                              onClick={() => setExpandedGameB(expandedGameB === game.game_id ? null : game.game_id)}
                            >
                              <div className="game-week">
                                Week {game.week}
                                {game.is_divisional_game && <span className="division-badge">🏆</span>}
                                {isCommonOpp && <span className="common-opp-badge">⚡</span>}
                              </div>
                              <div className="game-date">{formatGameDate(game.game_date)}</div>
                              <div className="game-matchup">
                                <img src={getTeamLogo(game.opponent)} alt={game.opponent} className="opponent-logo-small" />
                                {game.is_home ? 'vs' : '@'} {game.opponent}
                              </div>
                              <div className="game-result">
                                {game.result ? (
                                  <span className={`result-badge ${game.result === 'W' ? 'win-badge' : 'loss-badge'}`}>
                                    {game.result} {game.team_points}-{game.is_home ? game.away_score : game.home_score}
                                  </span>
                                ) : (
                                  <span className="upcoming-badge">TBD</span>
                                )}
                              </div>
                              <div className="expand-icon">{expandedGameB === game.game_id ? '▼' : '▶'}</div>
                            </div>
                            
                            {expandedGameB === game.game_id && (
                              <div className="game-row-details">
                                <div className="game-stats-grid">
                                  <div className="stat-item">
                                    <span className="stat-label">Total Yards</span>
                                    <span className="stat-value">{game.total_yards || 'N/A'}</span>
                                  </div>
                                  <div className="stat-item">
                                    <span className="stat-label">Pass Yards</span>
                                    <span className="stat-value">{game.passing_yards || 'N/A'}</span>
                                  </div>
                                  <div className="stat-item">
                                    <span className="stat-label">Rush Yards</span>
                                    <span className="stat-value">{game.rushing_yards || 'N/A'}</span>
                                  </div>
                                  <div className="stat-item">
                                    <span className="stat-label">Completion %</span>
                                    <span className="stat-value">{game.completion_pct ? `${game.completion_pct}%` : 'N/A'}</span>
                                  </div>
                                  <div className="stat-item">
                                    <span className="stat-label">Yards/Play</span>
                                    <span className="stat-value">{game.yards_per_play || 'N/A'}</span>
                                  </div>
                                  <div className="stat-item">
                                    <span className="stat-label">Third Down %</span>
                                    <span className="stat-value">{game.third_down_pct ? `${game.third_down_pct}%` : 'N/A'}</span>
                                  </div>
                                  <div className="stat-item">
                                    <span className="stat-label">Turnovers</span>
                                    <span className="stat-value">{game.turnovers !== null ? game.turnovers : 'N/A'}</span>
                                  </div>
                                  <div className="stat-item">
                                    <span className="stat-label">Rest Days</span>
                                    <span className="stat-value">{game.rest_days || 'N/A'}</span>
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>
                        );
                      })
                    )}
                  </div>
                </>
              )}

              {!selectedTeamB && (
                <div className="no-data-message">
                  <p>Select a team to view schedule</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default GameStatistics;
