import React, { useState, useEffect } from 'react';
import './ModelPerformance.css';
import { getDefaultSeason, getRecentSeasons } from './utils/season';
import { getPerformanceStatsUrl, getSeasonAiVsVegasUrl } from './utils/mlApi';

function ModelPerformance() {
  const defaultSeason = getDefaultSeason();
  const seasonOptions = getRecentSeasons(6, 1999, defaultSeason);

  const [performanceData, setPerformanceData] = useState(null);
  const [seasonVsVegas, setSeasonVsVegas] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [error, setError] = useState(null);
  const [selectedSeason, setSelectedSeason] = useState(defaultSeason);

  useEffect(() => {
    fetchPerformance();
    const interval = setInterval(() => fetchPerformance({ silent: true }), 10000); // Refresh every 10 seconds
    const onFocus = () => fetchPerformance({ silent: true });
    window.addEventListener('focus', onFocus);
    document.addEventListener('visibilitychange', onFocus);

    return () => {
      clearInterval(interval);
      window.removeEventListener('focus', onFocus);
      document.removeEventListener('visibilitychange', onFocus);
    };
  }, [selectedSeason]);

  const fetchPerformanceForSeason = async (season) => {
    const response = await fetch(getPerformanceStatsUrl(season));
    return response.json();
  };

  const fetchSeasonVsVegasForSeason = async (season) => {
    const response = await fetch(getSeasonAiVsVegasUrl(season));
    return response.json();
  };

  const fetchPerformance = async ({ silent = false } = {}) => {
    if (!silent) {
      setRefreshing(true);
    }
    try {
      const [data, vsVegasData] = await Promise.all([
        fetchPerformanceForSeason(selectedSeason),
        fetchSeasonVsVegasForSeason(selectedSeason)
      ]);
      
      if (data.success) {
        setPerformanceData(data);
        setSeasonVsVegas(vsVegasData?.success ? vsVegasData : null);
        setLastUpdated(new Date());
        setError(null);
      } else {
        setError(data.error || 'Failed to load performance data');
      }
      setLoading(false);
    } catch (err) {
      if (!silent) {
        setError('Unable to connect to API');
      }
      setLoading(false);
    } finally {
      if (!silent) {
        setRefreshing(false);
      }
    }
  };

  const formatLastUpdated = () => {
    if (!lastUpdated) {
      return 'Waiting for first sync';
    }
    return `Last updated ${lastUpdated.toLocaleTimeString()}`;
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

  const modelBreakdown = performanceData?.model_breakdown || {};
  const seasonTrend = performanceData?.season_trend || [];
  const integrity = performanceData?.integrity || {};
  const warnings = performanceData?.warnings || [];
  const xgbSummary = modelBreakdown?.xgb || {};
  const eloSummary = modelBreakdown?.elo || {};
  const agreementSummary = modelBreakdown?.agreement || {};
  const vegasSummary = modelBreakdown?.vegas || {};
  const completedGames = Number(performanceData?.completed_games || 0);

  const xgbGames = Number(xgbSummary?.scored_games || 0);
  const eloGames = Number(eloSummary?.scored_games || 0);
  const hasAnyPerformanceData = xgbGames > 0 || eloGames > 0;

  const getModelDataStatus = (modelName, summary) => {
    const predictedGames = Number(summary?.predicted_games || 0);
    const scoredGames = Number(summary?.scored_games || 0);

    if (completedGames === 0) {
      return `No completed regular-season games are available for ${selectedSeason}.`;
    }

    if (predictedGames === 0) {
      return `${modelName} has no tracked prediction rows for this season.`;
    }

    if (scoredGames === 0) {
      return `${modelName} predictions exist but no rows are scored yet.`;
    }

    if (scoredGames < completedGames) {
      return `${modelName} has partial scored coverage (${scoredGames}/${completedGames}).`;
    }

    return `${modelName} has full scored coverage (${scoredGames}/${completedGames}).`;
  };

  const sortedSeasonTrend = seasonTrend
    .filter((row) => Number(row?.season || 0) >= 2021)
    .sort((a, b) => {
      const seasonA = Number(a?.season || 0);
      const seasonB = Number(b?.season || 0);
      return seasonA - seasonB;
    });

  if (!hasAnyPerformanceData) {
    const completedGames = Number(performanceData?.completed_games || 0);

    return (
      <div className="performance-container">
        <div className="no-data-message">
          <span className="info-icon">📊</span>
          <h3>No Scored Model Data For {selectedSeason}</h3>
          <p>Completed games: {completedGames}</p>
          <p>XGBoost scored predictions: {xgbGames}</p>
          <p>Elo scored predictions: {eloGames}</p>
          <p className="hint">This season is selected correctly; data is not being hidden by auto-fallback.</p>
        </div>
      </div>
    );
  }

  const { overall, by_week } = performanceData;
  const primaryModel = overall?.model === 'elo' ? 'elo' : 'xgb';
  const primarySummary = primaryModel === 'elo' ? eloSummary : xgbSummary;
  const winRate = parseFloat(primarySummary?.win_accuracy ?? overall?.win_accuracy) || 0;
  const avgError = parseFloat(primarySummary?.avg_margin_error ?? overall?.avg_margin_error) || 0;

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
  const hasAtsData = Boolean(
    seasonVsVegas
    && Number.isFinite(Number(seasonVsVegas?.total_games))
    && Number(seasonVsVegas?.total_games) > 0
  );

  const aiVsVegasAiPct = hasAtsData
    ? Number(seasonVsVegas.ai_percentage || 0)
    : 0;
  const aiVsVegasVegasPct = hasAtsData
    ? Number(seasonVsVegas.vegas_percentage || 0)
    : 0;
  const beatVegas = aiVsVegasAiPct - aiVsVegasVegasPct;
  const vegasStatus = !hasAtsData
    ? 'UNAVAILABLE'
    : (aiVsVegasAiPct >= aiVsVegasVegasPct ? 'BEATING' : 'BELOW');

  const aiVsVegasRecord = hasAtsData
    ? `${seasonVsVegas.ai_wins} - ${seasonVsVegas.vegas_wins}`
    : 'Unavailable';

  const aiVsVegasDetail = hasAtsData
    ? `Ties ${seasonVsVegas.ties} | Games ${seasonVsVegas.total_games}`
    : 'ATS season data unavailable';

  return (
    <div className="performance-container">
      {/* Season Selector */}
      <div className="season-selector-container">
        <h2 className="page-title">📊 AI Model Performance Tracking</h2>
        <div className="season-selector">
          {seasonOptions.map((season) => (
            <button
              key={season}
              className={`season-btn ${selectedSeason === season ? 'active' : ''}`}
              onClick={() => setSelectedSeason(season)}
            >
              {season} Season
            </button>
          ))}
        </div>
        <div className="live-status-row">
          <div className="live-status-text">
            Live sync every 10s | {formatLastUpdated()}
          </div>
          <button
            className="refresh-now-btn"
            type="button"
            onClick={() => fetchPerformance()}
            disabled={refreshing}
          >
            {refreshing ? 'Refreshing...' : 'Refresh Now'}
          </button>
        </div>
      </div>

      {/* HERO - AI vs Vegas Comparison */}
      <div className="vegas-hero">
        <h2 className="hero-title">🎯 AI vs Vegas Performance - {selectedSeason} Season</h2>
        <div className="hero-comparison">
          <div className="comparison-side ai-side">
            <div className="side-label">H.C. LOMBARDO AI (SPREAD H2H)</div>
            <div className="side-number ai-number">{hasAtsData ? `${aiVsVegasAiPct.toFixed(1)}%` : 'N/A'}</div>
            <div className="side-detail">Record: {aiVsVegasRecord}</div>
            {hasAtsData ? (
              <div className="side-tier" style={{ color: perfTier.color }}>
                {perfTier.emoji} {perfTier.tier}
              </div>
            ) : (
              <div className="side-tier" style={{ color: '#6b7280' }}>
                ATS unavailable
              </div>
            )}
          </div>

          <div className="comparison-middle">
            <div className={`delta-badge ${vegasStatus.toLowerCase()}`}>
              {hasAtsData ? (
                <>
                  <div className="delta-number">
                    {beatVegas > 0 ? '+' : ''}{beatVegas.toFixed(1)}%
                  </div>
                  <div className="delta-label">{vegasStatus} VEGAS</div>
                </>
              ) : (
                <>
                  <div className="delta-number">N/A</div>
                  <div className="delta-label">ATS UNAVAILABLE</div>
                </>
              )}
            </div>
            {hasAtsData && beatVegas >= 2 && (
              <div className="winning-streak">Significantly outperforming</div>
            )}
          </div>

          <div className="comparison-side vegas-side">
            <div className="side-label">VEGAS SPREADS (SPREAD H2H)</div>
            <div className="side-number vegas-number">{hasAtsData ? `${aiVsVegasVegasPct.toFixed(1)}%` : 'N/A'}</div>
            <div className="side-detail">{aiVsVegasDetail}</div>
            <div className="side-tier" style={{ color: '#6b7280' }}>
              📈 Benchmark
            </div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="quick-stats">
        {hasAtsData ? (
          <>
            <div className="quick-stat">
              <div className="stat-icon-big">🎲</div>
              <div className="stat-value-big">{seasonVsVegas.total_games}</div>
              <div className="stat-label-small">H2H Games</div>
            </div>
            <div className="quick-stat">
              <div className="stat-icon-big">🤖</div>
              <div className="stat-value-big">{seasonVsVegas.ai_wins}</div>
              <div className="stat-label-small">AI Wins</div>
            </div>
            <div className="quick-stat">
              <div className="stat-icon-big">🎰</div>
              <div className="stat-value-big">{seasonVsVegas.vegas_wins}</div>
              <div className="stat-label-small">Vegas Wins</div>
            </div>
            <div className="quick-stat">
              <div className="stat-icon-big">🤝</div>
              <div className="stat-value-big">{seasonVsVegas.ties}</div>
              <div className="stat-label-small">Ties</div>
            </div>
          </>
        ) : (
          <>
            <div className="quick-stat">
              <div className="stat-icon-big">🎲</div>
              <div className="stat-value-big">{overall.total_games}</div>
              <div className="stat-label-small">Primary Model Games</div>
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
              <div className="stat-label-small">{selectedSeason} Season</div>
            </div>
          </>
        )}
      </div>

      <div className="performance-insights">
        <h3>🤖 Model Coverage & Accuracy</h3>
        <div className="insights-grid">
          <div className="insight-card">
            <div className="insight-icon">🧠</div>
            <div className="insight-content">
              <h4>XGBoost</h4>
              <p>
                Accuracy: {xgbGames > 0 ? `${(parseFloat(xgbSummary?.win_accuracy) || 0).toFixed(1)}%` : 'N/A'}
                {' '}| Scored: {xgbGames}
                {' '}| Coverage: {(parseFloat(xgbSummary?.coverage_pct) || 0).toFixed(1)}%
              </p>
              <p className="data-availability">{getModelDataStatus('XGBoost', xgbSummary)}</p>
            </div>
          </div>

          <div className="insight-card">
            <div className="insight-icon">📈</div>
            <div className="insight-content">
              <h4>Elo</h4>
              <p>
                Accuracy: {eloGames > 0 ? `${(parseFloat(eloSummary?.win_accuracy) || 0).toFixed(1)}%` : 'N/A'}
                {' '}| Scored: {eloGames}
                {' '}| Coverage: {(parseFloat(eloSummary?.coverage_pct) || 0).toFixed(1)}%
              </p>
              <p className="data-availability">{getModelDataStatus('Elo', eloSummary)}</p>
            </div>
          </div>

          <div className="insight-card">
            <div className="insight-icon">🤝</div>
            <div className="insight-content">
              <h4>Head-to-Head Agreement</h4>
              <p>
                Agreement: {(parseFloat(agreementSummary?.agreement_rate) || 0).toFixed(1)}%
                {' '}| Both Models: {agreementSummary?.both_models_games || 0}
                {' '}| Splits: {agreementSummary?.split_games || 0}
              </p>
              <p className="data-availability">
                Head-to-head on splits: XGBoost {agreementSummary?.xgb_head_to_head_wins || 0}
                {' '}| Elo {agreementSummary?.elo_head_to_head_wins || 0}
                {' '}| Ties {agreementSummary?.head_to_head_ties || 0}
              </p>
            </div>
          </div>

          <div className="insight-card">
            <div className="insight-icon">🎰</div>
            <div className="insight-content">
              <h4>Vegas Benchmark</h4>
              <p>
                Accuracy: {(parseFloat(vegasSummary?.win_accuracy) || 0).toFixed(1)}%
                {' '}| Correct: {vegasSummary?.correct_predictions || 0}
                {' '}| Evaluable: {vegasSummary?.evaluable_games || 0}
              </p>
              <p className="data-availability">
                Evaluable spread rows: {vegasSummary?.evaluable_games || 0}/{completedGames}
              </p>
            </div>
          </div>
        </div>
      </div>

      {sortedSeasonTrend.length > 0 && (
        <div className="season-trend-section">
          <h3>📈 Multi-Season Trend</h3>
          <p className="season-trend-subtitle">
            Accuracy and scored coverage by season across XGBoost, Elo, and Vegas benchmark.
          </p>

          <div className="season-trend-grid">
            {sortedSeasonTrend.map((seasonRow) => {
              const trendSeason = seasonRow?.season;
              const trendXgb = seasonRow?.xgb || {};
              const trendElo = seasonRow?.elo || {};
              const trendVegas = seasonRow?.vegas || {};

              const trendXgbAcc = Number(trendXgb?.win_accuracy || 0);
              const trendEloAcc = Number(trendElo?.win_accuracy || 0);
              const trendVegasAcc = Number(trendVegas?.win_accuracy || 0);

              return (
                <div key={trendSeason} className="season-trend-card">
                  <h4>{trendSeason} Season</h4>
                  <p className="season-trend-meta">Completed games: {seasonRow?.completed_games || 0}</p>

                  <div className="trend-row">
                    <span className="trend-label">XGBoost</span>
                    <div className="trend-bar-bg">
                      <div className="trend-bar trend-bar-xgb" style={{ width: `${trendXgbAcc}%` }}></div>
                    </div>
                    <span className="trend-value">{trendXgbAcc.toFixed(1)}%</span>
                  </div>
                  <p className="trend-coverage">Coverage: {Number(trendXgb?.coverage_pct || 0).toFixed(1)}%</p>

                  <div className="trend-row">
                    <span className="trend-label">Elo</span>
                    <div className="trend-bar-bg">
                      <div className="trend-bar trend-bar-elo" style={{ width: `${trendEloAcc}%` }}></div>
                    </div>
                    <span className="trend-value">{trendEloAcc.toFixed(1)}%</span>
                  </div>
                  <p className="trend-coverage">Coverage: {Number(trendElo?.coverage_pct || 0).toFixed(1)}%</p>

                  <div className="trend-row">
                    <span className="trend-label">Vegas</span>
                    <div className="trend-bar-bg">
                      <div className="trend-bar trend-bar-vegas" style={{ width: `${trendVegasAcc}%` }}></div>
                    </div>
                    <span className="trend-value">{trendVegasAcc.toFixed(1)}%</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {warnings.length > 0 && (
        <div className="performance-insights">
          <h3>⚠️ Data Integrity Warnings</h3>
          <div className="insights-grid">
            {warnings.map((warningText, idx) => (
              <div key={idx} className="insight-card">
                <div className="insight-icon">🧪</div>
                <div className="insight-content">
                  <h4>Quality Check</h4>
                  <p>{warningText}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {integrity?.leakage && integrity?.totals_line_lock && (
        <div className="performance-insights">
          <h3>🔍 Integrity Snapshot</h3>
          <div className="insights-grid">
            <div className="insight-card">
              <div className="insight-icon">⏱️</div>
              <div className="insight-content">
                <h4>Prediction Timing</h4>
                <p>Predicted after game date: {(parseFloat(integrity?.leakage?.predicted_after_game_date_pct) || 0).toFixed(1)}%</p>
              </div>
            </div>

            <div className="insight-card">
              <div className="insight-icon">➕➖</div>
              <div className="insight-content">
                <h4>Margin Sign Consistency</h4>
                <p>Inconsistent actual margin sign: {(parseFloat(integrity?.margin_sign?.inconsistent_pct) || 0).toFixed(1)}%</p>
              </div>
            </div>

            <div className="insight-card">
              <div className="insight-icon">🎯</div>
              <div className="insight-content">
                <h4>Totals Line Lock</h4>
                <p>Predicted total = Vegas total: {(parseFloat(integrity?.totals_line_lock?.line_locked_pct) || 0).toFixed(1)}%</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Accuracy Progress Bar */}
      <div className="accuracy-visualization">
        <h3>Win/Loss Accuracy ({primaryModel === 'elo' ? 'Elo' : 'XGBoost'})</h3>
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
          <h3>📅 Week-by-Week Results ({primaryModel === 'elo' ? 'Elo' : 'XGBoost'})</h3>

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

          </div>
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
