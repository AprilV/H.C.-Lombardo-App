import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './GameStatistics.css';

const API_URL = 'http://127.0.0.1:5000';

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

function GameStatistics() {
  // Team A state (with its own season)
  const [seasonA, setSeasonA] = useState('2025');
  const [teamAList, setTeamAList] = useState([]);
  const [selectedTeamA, setSelectedTeamA] = useState('');
  const [teamAData, setTeamAData] = useState(null);
  
  // Team B state (with its own season)
  const [seasonB, setSeasonB] = useState('2025');
  const [teamBList, setTeamBList] = useState([]);
  const [selectedTeamB, setSelectedTeamB] = useState('');
  const [teamBData, setTeamBData] = useState(null);
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expandedCategories, setExpandedCategories] = useState({
    'Record': true,
    'Scoring': true,
    'Offense': true,
  });
  
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
    }
  }, [selectedTeamA, seasonA]);

  // Load Team B data when selected
  useEffect(() => {
    if (selectedTeamB && seasonB) {
      loadTeamData('B', selectedTeamB, seasonB);
    }
  }, [selectedTeamB, seasonB]);

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

  const getTeamLogo = (teamAbbr) => {
    // ESPN team logos
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

  const calculateDifferential = (teamAVal, teamBVal, format) => {
    if (teamAVal === null || teamAVal === undefined || teamBVal === null || teamBVal === undefined) {
      return { diff: null, display: '---', better: 'none' };
    }
    
    const diff = teamAVal - teamBVal;
    const absDiff = Math.abs(diff);
    
    let display = '';
    if (format === 'percent') {
      display = `${absDiff.toFixed(1)}%`;
    } else if (format === 'decimal') {
      display = absDiff.toFixed(1);
    } else {
      display = Math.round(absDiff).toString();
    }
    
    // Determine which team is better (higher is better for most stats, except turnovers/penalties)
    const better = diff > 0 ? 'A' : diff < 0 ? 'B' : 'tie';
    
    return { diff, display, better };
  };

  const toggleCategory = (category) => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
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
        <h1>🏈 Team Matchup Comparison</h1>
        <p className="subtitle">Compare any two teams from any season • All 58 statistics</p>
      </div>

      {error && (
        <div className="error-banner">
          ⚠️ {error}
        </div>
      )}

      {/* Two-Team Comparison Layout */}
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
              <option value="">-- Choose Team A --</option>
              {teamAList.map(team => (
                <option key={team.team} value={team.team}>
                  {team.team} ({team.wins || 0}-{team.losses || 0})
                </option>
              ))}
            </select>
          </div>

          {teamAData ? (
            <div className="team-stats-display">
              {/* Team Logo */}
              <div className="team-logo-container">
                <img 
                  src={getTeamLogo(selectedTeamA)} 
                  alt={`${selectedTeamA} logo`}
                  className="team-logo"
                  onError={(e) => {
                    e.target.style.display = 'none';
                  }}
                />
                <div className="team-name-display">{selectedTeamA}</div>
              </div>
              
              <div className="team-record-badge">
                {teamAData.wins}-{teamAData.losses}
                <span className="record-label">Record ({seasonA})</span>
              </div>
              
              {/* Stats by Category */}
              {Object.entries(STAT_CATEGORIES).map(([category, stats]) => (
                <div key={category} className="stat-category-section">
                  <div 
                    className="category-header"
                    onClick={() => toggleCategory(category)}
                  >
                    <h3>{category}</h3>
                    <span className="toggle-icon">
                      {expandedCategories[category] ? '▼' : '▶'}
                    </span>
                  </div>
                  
                  {expandedCategories[category] && (
                    <div className="category-stats">
                      {stats.map(stat => (
                        <div key={stat.key} className="stat-row">
                          <span className="stat-label">{stat.label}:</span>
                          <span className="stat-value">
                            {formatStatValue(teamAData[stat.key], stat.format)}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-team-state">
              <div className="empty-icon">🏈</div>
              <p>Select Team A</p>
            </div>
          )}
        </div>

        {/* Differential Panel */}
        <div className="differential-panel">
          <div className="differential-header">
            <h2>📊 Comparison</h2>
            <p>Statistical Differentials</p>
          </div>

          {teamAData && teamBData ? (
            <div className="differentials-display">
              {Object.entries(STAT_CATEGORIES).map(([category, stats]) => (
                expandedCategories[category] && (
                  <div key={category} className="diff-category">
                    <h4>{category}</h4>
                    {stats.map(stat => {
                      const { diff, display, better } = calculateDifferential(
                        teamAData[stat.key],
                        teamBData[stat.key],
                        stat.format
                      );
                      
                      return (
                        <div key={stat.key} className={`diff-row ${better !== 'none' ? `better-${better}` : ''}`}>
                          <span className="diff-label">{stat.label}</span>
                          <span className="diff-value">
                            {better === 'A' && '← '}
                            {display}
                            {better === 'B' && ' →'}
                            {better === 'tie' && ' ='}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                )
              ))}
            </div>
          ) : (
            <div className="empty-diff-state">
              <div className="empty-icon">📊</div>
              <p>Select both teams to see statistical comparisons</p>
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
              <option value="">-- Choose Team B --</option>
              {teamBList.map(team => (
                <option key={team.team} value={team.team}>
                  {team.team} ({team.wins || 0}-{team.losses || 0})
                </option>
              ))}
            </select>
          </div>

          {teamBData ? (
            <div className="team-stats-display">
              {/* Team Logo */}
              <div className="team-logo-container">
                <img 
                  src={getTeamLogo(selectedTeamB)} 
                  alt={`${selectedTeamB} logo`}
                  className="team-logo"
                  onError={(e) => {
                    e.target.style.display = 'none';
                  }}
                />
                <div className="team-name-display">{selectedTeamB}</div>
              </div>
              
              <div className="team-record-badge">
                {teamBData.wins}-{teamBData.losses}
                <span className="record-label">Record ({seasonB})</span>
              </div>
              
              {/* Stats by Category */}
              {Object.entries(STAT_CATEGORIES).map(([category, stats]) => (
                <div key={category} className="stat-category-section">
                  <div 
                    className="category-header"
                    onClick={() => toggleCategory(category)}
                  >
                    <h3>{category}</h3>
                    <span className="toggle-icon">
                      {expandedCategories[category] ? '▼' : '▶'}
                    </span>
                  </div>
                  
                  {expandedCategories[category] && (
                    <div className="category-stats">
                      {stats.map(stat => (
                        <div key={stat.key} className="stat-row">
                          <span className="stat-label">{stat.label}:</span>
                          <span className="stat-value">
                            {formatStatValue(teamBData[stat.key], stat.format)}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-team-state">
              <div className="empty-icon">🏈</div>
              <p>Select Team B</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default GameStatistics;
