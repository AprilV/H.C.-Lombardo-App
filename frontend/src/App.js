import React, { useState, useEffect } from 'react';
import './App.css';

const API_URL = 'http://127.0.0.1:5000';

function App() {
  const [serverStatus, setServerStatus] = useState(null);
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Test server connection on mount
  useEffect(() => {
    testConnection();
    fetchTeams();
  }, []);

  const testConnection = async () => {
    try {
      const response = await fetch(`${API_URL}/health`);
      const data = await response.json();
      setServerStatus(data);
    } catch (err) {
      console.error('Connection test failed:', err);
      setError('Cannot connect to backend server at ' + API_URL);
    }
  };

  const fetchTeams = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/teams`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setTeams(data.teams || []);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch teams:', err);
      setError('Failed to load NFL teams: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const getRecordColor = (wins, losses) => {
    const total = wins + losses;
    if (total === 0) return 'neutral';
    const winPct = wins / total;
    if (winPct >= 0.6) return 'winning';
    if (winPct >= 0.4) return 'even';
    return 'losing';
  };

  return (
    <div className="App">
      <header className="App-header">
        <img 
          src="https://a.espncdn.com/i/teamlogos/leagues/500/nfl.png" 
          alt="NFL Logo" 
          className="nfl-logo"
        />
        <h1>H.C. Lombardo NFL Analytics</h1>
        <p className="subtitle">Professional Gambling Analytics Platform</p>
      </header>

      <main className="App-main">
        {/* Server Status */}
        <section className="status-section">
          <h2>System Status</h2>
          {serverStatus ? (
            <div className="status-card success">
              <div className="status-item">
                <span className="status-label">Backend:</span>
                <span className="status-value good">{serverStatus.status}</span>
              </div>
              <div className="status-item">
                <span className="status-label">Database:</span>
                <span className="status-value good">{serverStatus.database}</span>
              </div>
              <div className="status-item">
                <span className="status-label">CORS:</span>
                <span className="status-value good">{serverStatus.cors}</span>
              </div>
            </div>
          ) : (
            <div className="status-card error">
              <p>⚠️ Backend not connected</p>
            </div>
          )}
        </section>

        {/* Error Display */}
        {error && (
          <section className="error-section">
            <div className="error-card">
              <h3>⚠️ Error</h3>
              <p>{error}</p>
            </div>
          </section>
        )}

        {/* Teams List */}
        <section className="teams-section">
          <div className="section-header">
            <h2>NFL Teams</h2>
            <span className="team-count">({teams.length} teams)</span>
          </div>
          
          {loading ? (
            <div className="loading">Loading teams...</div>
          ) : teams.length > 0 ? (
            <div className="teams-grid">
              {teams.map((team, index) => (
                <div key={index} className={`team-card ${getRecordColor(team.wins, team.losses)}`}>
                  <div className="team-header">
                    <img 
                      src={`https://a.espncdn.com/i/teamlogos/nfl/500/${team.abbreviation?.toLowerCase()}.png`}
                      alt={`${team.name} logo`}
                      className="team-logo"
                      onError={(e) => {e.target.style.display='none'}}
                    />
                    <div className="team-info">
                      <h3>{team.name}</h3>
                      <span className="team-abbr">{team.abbreviation}</span>
                    </div>
                  </div>
                  <div className="team-stats">
                    <div className="stat">
                      <span className="stat-label">Record</span>
                      <span className="stat-value">{team.wins}-{team.losses}</span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">PPG</span>
                      <span className="stat-value">{team.ppg?.toFixed(1) || 'N/A'}</span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">PA</span>
                      <span className="stat-value">{team.pa?.toFixed(1) || 'N/A'}</span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">Games</span>
                      <span className="stat-value">{team.games_played}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p>No teams found</p>
          )}
        </section>

        {/* Actions */}
        <section className="actions-section">
          <button onClick={fetchTeams} className="refresh-btn" disabled={loading}>
            {loading ? '⏳ Loading...' : '🔄 Refresh Data'}
          </button>
        </section>
      </main>

      <footer className="App-footer">
        <p>H.C. Lombardo NFL Analytics Platform © 2025</p>
        <p className="footer-note">Production Environment</p>
      </footer>
    </div>
  );
}

export default App;
