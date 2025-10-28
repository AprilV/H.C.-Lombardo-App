import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './HistoricalData.css';

const API_URL = 'http://127.0.0.1:5000';

function HistoricalData() {
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadTeams();
  }, []);

  const loadTeams = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/hcl/teams`);
      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to load teams');
      }
      
      setTeams(data.teams);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTeamClick = (teamAbbr) => {
    navigate(`/team/${teamAbbr}`);
  };

  const getStatClass = (value, threshold, inverted = false) => {
    if (inverted) {
      return value < threshold ? 'good' : value > threshold ? 'bad' : '';
    }
    return value > threshold ? 'good' : value < threshold ? 'bad' : '';
  };

  if (loading) {
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
        <h1>🏈 Historical Team Data</h1>
        <div className="badge">2025 SEASON</div>
        <div className="info">
          Database: <strong>nfl_analytics</strong> | 
          Data: <strong>Weeks 1-7</strong> | 
          Teams: <strong>{teams.length}</strong>
        </div>
      </div>

      <div className="teams-grid">
        {teams.map((team) => (
          <div 
            key={team.team} 
            className="team-card"
            onClick={() => handleTeamClick(team.team)}
          >
            <div className="team-header">
              <div>
                <div className="team-name">{team.team}</div>
                <div className="team-abbr">{team.team}</div>
              </div>
              <div className="team-record">
                {team.wins || 0}-{team.losses || 0}
              </div>
            </div>

            <div className="stats-row">
              <div className="stat">
                <div className="stat-label">PPG</div>
                <div className={`stat-value ${getStatClass(team.ppg, 25, false)}`}>
                  {team.ppg || 0}
                </div>
              </div>
              <div className="stat">
                <div className="stat-label">EPA/Play</div>
                <div className={`stat-value ${getStatClass(team.epa_per_play, 0.1, false)}`}>
                  {team.epa_per_play || 0}
                </div>
              </div>
              <div className="stat">
                <div className="stat-label">Success Rate</div>
                <div className={`stat-value ${getStatClass(team.success_rate, 0.5, false)}`}>
                  {team.success_rate || 0}
                </div>
              </div>
              <div className="stat">
                <div className="stat-label">Yards/Play</div>
                <div className={`stat-value ${getStatClass(team.yards_per_play, 6, false)}`}>
                  {team.yards_per_play || 0}
                </div>
              </div>
            </div>

            <div className="click-hint">
              Click for details →
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default HistoricalData;
