import React, { useState, useEffect } from 'react';
import './App.css';

const API_URL = 'http://127.0.0.1:5003';

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

  return (
    <div className="App">
      <header className="App-header">
        <h1>🏈 H.C. Lombardo NFL Analytics</h1>
        <p>Step 5: React + Flask + PostgreSQL Integration Test</p>
      </header>

      <main className="App-main">
        {/* Server Status */}
        <section className="status-section">
          <h2>Backend Status</h2>
          {serverStatus ? (
            <div className="status-card success">
              <p>✓ Status: {serverStatus.status}</p>
              <p>✓ Database: {serverStatus.database}</p>
              <p>✓ CORS: {serverStatus.cors}</p>
              <p>✓ Port: {serverStatus.port}</p>
            </div>
          ) : (
            <div className="status-card error">
              <p>✗ Backend not connected</p>
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
          <h2>NFL Teams ({teams.length})</h2>
          
          {loading ? (
            <p>Loading teams...</p>
          ) : teams.length > 0 ? (
            <div className="teams-grid">
              {teams.map((team, index) => (
                <div key={index} className="team-card">
                  <h3>{team.name}</h3>
                  <p className="team-abbr">{team.abbreviation}</p>
                  <div className="team-stats">
                    <span>W: {team.wins}</span>
                    <span>L: {team.losses}</span>
                    <span>PPG: {team.ppg?.toFixed(1) || 'N/A'}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p>No teams found</p>
          )}
        </section>

        {/* Refresh Button */}
        <section className="actions-section">
          <button onClick={fetchTeams} className="refresh-btn">
            🔄 Refresh Teams
          </button>
        </section>
      </main>

      <footer className="App-footer">
        <p>Step-by-Step Testing - Testbed Only</p>
      </footer>
    </div>
  );
}

export default App;
