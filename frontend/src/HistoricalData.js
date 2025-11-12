import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './HistoricalData.css';

const API_URL = 'http://127.0.0.1:5000';

// All available statistics from nflverse data (ALL stats from team_game_stats aggregated)
const ALL_STATS = [
  // Record & Games
  { value: 'games_played', label: 'Games Played', category: 'Record' },
  { value: 'wins', label: 'Wins', category: 'Record' },
  { value: 'losses', label: 'Losses', category: 'Record' },
  { value: 'home_wins', label: 'Home Wins', category: 'Record' },
  { value: 'away_wins', label: 'Away Wins', category: 'Record' },
  
  // Scoring
  { value: 'ppg', label: 'Points Per Game', category: 'Scoring' },
  { value: 'total_points', label: 'Total Points', category: 'Scoring' },
  { value: 'ppg_home', label: 'Home PPG', category: 'Scoring' },
  { value: 'ppg_away', label: 'Away PPG', category: 'Scoring' },
  { value: 'touchdowns_per_game', label: 'TDs Per Game', category: 'Scoring' },
  { value: 'fg_per_game', label: 'FGs Per Game', category: 'Scoring' },
  { value: 'fg_att_per_game', label: 'FG Attempts Per Game', category: 'Scoring' },
  
  // Offensive Totals
  { value: 'total_yards_per_game', label: 'Total Yards/Game', category: 'Offense' },
  { value: 'passing_yards_per_game', label: 'Passing Yards/Game', category: 'Offense' },
  { value: 'rushing_yards_per_game', label: 'Rushing Yards/Game', category: 'Offense' },
  { value: 'plays_per_game', label: 'Plays Per Game', category: 'Offense' },
  { value: 'yards_per_play', label: 'Yards Per Play', category: 'Offense' },
  
  // Passing Stats
  { value: 'completions_per_game', label: 'Completions/Game', category: 'Passing' },
  { value: 'passing_att_per_game', label: 'Pass Attempts/Game', category: 'Passing' },
  { value: 'completion_pct', label: 'Completion %', category: 'Passing' },
  { value: 'passing_tds_per_game', label: 'Pass TDs/Game', category: 'Passing' },
  { value: 'interceptions_per_game', label: 'INTs/Game', category: 'Passing' },
  { value: 'sacks_taken_per_game', label: 'Sacks Taken/Game', category: 'Passing' },
  { value: 'sack_yards_lost_per_game', label: 'Sack Yards Lost/Game', category: 'Passing' },
  { value: 'qb_rating', label: 'QB Rating', category: 'Passing' },
  
  // Rushing Stats
  { value: 'rushing_att_per_game', label: 'Rush Attempts/Game', category: 'Rushing' },
  { value: 'yards_per_carry', label: 'Yards Per Carry', category: 'Rushing' },
  { value: 'rushing_tds_per_game', label: 'Rush TDs/Game', category: 'Rushing' },
  
  // Efficiency Metrics
  { value: 'third_down_pct', label: 'Third Down %', category: 'Efficiency' },
  { value: 'fourth_down_pct', label: 'Fourth Down %', category: 'Efficiency' },
  { value: 'red_zone_pct', label: 'Red Zone %', category: 'Efficiency' },
  { value: 'time_of_possession_pct', label: 'Time of Possession %', category: 'Efficiency' },
  { value: 'early_down_success_rate', label: 'Early Down Success %', category: 'Efficiency' },
  
  // Special Teams
  { value: 'punts_per_game', label: 'Punts/Game', category: 'Special Teams' },
  { value: 'punt_avg_yards', label: 'Punt Average', category: 'Special Teams' },
  { value: 'kickoff_return_yards_per_game', label: 'KR Yards/Game', category: 'Special Teams' },
  { value: 'punt_return_yards_per_game', label: 'PR Yards/Game', category: 'Special Teams' },
  
  // Defense/Turnovers
  { value: 'total_turnovers', label: 'Total Turnovers', category: 'Turnovers' },
  { value: 'turnovers_per_game', label: 'Turnovers/Game', category: 'Turnovers' },
  { value: 'fumbles_lost_per_game', label: 'Fumbles Lost/Game', category: 'Turnovers' },
  
  // Penalties
  { value: 'penalties_per_game', label: 'Penalties/Game', category: 'Penalties' },
  { value: 'penalty_yards_per_game', label: 'Penalty Yards/Game', category: 'Penalties' },
  
  // Advanced Metrics
  { value: 'drives_per_game', label: 'Drives/Game', category: 'Advanced' },
  { value: 'starting_field_pos_yds', label: 'Avg Starting Field Position', category: 'Advanced' }
];

