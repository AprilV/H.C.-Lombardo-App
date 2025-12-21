import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './TeamComparison.css';
import './TeamComparison-light.css';

const API_URL = 'https://api.aprilsykes.dev';

// All available statistics organized by category
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

function TeamComparison() {
  // View Mode
  const [viewMode, setViewMode] = useState('comparison'); // 'comparison', 'schedule', 'head-to-head'
  
  // Team A state
  const [seasonA, setSeasonA] = useState('2025');
  const [teamAList, setTeamAList] = useState([]);
  const [selectedTeamA, setSelectedTeamA] = useState('');
  const [teamAData, setTeamAData] = useState(null);
  const [teamASchedule, setTeamASchedule] = useState([]);
  
  // Team B state
  const [seasonB, setSeasonB] = useState('2025');
  const [teamBList, setTeamBList] = useState([]);
  const [selectedTeamB, setSelectedTeamB] = useState('');
  const [teamBData, setTeamBData] = useState(null);
  const [teamBSchedule, setTeamBSchedule] = useState([]);
  
  // UI state
  const [selectedStats, setSelectedStats] = useState(new Set([
    'ppg', 'total_yards_per_game', 'passing_yards_per_game', 'rushing_yards_per_game',
    'completion_pct', 'qb_rating', 'third_down_pct', 'turnovers_per_game'
  ]));
  const [showStatPicker, setShowStatPicker] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expandedGameA, setExpandedGameA] = useState(null);
  const [expandedGameB, setExpandedGameB] = useState(null);
  
  const navigate = useNavigate();

  // Generate season years (1999-2025)
  const seasons = [];
  for (let year = 2025; year >= 1999; year--) {
    seasons.push(year);
  }

  // Load teams when season changes
  useEffect(() => {
    if (seasonA) loadTeamsA();
  }, [seasonA]);

  useEffect(() => {
    if (seasonB) loadTeamsB();
  }, [seasonB]);

  // Load team data when selection changes
  useEffect(() => {
    if (selectedTeamA && seasonA) {
      loadTeamData('A', selectedTeamA, seasonA);
      if (viewMode === 'schedule') {
        loadTeamSchedule('A', selectedTeamA, seasonA);
      }
    }
  }, [selectedTeamA, seasonA, viewMode]);

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
      if (data.success) {
        setTeamAList(data.teams.sort((a, b) => a.team.localeCompare(b.team)));
        setError(null);
      }
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
      if (data.success) {
        setTeamBList(data.teams.sort((a, b) => a.team.localeCompare(b.team)));
        setError(null);
      }
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
      if (data.success) {
        if (team === 'A') {
          setTeamAData(data.team);
        } else {
          setTeamBData(data.team);
        }
        setError(null);
      }
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
      if (data.success) {
        const sortedGames = data.games.sort((a, b) => a.week - b.week);
        if (team === 'A') {
          setTeamASchedule(sortedGames);
        } else {
          setTeamBSchedule(sortedGames);
        }
        setError(null);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getTeamLogo = (teamAbbr) => {
    return `https://a.espncdn.com/i/teamlogos/nfl/500/${teamAbbr}.png`;
  };

  const formatValue = (value, format) => {
    if (value === null || value === undefined) return 'N/A';
    switch (format) {
      case 'int': return Math.round(value);
      case 'percent': return `${parseFloat(value).toFixed(1)}%`;
      case 'decimal': return parseFloat(value).toFixed(1);
      default: return value;
    }
  };

  const formatGameDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const calculateDifferential = (teamAVal, teamBVal, format) => {
    if (teamAVal === null || teamAVal === undefined || teamBVal === null || teamBVal === undefined) {
      return { diff: null, display: '---', better: 'none' };
    }
    const diff = teamAVal - teamBVal;
    const absDiff = Math.abs(diff);
    let display = '';
    if (format === 'percent') display = `${absDiff.toFixed(1)}%`;
    else if (format === 'decimal') display = absDiff.toFixed(1);
    else display = Math.round(absDiff).toString();
    const better = diff > 0 ? 'A' : diff < 0 ? 'B' : 'tie';
    return { diff, display, better };
  };

  const toggleStat = (statKey) => {
    const newSet = new Set(selectedStats);
    if (newSet.has(statKey)) {
      newSet.delete(statKey);
    } else {
      newSet.add(statKey);
    }
    setSelectedStats(newSet);
  };

  const getSelectedStatsArray = () => {
    const allStats = [];
    Object.entries(STAT_CATEGORIES).forEach(([category, stats]) => {
      stats.forEach(stat => {
        if (selectedStats.has(stat.key)) {
          allStats.push({ ...stat, category });
        }
      });
    });
    return allStats;
  };

  return (
    <div className="team-comparison">
      {/* Header */}
      <div className="comparison-header">
        <h1>📊 Team Comparison & Analysis</h1>
        <p className="subtitle">Compare teams across any season (1999-2025) • Historical stats • Head-to-head matchups • Weekly schedules</p>
      </div>

      {error && (
        <div className="error-banner">⚠️ {error}</div>
      )}

      {/* View Mode Tabs */}
      <div className="view-tabs">
        <button 
          className={`tab-button ${viewMode === 'comparison' ? 'active' : ''}`}
          onClick={() => setViewMode('comparison')}
        >
          📊 Season Averages
        </button>
        <button 
          className={`tab-button ${viewMode === 'head-to-head' ? 'active' : ''}`}
          onClick={() => setViewMode('head-to-head')}
        >
          ⚔️ Head-to-Head
        </button>
        <button 
          className={`tab-button ${viewMode === 'schedule' ? 'active' : ''}`}
          onClick={() => setViewMode('schedule')}
        >
          📅 Weekly Schedules
        </button>
      </div>

      {/* Team Selection Bar */}
      <div className="team-selection-bar">
        <div className="team-select-group">
          <label>Team A</label>
          <select value={seasonA} onChange={(e) => setSeasonA(e.target.value)} className="season-select">
            {seasons.map(year => <option key={year} value={year}>{year}</option>)}
          </select>
          <select 
            value={selectedTeamA} 
            onChange={(e) => setSelectedTeamA(e.target.value)}
            className="team-select"
          >
            <option value="">-- Select Team A --</option>
            {teamAList.map(team => (
              <option key={team.team} value={team.team}>
                {team.team} ({team.wins || 0}-{team.losses || 0})
              </option>
            ))}
          </select>
        </div>

        <div className="vs-divider">VS</div>

        <div className="team-select-group">
          <label>Team B</label>
          <select value={seasonB} onChange={(e) => setSeasonB(e.target.value)} className="season-select">
            {seasons.map(year => <option key={year} value={year}>{year}</option>)}
          </select>
          <select 
            value={selectedTeamB} 
            onChange={(e) => setSelectedTeamB(e.target.value)}
            className="team-select"
          >
            <option value="">-- Select Team B --</option>
            {teamBList.map(team => (
              <option key={team.team} value={team.team}>
                {team.team} ({team.wins || 0}-{team.losses || 0})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Stat Picker (for comparison view) */}
      {viewMode === 'comparison' && (
        <div className="stat-picker-section">
          <button 
            className="stat-picker-toggle-btn"
            onClick={() => setShowStatPicker(!showStatPicker)}
          >
            {showStatPicker ? '✖ Hide' : '⚙️ Customize'} Stats ({selectedStats.size} selected)
          </button>

          {showStatPicker && (
            <div className="stat-picker-panel">
              <div className="stat-picker-grid">
                {Object.entries(STAT_CATEGORIES).map(([category, stats]) => (
                  <div key={category} className="stat-category-box">
                    <h3>{category}</h3>
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
        </div>
      )}

      {/* Content Area */}
      {viewMode === 'comparison' && (
        <div className="comparison-view">
          {(!selectedTeamA || !selectedTeamB) && (
            <div className="empty-state">Select both teams to compare their season averages</div>
          )}

          {selectedTeamA && selectedTeamB && teamAData && teamBData && (
            <div className="comparison-grid">
              {/* Team A Column */}
              <div className="team-column">
                <div className="team-header-card">
                  <img src={getTeamLogo(selectedTeamA)} alt={selectedTeamA} className="team-logo-large" />
                  <h2>{selectedTeamA}</h2>
                  <div className="team-record">{teamAData.wins}-{teamAData.losses}</div>
                  <div className="team-season">{seasonA} Season</div>
                </div>
                <div className="stats-list">
                  {getSelectedStatsArray().map(stat => (
                    <div key={stat.key} className="stat-item">
                      <span className="stat-label">{stat.label}</span>
                      <span className="stat-value">{formatValue(teamAData[stat.key], stat.format)}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Differential Column */}
              <div className="differential-column">
                <div className="differential-header">
                  <h3>Advantage</h3>
                </div>
                <div className="stats-list">
                  {getSelectedStatsArray().map(stat => {
                    const diff = calculateDifferential(teamAData[stat.key], teamBData[stat.key], stat.format);
                    return (
                      <div key={stat.key} className={`stat-item differential-item ${diff.better}`}>
                        <span className="differential-value">{diff.display}</span>
                        <span className="differential-arrow">
                          {diff.better === 'A' ? '←' : diff.better === 'B' ? '→' : '='}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Team B Column */}
              <div className="team-column">
                <div className="team-header-card">
                  <img src={getTeamLogo(selectedTeamB)} alt={selectedTeamB} className="team-logo-large" />
                  <h2>{selectedTeamB}</h2>
                  <div className="team-record">{teamBData.wins}-{teamBData.losses}</div>
                  <div className="team-season">{seasonB} Season</div>
                </div>
                <div className="stats-list">
                  {getSelectedStatsArray().map(stat => (
                    <div key={stat.key} className="stat-item">
                      <span className="stat-label">{stat.label}</span>
                      <span className="stat-value">{formatValue(teamBData[stat.key], stat.format)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {viewMode === 'head-to-head' && (
        <div className="head-to-head-view">
          {(!selectedTeamA || !selectedTeamB) && (
            <div className="empty-state">Select both teams for head-to-head analysis</div>
          )}

          {selectedTeamA && selectedTeamB && teamAData && teamBData && (
            <div className="head-to-head-grid">
              {Object.entries(STAT_CATEGORIES).map(([category, stats]) => (
                <div key={category} className="h2h-category-card">
                  <h3 className="h2h-category-title">{category}</h3>
                  <div className="h2h-stats-table">
                    <div className="h2h-table-header">
                      <div className="h2h-cell h2h-team">{selectedTeamA}</div>
                      <div className="h2h-cell h2h-stat">Statistic</div>
                      <div className="h2h-cell h2h-team">{selectedTeamB}</div>
                    </div>
                    {stats.map(stat => {
                      const diff = calculateDifferential(teamAData[stat.key], teamBData[stat.key], stat.format);
                      return (
                        <div key={stat.key} className="h2h-table-row">
                          <div className={`h2h-cell h2h-value ${diff.better === 'A' ? 'winner' : ''}`}>
                            {formatValue(teamAData[stat.key], stat.format)}
                          </div>
                          <div className="h2h-cell h2h-stat-label">{stat.label}</div>
                          <div className={`h2h-cell h2h-value ${diff.better === 'B' ? 'winner' : ''}`}>
                            {formatValue(teamBData[stat.key], stat.format)}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {viewMode === 'schedule' && (
        <div className="schedule-view">
          <div className="schedule-grid">
            {/* Team A Schedule */}
            <div className="schedule-column">
              <h3 className="schedule-column-title">
                {selectedTeamA ? `${selectedTeamA} - ${seasonA}` : 'Team A Schedule'}
              </h3>
              {selectedTeamA && teamASchedule.length > 0 ? (
                teamASchedule.map(game => (
                  <div key={game.game_id} className={`schedule-game-card ${game.result === 'W' ? 'win' : game.result === 'L' ? 'loss' : 'upcoming'}`}>
                    <div className="game-header" onClick={() => setExpandedGameA(expandedGameA === game.game_id ? null : game.game_id)}>
                      <div className="game-week-date">
                        <span className="game-week">Week {game.week}</span>
                        <span className="game-date">{formatGameDate(game.game_date)}</span>
                      </div>
                      <div className="game-matchup-info">
                        <img src={getTeamLogo(game.opponent)} alt={game.opponent} className="opponent-logo-sm" />
                        <span className="opponent-name">{game.is_home ? 'vs' : '@'} {game.opponent}</span>
                      </div>
                      <div className="game-result-badge">
                        {game.result ? `${game.result} ${game.team_points}-${game.is_home ? game.away_score : game.home_score}` : 'TBD'}
                      </div>
                    </div>
                    {expandedGameA === game.game_id && (
                      <div className="game-details">
                        <div className="game-stats-row">
                          <div className="game-stat"><label>Total Yards</label><span>{game.total_yards || 'N/A'}</span></div>
                          <div className="game-stat"><label>Pass Yards</label><span>{game.passing_yards || 'N/A'}</span></div>
                          <div className="game-stat"><label>Rush Yards</label><span>{game.rushing_yards || 'N/A'}</span></div>
                          <div className="game-stat"><label>Turnovers</label><span>{game.turnovers ?? 'N/A'}</span></div>
                        </div>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="empty-state-small">Select Team A to view schedule</div>
              )}
            </div>

            {/* Team B Schedule */}
            <div className="schedule-column">
              <h3 className="schedule-column-title">
                {selectedTeamB ? `${selectedTeamB} - ${seasonB}` : 'Team B Schedule'}
              </h3>
              {selectedTeamB && teamBSchedule.length > 0 ? (
                teamBSchedule.map(game => (
                  <div key={game.game_id} className={`schedule-game-card ${game.result === 'W' ? 'win' : game.result === 'L' ? 'loss' : 'upcoming'}`}>
                    <div className="game-header" onClick={() => setExpandedGameB(expandedGameB === game.game_id ? null : game.game_id)}>
                      <div className="game-week-date">
                        <span className="game-week">Week {game.week}</span>
                        <span className="game-date">{formatGameDate(game.game_date)}</span>
                      </div>
                      <div className="game-matchup-info">
                        <img src={getTeamLogo(game.opponent)} alt={game.opponent} className="opponent-logo-sm" />
                        <span className="opponent-name">{game.is_home ? 'vs' : '@'} {game.opponent}</span>
                      </div>
                      <div className="game-result-badge">
                        {game.result ? `${game.result} ${game.team_points}-${game.is_home ? game.away_score : game.home_score}` : 'TBD'}
                      </div>
                    </div>
                    {expandedGameB === game.game_id && (
                      <div className="game-details">
                        <div className="game-stats-row">
                          <div className="game-stat"><label>Total Yards</label><span>{game.total_yards || 'N/A'}</span></div>
                          <div className="game-stat"><label>Pass Yards</label><span>{game.passing_yards || 'N/A'}</span></div>
                          <div className="game-stat"><label>Rush Yards</label><span>{game.rushing_yards || 'N/A'}</span></div>
                          <div className="game-stat"><label>Turnovers</label><span>{game.turnovers ?? 'N/A'}</span></div>
                        </div>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="empty-state-small">Select Team B to view schedule</div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default TeamComparison;
