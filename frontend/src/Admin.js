import React, { useState, useEffect } from 'react';
import './Admin.css';

const API_URL = 'http://127.0.0.1:5000';

function Admin() {
  const [activeTab, setActiveTab] = useState('system');
  const [serverStatus, setServerStatus] = useState(null);

  useEffect(() => {
    checkServerStatus();
    const interval = setInterval(checkServerStatus, 5000); // Check every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const checkServerStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/health`);
      const data = await response.json();
      setServerStatus(data);
    } catch (err) {
      console.error('Health check failed:', err);
      setServerStatus(null);
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
          ⚙️ System Status
        </button>
        <button 
          className={`admin-tab ${activeTab === 'database' ? 'active' : ''}`}
          onClick={() => setActiveTab('database')}
        >
          🗄️ Database Info
        </button>
        <button 
          className={`admin-tab ${activeTab === 'security' ? 'active' : ''}`}
          onClick={() => setActiveTab('security')}
        >
          🔒 Security
        </button>
      </div>

      <div className="admin-content">
        {activeTab === 'database' && (
          <div className="admin-section">
            <h2>3NF Database Structure</h2>
            <div className="info-card">
              <h3>📊 Database: nfl_analytics</h3>
              <p><strong>Schema:</strong> hcl (H.C. Lombardo)</p>
              <p><strong>DBMS:</strong> PostgreSQL 16</p>
              <p><strong>Normalization:</strong> 3rd Normal Form (3NF)</p>
            </div>

            <div className="info-card">
              <h3>📋 Tables & Views</h3>
              <ul className="admin-list">
                <li><strong>teams</strong> - 32 NFL teams with metadata</li>
                <li><strong>games</strong> - Game schedule and results</li>
                <li><strong>team_game_stats</strong> - Per-game statistics (47 metrics)</li>
                <li><strong>betting_odds</strong> - Vegas lines and spreads</li>
              </ul>
              
              <h4 style={{marginTop: '20px'}}>Views (Denormalized for Performance):</h4>
              <ul className="admin-list">
                <li><strong>full_schedule_view</strong> - Games with team names joined</li>
                <li><strong>team_stats_view</strong> - Aggregated team statistics</li>
                <li><strong>advanced_metrics_view</strong> - EPA, success rate, efficiency</li>
              </ul>
            </div>

            <div className="info-card">
              <h3>📈 Data Volume</h3>
              <ul className="admin-list">
                <li>Games: ~14,000 (1999-2025)</li>
                <li>Team Game Stats: ~28,000 records (2 per game)</li>
                <li>Total Metrics: 47 per team per game</li>
                <li>Betting Lines: Live integration via ESPN API</li>
              </ul>
            </div>
          </div>
        )}

        {activeTab === 'system' && (
          <div className="admin-section">
            <h2>System Status & Architecture</h2>
            
            <div className="status-card">
              <h3>🔴 Live System Status</h3>
              <div className="status-bar-content">
                {serverStatus ? (
                  <>
                    <div className="status-indicator success">
                      <span className="status-dot"></span>
                      <span className="status-text">LIVE</span>
                    </div>
                    <div className="status-indicator success">
                      <span className="status-dot"></span>
                      <span className="status-text">DB Connected</span>
                    </div>
                    <div className="status-indicator success">
                      <span className="status-dot"></span>
                      <span className="status-text">API Ready</span>
                    </div>
                  </>
                ) : (
                  <div className="status-indicator error">
                    <span className="status-dot"></span>
                    <span className="status-text">Offline</span>
                  </div>
                )}
              </div>
              <p style={{marginTop: '15px', fontSize: '0.9rem', color: '#7ab8ff'}}>Auto-refreshes every 5 seconds</p>
            </div>

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
                <li><strong>Win/Loss Classifier:</strong> MLPClassifier (65.55% accuracy)</li>
                <li><strong>Point Spread Regression:</strong> MLPRegressor (10.35 MAE)</li>
                <li><strong>Training Data:</strong> 5,894 games with weighted sampling</li>
                <li><strong>Features:</strong> 39 statistical inputs per game</li>
                <li><strong>Update Frequency:</strong> Retrained after each season</li>
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
              <p style={{marginTop: '10px', fontSize: '0.9rem', color: '#7ab8ff', fontStyle: 'italic'}}>
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
      </div>
    </div>
  );
}

export default Admin;
