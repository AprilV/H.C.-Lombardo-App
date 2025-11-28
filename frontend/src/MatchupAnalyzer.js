import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './MatchupAnalyzer.css';

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

function MatchupAnalyzer() {
  // Team A state
  const [teamAList, setTeamAList] = useState([]);
  const [selectedTeamA, setSelectedTeamA] = useState('');
  const [teamAData, setTeamAData] = useState(null);
  
  // Team B state
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
  const season = 2025; // Current season only for matchup analysis

  // Load teams on mount
  useEffect(() => {
    loadTeams();
  }, []);

  // Load team data when selection changes
  useEffect(() => {
    if (selectedTeamA) {
      loadTeamData('A', selectedTeamA);
    }
  }, [selectedTeamA]);

  useEffect(() => {
    if (selectedTeamB) {
      loadTeamData('B', selectedTeamB);
    }
  }, [selectedTeamB]);

  const loadTeams = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/hcl/teams?season=${season}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setTeamAList(data.teams || []);
      setTeamBList(data.teams || []);
      setError(null);
    } catch (err) {
      console.error('Error loading teams:', err);
      setError('Failed to load teams. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const loadTeamData = async (team, abbr) => {
    try {
      const response = await fetch(`${API_URL}/api/hcl/teams/${abbr}?season=${season}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (team === 'A') {
        setTeamAData(data.team);
      } else {
        setTeamBData(data.team);
      }
      
      setError(null);
    } catch (err) {
      console.error(`Error loading team ${team} data:`, err);
      setError(`Failed to load ${abbr} data. Please try again.`);
    }
  };

  const getTeamLogo = (teamAbbr) => {
    return `https://a.espncdn.com/i/teamlogos/nfl/500/${teamAbbr}.png`;
  };

  const formatValue = (value, format) => {
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
      <div className="matchup-analyzer">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  return (
    <div className="matchup-analyzer">
      {/* Header */}
      <div className="matchup-header">
        <h1>🎯 Matchup Analyzer</h1>
        <p className="subtitle">Head-to-head comparison • 2025 Season • Statistical edge analysis</p>
      </div>

      {error && (
        <div className="error-banner">
          ⚠️ {error}
        </div>
      )}

      {/* Three-Column Matchup Layout */}
      <div className="matchup-container">
        {/* Team A Card */}
        <div className="team-card team-a-card">
          <div className="team-card-header">
            <h2>Team A</h2>
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
                  {team.team} ({team.wins || 0}-{team.losses || 0}{(team.ties || 0) > 0 ? `-${team.ties}` : ''})
                </option>
              ))}
            </select>
          </div>

          {teamAData && (
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
                {teamAData.wins}-{teamAData.losses}{(teamAData.ties || 0) > 0 ? `-${teamAData.ties}` : ''}
                <span className="record-label">2025 Record</span>
              </div>

              {/* Stats Categories */}
              <div className="stats-categories">
                {Object.entries(STAT_CATEGORIES).map(([category, stats]) => (
                  <div key={category} className="stat-category">
                    <div 
                      className="category-header"
                      onClick={() => toggleCategory(category)}
                    >
                      <h3>{category}</h3>
                      <span className="toggle-icon">
                        {expandedCategories[category] ? '−' : '+'}
                      </span>
                    </div>
                    
                    {expandedCategories[category] && (
                      <div className="category-stats">
                        {stats.map(stat => (
                          <div key={stat.key} className="stat-row">
                            <span className="stat-label">{stat.label}</span>
                            <span className="stat-value">
                              {formatValue(teamAData[stat.key], stat.format)}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Differential Panel */}
        <div className="differential-panel">
          <div className="differential-header">
            <h2>📊 Advantage</h2>
            <p>Statistical Edge</p>
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
              <div className="empty-icon">🎯</div>
              <p>Select both teams to analyze matchup</p>
              <small>Compare stats to find competitive advantages</small>
            </div>
          )}
        </div>

        {/* Team B Card */}
        <div className="team-card team-b-card">
          <div className="team-card-header">
            <h2>Team B</h2>
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

          {teamBData && (
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
                {teamBData.wins}-{teamBData.losses}{(teamBData.ties || 0) > 0 ? `-${teamBData.ties}` : ''}
                <span className="record-label">2025 Record</span>
              </div>

              {/* Stats Categories */}
              <div className="stats-categories">
                {Object.entries(STAT_CATEGORIES).map(([category, stats]) => (
                  <div key={category} className="stat-category">
                    <div 
                      className="category-header"
                      onClick={() => toggleCategory(category)}
                    >
                      <h3>{category}</h3>
                      <span className="toggle-icon">
                        {expandedCategories[category] ? '−' : '+'}
                      </span>
                    </div>
                    
                    {expandedCategories[category] && (
                      <div className="category-stats">
                        {stats.map(stat => (
                          <div key={stat.key} className="stat-row">
                            <span className="stat-label">{stat.label}</span>
                            <span className="stat-value">
                              {formatValue(teamBData[stat.key], stat.format)}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default MatchupAnalyzer;
