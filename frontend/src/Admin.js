import React, { useState, useEffect } from 'react';
import './Admin.css';
import ModelPerformance from './ModelPerformance';
import Settings from './Settings';

const API_URL = (typeof window !== 'undefined' && (window.location.hostname === 'hclombardo.com' || window.location.hostname === 'www.hclombardo.com' || window.location.hostname.endsWith('.netlify.app'))) ? '' : (process.env.REACT_APP_API_URL ?? '');

function Admin() {
  const [activeTab, setActiveTab] = useState('performance');
  const [dbStats, setDbStats] = useState(null);
  const [dbCheckedAt, setDbCheckedAt] = useState(null);

  useEffect(() => {
    fetchDatabaseStats();
    return undefined;
  }, []);

  const fetchDatabaseStats = async () => {
    try {
      const response = await fetch(`${API_URL}/api/teams`);
      if (!response.ok) {
        throw new Error('Database check failed');
      }

      const data = await response.json();
      if (Array.isArray(data.teams) && data.teams.length > 0) {
        const totalGames = data.teams.reduce((sum, team) => sum + (Number(team.games_played) || 0), 0);

        setDbStats({
          teams: data.teams.length,
          games: totalGames
        });
      } else {
        setDbStats(null);
      }
    } catch (err) {
      setDbStats(null);
    } finally {
      setDbCheckedAt(Date.now());
    }
  };

  const databaseOperational = Boolean(dbStats);
  const gamesLoadedDisplay = dbStats?.games ? dbStats.games.toLocaleString() : '~14,000';
  const teamsTrackedDisplay = dbStats?.teams || 32;

  const formatCheckedAt = (value) => {
    if (!value) {
      return 'Checking...';
    }

    return new Date(value).toLocaleTimeString([], {
      hour: 'numeric',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  return (
    <div className="admin-container">
      <div className="admin-header">
        <h1>About H.C. Lombardo</h1>
        <p className="admin-subtitle">Smarter NFL predictions that help you find the edge with confidence.</p>
      </div>

      <div className="admin-tabs">
        <button
          className={`admin-tab ${activeTab === 'performance' ? 'active' : ''}`}
          onClick={() => setActiveTab('performance')}
        >
          📊 AI Performance
        </button>
        <button
          className={`admin-tab ${activeTab === 'neural-net' ? 'active' : ''}`}
          onClick={() => setActiveTab('neural-net')}
        >
          🧠 Prediction Models
        </button>
        <button
          className={`admin-tab ${activeTab === 'database' ? 'active' : ''}`}
          onClick={() => setActiveTab('database')}
        >
          📊 The Data Behind the Picks
        </button>
        <button
          className={`admin-tab ${activeTab === 'settings' ? 'active' : ''}`}
          onClick={() => setActiveTab('settings')}
        >
          ⚙️ Settings
        </button>
      </div>

      <div className="admin-content">
        {activeTab === 'performance' && (
          <div className="admin-section">
            <div className="performance-header">
              <h2>🏈 Prediction Performance</h2>
            </div>

            <div className="ai-performance-summary">
              <p>Get AI-powered picks designed to uncover value the market can miss.</p>
              <p>Every forecast is tuned for real betting decisions, from likely winners to spread confidence.</p>
              <p>Validated against real outcomes and Vegas lines to keep your trust earned, not assumed.</p>
              <p>Use it as your confidence layer before you place a wager.</p>
            </div>

            <ModelPerformance />
          </div>
        )}

        {activeTab === 'neural-net' && (
          <div className="admin-section">
            <h2>🧠 AI Prediction Engine</h2>
            <div className="admin-iframe-intro">
              <p>Experience the intelligence behind every pick in an immersive 3D view.</p>
              <p className="admin-iframe-subtext">Built to help you decide faster and bet with more conviction.</p>
            </div>
            <div className="visualization-container">
              <iframe
                src="/admin-both-models.html"
                style={{
                  width: '100%',
                  height: '800px',
                  border: 'none',
                  borderRadius: '12px',
                  background: 'rgba(10, 14, 39, 0.6)',
                  boxShadow: '0 8px 24px rgba(0, 0, 0, 0.4)'
                }}
                title="Prediction Models 3D"
              />
            </div>
          </div>
        )}

        {activeTab === 'database' && (
          <div className="admin-section">
            <h2>📊 The Data Behind the Picks</h2>
            <p className="admin-data-intro">
              Deep historical coverage gives every forecast stronger context before game day.
            </p>

            <div className="data-summary-grid">
              <div className="data-summary-card data-summary-card-accent">
                <h3>📚 Data Coverage</h3>
                <div className="data-summary-metric">{gamesLoadedDisplay}</div>
                <p>Decades of NFL history from 1999-2025 power our forecasting confidence.</p>
                <p className="detail">{teamsTrackedDisplay} teams tracked across long-term performance trends.</p>
              </div>

              <div className="data-summary-card">
                <h3>🎯 Betting Insight</h3>
                <p>Game-by-game performance and line context help surface sharper value spots.</p>
                <p>Fresh game information keeps your edge current as the slate evolves.</p>
                <div className={`data-status-chip ${databaseOperational ? 'online' : 'offline'}`}>
                  {databaseOperational ? 'Operational' : 'Unavailable'}
                </div>
                <p className="detail">Data health checked at {formatCheckedAt(dbCheckedAt)}</p>
              </div>

              <div className="data-summary-card">
                <h3>🧠 Model Results</h3>
                <p>Winner forecasting currently tracks at 65.55% accuracy.</p>
                <p>Spread forecasting currently tracks at 10.35 MAE.</p>
                <p className="detail">Results are measured against real outcomes to keep your confidence grounded.</p>
              </div>

              <div className="data-summary-card">
                <h3>🌐 Powered By</h3>
                <p>Advanced prediction intelligence built from long-term NFL history.</p>
                <p>Trusted public data coverage from NFLverse and ESPN API.</p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="admin-section admin-settings-section">
            <Settings />
          </div>
        )}
      </div>
    </div>
  );
}

export default Admin;
