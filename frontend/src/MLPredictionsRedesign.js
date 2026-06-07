import React, { useState, useEffect } from 'react';
import './MLPredictionsRedesign.css';
import { getDefaultSeason, getRecentSeasons } from './utils/season';
import { getEspnTeamLogoUrl } from './utils/teamLogos';
import { getSeasonAiVsVegasUrl } from './utils/mlApi';

const API_URL = process.env.REACT_APP_API_URL ?? '';

function MLPredictionsRedesign() {
  const defaultSeason = getDefaultSeason();
  const seasonOptions = getRecentSeasons(6, 2020, defaultSeason);

  const [season, setSeason] = useState(defaultSeason);
  const [week, setWeek] = useState(null);
  const [availableWeeks, setAvailableWeeks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [combinedData, setCombinedData] = useState([]);
  const [seasonStats, setSeasonStats] = useState(null);
  const [seasonStatsLoading, setSeasonStatsLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [error, setError] = useState(null);
  const [authRequired, setAuthRequired] = useState(false);
  const [authUsername, setAuthUsername] = useState('');
  const [authPassword, setAuthPassword] = useState('');
  const [view, setView] = useState('winner-picks'); // 'winner-picks', 'spreads'

  const authHeader = authUsername && authPassword
    ? `Basic ${window.btoa(`${authUsername}:${authPassword}`)}`
    : '';

  const fetchJson = async (url) => {
    const response = await fetch(url, {
      credentials: 'include',
      headers: {
        Accept: 'application/json',
        ...(authHeader ? { Authorization: authHeader } : {})
      }
    });

    if (!response.ok) {
      const body = await response.text();
      const summary = body ? body.slice(0, 120) : `HTTP ${response.status}`;
      if (response.status === 401) {
        throw new Error(`AUTH_REQUIRED: ${summary}`);
      }
      throw new Error(`HTTP_${response.status}: ${summary}`);
    }

    return response.json();
  };

  useEffect(() => {
    fetchAvailableWeeks();
    fetchUpcomingPredictions();
  }, []);

  useEffect(() => {
    if (week && season) {
      fetchCombinedPredictions();
    }
  }, [week, season]);

  useEffect(() => {
    if (season) {
      fetchSeasonStats(season);
    }
  }, [season]);

  useEffect(() => {
    const interval = setInterval(() => {
      if (season) {
        fetchSeasonStats(season, { silent: true });
      }
      if (week && season) {
        fetchCombinedPredictions({ silent: true });
      }
    }, 10000);

    const onFocus = () => {
      if (season) {
        fetchSeasonStats(season, { silent: true });
      }
      if (week && season) {
        fetchCombinedPredictions({ silent: true });
      }
    };

    window.addEventListener('focus', onFocus);
    document.addEventListener('visibilitychange', onFocus);

    return () => {
      clearInterval(interval);
      window.removeEventListener('focus', onFocus);
      document.removeEventListener('visibilitychange', onFocus);
    };
  }, [season, week]);

  const fetchAvailableWeeks = async () => {
    try {
      const data = await fetchJson(`${API_URL}/api/ml/available-weeks`);
      if (data.success) {
        setAvailableWeeks(data.weeks || []);
      }
    } catch (err) {
      setAvailableWeeks([]);
    }
  };

  const fetchUpcomingPredictions = async () => {
    setLoading(true);
    try {
      const data = await fetchJson(`${API_URL}/api/ml/predict-upcoming`);
      
      if (data.season && data.week) {
        setSeason(data.season);
        setWeek(data.week);
      }
      setAuthRequired(false);
    } catch (err) {
      if (String(err?.message || '').includes('AUTH_REQUIRED')) {
        setAuthRequired(true);
        setError('Authentication required for ML endpoints. Enter credentials and retry.');
      } else {
        setError('Failed to load upcoming predictions');
      }
    }
    setLoading(false);
  };

  const fetchCombinedPredictions = async ({ silent = false } = {}) => {
    if (!silent) {
      setRefreshing(true);
      setLoading(true);
      setError(null);
    }
    try {
      const data = await fetchJson(`${API_URL}/api/predictions/combined/${season}/${week}`);
      
      if (data.success) {
        setCombinedData(data.predictions || []);
        setLastUpdated(new Date());
        setAuthRequired(false);
      } else {
        setError(data.message || 'No predictions available');
      }
    } catch (err) {
      if (!silent) {
        if (String(err?.message || '').includes('AUTH_REQUIRED')) {
          setAuthRequired(true);
          setError('Authentication required for ML endpoints. Enter credentials and retry.');
        } else {
          setError('Failed to load predictions');
        }
      }
    }
    if (!silent) {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const fetchSeasonStats = async (selectedSeason = season, { silent = false } = {}) => {
    if (!silent) {
      setSeasonStatsLoading(true);
    }
    try {
      const data = await fetchJson(getSeasonAiVsVegasUrl(selectedSeason));

      if (data.success) {
        setSeasonStats(data);
        setLastUpdated(new Date());
        setAuthRequired(false);
      } else {
        setSeasonStats(null);
      }
    } catch (err) {
      if (!silent) {
        if (String(err?.message || '').includes('AUTH_REQUIRED')) {
          setAuthRequired(true);
          setError('Authentication required for ML endpoints. Enter credentials and retry.');
        }
        setSeasonStats(null);
      }
    }
    if (!silent) {
      setSeasonStatsLoading(false);
    }
  };

  const refreshAll = async () => {
    setRefreshing(true);
    try {
      if (season) {
        await fetchSeasonStats(season);
      }
      if (week && season) {
        await fetchCombinedPredictions();
      }
    } finally {
      setRefreshing(false);
    }
  };

  const formatLastUpdated = () => {
    if (!lastUpdated) {
      return 'Waiting for first sync';
    }
    return `Last updated ${lastUpdated.toLocaleTimeString()}`;
  };

  const getTeamLogo = (team) => {
    return getEspnTeamLogoUrl(team);
  };

  const formatTeamLabel = (team) => {
    if (!team || typeof team !== 'string') {
      return 'TBD';
    }

    const trimmed = team.trim();
    if (!trimmed) {
      return 'TBD';
    }

    const normalized = trimmed.toUpperCase();
    if (['UNDEFINED', 'NULL', 'NAN', 'NONE', 'N/A', 'NA', 'TBD', '-'].includes(normalized)) {
      return 'TBD';
    }

    return trimmed;
  };

  const formatSpreadForHome = (team, spread) => {
    if (!team || spread === null || spread === undefined || Number.isNaN(Number(spread))) {
      return 'N/A';
    }

    const value = Number(spread);
    return `${team} ${value > 0 ? '+' : ''}${value.toFixed(1)}`;
  };

  const getModelResultMeta = (correct, label) => {
    if (correct === true) {
      return { className: 'correct', text: `${label} Correct`, icon: '✅' };
    }

    if (correct === false) {
      return { className: 'wrong', text: `${label} Missed`, icon: '❌' };
    }

    return { className: 'unknown', text: `${label} Pending`, icon: '⏳' };
  };

  const renderWinnerPicks = () => {
    if (!combinedData || combinedData.length === 0) return null;

    return (
      <div className="winner-picks-view">
        <div className="section-header">
          <h2>🏆 Winner Predictions</h2>
          <p>Who will win each game? Combined AI + Elo analysis</p>
        </div>

        <div className="picks-grid">
          {combinedData.map((game, idx) => {
            const hasElo = !!game.elo;
            const hasXgb = !!game.xgb;
            const eloWinner = game.elo?.predicted_winner;
            const xgbWinner = game.xgb?.predicted_winner;
            const agreement = hasElo && hasXgb ? game.agreement : null;

            const isFinal = game.game_status === 'final';
            const actual = game.actual || {};
            const modelResults = game.model_results || {};
            const xgbResultMeta = hasXgb ? getModelResultMeta(modelResults.xgb_correct, 'AI') : null;
            const eloResultMeta = hasElo ? getModelResultMeta(modelResults.elo_correct, 'Elo') : null;

            const eloConf = hasElo ? (game.elo?.confidence || 0) : null;
            const xgbConf = hasXgb ? (game.xgb?.confidence || 0) : null;
            const avgConf = (eloConf + xgbConf) / 2;

            return (
              <div key={idx} className={`pick-card ${agreement ? 'agreement' : 'disagreement'}`}>
                <div className="pick-header">
                  <div className="matchup-teams">
                    <img src={getTeamLogo(game.away_team)} alt={game.away_team} className="team-logo-small" />
                    <span className="team-name">{game.away_team}</span>
                    <span className="vs">@</span>
                    <span className="team-name">{game.home_team}</span>
                    <img src={getTeamLogo(game.home_team)} alt={game.home_team} className="team-logo-small" />
                  </div>
                </div>

                <div className="pick-body">
                  {hasElo && hasXgb && agreement ? (
                    <>
                      <div className="consensus-pick">
                        <div className="consensus-badge">✓ CONSENSUS</div>
                        <div className="winner-display">
                          <img src={getTeamLogo(eloWinner)} alt={eloWinner} className="winner-logo" />
                          <span className="winner-team">{formatTeamLabel(eloWinner)}</span>
                        </div>
                        <div className="confidence-bar">
                          <div className="confidence-fill" style={{width: `${avgConf * 100}%`}}></div>
                          <span className="confidence-text">{(avgConf * 100).toFixed(0)}% Confidence</span>
                        </div>
                      </div>

                      <div className="model-breakdown">
                        <div className="model-conf">
                          <span className="model-label">📈 Elo:</span>
                          <span className="conf-value">{(eloConf * 100).toFixed(0)}%</span>
                        </div>
                        <div className="model-conf">
                          <span className="model-label">🤖 AI:</span>
                          <span className="conf-value">{(xgbConf * 100).toFixed(0)}%</span>
                        </div>
                        <div className="model-conf vegas">
                          <span className="model-label">🎰 Vegas:</span>
                          <span className="conf-value">
                            {formatSpreadForHome(game.home_team, game.vegas_spread)}
                          </span>
                        </div>
                      </div>
                    </>
                  ) : hasElo && hasXgb ? (
                    <>
                      <div className="split-badge">⚠️ SPLIT PREDICTION</div>
                      <div className="split-picks">
                        <div className="split-pick">
                          <div className="split-model">📈 Elo</div>
                          <div className="split-winner">
                            <img src={getTeamLogo(eloWinner)} alt={eloWinner} className="split-logo" />
                            <span>{formatTeamLabel(eloWinner)}</span>
                          </div>
                          <div className="split-conf">{(eloConf * 100).toFixed(0)}%</div>
                        </div>
                        <div className="vs-divider">vs</div>
                        <div className="split-pick">
                          <div className="split-model">🤖 AI</div>
                          <div className="split-winner">
                            <img src={getTeamLogo(xgbWinner)} alt={xgbWinner} className="split-logo" />
                            <span>{formatTeamLabel(xgbWinner)}</span>
                          </div>
                          <div className="split-conf">{(xgbConf * 100).toFixed(0)}%</div>
                        </div>
                      </div>

                      <div className="model-breakdown split-info">
                        <div className="split-note">Models disagree - toss-up game</div>
                        <div className="model-conf vegas">
                          <span className="model-label">🎰 Vegas Line:</span>
                          <span className="conf-value">
                            {formatSpreadForHome(game.home_team, game.vegas_spread)}
                          </span>
                        </div>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="split-badge">ℹ️ SINGLE MODEL AVAILABLE</div>
                      <div className="split-picks">
                        <div className="split-pick">
                          <div className="split-model">{hasElo ? '📈 Elo' : '🤖 AI'}</div>
                          <div className="split-winner">
                            <img
                              src={getTeamLogo(hasElo ? eloWinner : xgbWinner)}
                              alt={hasElo ? eloWinner : xgbWinner}
                              className="split-logo"
                            />
                            <span>{formatTeamLabel(hasElo ? eloWinner : xgbWinner)}</span>
                          </div>
                          <div className="split-conf">
                            {hasElo ? `${(eloConf * 100).toFixed(0)}%` : `${(xgbConf * 100).toFixed(0)}%`}
                          </div>
                        </div>
                        <div className="vs-divider">vs</div>
                        <div className="split-pick">
                          <div className="split-model">{hasElo ? '🤖 AI' : '📈 Elo'}</div>
                          <div className="split-winner">
                            <span>{hasElo ? 'Pending' : 'Pending'}</span>
                          </div>
                          <div className="split-conf">N/A</div>
                        </div>
                      </div>

                      <div className="model-breakdown split-info">
                        <div className="split-note">One model is available for this matchup right now</div>
                        <div className="model-conf vegas">
                          <span className="model-label">🎰 Vegas Line:</span>
                          <span className="conf-value">{formatSpreadForHome(game.home_team, game.vegas_spread)}</span>
                        </div>
                      </div>
                    </>
                  )}

                  <div className={`pick-outcome-strip ${isFinal ? 'final' : 'scheduled'}`}>
                    {isFinal ? (
                      <>
                        <div className="final-result-line">
                          Final: {game.away_team} {actual.away_score} - {game.home_team} {actual.home_score}
                          {' '}| Winner: {actual.winner}
                        </div>
                        <div className="model-results-line">
                          {xgbResultMeta && (
                            <span className={`model-result-badge ${xgbResultMeta.className}`}>
                              {xgbResultMeta.icon} {xgbResultMeta.text}
                            </span>
                          )}
                          {eloResultMeta && (
                            <span className={`model-result-badge ${eloResultMeta.className}`}>
                              {eloResultMeta.icon} {eloResultMeta.text}
                            </span>
                          )}
                        </div>
                      </>
                    ) : (
                      <div className="final-result-line">Scheduled - final result pending</div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const renderSpreads = () => {
    if (!combinedData || combinedData.length === 0) return null;

    return (
      <div className="spreads-view">
        <div className="section-header">
          <h2>📊 Point Spread Analysis</h2>
          <p>By how much? Spread predictions vs Vegas lines</p>
        </div>

        <div className="spreads-table">
          <div className="table-header">
            <div className="col-matchup">Matchup</div>
            <div className="col-spread">Elo Spread</div>
            <div className="col-spread">AI Spread</div>
            <div className="col-spread">Vegas Line</div>
            <div className="col-edge">Edge</div>
          </div>

          {combinedData.map((game, idx) => {
            const eloSpread = game.elo?.spread;
            const xgbSpread = game.xgb?.spread;
            const vegasSpread = game.vegas_spread;

            const hasVegas = vegasSpread !== null && vegasSpread !== undefined;
            const hasEloSpread = eloSpread !== null && eloSpread !== undefined;
            const hasXgbSpread = xgbSpread !== null && xgbSpread !== undefined;

            const eloEdge = hasVegas && hasEloSpread ? Math.abs(eloSpread - vegasSpread) : 0;
            const xgbEdge = hasVegas && hasXgbSpread ? Math.abs(xgbSpread - vegasSpread) : 0;
            const maxEdge = Math.max(eloEdge, xgbEdge);

            const hasValue = hasVegas && maxEdge >= 3.0;

            return (
              <div key={idx} className={`table-row ${hasValue ? 'value-play' : ''}`}>
                <div className="col-matchup">
                  <img src={getTeamLogo(game.away_team)} alt={game.away_team} className="tiny-logo" />
                  <span className="team-abbr">{game.away_team}</span>
                  <span className="at-symbol">@</span>
                  <span className="team-abbr">{game.home_team}</span>
                  <img src={getTeamLogo(game.home_team)} alt={game.home_team} className="tiny-logo" />
                </div>

                <div className="col-spread">
                  <span className={`spread-value ${hasEloSpread && eloEdge >= 3 ? 'edge-highlight' : ''}`}>
                    {formatSpreadForHome(game.home_team, eloSpread)}
                  </span>
                </div>

                <div className="col-spread">
                  <span className={`spread-value ${hasXgbSpread && xgbEdge >= 3 ? 'edge-highlight' : ''}`}>
                    {formatSpreadForHome(game.home_team, xgbSpread)}
                  </span>
                </div>

                <div className="col-spread vegas-col">
                  <span className="spread-value">
                    {formatSpreadForHome(game.home_team, vegasSpread)}
                  </span>
                </div>

                <div className="col-edge">
                  {hasValue ? (
                    <span className="edge-badge">💎 {maxEdge.toFixed(1)} pts</span>
                  ) : (
                    <span className="no-edge">-</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        <div className="spreads-legend">
          <div className="legend-item">
            <span className="legend-badge value">💎</span>
            <span className="legend-text">Value Play (3+ point difference from Vegas)</span>
          </div>
        </div>
      </div>
    );
  };

  const hasSeasonAtsData = Boolean(
    seasonStats
    && Number.isFinite(Number(seasonStats.total_games))
    && Number(seasonStats.total_games) > 0
  );
  const seasonAiPct = hasSeasonAtsData ? Number(seasonStats.ai_percentage || 0) : null;
  const seasonVegasPct = hasSeasonAtsData ? Number(seasonStats.vegas_percentage || 0) : null;
  const seasonDeltaPct = hasSeasonAtsData ? (seasonAiPct - seasonVegasPct) : null;
  const seasonDeltaClass = hasSeasonAtsData
    ? (seasonAiPct >= seasonVegasPct ? 'positive' : 'negative')
    : '';
  const seasonRecordText = hasSeasonAtsData
    ? `Record: AI ${seasonStats.ai_wins} - Vegas ${seasonStats.vegas_wins} | Ties ${seasonStats.ties} | Games ${seasonStats.total_games}`
    : 'ATS season data unavailable';

  if (loading) {
    return (
      <div className="ml-predictions-redesign">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading predictions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="ml-predictions-redesign">
      <div className="page-header">
        <h1>🧠 AI NFL Predictions</h1>
        <p className="subtitle">Combined AI Analysis: Elo + XGBoost + Vegas</p>
      </div>

      <div className="simple-legend">
        <div className="legend-row">
          <div className="legend-item">
            <span className="legend-icon">📈</span>
            <div className="legend-text">
              <strong>Elo:</strong> Team strength rankings (like chess ratings)
            </div>
          </div>
          <div className="legend-item">
            <span className="legend-icon">🤖</span>
            <div className="legend-text">
              <strong>AI:</strong> Computer learns from 20 years of games
            </div>
          </div>
          <div className="legend-item">
            <span className="legend-icon">🎰</span>
            <div className="legend-text">
              <strong>Vegas:</strong> Las Vegas betting line
            </div>
          </div>
        </div>
        <div className="legend-row">
          <div className="legend-item">
            <span className="legend-icon">✅</span>
            <div className="legend-text">
              <strong>Consensus:</strong> Both Elo and AI agree (more confident)
            </div>
          </div>
          <div className="legend-item">
            <span className="legend-icon">⚠️</span>
            <div className="legend-text">
              <strong>Split:</strong> Models pick different winners (toss-up)
            </div>
          </div>
          <div className="legend-item">
            <span className="legend-icon">💎</span>
            <div className="legend-text">
              <strong>Value:</strong> 3+ point edge over Vegas
            </div>
          </div>
        </div>
      </div>

      <div className="controls-bar">
        <div className="week-selector-redesign">
          <label>Season:</label>
          <select value={season} onChange={(e) => setSeason(Number(e.target.value))}>
            {seasonOptions.map((optionSeason) => (
              <option key={optionSeason} value={optionSeason}>{optionSeason}</option>
            ))}
          </select>
        </div>

        <div className="week-selector-redesign">
          <label>Week:</label>
          <select value={week || ''} onChange={(e) => setWeek(Number(e.target.value))}>
            <option value="">Select Week</option>
            {[...Array(18)].map((_, i) => (
              <option key={i + 1} value={i + 1}>Week {i + 1}</option>
            ))}
          </select>
        </div>

        <button className="load-btn" onClick={() => fetchCombinedPredictions()}>
          Load Week
        </button>
      </div>

      <div className="predictions-live-row">
        <div className="predictions-live-text">
          Live sync every 10s | {formatLastUpdated()}
        </div>
        <button
          className="predictions-refresh-btn"
          type="button"
          onClick={refreshAll}
          disabled={refreshing}
        >
          {refreshing ? 'Refreshing...' : 'Refresh Now'}
        </button>
      </div>

      <div className="season-benchmark" aria-live="polite">
        <div className="season-benchmark-header">
          <h3>AI vs Vegas - {season} Season</h3>
          <p>Spread head-to-head win rates</p>
        </div>

        {seasonStatsLoading ? (
          <div className="season-benchmark-loading">Updating season benchmark...</div>
        ) : (
          <>
            <div className="season-benchmark-grid">
              <div className="benchmark-tile ai">
                <div className="benchmark-label">AI Win %</div>
                <div className="benchmark-value">
                  {seasonAiPct === null ? 'N/A' : `${seasonAiPct.toFixed(1)}%`}
                </div>
              </div>

              <div className="benchmark-tile vegas">
                <div className="benchmark-label">Vegas Win %</div>
                <div className="benchmark-value">
                  {seasonVegasPct === null ? 'N/A' : `${seasonVegasPct.toFixed(1)}%`}
                </div>
              </div>

              <div className={["benchmark-tile delta", seasonDeltaClass].filter(Boolean).join(' ')}>
                <div className="benchmark-label">AI vs Vegas</div>
                <div className="benchmark-value">
                  {seasonDeltaPct === null
                    ? 'N/A'
                    : `${seasonDeltaPct >= 0 ? '+' : ''}${seasonDeltaPct.toFixed(1)}%`}
                </div>
              </div>
            </div>

            <div className="season-benchmark-detail">
              {seasonRecordText}
            </div>
          </>
        )}
      </div>

      <div className="view-tabs">
        <button 
          className={`view-tab ${view === 'winner-picks' ? 'active' : ''}`}
          onClick={() => setView('winner-picks')}
        >
          🏆 Winner Picks
        </button>
        <button 
          className={`view-tab ${view === 'spreads' ? 'active' : ''}`}
          onClick={() => setView('spreads')}
        >
          📊 Point Spreads
        </button>
      </div>

      {error && (
        <div className="error-message">
          <p>{error}</p>
          {authRequired && (
            <div className="ml-auth-panel">
              <input
                type="text"
                className="ml-auth-input"
                placeholder="API username"
                value={authUsername}
                onChange={(event) => setAuthUsername(event.target.value)}
                autoComplete="username"
              />
              <input
                type="password"
                className="ml-auth-input"
                placeholder="API password"
                value={authPassword}
                onChange={(event) => setAuthPassword(event.target.value)}
                autoComplete="current-password"
              />
              <button className="load-btn" type="button" onClick={refreshAll}>
                Retry Authenticated Fetch
              </button>
            </div>
          )}
        </div>
      )}

      <div className="content-area">
        {view === 'winner-picks' && renderWinnerPicks()}
        {view === 'spreads' && renderSpreads()}
      </div>
    </div>
  );
}

export default MLPredictionsRedesign;
