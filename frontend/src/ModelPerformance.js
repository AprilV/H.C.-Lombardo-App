import React, { useState, useEffect } from 'react';
import './ModelPerformance.css';

const API_URL = '';

function ModelPerformance() {
  const [performanceData, setPerformanceData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedSeason, setSelectedSeason] = useState(2025);

  useEffect(() => {
    fetchPerformance();
    const interval = setInterval(fetchPerformance, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [selectedSeason]);

  const fetchPerformance = async () => {
    try {
      const response = await fetch(`${API_URL}/api/ml/performance-stats?season=${selectedSeason}`);
      const data = await response.json();
      
      if (data.success) {
        setPerformanceData(data);
        setError(null);
      } else {
        setError(data.error || 'Failed to load performance data');
      }
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch performance:', err);
      setError('Unable to connect to API');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="performance-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading performance data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="performance-container">
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          <p>{error}</p>
          <button onClick={fetchPerformance} className="retry-button">Retry</button>
        </div>
      </div>
    );
  }

  if (!performanceData || !performanceData.overall || performanceData.overall.total_games === 0) {
    return (
      <div className="performance-container">
        <div className="no-data-message">
          <span className="info-icon">📊</span>
          <h3>No Performance Data Yet</h3>
          <p>Performance stats will appear once 2025 games are predicted and results are recorded.</p>
          <p className="hint">Visit the ML Predictions page to generate predictions for upcoming games.</p>
        </div>
      </div>
    );
  }

  const { overall, by_week } = performanceData;
  const winRate = parseFloat(overall.win_accuracy) || 0;
  const avgError = parseFloat(overall.avg_margin_error) || 0;

  // Calculate performance tier
  const getPerformanceTier = (accuracy) => {
    if (accuracy >= 70) return { tier: 'Exceptional', color: '#10b981', emoji: '🔥' };
    if (accuracy >= 60) return { tier: 'Strong', color: '#3b82f6', emoji: '💪' };
    if (accuracy >= 55) return { tier: 'Above Average', color: '#8b5cf6', emoji: '📈' };
    if (accuracy >= 50) return { tier: 'Average', color: '#f59e0b', emoji: '⚖️' };
    return { tier: 'Below Target', color: '#ef4444', emoji: '⚠️' };
  };

  const perfTier = getPerformanceTier(winRate);

  // Vegas comparison
  const vegasAccuracy = 52.5; // Industry standard
  const beatVegas = winRate - vegasAccuracy;
  const vegasStatus = winRate >= vegasAccuracy ? 'BEATING' : 'BELOW';

  return (
    <div className="performance-container">
      {/* Season Selector */}
      <div className="season-selector-container">
        <h2 className="page-title">📊 AI Model Performance Tracking</h2>
        <div className="season-selector">
          <button 
            className={`season-btn ${selectedSeason === 2025 ? 'active' : ''}`}
            onClick={() => setSelectedSeason(2025)}
          >
            2025 Season
          </button>
          <button 
            className={`season-btn ${selectedSeason === 2024 ? 'active' : ''}`}
            onClick={() => setSelectedSeason(2024)}
          >
            2024 Season
          </button>
          <button 
            className={`season-btn ${selectedSeason === 2023 ? 'active' : ''}`}
            onClick={() => setSelectedSeason(2023)}
          >
            2023 Season
          </button>
        </div>
      </div>

      {/* HERO - AI vs Vegas Comparison */}
      <div className="vegas-hero">
        <h2 className="hero-title">🎯 AI vs Vegas Performance - {selectedSeason} Season</h2>
        <div className="hero-comparison">
          <div className="comparison-side ai-side">
            <div className="side-label">H.C. LOMBARDO AI</div>
            <div className="side-number ai-number">{winRate.toFixed(1)}%</div>
            <div className="side-detail">{overall.correct_predictions}/{overall.total_games} wins</div>
            <div className="side-tier" style={{ color: perfTier.color }}>
              {perfTier.emoji} {perfTier.tier}
            </div>
          </div>

          <div className="comparison-middle">
            <div className={`delta-badge ${vegasStatus.toLowerCase()}`}>
              <div className="delta-number">
                {beatVegas > 0 ? '+' : ''}{beatVegas.toFixed(1)}%
              </div>
              <div className="delta-label">{vegasStatus} VEGAS</div>
            </div>
            {beatVegas >= 2 && (
              <div className="winning-streak">🔥 Significantly outperforming!</div>
            )}
          </div>

          <div className="comparison-side vegas-side">
            <div className="side-label">VEGAS SPREADS</div>
            <div className="side-number vegas-number">{vegasAccuracy.toFixed(1)}%</div>
            <div className="side-detail">Industry Standard</div>
            <div className="side-tier" style={{ color: '#6b7280' }}>
              📈 Benchmark
            </div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="quick-stats">
        <div className="quick-stat">
          <div className="stat-icon-big">🎲</div>
          <div className="stat-value-big">{overall.total_games}</div>
          <div className="stat-label-small">Games Tracked</div>
        </div>
        <div className="quick-stat">
          <div className="stat-icon-big">✅</div>
          <div className="stat-value-big">{overall.correct_predictions}</div>
          <div className="stat-label-small">Correct Picks</div>
        </div>
        <div className="quick-stat">
          <div className="stat-icon-big">📏</div>
          <div className="stat-value-big">{avgError.toFixed(1)}</div>
          <div className="stat-label-small">Margin Error</div>
        </div>
        <div className="quick-stat">
          <div className="stat-icon-big">📅</div>
          <div className="stat-value-big">Wk {overall.first_week}-{overall.latest_week}</div>
          <div className="stat-label-small">2025 Season</div>
        </div>
      </div>

      {/* Accuracy Progress Bar */}
      <div className="accuracy-visualization">
        <h3>Win/Loss Accuracy</h3>
        <div className="progress-bar-container">
          <div className="progress-bar-bg">
            <div 
              className="progress-bar-fill" 
              style={{ 
                width: `${winRate}%`,
                background: `linear-gradient(90deg, ${perfTier.color}, ${perfTier.color}dd)`
              }}
            >
              <span className="progress-label">{winRate.toFixed(1)}%</span>
            </div>
          </div>
          <div className="progress-markers">
            <span className="marker">0%</span>
            <span className="marker">50%</span>
            <span className="marker">60%</span>
            <span className="marker">70%</span>
            <span className="marker">100%</span>
          </div>
        </div>
        <div className="benchmark-info">
          <div className="benchmark-item">
            <span className="benchmark-dot" style={{ background: '#ef4444' }}></span>
            <span>Below 50%: Coin Flip</span>
          </div>
          <div className="benchmark-item">
            <span className="benchmark-dot" style={{ background: '#f59e0b' }}></span>
            <span>50-55%: Average</span>
          </div>
          <div className="benchmark-item">
            <span className="benchmark-dot" style={{ background: '#8b5cf6' }}></span>
            <span>55-60%: Above Average</span>
          </div>
          <div className="benchmark-item">
            <span className="benchmark-dot" style={{ background: '#3b82f6' }}></span>
            <span>60-70%: Strong (Beats Vegas)</span>
          </div>
          <div className="benchmark-item">
            <span className="benchmark-dot" style={{ background: '#10b981' }}></span>
            <span>70%+: Exceptional</span>
          </div>
        </div>
      </div>

      {/* Week-by-Week Performance */}
      {by_week && by_week.length > 0 && (
        <div className="weekly-performance">
          <h3>📅 Week-by-Week Results</h3>

          <div className="weekly-chart">
            {/* Actual tracked weeks */}
            {by_week.map((week, index) => {
              const weekAccuracy = parseFloat(week.accuracy) || 0;
              const weekTier = getPerformanceTier(weekAccuracy);
              
              return (
                <div key={week.week} className="week-bar-container">
                  <div className="week-label">Week {week.week}</div>
                  <div className="week-bar-wrapper">
                    <div 
                      className="week-bar" 
                      style={{ 
                        width: `${weekAccuracy}%`,
                        background: weekTier.color
                      }}
                    >
                      <span className="week-bar-label">
                        {week.correct}/{week.games}
                      </span>
                    </div>
                    <span className="week-percentage">{weekAccuracy.toFixed(0)}%</span>
                  </div>
                </div>
              );
            })}

            {/* Week 1 Placeholder - ONLY show for 2023 season */}
            {selectedSeason === 2023 && (
              <div className="week-bar-container week-excluded">
                <div className="week-label">Week 1</div>
                <div className="week-bar-wrapper">
                  <div className="week-bar-excluded">
                    <span className="excluded-label">⚠️ Not Tracked - No prior 2023 data</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Week 1 Note - ONLY show for 2023 season */}
          {selectedSeason === 2023 && (
            <div className="week1-note">
              💡 <strong>Note:</strong> ML model requires current season rolling averages. 
              Week 1 2023 cannot use 2022 data (not available in dataset).
            </div>
          )}
        </div>
      )}

      {/* Performance Insights */}
      <div className="performance-insights">
        <h3>💡 Performance Insights</h3>
        <div className="insights-grid">
          <div className="insight-card">
            <div className="insight-icon">🎯</div>
            <div className="insight-content">
              <h4>Accuracy vs Vegas</h4>
              <p>
                {winRate >= 60 
                  ? `Beating Vegas spreads (~52-55%)! Model is performing exceptionally well.`
                  : winRate >= 55
                  ? `Above Vegas average. Model shows predictive value.`
                  : winRate >= 50
                  ? `Competitive with Vegas spreads. Room for improvement.`
                  : `Below Vegas benchmarks. May need model retraining or feature updates.`
                }
              </p>
            </div>
          </div>

          <div className="insight-card">
            <div className="insight-icon">📈</div>
            <div className="insight-content">
              <h4>Margin Prediction</h4>
              <p>
                {avgError < 10 
                  ? `Excellent margin accuracy (${avgError.toFixed(1)} pts). Very close to actual spreads.`
                  : avgError < 12
                  ? `Good margin predictions (${avgError.toFixed(1)} pts). Within expected range.`
                  : `Margin error of ${avgError.toFixed(1)} pts suggests opportunity to improve spread model.`
                }
              </p>
            </div>
          </div>

          <div className="insight-card">
            <div className="insight-icon">🔄</div>
            <div className="insight-content">
              <h4>Sample Size</h4>
              <p>
                {overall.total_games >= 100
                  ? `Strong sample size (${overall.total_games} games). Results are statistically significant.`
                  : overall.total_games >= 50
                  ? `Moderate sample (${overall.total_games} games). Accuracy should stabilize with more data.`
                  : `Early sample (${overall.total_games} games). Performance may vary as more games are predicted.`
                }
              </p>
            </div>
          </div>

          <div className="insight-card">
            <div className="insight-icon">⏱️</div>
            <div className="insight-content">
              <h4>Tracking Period</h4>
              <p>
                Weeks {overall.first_week} through {overall.latest_week} tracked. 
                {' '}Predictions automatically saved and scored after each game.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Last Updated */}
      <div className="last-updated">
        <span className="update-icon">🔄</span>
        Last updated: {new Date().toLocaleTimeString()}
        <span className="auto-refresh">• Auto-refreshes every 30 seconds</span>
      </div>
    </div>
  );
}

export default ModelPerformance;
