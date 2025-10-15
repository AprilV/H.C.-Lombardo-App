import React, { useState, useEffect } from 'react';
import './App.css';

const API_URL = 'http://127.0.0.1:5000';

function App() {
  const [serverStatus, setServerStatus] = useState(null);
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // New state for dropdown interface
  const [selectedTeam, setSelectedTeam] = useState('');
  const [selectedStat, setSelectedStat] = useState('');
  const [showAllStats, setShowAllStats] = useState(true);
  const [teamDetails, setTeamDetails] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);

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

  // Fetch detailed team data
  const fetchTeamDetails = async (abbreviation) => {
    if (!abbreviation) return;
    
    try {
      setDetailsLoading(true);
      const response = await fetch(`${API_URL}/api/teams/${abbreviation}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setTeamDetails(data);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch team details:', err);
      setError('Failed to load team details: ' + err.message);
    } finally {
      setDetailsLoading(false);
    }
  };

  // Handle view stats button click
  const handleViewStats = () => {
    if (selectedTeam) {
      fetchTeamDetails(selectedTeam);
    }
  };

  // Available stats for dropdown
  const availableStats = [
    { value: 'wins', label: 'Wins' },
    { value: 'losses', label: 'Losses' },
    { value: 'ties', label: 'Ties' },
    { value: 'ppg', label: 'Points Per Game (PPG)' },
    { value: 'pa', label: 'Points Against (PA)' },
    { value: 'games_played', label: 'Games Played' },
  ];

  // Format stat value
  const formatStatValue = (key, value) => {
    if (value === null || value === undefined) return 'N/A';
    if (key === 'ppg' || key === 'pa') return value.toFixed(1);
    return value;
  };

  // Get stat label
  const getStatLabel = (key) => {
    const stat = availableStats.find(s => s.value === key);
    return stat ? stat.label : key.replace('_', ' ').toUpperCase();
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
        {/* Scrolling NFL Logos Background */}
        <div className="nfl-background">
          <div className="nfl-scroll">
            {[...Array(20)].map((_, i) => (
              <img 
                key={i}
                src="https://a.espncdn.com/i/teamlogos/leagues/500/nfl.png" 
                alt="" 
                className="nfl-watermark"
              />
            ))}
          </div>
        </div>

        {/* Compact Server Status Bar */}
        <section className="status-bar">
          {serverStatus ? (
            <div className="status-bar-content">
              <div className="status-indicator success">
                <span className="status-dot"></span>
                <span className="status-text">🚀 LIVE</span>
              </div>
              <div className="status-indicator success">
                <span className="status-dot"></span>
                <span className="status-text">💾 DB Connected</span>
              </div>
              <div className="status-indicator success">
                <span className="status-dot"></span>
                <span className="status-text">🔗 API Ready</span>
              </div>
            </div>
          ) : (
            <div className="status-bar-content error">
              <div className="status-indicator error">
                <span className="status-dot"></span>
                <span className="status-text">⚠️ Offline</span>
              </div>
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

        {/* NEW: Team Selection Interface */}
        <section className="selection-section">
          <div className="selection-card">
            <h2 className="selection-title">🏈 Select Team & Stats</h2>
            
            <div className="selection-controls">
              {/* Team Dropdown */}
              <div className="control-group">
                <label htmlFor="team-select">Select Team:</label>
                <select 
                  id="team-select"
                  className="team-dropdown"
                  value={selectedTeam}
                  onChange={(e) => setSelectedTeam(e.target.value)}
                  disabled={loading}
                >
                  <option value="">-- Choose a Team --</option>
                  {teams
                    .sort((a, b) => a.name.localeCompare(b.name))
                    .map((team) => (
                      <option key={team.abbreviation} value={team.abbreviation}>
                        {team.name} ({team.abbreviation})
                      </option>
                    ))}
                </select>
              </div>

              {/* Show All Stats Checkbox */}
              <div className="control-group checkbox-group">
                <label>
                  <input 
                    type="checkbox"
                    checked={showAllStats}
                    onChange={(e) => {
                      setShowAllStats(e.target.checked);
                      if (e.target.checked) setSelectedStat('');
                    }}
                  />
                  <span className="checkbox-label">Show All Stats</span>
                </label>
              </div>

              {/* Stat Dropdown (only if not showing all) */}
              {!showAllStats && (
                <div className="control-group">
                  <label htmlFor="stat-select">Select Stat:</label>
                  <select 
                    id="stat-select"
                    className="stat-dropdown"
                    value={selectedStat}
                    onChange={(e) => setSelectedStat(e.target.value)}
                  >
                    <option value="">-- Choose a Stat --</option>
                    {availableStats.map((stat) => (
                      <option key={stat.value} value={stat.value}>
                        {stat.label}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* View Stats Button */}
              <button 
                className="view-stats-btn"
                onClick={handleViewStats}
                disabled={!selectedTeam || detailsLoading}
              >
                {detailsLoading ? '⏳ Loading...' : '📊 View Stats'}
              </button>
            </div>
          </div>
        </section>

        {/* Team Details Display */}
        {teamDetails && (
          <section className="results-section">
            <div className="results-card">
              <div className="team-header-large">
                <img 
                  src={`https://a.espncdn.com/i/teamlogos/nfl/500/${teamDetails.abbreviation?.toLowerCase()}.png`}
                  alt={`${teamDetails.name} logo`}
                  className="team-logo-large"
                  onError={(e) => {e.target.style.display='none'}}
                />
                <div className="team-info-large">
                  <h2>{teamDetails.name}</h2>
                  <span className="team-abbr-large">{teamDetails.abbreviation}</span>
                  <div className="record-badge">
                    {teamDetails.wins}-{teamDetails.losses}{teamDetails.ties > 0 ? `-${teamDetails.ties}` : ''}
                  </div>
                </div>
              </div>

              <div className="stats-display">
                <h3>📊 Team Statistics</h3>
                {showAllStats ? (
                  <div className="stats-grid-large">
                    {availableStats.map((stat) => (
                      <div key={stat.value} className="stat-item-large">
                        <span className="stat-label-large">{stat.label}</span>
                        <span className="stat-value-large">
                          {formatStatValue(stat.value, teamDetails[stat.value])}
                        </span>
                      </div>
                    ))}
                    {teamDetails.last_updated && (
                      <div className="stat-item-large last-updated">
                        <span className="stat-label-large">Last Updated</span>
                        <span className="stat-value-large">
                          {new Date(teamDetails.last_updated).toLocaleString()}
                        </span>
                      </div>
                    )}
                  </div>
                ) : selectedStat ? (
                  <div className="single-stat-display">
                    <div className="stat-item-huge">
                      <span className="stat-label-huge">{getStatLabel(selectedStat)}</span>
                      <span className="stat-value-huge">
                        {formatStatValue(selectedStat, teamDetails[selectedStat])}
                      </span>
                    </div>
                  </div>
                ) : (
                  <p className="no-stat-selected">Please select a stat to view</p>
                )}
              </div>
            </div>
          </section>
        )}

        {/* Quick Actions */}
        <section className="actions-section">
          <button onClick={fetchTeams} className="refresh-btn" disabled={loading}>
            {loading ? '⏳ Loading...' : '🔄 Refresh Teams'}
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
