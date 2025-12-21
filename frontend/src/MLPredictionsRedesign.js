import React, { useState, useEffect } from 'react';
import './MLPredictionsRedesign.css';
import './MLPredictionsRedesign-light.css';

const API_URL = 'https://api.aprilsykes.dev';

function MLPredictionsRedesign() {
  const [season, setSeason] = useState(2025);
  const [week, setWeek] = useState(null);
  const [availableWeeks, setAvailableWeeks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [combinedData, setCombinedData] = useState([]);
  const [error, setError] = useState(null);
  const [view, setView] = useState('winner-picks'); // 'winner-picks', 'spreads'

  useEffect(() => {
    fetchAvailableWeeks();
    fetchUpcomingPredictions();
  }, []);

  useEffect(() => {
    if (week && season) {
      fetchCombinedPredictions();
    }
  }, [week, season]);

  const fetchAvailableWeeks = async () => {
    try {
      const response = await fetch(`${API_URL}/api/ml/available-weeks`);
      const data = await response.json();
      if (data.success) {
        setAvailableWeeks(data.weeks || []);
      }
    } catch (err) {
      console.error('Error fetching available weeks:', err);
    }
  };

  const fetchUpcomingPredictions = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/ml/predict-upcoming`);
      const data = await response.json();
      
      if (data.season && data.week) {
        setSeason(data.season);
        setWeek(data.week);
      }
    } catch (err) {
      console.error('Error fetching upcoming:', err);
    }
    setLoading(false);
  };

  const fetchCombinedPredictions = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/predictions/combined/${season}/${week}`);
      const data = await response.json();
      
      if (data.success) {
        setCombinedData(data.predictions || []);
      } else {
        setError(data.message || 'No predictions available');
      }
    } catch (err) {
      console.error('Error:', err);
      setError('Failed to load predictions');
    }
    setLoading(false);
  };

  const getTeamLogo = (team) => {
    return `https://a.espncdn.com/i/teamlogos/nfl/500/${team}.png`;
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
            const eloWinner = game.elo?.predicted_winner;
            const xgbWinner = game.xgb?.predicted_winner;
            const agreement = game.agreement;

            const eloConf = game.elo?.confidence || 0;
            const xgbConf = game.xgb?.confidence || 0;
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
                  {agreement ? (
                    <>
                      <div className="consensus-pick">
                        <div className="consensus-badge">✓ CONSENSUS</div>
                        <div className="winner-display">
                          <img src={getTeamLogo(eloWinner)} alt={eloWinner} className="winner-logo" />
                          <span className="winner-team">{eloWinner}</span>
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
                            {game.vegas_spread !== null ? 
                              `${game.home_team} ${game.vegas_spread > 0 ? '+' : ''}${game.vegas_spread.toFixed(1)}` : 
                              'Not available'}
                          </span>
                        </div>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="split-badge">⚠️ SPLIT PREDICTION</div>
                      <div className="split-picks">
                        <div className="split-pick">
                          <div className="split-model">📈 Elo</div>
                          <div className="split-winner">
                            <img src={getTeamLogo(eloWinner)} alt={eloWinner} className="split-logo" />
                            <span>{eloWinner}</span>
                          </div>
                          <div className="split-conf">{(eloConf * 100).toFixed(0)}%</div>
                        </div>
                        <div className="vs-divider">vs</div>
                        <div className="split-pick">
                          <div className="split-model">🤖 AI</div>
                          <div className="split-winner">
                            <img src={getTeamLogo(xgbWinner)} alt={xgbWinner} className="split-logo" />
                            <span>{xgbWinner}</span>
                          </div>
                          <div className="split-conf">{(xgbConf * 100).toFixed(0)}%</div>
                        </div>
                      </div>

                      <div className="model-breakdown split-info">
                        <div className="split-note">Models disagree - toss-up game</div>
                        <div className="model-conf vegas">
                          <span className="model-label">🎰 Vegas Line:</span>
                          <span className="conf-value">
                            {game.vegas_spread !== null ? 
                              `${game.home_team} ${game.vegas_spread > 0 ? '+' : ''}${game.vegas_spread.toFixed(1)}` : 
                              'Not available'}
                          </span>
                        </div>
                      </div>
                    </>
                  )}
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
            const eloSpread = game.elo?.spread || 0;
            const xgbSpread = game.xgb?.spread || 0;
            const vegasSpread = game.vegas_spread;

            const eloEdge = vegasSpread !== null && vegasSpread !== undefined ? Math.abs(eloSpread - vegasSpread) : 0;
            const xgbEdge = vegasSpread !== null && vegasSpread !== undefined ? Math.abs(xgbSpread - vegasSpread) : 0;
            const maxEdge = Math.max(eloEdge, xgbEdge);

            const hasValue = vegasSpread !== null && vegasSpread !== undefined && maxEdge >= 3.0;

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
                  <span className={`spread-value ${eloEdge >= 3 ? 'edge-highlight' : ''}`}>
                    {game.home_team} {eloSpread > 0 ? '+' : ''}{eloSpread.toFixed(1)}
                  </span>
                </div>

                <div className="col-spread">
                  <span className={`spread-value ${xgbEdge >= 3 ? 'edge-highlight' : ''}`}>
                    {game.home_team} {xgbSpread > 0 ? '+' : ''}{xgbSpread.toFixed(1)}
                  </span>
                </div>

                <div className="col-spread vegas-col">
                  <span className="spread-value">
                    {vegasSpread !== null && vegasSpread !== undefined ? 
                      `${game.home_team} ${vegasSpread > 0 ? '+' : ''}${vegasSpread.toFixed(1)}` : 
                      'N/A'}
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
            <option value={2025}>2025</option>
            <option value={2024}>2024</option>
            <option value={2023}>2023</option>
            <option value={2022}>2022</option>
            <option value={2021}>2021</option>
            <option value={2020}>2020</option>
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

        <button className="load-btn" onClick={fetchCombinedPredictions}>
          Load Week
        </button>
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