function HistoricalData() {
  const [allTeams, setAllTeams] = useState([]);
  const [selectedTeam, setSelectedTeam] = useState('');
  const [selectedSeason, setSelectedSeason] = useState('2024'); // Default to 2024 (most recent with stats)
  const [teamStats, setTeamStats] = useState(null);
  const [selectedStats, setSelectedStats] = useState(['ppg', 'total_yards_per_game', 'passing_yards_per_game', 'rushing_yards_per_game']); // Default 4 stats
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Generate season years (1999-2025)
  const seasons = [];
  for (let year = 2025; year >= 1999; year--) {
    seasons.push(year);
  }

  useEffect(() => {
    loadTeamsList();
  }, [selectedSeason]);

  useEffect(() => {
    if (selectedTeam && selectedSeason) {
      loadTeamData();
    }
  }, [selectedTeam, selectedSeason]);

  const loadTeamsList = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/hcl/teams?season=${selectedSeason}`);
      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to load teams');
      }
      
      setAllTeams(data.teams);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadTeamData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/hcl/teams/${selectedTeam}?season=${selectedSeason}`);
      const data = await response.json();
      
      console.log('API Response:', data); // DEBUG
      console.log('Team data:', data.team); // DEBUG
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to load team data');
      }
      
      // API returns data.team not data.stats
      setTeamStats(data.team);
      console.log('teamStats set to:', data.team); // DEBUG
      setError(null);
    } catch (err) {
      console.error('Error loading team data:', err); // DEBUG
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const addStatColumn = () => {
    if (selectedStats.length < 8) { // Max 8 stat columns
      setSelectedStats([...selectedStats, '']);
    }
  };

  const removeStatColumn = (index) => {
    const newStats = selectedStats.filter((_, i) => i !== index);
    setSelectedStats(newStats);
  };

  const updateStatColumn = (index, value) => {
    const newStats = [...selectedStats];
    newStats[index] = value;
    setSelectedStats(newStats);
  };

  const formatStatValue = (statKey, value) => {
    if (value === null || value === undefined) return 'N/A';
    if (typeof value === 'number') {
      // Format percentages
      if (statKey.includes('pct') || statKey.includes('rate')) {
        return `${value.toFixed(1)}%`;
      }
      // Format decimals
      return value % 1 === 0 ? value : value.toFixed(2);
    }
    return value;
  };

  const getStatLabel = (statKey) => {
    const stat = ALL_STATS.find(s => s.value === statKey);
    return stat ? stat.label : statKey;
  };

  const getAvailableStats = (currentIndex) => {
    // Return stats that aren't already selected in other dropdowns
    return ALL_STATS.filter(stat => 
      !selectedStats.some((selected, idx) => idx !== currentIndex && selected === stat.value)
    );
  };

  if (loading && !allTeams.length) {
    return (
      <div className="historical-data">
        <div className="loading">Loading teams...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="historical-data">
        <div className="error">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="historical-data">
      <div className="header">
        <h1>📊 Historical Team Statistics Spreadsheet</h1>
        <p className="subtitle">Custom stat viewer - select team, season, and choose your stats</p>
      </div>

      {/* Instructions */}
      <div className="instructions-box">
        <h3>📋 How to Use:</h3>
        <ol>
          <li><strong>Step 1:</strong> Select a <strong>Season</strong> (1999-2025)</li>
          <li><strong>Step 2:</strong> Choose a <strong>Team</strong> from the dropdown</li>
          <li><strong>Step 3:</strong> Select up to <strong>8 statistics</strong> you want to view using the dropdown boxes</li>
          <li><strong>Step 4:</strong> Click <strong>"+ Add Stat Column"</strong> to add more stats (max 8 total)</li>
          <li><strong>Step 5:</strong> Click the <strong>X button</strong> next to any stat to remove it</li>
        </ol>
        <p><em>💡 Tip: Each dropdown shows all available stats grouped by category. Stats already selected won't appear in other dropdowns.</em></p>
      </div>

      {/* Control Panel */}
      <div className="control-panel">
        <div className="control-group">
          <label htmlFor="season-select">📅 Season</label>
          <select 
            id="season-select"
            value={selectedSeason} 
            onChange={(e) => {
              setSelectedSeason(e.target.value);
              setSelectedTeam('');
              setTeamStats(null);
            }}
            className="dropdown"
          >
            {seasons.map(year => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>
        </div>

        <div className="control-group">
          <label htmlFor="team-select">🏈 Team</label>
          <select 
            id="team-select"
            value={selectedTeam} 
            onChange={(e) => setSelectedTeam(e.target.value)}
            className="dropdown"
          >
            <option value="">-- Select Team --</option>
            {allTeams.map(team => (
              <option key={team.team} value={team.team}>
                {team.team} ({team.wins || 0}-{team.losses || 0})
              </option>
            ))}
          </select>
        </div>

        <button 
          className="add-column-btn"
          onClick={addStatColumn}
          disabled={selectedStats.length >= 8}
        >
          + Add Stat Column {selectedStats.length >= 8 && '(Max 8)'}
        </button>
      </div>

      {/* Spreadsheet-style Stat Selector */}
      {selectedTeam && (
        <div className="spreadsheet-container">
          <h3>Select Statistics to Display:</h3>
          <div className="stat-dropdowns-row">
            {selectedStats.map((statKey, index) => (
              <div key={index} className="stat-column">
                <div className="stat-column-header">
                  <label>Stat #{index + 1}</label>
                  <button 
                    className="remove-column-btn"
                    onClick={() => removeStatColumn(index)}
                    title="Remove this stat"
                  >
                    ✕
                  </button>
                </div>
                <select
                  value={statKey}
                  onChange={(e) => updateStatColumn(index, e.target.value)}
                  className="stat-dropdown"
                >
                  <option value="">-- Select Stat --</option>
                  {/* Group stats by category */}
                  {['Scoring', 'Offense', 'Passing', 'Rushing', 'Efficiency', 'Defense', 'Other'].map(category => {
                    const categoryStats = getAvailableStats(index).filter(s => s.category === category);
                    if (categoryStats.length === 0) return null;
                    return (
                      <optgroup key={category} label={category}>
                        {categoryStats.map(stat => (
                          <option key={stat.value} value={stat.value}>
                            {stat.label}
                          </option>
                        ))}
                      </optgroup>
                    );
                  })}
                </select>
              </div>
            ))}
          </div>

          {/* Display Selected Stats */}
          {teamStats && (
            <div className="stats-display-table">
              <h3>📈 {selectedTeam} - {selectedSeason} Season Statistics</h3>
              <table className="stats-table">
                <thead>
                  <tr>
                    <th className="stat-number">#</th>
                    {selectedStats.map((statKey, index) => (
                      <th key={index}>
                        {statKey ? getStatLabel(statKey) : '---'}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td className="stat-number">Value</td>
                    {selectedStats.map((statKey, index) => (
                      <td key={index} className="stat-value">
                        {statKey && teamStats[statKey] !== undefined 
                          ? formatStatValue(statKey, teamStats[statKey])
                          : '---'
                        }
                      </td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>
          )}

          {!teamStats && (
            <div className="no-data-message">
              <p>Select a team to view statistics</p>
            </div>
          )}
        </div>
      )}

      {!selectedTeam && (
        <div className="welcome-message">
          <p>👆 Select a season and team above to get started</p>
        </div>
      )}
    </div>
  );
};

export default HistoricalData;
