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
    }, 5000); // Check every 5 seconds
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
      if (data.success && data.teams) {
        const totalGames = data.teams.reduce((sum, t) => sum + (t.games_played || 0), 0);
        const totalYards = data.teams.reduce((sum, t) => sum + (t.total_yards || 0), 0);
        setDbStats({
          teams: data.teams.length,
          games: totalGames,
          avgYards: (totalYards / data.teams.length).toFixed(1)
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
          ⚙️ App Status
        </button>
        <button 
          className={`admin-tab ${activeTab === 'topology' ? 'active' : ''}`}
          onClick={() => setActiveTab('topology')}
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
          <div className="admin-section">
            <h2>⚙️ App Status & Health</h2>
            <div className="info-grid">
              <div className="info-card">
                <div className="info-icon">📱</div>
                <h3>Application Server</h3>
                {serverStatus ? (
                  <>
                    <div className="status-indicator online">● Online</div>
                    <p>Backend services operational</p>
                    <p className="detail">Processing requests</p>
                  </>
                ) : (
                  <>
                    <div className="status-indicator offline">● Offline</div>
                    <p>Unable to connect to backend</p>
                  </>
                )}
              </div>

              <div className="info-card">
                <div className="info-icon">🗄️</div>
                <h3>Data Storage</h3>
                {serverStatus ? (
                  <>
                    <div className="status-indicator online">● Connected</div>
                    <p>Data storage system active</p>
                    <p className="detail">HCL schema loaded</p>
                  </>
                ) : (
                  <>
                    <div className="status-indicator offline">● Disconnected</div>
                    <p>Data storage unavailable</p>
                  </>
                )}
              </div>

              <div className="info-card">
                <div className="info-icon">⚡</div>
                <h3>App Environment</h3>
                <div className="status-indicator online">● Development</div>
                <p>Hot reload enabled</p>
                <p className="detail">Real-time updates active</p>
              </div>

              <div className="info-card">
                <div className="info-icon">🔄</div>
                <h3>Live Data Sync</h3>
                <div className="status-indicator online">● Running</div>
                <p>Game scores & stats syncing</p>
                <p className="detail">Updates every 15 minutes</p>
              </div>

              <div className="info-card">
                <div className="info-icon">🎯</div>
                <h3>Prediction Engine</h3>
                <div className="status-indicator online">● Ready</div>
                <p>Win/Loss Classifier active</p>
                <p className="detail">Score Regressor active</p>
              </div>

              <div className="info-card">
                <div className="info-icon">📊</div>
                <h3>App Technology</h3>
                <p>React 18 Web Application</p>
                <p>Neural Network AI Models</p>
                <p className="detail">Real-time data processing</p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'topology' && (
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

        {activeTab === 'system' && (
          <div className="admin-section">
            <h2>🏗️ Tech Stack & Infrastructure</h2>

            <div className="info-card">
              <h3>🏗️ Tech Stack</h3>
              <ul className="admin-list">
                <li><strong>Frontend:</strong> React 18 + React Router</li>
                <li><strong>Backend:</strong> Flask (Python 3.11)</li>
                <li><strong>Database:</strong> PostgreSQL 16</li>
                <li><strong>ML Framework:</strong> scikit-learn (Neural Networks)</li>
                <li><strong>Charts:</strong> Chart.js</li>
                <li><strong>Data Sources:</strong> ESPN API, nflverse</li>
              </ul>
            </div>

            <div className="info-card">
              <h3>🤖 Machine Learning Models</h3>
              <ul className="admin-list">
                <li><strong>Win/Loss Classifier:</strong> MLPClassifier (65.55% accuracy on test set)</li>
                <li><strong>Point Spread Regression:</strong> MLPRegressor (10.35 MAE on test set)</li>
                <li><strong>Training Data:</strong> 5,894 games with weighted sampling</li>
                <li><strong>Features:</strong> 39 statistical inputs per game</li>
                <li><strong>Update Frequency:</strong> Retrained after each season</li>
              </ul>
            </div>

            <div className="info-card">
              <h3>🔄 Model Retraining Strategy</h3>
              <p><strong>Why We Don't Retrain Weekly:</strong></p>
              <ul className="admin-list">
                <li><strong>Data Volume:</strong> Training set has 5,894 games. Adding 16 games/week (0.27% increase) has negligible impact.</li>
                <li><strong>Seasonality:</strong> NFL statistics stabilize around Week 4-5. Early-season anomalies would add noise, not signal.</li>
                <li><strong>Overfitting Risk:</strong> Training on current season data risks overfitting to small sample. Model would chase weekly noise instead of true patterns.</li>
                <li><strong>Computational Cost:</strong> Full retraining takes ~2 hours (feature engineering + hyperparameter tuning). Weekly retraining unnecessary.</li>
              </ul>
              
              <p style={{marginTop: '15px'}}><strong>When We DO Retrain:</strong></p>
              <ul className="admin-list">
                <li><strong>End of Season:</strong> After playoffs complete, add full 2025 season (~285 games) to training set.</li>
                <li><strong>Rule Changes:</strong> Major NFL rule changes affecting scoring or gameplay require immediate retraining.</li>
                <li><strong>Performance Degradation:</strong> If 2025 accuracy drops below 55%, investigate and retrain with updated features.</li>
              </ul>
            </div>

            <div className="info-card">
              <h3>🔁 Model Retraining Strategy</h3>
              <ul className="admin-list">
                <li><strong>Weekly Retraining:</strong> Not necessary - models use dynamic rolling features</li>
                <li><strong>Current Performance:</strong> 65.55% accuracy shows strong generalization</li>
                <li><strong>Data Updates:</strong> nfl_database_loader.py handles weekly game stats automatically</li>
                <li><strong>Prediction Improvement:</strong> Accuracy improves as season progresses (more data)</li>
                <li><strong>End-of-Season:</strong> Retrain with 2025 data for next season</li>
                <li><strong>Monitor Trigger:</strong> Retrain if accuracy drops significantly mid-season</li>
              </ul>
              <p className="admin-note">
                💡 Models are pre-trained on patterns, not specific teams. Weekly stats feed into dynamic features for predictions.
              </p>
            </div>

            <div className="info-card">
              <h3>🔄 Data Pipeline</h3>
              <ul className="admin-list">
                <li><strong>Live Updates:</strong> Every 15 minutes during games</li>
                <li><strong>Historical Data:</strong> Batch loaded from nflverse</li>
                <li><strong>Betting Odds:</strong> Real-time ESPN integration</li>
                <li><strong>Feature Engineering:</strong> Rolling stats, pre-game calculations</li>
              </ul>
            </div>
          </div>
        )}

        {activeTab === 'security' && (
          <div className="admin-section">
            <h2>Security & Access Control</h2>
            <div className="info-card">
              <h3>🔒 Current Status</h3>
              <p className="warning-text">⚠️ Authentication not yet implemented</p>
              <p>This admin panel is currently accessible to all users. Future enhancements will include:</p>
            </div>

            <div className="info-card">
              <h3>🚀 Planned Security Features</h3>
              <ul className="admin-list">
                <li><strong>User Authentication:</strong> Login system with JWT tokens</li>
                <li><strong>Role-Based Access:</strong> Admin, User, Guest roles</li>
                <li><strong>API Key Management:</strong> Secure external API credentials</li>
                <li><strong>Rate Limiting:</strong> Prevent API abuse</li>
                <li><strong>Audit Logging:</strong> Track admin actions</li>
                <li><strong>HTTPS/SSL:</strong> Encrypted connections</li>
              </ul>
            </div>

            <div className="info-card">
              <h3>🔑 Database Security</h3>
              <ul className="admin-list">
                <li><strong>Password:</strong> Stored in environment variables</li>
                <li><strong>Access:</strong> Localhost only (no external exposure)</li>
                <li><strong>Backups:</strong> Manual snapshots before major changes</li>
                <li><strong>SQL Injection:</strong> Protected via parameterized queries</li>
              </ul>
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
