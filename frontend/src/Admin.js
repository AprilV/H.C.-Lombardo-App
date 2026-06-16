import React, { useState, useEffect } from 'react';
import './Admin.css';
import ModelPerformance from './ModelPerformance';
import Settings from './Settings';

const API_URL = (typeof window !== 'undefined' && (window.location.hostname === 'hclombardo.com' || window.location.hostname === 'www.hclombardo.com' || window.location.hostname.endsWith('.netlify.app'))) ? '' : (process.env.REACT_APP_API_URL ?? '');

function Admin() {
  const [activeTab, setActiveTab] = useState('system');
  const [serverStatus, setServerStatus] = useState(null);
  const [dbStats, setDbStats] = useState(null);
  const [serverCheckedAt, setServerCheckedAt] = useState(null);
  const [dbCheckedAt, setDbCheckedAt] = useState(null);
  const [isUpdating, setIsUpdating] = useState(false);
  const [updateMessage, setUpdateMessage] = useState(null);

  useEffect(() => {
    checkServerStatus();
    fetchDatabaseStats();

    const interval = setInterval(() => {
      checkServerStatus();
      fetchDatabaseStats();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const checkServerStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/health`);
      if (!response.ok) {
        throw new Error('Health check failed');
      }

      const data = await response.json();
      setServerStatus(data);
    } catch (err) {
      setServerStatus(null);
    } finally {
      setServerCheckedAt(Date.now());
    }
  };

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

  const apiOperational = Boolean(serverStatus);
  const databaseOperational = Boolean(dbStats);
  const allSystemsOperational = apiOperational && databaseOperational;
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

  const handleUpdatePredictions = async () => {
    setIsUpdating(true);
    setUpdateMessage(null);

    try {
      const response = await fetch(`${API_URL}/api/ml/update-results`, {
        method: 'POST'
      });
      const data = await response.json();

      if (data.success) {
        setUpdateMessage({
          type: 'success',
          text: `✅ Updated ${data.updated} predictions with actual results!`
        });
      } else {
        setUpdateMessage({
          type: 'error',
          text: `❌ Error: ${data.error}`
        });
      }
    } catch (err) {
      setUpdateMessage({
        type: 'error',
        text: `❌ Failed to update predictions: ${err.message}`
      });
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div className="admin-container">
      <div className="admin-header">
        <h1>🔧 Admin Panel</h1>
        <p className="admin-subtitle">System Administration & Internal Tools</p>
      </div>

      <div className="admin-tabs">
        <button
          className={`admin-tab ${activeTab === 'system' ? 'active' : ''}`}
          onClick={() => setActiveTab('system')}
        >
          🟢 System Status
        </button>
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
          🗄️ Data Storage
        </button>
        <button
          className={`admin-tab ${activeTab === 'settings' ? 'active' : ''}`}
          onClick={() => setActiveTab('settings')}
        >
          ⚙️ Settings
        </button>
      </div>

      <div className="admin-content">
        {activeTab === 'system' && (
          <div className="admin-section admin-live-status">
            <h2>🟢 System Status</h2>
            <div className={`system-status-summary ${allSystemsOperational ? 'healthy' : 'issue'}`}>
              <span className="system-status-summary-dot" aria-hidden="true"></span>
              <span className="system-status-summary-text">
                {allSystemsOperational ? 'All Systems Operational' : 'Service Issue Detected'}
              </span>
            </div>

            <div className="system-status-grid">
              <div className="system-status-card operational">
                <div className="system-status-card-top">
                  <h3>Application</h3>
                  <span className="system-status-dot operational" aria-label="Application operational"></span>
                </div>
                <p className="system-status-label">Operational</p>
                <p className="system-status-time">Live in browser</p>
              </div>

              <div className={`system-status-card ${apiOperational ? 'operational' : 'unavailable'}`}>
                <div className="system-status-card-top">
                  <h3>API Server</h3>
                  <span
                    className={`system-status-dot ${apiOperational ? 'operational' : 'unavailable'}`}
                    aria-label={apiOperational ? 'API server operational' : 'API server unavailable'}
                  ></span>
                </div>
                <p className="system-status-label">{apiOperational ? 'Operational' : 'Unavailable'}</p>
                <p className="system-status-time">Last checked {formatCheckedAt(serverCheckedAt)}</p>
              </div>

              <div className={`system-status-card ${databaseOperational ? 'operational' : 'unavailable'}`}>
                <div className="system-status-card-top">
                  <h3>Database</h3>
                  <span
                    className={`system-status-dot ${databaseOperational ? 'operational' : 'unavailable'}`}
                    aria-label={databaseOperational ? 'Database operational' : 'Database unavailable'}
                  ></span>
                </div>
                <p className="system-status-label">{databaseOperational ? 'Operational' : 'Unavailable'}</p>
                <p className="system-status-time">Last checked {formatCheckedAt(dbCheckedAt)}</p>
              </div>
            </div>

            <div className="admin-iframe-intro">
              <p>Interactive 3D system view</p>
              <p className="admin-iframe-subtext">Status strip reflects current live checks</p>
            </div>

            <div className="visualization-container">
              <iframe
                src="/admin-topology.html"
                style={{
                  width: '100%',
                  height: '800px',
                  border: 'none',
                  borderRadius: '12px',
                  background: 'rgba(10, 14, 39, 0.6)',
                  boxShadow: '0 8px 24px rgba(0, 0, 0, 0.4)'
                }}
                title="System Topology 3D"
              />
            </div>
          </div>
        )}

        {activeTab === 'performance' && (
          <div className="admin-section">
            <div className="performance-header">
              <h2>🏈 AI Model Performance Tracking</h2>
              <button
                className={`update-btn ${isUpdating ? 'updating' : ''}`}
                onClick={handleUpdatePredictions}
                disabled={isUpdating}
              >
                {isUpdating ? '⏳ Updating...' : '🔄 Update Results'}
              </button>
            </div>

            {updateMessage && (
              <div className={`update-message ${updateMessage.type}`}>
                {updateMessage.text}
              </div>
            )}

            <ModelPerformance />
          </div>
        )}

        {activeTab === 'neural-net' && (
          <div className="admin-section">
            <h2>🧠 Prediction Models - 3D Neural Networks</h2>
            <div className="admin-iframe-intro">
              <p>Interactive 3D visualization of our AI prediction models</p>
              <p className="admin-iframe-subtext">🟢 Win/Loss Classifier • 🔴 Score Regressor</p>
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
            <h2>🗄️ Data Summary</h2>
            <p className="admin-data-intro">
              High-level coverage and model outcomes powering this experience.
            </p>

            <div className="data-summary-grid">
              <div className="data-summary-card data-summary-card-accent">
                <h3>📚 Data Coverage</h3>
                <div className="data-summary-metric">{gamesLoadedDisplay}</div>
                <p>Historical NFL games spanning 1999-2025 seasons.</p>
                <p className="detail">{teamsTrackedDisplay} teams tracked across game history.</p>
              </div>

              <div className="data-summary-card">
                <h3>📊 Game Data</h3>
                <p>Per-game team statistics and betting lines for matchup analysis.</p>
                <p>Live updates continue throughout active game windows.</p>
                <div className={`data-status-chip ${databaseOperational ? 'online' : 'offline'}`}>
                  {databaseOperational ? 'Operational' : 'Unavailable'}
                </div>
                <p className="detail">Last checked {formatCheckedAt(dbCheckedAt)}</p>
              </div>

              <div className="data-summary-card">
                <h3>🧠 Model Results</h3>
                <p>Win/Loss prediction model currently tracks at 65.55% accuracy.</p>
                <p>Point spread model is currently at 10.35 MAE.</p>
                <p className="detail">Performance is monitored throughout the season.</p>
              </div>

              <div className="data-summary-card">
                <h3>🌐 Powered By</h3>
                <p>Machine learning models trained on historical NFL data.</p>
                <p>Public data feeds from NFLverse and ESPN API.</p>
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
