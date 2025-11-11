import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './HistoricalData.css';

const API_URL = 'http://127.0.0.1:5000';

// Available stat categories for dropdown
const STAT_CATEGORIES = [
  { value: 'all', label: 'All Statistics' },
  { value: 'offense', label: 'Offensive Stats' },
  { value: 'defense', label: 'Defensive Stats' },
  { value: 'passing', label: 'Passing Stats' },
  { value: 'rushing', label: 'Rushing Stats' },
  { value: 'advanced', label: 'Advanced Metrics (EPA)' },
  { value: 'efficiency', label: 'Efficiency Stats' },
  { value: 'scoring', label: 'Scoring Stats' }
];

// Stat definitions for spreadsheet columns
const STAT_DEFINITIONS = {
  offense: ['ppg', 'total_yards', 'yards_per_play', 'completion_pct', 'pass_yards', 'rush_yards', 'first_downs', 'third_down_pct'],
  defense: ['opp_ppg', 'opp_yards', 'opp_yards_per_play', 'sacks', 'interceptions', 'fumbles_recovered', 'turnovers_forced'],
  passing: ['pass_yards', 'pass_attempts', 'pass_completions', 'completion_pct', 'pass_tds', 'interceptions', 'qb_rating'],
  rushing: ['rush_yards', 'rush_attempts', 'rush_avg', 'rush_tds', 'first_downs_rush'],
  advanced: ['epa_per_play', 'success_rate', 'explosive_play_rate', 'stuff_rate'],
  efficiency: ['yards_per_play', 'third_down_pct', 'red_zone_pct', 'time_of_possession'],
  scoring: ['ppg', 'points', 'touchdowns', 'field_goals', 'red_zone_scores']
};

function HistoricalData() {
  const [allTeams, setAllTeams] = useState([]);
  const [teamData, setTeamData] = useState(null);
  const [selectedTeam, setSelectedTeam] = useState('');
  const [selectedSeason, setSelectedSeason] = useState('2025');
  const [selectedStatCategory, setSelectedStatCategory] = useState('all');
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
  }, []);

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
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to load team data');
      }
      
      setTeamData(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getStatClass = (value, threshold, inverted = false) => {
    if (inverted) {
      return value < threshold ? 'good' : value > threshold ? 'bad' : '';
    }
    return value > threshold ? 'good' : value < threshold ? 'bad' : '';
  };

  const formatStatValue = (value) => {
    if (value === null || value === undefined) return 'N/A';
    if (typeof value === 'number') {
      return value % 1 === 0 ? value : value.toFixed(2);
    }
    return value;
  };

  const getStatsToDisplay = () => {
    if (!teamData || !teamData.stats) return [];
    
    const stats = teamData.stats;
    let statsArray = [];

    if (selectedStatCategory === 'all') {
      // Show all available stats
      Object.keys(stats).forEach(key => {
        if (key !== 'team' && key !== 'season') {
          statsArray.push({ key, value: stats[key], label: formatStatLabel(key) });
        }
      });
    } else {
      // Show stats for selected category
      const categoryStats = STAT_DEFINITIONS[selectedStatCategory] || [];
      categoryStats.forEach(key => {
        if (stats[key] !== undefined) {
          statsArray.push({ key, value: stats[key], label: formatStatLabel(key) });
        }
      });
    }

    return statsArray;
  };

  const formatStatLabel = (key) => {
    return key
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
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
        <h1>📊 Historical Team Data Viewer</h1>
        <p className="subtitle">Select team, season, and stat category to view detailed statistics</p>
      </div>

      {/* Control Panel */}
      <div className="control-panel">
        <div className="control-group">
          <label htmlFor="team-select">Team</label>
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

        <div className="control-group">
          <label htmlFor="season-select">Season</label>
          <select 
            id="season-select"
            value={selectedSeason} 
            onChange={(e) => {
              setSelectedSeason(e.target.value);
              setSelectedTeam(''); // Reset team selection when season changes
            }}
            className="dropdown"
          >
            {seasons.map(year => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>
        </div>

        <div className="control-group">
          <label htmlFor="stat-select">Stat Category</label>
          <select 
            id="stat-select"
            value={selectedStatCategory} 
            onChange={(e) => setSelectedStatCategory(e.target.value)}
            className="dropdown"
          >
            {STAT_CATEGORIES.map(cat => (
              <option key={cat.value} value={cat.value}>{cat.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Data Display */}
      {!selectedTeam && (
        <div className="empty-state">
          <div className="empty-icon">📋</div>
          <h3>Select a team to view statistics</h3>
          <p>Choose a team from the dropdown above to see their detailed season data</p>
        </div>
      )}

      {selectedTeam && loading && (
        <div className="loading">Loading data for {selectedTeam}...</div>
      )}

      {selectedTeam && !loading && teamData && (
        <div className="data-display">
          <div className="team-info-banner">
            <div className="team-title">
              <h2>{selectedTeam}</h2>
              <span className="season-badge">{selectedSeason} Season</span>
            </div>
            <div className="record">
              Record: {teamData.stats?.wins || 0}-{teamData.stats?.losses || 0}
              {teamData.stats?.games_played && ` (${teamData.stats.games_played} games)`}
            </div>
          </div>

          <div className="stats-spreadsheet">
            <table className="stats-table">
              <thead>
                <tr>
                  <th>Statistic</th>
                  <th>Value</th>
                  <th>Category</th>
                </tr>
              </thead>
              <tbody>
                {getStatsToDisplay().map((stat, index) => (
                  <tr key={index}>
                    <td className="stat-name">{stat.label}</td>
                    <td className="stat-value">{formatStatValue(stat.value)}</td>
                    <td className="stat-category">{selectedStatCategory === 'all' ? 'General' : formatStatLabel(selectedStatCategory)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {getStatsToDisplay().length === 0 && (
            <div className="no-data">
              <p>No statistics available for this selection</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default HistoricalData;
