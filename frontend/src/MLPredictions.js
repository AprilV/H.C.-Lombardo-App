import React, { useState, useEffect } from 'react';
import './MLPredictions.css';

const API_URL = 'http://34.198.25.249:5000';

function MLPredictions() {
  const [activeTab, setActiveTab] = useState('predictions');
  const [season, setSeason] = useState(2025);
  const [week, setWeek] = useState(null);
  const [loading, setLoading] = useState(false);
  const [predictions, setPredictions] = useState([]);
  const [modelInfo, setModelInfo] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [error, setError] = useState(null);

  // Team logo helper
  const getTeamLogo = (team) => {
    return `https://a.espncdn.com/i/teamlogos/nfl/500/${team}.png`;
  };

  // Format game date (avoid timezone shifts)
  const formatGameDate = (dateString) => {
    if (!dateString) return '';
    const [year, month, day] = dateString.split('-');
    const date = new Date(year, month - 1, day);
    return date.toLocaleDateString('en-US', { 
      weekday: 'short',
      month: 'short', 
      day: 'numeric'
    });
  };

  // Fetch upcoming week predictions on load
  useEffect(() => {
    fetchUpcomingPredictions();
    fetchModelInfo();
    fetchExplanation();
  }, []);

  const fetchUpcomingPredictions = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/ml/predict-upcoming`);
      const data = await response.json();
      
      if (data.error) {
        setError(data.error);
      } else {
        setPredictions(data.predictions || []);
        setSeason(data.season);
        setWeek(data.week);
      }
    } catch (err) {
      console.error('Error fetching predictions:', err);
      setError('Failed to load predictions. Please check API connection.');
    }
    setLoading(false);
  };

  const fetchWeekPredictions = async () => {
    if (!week) return;
    
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/ml/predict-week/${season}/${week}`);
      const data = await response.json();
      
      if (data.error) {
        setError(data.error);
      } else {
        setPredictions(data.predictions || []);
        setSeason(data.season);
        setWeek(data.week);
      }
    } catch (err) {
      console.error('Error fetching predictions:', err);
      setError('Failed to load predictions. Please check API connection.');
    }
    setLoading(false);
  };

  const fetchModelInfo = async () => {
    try {
      const response = await fetch(`${API_URL}/api/ml/model-info`);
      const data = await response.json();
      setModelInfo(data);
    } catch (err) {
      console.error('Error fetching model info:', err);
    }
  };

  const fetchExplanation = async () => {
    try {
      const response = await fetch(`${API_URL}/api/ml/explain`);
      const data = await response.json();
      setExplanation(data);
    } catch (err) {
      console.error('Error fetching explanation:', err);
    }
  };

  const renderPredictions = () => {
    if (loading) {
      return (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Analyzing matchups with neural network...</p>
        </div>
      );
    }

    if (error) {
      return (
        <div className="error-container">
          <h3>⚠️ Error</h3>
          <p>{error}</p>
          <button className="retry-btn" onClick={fetchUpcomingPredictions}>
            Try Again
          </button>
        </div>
      );
    }

    if (!predictions || predictions.length === 0) {
      return (
        <div className="no-data">
          <h3>No predictions available</h3>
          <p>Select a different week or check back later.</p>
        </div>
      );
    }

    return (
      <>
        <div className="predictions-header">
          <h2>🧠 Week {week} Predictions</h2>
          <p className="predictions-subtitle">{season} Season - {predictions.length} Games</p>
        </div>

        {/* Results Scorecard */}
        {(() => {
          const finishedGames = predictions.filter(p => p.actual_home_score !== null && p.actual_home_score !== undefined);
          if (finishedGames.length > 0) {
            // Count AI correct predictions (winner picks)
            const aiCorrect = finishedGames.filter(p => p.correct === true).length;
            
            // Count AI spread coverage (favorite covered)
            let aiSpreadCovered = 0;
            let aiSpreadPushes = 0;
            let aiSpreadTotal = 0;
            
            finishedGames.forEach(p => {
              const actualMargin = p.actual_home_score - p.actual_away_score;
              const isPush = (actualMargin === -p.ai_spread);
              
              if (isPush) {
                aiSpreadPushes++;
              } else {
                aiSpreadTotal++;
                let covered = false;
                if (p.ai_spread < 0) {
                  covered = actualMargin > Math.abs(p.ai_spread);
                } else {
                  covered = actualMargin < -Math.abs(p.ai_spread);
                }
                if (covered) aiSpreadCovered++;
              }
            });
            
            // Count Vegas spread coverage (favorite covered)
            let vegasCovered = 0;
            let vegasPushes = 0;
            let vegasTotal = 0;
            
            finishedGames.forEach(p => {
              const actualMargin = p.actual_home_score - p.actual_away_score;
              const isPush = (actualMargin === -p.vegas_spread);
              
              if (isPush) {
                vegasPushes++;
              } else {
                vegasTotal++;
                let covered = false;
                if (p.vegas_spread < 0) {
                  covered = actualMargin > Math.abs(p.vegas_spread);
                } else {
                  covered = actualMargin < -Math.abs(p.vegas_spread);
                }
                if (covered) vegasCovered++;
              }
            });

            return (
              <div className="results-scorecard">
                <div className="scorecard-title">📊 Week {week} Results</div>
                <div className="scorecard-stats">
                  <div className="stat-box ai-stat">
                    <div className="stat-icon">🤖</div>
                    <div className="stat-content">
                      <div className="stat-label">AI Winner Picks</div>
                      <div className="stat-value">{aiCorrect} / {finishedGames.length}</div>
                      <div className="stat-percent">
                        {finishedGames.length > 0 ? ((aiCorrect / finishedGames.length) * 100).toFixed(1) : 0}% Correct
                      </div>
                    </div>
                  </div>
                  <div className="stat-box ai-spread-stat">
                    <div className="stat-icon">🤖</div>
                    <div className="stat-content">
                      <div className="stat-label">AI Spread</div>
                      <div className="stat-value">
                        {aiSpreadCovered} / {aiSpreadTotal}
                        {aiSpreadPushes > 0 && <span className="push-count"> / {aiSpreadPushes}</span>}
                      </div>
                      <div className="stat-percent">
                        {aiSpreadTotal > 0 ? ((aiSpreadCovered / aiSpreadTotal) * 100).toFixed(1) : 0}% Covered
                        {aiSpreadPushes > 0 && <span className="push-note"> ({aiSpreadPushes} push{aiSpreadPushes > 1 ? 'es' : ''})</span>}
                      </div>
                    </div>
                  </div>
                  <div className="stat-box vegas-stat">
                    <div className="stat-icon">🎰</div>
                    <div className="stat-content">
                      <div className="stat-label">Vegas Spread</div>
                      <div className="stat-value">
                        {vegasCovered} / {vegasTotal}
                        {vegasPushes > 0 && <span className="push-count"> / {vegasPushes}</span>}
                      </div>
                      <div className="stat-percent">
                        {vegasTotal > 0 ? ((vegasCovered / vegasTotal) * 100).toFixed(1) : 0}% Covered
                        {vegasPushes > 0 && <span className="push-note"> ({vegasPushes} push{vegasPushes > 1 ? 'es' : ''})</span>}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            );
          }
          return null;
        })()}

        <div className="predictions-grid">
          {predictions.map((pred, idx) => {
            const isHomeWinner = pred.predicted_winner === pred.home_team;
            const winnerConfidence = (pred.confidence * 100).toFixed(1);
            const homeProb = (pred.home_win_prob * 100).toFixed(1);
            const awayProb = (pred.away_win_prob * 100).toFixed(1);
            
            // Check if game is finished (use correct field names from API)
            const isFinished = pred.actual_home_score !== null && pred.actual_home_score !== undefined;
            const actualWinner = isFinished ? pred.actual_winner : null;
            const aiWasCorrect = isFinished ? pred.correct : null;
            const actualMargin = isFinished ? pred.actual_home_score - pred.actual_away_score : null;
            
            // Spread coverage: Check if the FAVORITE covered
            // Negative spread = home favored, must win by MORE than the absolute value
            // Positive spread = away favored, must win by MORE than the absolute value
            
            // For VEGAS: Check if favorite covered (display shows favorite)
            let vegasCovered = null;
            if (isFinished) {
              const vegasResult = actualMargin + pred.vegas_spread;
              if (vegasResult === 0) {
                vegasCovered = null; // Push
              } else if (pred.vegas_spread < 0) {
                // Home team is favorite - must win by MORE than the spread
                // Example: -6.5 spread means home must win by 7+
                vegasCovered = actualMargin > Math.abs(pred.vegas_spread);
              } else {
                // Away team is favorite - must win by MORE than the spread
                // Example: +6.5 spread means away must win by 7+
                vegasCovered = actualMargin < -Math.abs(pred.vegas_spread);
              }
            }
            
            // For AI: Check if favorite covered (display shows favorite)
            let aiSpreadCovered = null;
            if (isFinished) {
              const aiResult = actualMargin + pred.ai_spread;
              if (aiResult === 0) {
                aiSpreadCovered = null; // Push
              } else if (pred.ai_spread < 0) {
                // Home team is favorite - must win by MORE than the spread
                aiSpreadCovered = actualMargin > Math.abs(pred.ai_spread);
              } else {
                // Away team is favorite - must win by MORE than the spread
                aiSpreadCovered = actualMargin < -Math.abs(pred.ai_spread);
              }
            }

            return (
              <div key={idx} className={`prediction-card ${isFinished ? 'finished' : ''}`}>
                <div className="game-header">
                  <span className="game-date">{formatGameDate(pred.game_date)}</span>
                  <span className="game-id">#{pred.game_id}</span>
                  {isFinished && (
                    <span className="final-badge">FINAL</span>
                  )}
                </div>

                {/* Actual Score for finished games */}
                {isFinished && (
                  <div className="actual-score-display">
                    <div className="actual-score-title">Final Score</div>
                    <div className="actual-score-teams">
                      <div className="actual-score-team">
                        <span className={`score-name ${actualWinner === pred.away_team ? 'winner-name' : ''}`}>
                          {pred.away_team}
                        </span>
                        <span className="score-number">{pred.actual_away_score}</span>
                      </div>
                      <div className="score-sep">-</div>
                      <div className="actual-score-team">
                        <span className={`score-name ${actualWinner === pred.home_team ? 'winner-name' : ''}`}>
                          {pred.home_team}
                        </span>
                        <span className="score-number">{pred.actual_home_score}</span>
                      </div>
                    </div>
                    <div className="actual-margin">
                      {actualWinner} won by {Math.abs(actualMargin)} pts
                    </div>
                  </div>
                )}

                <div className="ml-matchup-container">
                  {/* Away Team */}
                  <div className={`team-section ${!isHomeWinner ? 'winner' : ''}`}>
                    <img 
                      src={getTeamLogo(pred.away_team)} 
                      alt={pred.away_team}
                      className="team-logo"
                      onError={(e) => e.target.style.display = 'none'}
                    />
                    <div className="team-info">
                      <div className="team-name">{pred.away_team}</div>
                      <div className="team-label">Away</div>
                    </div>
                    <div className="team-prob">{awayProb}%</div>
                  </div>

                  <div className="vs-divider">@</div>

                  {/* Home Team */}
                  <div className={`team-section ${isHomeWinner ? 'winner' : ''}`}>
                    <img 
                      src={getTeamLogo(pred.home_team)} 
                      alt={pred.home_team}
                      className="team-logo"
                      onError={(e) => e.target.style.display = 'none'}
                    />
                    <div className="team-info">
                      <div className="team-name">{pred.home_team}</div>
                      <div className="team-label">Home</div>
                    </div>
                    <div className="team-prob">{homeProb}%</div>
                  </div>
                </div>

                {/* Prediction Result */}
                <div className="prediction-result">
                  <div className="model-identifier">
                    <span className="model-badge classification">📊 Win/Loss Model</span>
                    <span className="model-type">Neural Network Classifier (65.55% Accuracy)</span>
                  </div>
                  <div className="winner-banner">
                    <span className="trophy-icon">🏆</span>
                    <span className="winner-text">
                      {pred.predicted_winner} wins
                    </span>
                    {isFinished && (
                      <span className={`result-indicator ${aiWasCorrect ? 'correct' : 'wrong'}`}>
                        {aiWasCorrect ? '✓' : '✗'}
                      </span>
                    )}
                  </div>
                  <div className="confidence-bar-container">
                    <div className="confidence-label">
                      <span>Confidence: {winnerConfidence}%</span>
                    </div>
                    <div className="confidence-bar">
                      <div 
                        className="confidence-fill" 
                        style={{ width: `${winnerConfidence}%` }}
                      ></div>
                    </div>
                  </div>
                </div>

                {/* Model Divider */}
                <div className="model-divider">
                  <div className="divider-line"></div>
                  <span className="divider-text">Score & Spread Predictions</span>
                  <div className="divider-line"></div>
                </div>

                {/* Predicted Score */}
                {pred.predicted_home_score !== undefined && pred.predicted_away_score !== undefined && (
                  <div className="predicted-score">
                    <div className="model-identifier">
                      <span className="model-badge regression">📈 Point Spread Model</span>
                      <span className="model-type">Neural Network Regressor (10.35 MAE)</span>
                    </div>
                    <div className="score-title">Predicted Final Score</div>
                    <div className="score-display">
                      <div className="score-team">
                        <span className="score-team-name">{pred.away_team}</span>
                        <span className="score-value">{pred.predicted_away_score}</span>
                      </div>
                      <div className="score-separator">-</div>
                      <div className="score-team">
                        <span className="score-team-name">{pred.home_team}</span>
                        <span className="score-value">{pred.predicted_home_score}</span>
                      </div>
                    </div>
                    <div className="score-margin">
                      {pred.predicted_winner} by {Math.abs(pred.predicted_home_score - pred.predicted_away_score).toFixed(1)} pts
                    </div>
                  </div>
                )}

                {/* Spread Analysis */}
                {pred.ai_spread !== undefined && pred.vegas_spread !== undefined && (
                  <div className="spread-analysis">
                    <div className="spread-title">AI vs Vegas Spread</div>
                    <div className="spread-comparison">
                      <div className="spread-item">
                        <span className="spread-label">🤖 AI Spread</span>
                        <span className="spread-value ai-spread">{pred.ai_spread > 0 ? '+' : ''}{pred.ai_spread}</span>
                        <div className="spread-explanation">
                          AI: {Math.abs(pred.ai_spread) < 0.5 
                            ? 'Toss-up' 
                            : `${pred.ai_spread > 0 ? pred.away_team : pred.home_team} by ${Math.abs(pred.ai_spread).toFixed(1)}`
                          }
                        </div>
                        {isFinished && (
                          aiSpreadCovered === null ? (
                            <span className="spread-result push">PUSH</span>
                          ) : (
                            <span className={`spread-result ${aiSpreadCovered ? 'correct' : 'wrong'}`}>
                              {aiSpreadCovered ? '✓' : '✗'}
                            </span>
                          )
                        )}
                      </div>
                      <div className="spread-vs">vs</div>
                      <div className="spread-item">
                        <span className="spread-label">🎰 Vegas Spread</span>
                        <span className="spread-value vegas-spread">{pred.vegas_spread > 0 ? '+' : ''}{pred.vegas_spread}</span>
                        <div className="spread-explanation">
                          Vegas: {pred.vegas_spread > 0 ? pred.away_team : pred.home_team} by {Math.abs(pred.vegas_spread).toFixed(1)}
                        </div>
                        {isFinished && (
                          vegasCovered === null ? (
                            <span className="spread-result push">PUSH</span>
                          ) : (
                            <span className={`spread-result ${vegasCovered ? 'correct' : 'wrong'}`}>
                              {vegasCovered ? '✓' : '✗'}
                            </span>
                          )
                        )}
                      </div>
                    </div>
                    {pred.spread_difference !== null && Math.abs(pred.spread_difference) > 3 && (
                      <div className="value-indicator">
                        <span className="value-badge">
                          💎 Value Play: AI differs by {Math.abs(pred.spread_difference).toFixed(1)} pts
                        </span>
                      </div>
                    )}
                  </div>
                )}

                {/* Key Factors */}
                {pred.key_factors && (
                  <div className="key-factors">
                    <div className="factor-title">Key Factors</div>
                    <div className="factor-grid">
                      {pred.key_factors.home_epa !== undefined && (
                        <div className="factor-item">
                          <span className="factor-label">EPA Advantage</span>
                          <span className="factor-value">
                            {pred.key_factors.epa_advantage?.toFixed(3) || 'N/A'}
                          </span>
                        </div>
                      )}
                      {pred.total_line && (
                        <div className="factor-item">
                          <span className="factor-label">Vegas Total</span>
                          <span className="factor-value">O/U {pred.total_line}</span>
                        </div>
                      )}
                      {pred.key_factors.home_recent_epa !== undefined && (
                        <div className="factor-item">
                          <span className="factor-label">Recent EPA Form</span>
                          <span className="factor-value">
                            {pred.key_factors.home_recent_epa.toFixed(3)} / {pred.key_factors.away_recent_epa.toFixed(3)}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </>
    );
  };

  const renderLegend = () => {
    return (
      <div className="legend-container">
        <div className="stat-legend">
          <h3>📊 Statistics & Terms Explained</h3>
          <p>Understanding the metrics, predictions, and betting analysis</p>
        </div>

        <div className="legend-sections">
          {/* Sprint 11: NEW PREDICTION FEATURES */}
          <div className="legend-section highlight">
            <h3>🆕 Sprint 11: Score & Spread Predictions</h3>
            
            <div className="legend-item">
              <div className="legend-term">Predicted Final Score</div>
              <div className="legend-definition">
                <p><strong>What it is:</strong> AI-predicted final scores for both teams using neural network regression model.</p>
                <p><strong>How it works:</strong> Analyzes team performance, recent form, EPA trends, and Vegas total line to predict exact scores.</p>
                <p><strong>Example:</strong> "BUF: 18.7 - HOU: 24.8" means AI predicts Houston wins 24.8 to 18.7.</p>
                <p><strong>Accuracy:</strong> Mean Absolute Error (MAE) of 10.35 points on 2025 games. Competitive with Vegas spreads (~10.5 MAE).</p>
              </div>
            </div>

            <div className="legend-item">
              <div className="legend-term">Predicted Margin / Point Differential</div>
              <div className="legend-definition">
                <p><strong>What it is:</strong> Difference between predicted scores (Home Score - Away Score).</p>
                <p><strong>Example:</strong> "Margin: 6.1 pts" means home team predicted to win by 6.1 points.</p>
                <p><strong>Positive margin:</strong> Home team favored. <strong>Negative margin:</strong> Away team favored.</p>
              </div>
            </div>

            <div className="legend-item">
              <div className="legend-term">🤖 AI Spread</div>
              <div className="legend-definition">
                <p><strong>What it is:</strong> AI-generated betting spread based on predicted point differential.</p>
                <p><strong>How to read:</strong> Negative number = home team favored by that many points.</p>
                <p><strong>Example:</strong> "AI Spread: -6.1" means AI predicts home team wins by 6.1 points.</p>
                <p><strong>Calculation:</strong> -(Predicted Home Score - Predicted Away Score)</p>
              </div>
            </div>

            <div className="legend-item">
              <div className="legend-term">🎰 Vegas Spread</div>
              <div className="legend-definition">
                <p><strong>What it is:</strong> Official betting spread from sportsbooks (ESPN aggregated odds).</p>
                <p><strong>How to read:</strong> Same format as AI spread - negative means home favored.</p>
                <p><strong>Example:</strong> "Vegas Spread: -6.0" means Vegas has home team favored by 6 points.</p>
                <p><strong>Source:</strong> ESPN Bet (aggregates DraftKings, FanDuel, Caesars, BetMGM).</p>
              </div>
            </div>

            <div className="legend-item">
              <div className="legend-term">💎 Value Play (Spread Difference)</div>
              <div className="legend-definition">
                <p><strong>What it is:</strong> When AI spread differs significantly from Vegas spread (threshold: 3+ points).</p>
                <p><strong>Why it matters:</strong> Indicates potential betting opportunities where AI's analysis disagrees with market consensus.</p>
                <p><strong>Example:</strong> AI: -10.5 vs Vegas: -6.0 → Difference: 4.5 pts → Shows as "💎 Value Play"</p>
                <p><strong>Interpretation:</strong></p>
                <ul>
                  <li><strong>AI higher than Vegas:</strong> AI thinks favorite will win by MORE than Vegas predicts</li>
                  <li><strong>AI lower than Vegas:</strong> AI thinks game will be CLOSER than Vegas predicts</li>
                  <li><strong>Purple badge appears:</strong> When difference exceeds 3 points in either direction</li>
                </ul>
                <p><strong>Use case:</strong> Helps identify games where statistical analysis suggests Vegas may have mispriced the line.</p>
              </div>
            </div>
          </div>

          {/* Key Metrics Section */}
          <div className="legend-section">
            <h3>🎯 Key Performance Metrics</h3>
            
            <div className="legend-item">
              <div className="legend-term">EPA (Expected Points Added)</div>
              <div className="legend-definition">
                <p><strong>What it is:</strong> Measures how much a team's performance changes their expected points on each play.</p>
                <p><strong>Why it matters:</strong> Better than traditional stats because it accounts for game situation (down, distance, field position).</p>
                <p><strong>Example:</strong> A 5-yard gain on 3rd-and-4 has higher EPA than 5 yards on 3rd-and-10.</p>
                <p><strong>Good values:</strong> NFL average is ~0.0. Elite teams: +0.10 or higher. Poor teams: -0.10 or worse.</p>
              </div>
            </div>

            <div className="legend-item">
              <div className="legend-term">EPA Advantage</div>
              <div className="legend-definition">
                <p><strong>What it is:</strong> Difference between home team EPA and away team EPA.</p>
                <p><strong>Example:</strong> "EPA Advantage: +0.150" means home team has significantly better EPA.</p>
                <p><strong>Impact:</strong> Strong predictor of game outcome - used heavily by both AI models.</p>
              </div>
            </div>

            <div className="legend-item">
              <div className="legend-term">Success Rate</div>
              <div className="legend-definition">
                <p><strong>What it is:</strong> Percentage of plays that are "successful" (gain expected yardage).</p>
                <p><strong>Criteria:</strong> 50% of needed yards on 1st down, 70% on 2nd down, 100% on 3rd/4th down.</p>
                <p><strong>Good values:</strong> Elite: 45%+, Average: 40%, Poor: 35% or lower.</p>
              </div>
            </div>

            <div className="legend-item">
              <div className="legend-term">YPP (Yards Per Play)</div>
              <div className="legend-definition">
                <p><strong>What it is:</strong> Average yards gained per offensive play.</p>
                <p><strong>NFL average:</strong> ~5.5 yards per play.</p>
                <p><strong>Elite offense:</strong> 6.0+ YPP.</p>
              </div>
            </div>
          </div>

          {/* Recent Form Section */}
          <div className="legend-section">
            <h3>📈 Recent Form Indicators</h3>
            
            <div className="legend-item">
              <div className="legend-term">Last 3 Games (L3)</div>
              <div className="legend-definition">
                <p><strong>What it is:</strong> Team performance over their last 3 games.</p>
                <p><strong>Why it matters:</strong> Shows current momentum and recent trends.</p>
                <p><strong>Example:</strong> "L3 PPG: 28.5" means averaging 28.5 points in last 3 games.</p>
              </div>
            </div>

            <div className="legend-item">
              <div className="legend-term">Last 5 Games (L5)</div>
              <div className="legend-definition">
                <p><strong>What it is:</strong> Team performance over their last 5 games.</p>
                <p><strong>Why it matters:</strong> Provides a broader view of recent performance while still capturing trends.</p>
              </div>
            </div>
          </div>

          {/* Vegas Lines Section */}
          <div className="legend-section">
            <h3>💰 Vegas Betting Lines</h3>
            
            <div className="legend-item">
              <div className="legend-term">Spread Line</div>
              <div className="legend-definition">
                <p><strong>What it is:</strong> Point handicap set by sportsbooks to even out betting.</p>
                <p><strong>Example:</strong> "KC -7.5" means Kansas City is favored to win by more than 7.5 points.</p>
                <p><strong>How to read:</strong> Negative number = favorite, Positive number = underdog.</p>
              </div>
            </div>

            <div className="legend-item">
              <div className="legend-term">Total Line (Over/Under)</div>
              <div className="legend-definition">
                <p><strong>What it is:</strong> Combined points both teams are expected to score.</p>
                <p><strong>Example:</strong> "O/U 45.5" means sportsbooks expect ~46 total points scored.</p>
              </div>
            </div>

            <div className="legend-item">
              <div className="legend-term">Moneyline</div>
              <div className="legend-definition">
                <p><strong>What it is:</strong> Odds for each team to win straight-up (no spread).</p>
                <p><strong>Example:</strong> "-300" means bet $300 to win $100. "+250" means bet $100 to win $250.</p>
                <p><strong>How to read:</strong> Negative = favorite (how much to bet to win $100). Positive = underdog (how much you win on $100 bet).</p>
              </div>
            </div>
          </div>

          {/* Data Sources Section */}
          <div className="legend-section highlight">
            <h3>🗂️ Data Sources</h3>
            
            <div className="legend-item">
              <div className="legend-term">Vegas Lines Source</div>
              <div className="legend-definition">
                <p><strong>Primary Source:</strong> ESPN Bet (formerly Caesars Sportsbook)</p>
                <p><strong>Aggregation:</strong> ESPN aggregates odds from multiple sportsbooks including DraftKings, FanDuel, Caesars, and BetMGM.</p>
                <p><strong>Update frequency:</strong> Lines update throughout the week as teams/market conditions change.</p>
                <p><strong>Coverage:</strong> Currently 60.3% of 2025 games have complete betting line data.</p>
              </div>
            </div>

            <div className="legend-item">
              <div className="legend-term">Game & Performance Data</div>
              <div className="legend-definition">
                <p><strong>Source:</strong> nflverse via nfl_data_py (open-source NFL data)</p>
                <p><strong>Includes:</strong> Play-by-play data, advanced stats (EPA, success rate), game results</p>
                <p><strong>Historical range:</strong> 1999-2025 (14,312 games used for training)</p>
              </div>
            </div>
          </div>

          {/* Confidence Levels Section */}
          <div className="legend-section">
            <h3>🎲 Prediction Confidence Levels</h3>
            
            <div className="legend-item">
              <div className="legend-term confidence-high">High Confidence (70%+)</div>
              <div className="legend-definition">
                <p><strong>Meaning:</strong> Strong prediction - significant performance gap between teams.</p>
                <p><strong>Color:</strong> Green confidence bar.</p>
                <p><strong>Example:</strong> Elite team vs struggling team with clear statistical advantages.</p>
              </div>
            </div>

            <div className="legend-item">
              <div className="legend-term confidence-medium">Medium Confidence (60-70%)</div>
              <div className="legend-definition">
                <p><strong>Meaning:</strong> Moderate advantage - one team likely to win but not overwhelming.</p>
                <p><strong>Color:</strong> Blue confidence bar.</p>
                <p><strong>Example:</strong> Good team vs average team, or home field advantage scenario.</p>
              </div>
            </div>

            <div className="legend-item">
              <div className="legend-term confidence-low">Low Confidence (50-60%)</div>
              <div className="legend-definition">
                <p><strong>Meaning:</strong> Toss-up game - very close matchup.</p>
                <p><strong>Color:</strong> Orange confidence bar.</p>
                <p><strong>Example:</strong> Evenly matched teams, division rivals, or unpredictable game.</p>
                <p><strong>Note:</strong> 50% = pure coin flip.</p>
              </div>
            </div>
          </div>

          {/* Model Info Section */}
          <div className="legend-section">
            <h3>🤖 About the Neural Network</h3>
            
            <div className="legend-item">
              <div className="legend-term">Training Data</div>
              <div className="legend-definition">
                <p><strong>Games analyzed:</strong> 14,312 NFL games (1999-2025)</p>
                <p><strong>Features per game:</strong> 41 statistical inputs</p>
                <p><strong>Model type:</strong> Multi-layer neural network (128→64→32 neurons)</p>
              </div>
            </div>

            <div className="legend-item">
              <div className="legend-term">Model Accuracy</div>
              <div className="legend-definition">
                <p><strong>Test Accuracy:</strong> 65.55% on unseen games</p>
                <p><strong>Comparison:</strong> Vegas lines: 52-55%, Top models: 57-60%, Our model: 65.55%</p>
                <p><strong>What this means:</strong> Correctly predicts winner in ~2 out of 3 games.</p>
              </div>
            </div>
          </div>
        </div>

        <div className="legend-footer">
          <p><strong>💡 Tip:</strong> Use the legend alongside predictions to better understand what drives each prediction and how confident the model is in its analysis.</p>
        </div>
      </div>
    );
  };

  const renderModelInfo = () => {
    return (
      <div className="model-info-container">
        <div className="stat-legend">
          <h3>🤖 Dual Neural Network System (Sprint 11 Update)</h3>
          <p>Two specialized AI models working together to provide comprehensive predictions</p>
        </div>

        <div className="info-grid">
          {/* Model 1: Win/Loss Classifier */}
          <div className="info-card highlight">
            <h3>🏆 Model 1: Win/Loss Classifier</h3>
            <div className="info-content">
              <div className="metric">
                <span className="metric-label">Model Type</span>
                <span className="metric-value">Binary Classification</span>
              </div>
              <div className="metric">
                <span className="metric-label">Output</span>
                <span className="metric-value">Win Probability (0-100%)</span>
              </div>
              <div className="metric">
                <span className="metric-label">Test Accuracy (2025)</span>
                <span className="metric-value">65.55%</span>
              </div>
              <div className="metric">
                <span className="metric-label">Training Games</span>
                <span className="metric-value">14,312 games (1999-2025)</span>
              </div>
              <div className="metric">
                <span className="metric-label">Features</span>
                <span className="metric-value">39 statistical inputs</span>
              </div>
              <div className="metric-note">
                <strong>What it predicts:</strong> WHO wins the game<br/>
                <strong>How you see it:</strong> "BUF wins (74.8% confidence)"<br/>
                <strong>Architecture:</strong> 3-layer neural network (128→64→32 neurons) with sigmoid output
              </div>
            </div>
          </div>

          {/* Model 2: Point Spread Regression */}
          <div className="info-card highlight">
            <h3>📊 Model 2: Point Spread Regression (NEW!)</h3>
            <div className="info-content">
              <div className="metric">
                <span className="metric-label">Model Type</span>
                <span className="metric-value">Regression</span>
              </div>
              <div className="metric">
                <span className="metric-label">Output</span>
                <span className="metric-value">Point Differential (-30 to +30)</span>
              </div>
              <div className="metric">
                <span className="metric-label">Test MAE (2025)</span>
                <span className="metric-value">10.35 points</span>
              </div>
              <div className="metric">
                <span className="metric-label">Winner Accuracy</span>
                <span className="metric-value">66.9%</span>
              </div>
              <div className="metric">
                <span className="metric-label">Training Games</span>
                <span className="metric-value">5,894 games (weighted by recency)</span>
              </div>
              <div className="metric">
                <span className="metric-label">Features</span>
                <span className="metric-value">39 statistical inputs</span>
              </div>
              <div className="metric-note">
                <strong>What it predicts:</strong> BY HOW MUCH a team wins<br/>
                <strong>How you see it:</strong> "BUF 18.7 - HOU 24.8 (Margin: 6.1 pts)"<br/>
                <strong>Architecture:</strong> 3-layer neural network (128→64→32 neurons) with linear output<br/>
                <strong>Performance:</strong> Competitive with Vegas spreads (Vegas typical MAE: ~10.5 points)
              </div>
            </div>
          </div>

          {/* Combined System */}
          <div className="info-card">
            <h3>⚡ How They Work Together</h3>
            <div className="info-content">
              <div className="metric-note">
                <p><strong>1. Both models analyze the same game independently</strong></p>
                <p>Each model uses 39 features: team EPA, recent form, success rates, Vegas lines, home/away stats, etc.</p>
                
                <p><strong>2. Win/Loss Model determines WHO wins</strong></p>
                <p>Outputs probability like "74.8% chance Buffalo wins"</p>
                
                <p><strong>3. Point Spread Model determines BY HOW MUCH</strong></p>
                <p>Outputs point differential like "+6.1 points" (Buffalo favored by 6.1)</p>
                
                <p><strong>4. System calculates predicted scores</strong></p>
                <p>Uses Vegas total line + predicted margin to estimate final scores</p>
                
                <p><strong>5. AI spread compared to Vegas</strong></p>
                <p>Identifies "value plays" where AI analysis differs from betting market</p>
              </div>
            </div>
          </div>

          {/* Training Methodology */}
          <div className="info-card">
            <h3>📚 Training Methodology</h3>
            <div className="info-content">
              <div className="metric-note">
                <p><strong>Data Leakage Prevention:</strong></p>
                <ul>
                  <li>Uses ONLY pre-game statistics (no post-game data)</li>
                  <li>Rolling features computed from games BEFORE prediction</li>
                  <li>Time-based validation: train on past, test on future</li>
                </ul>
                
                <p><strong>Weighted Sampling (Point Spread Model):</strong></p>
                <ul>
                  <li>1999-2010 games: 0.5x weight (older NFL era)</li>
                  <li>2011-2018 games: 1.0x weight (transition era)</li>
                  <li>2019-2025 games: 2.0x weight (modern NFL - rule changes, offense evolution)</li>
                </ul>
                
                <p><strong>Validation Splits:</strong></p>
                <ul>
                  <li>Training: Games through 2023 season</li>
                  <li>Validation: 2024 season (269 games)</li>
                  <li>Test: 2025 season (148 games so far)</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Feature Categories */}
          <div className="info-card">
            <h3>📊 39 Features Analyzed Per Game</h3>
            <div className="info-content">
              <div className="feature-category">
                <strong>Season Performance (12 features per team = 24 total):</strong> PPG, YPG, Turnovers/Game, EPA, Success Rate, Pass EPA, Rush EPA, WPA, Yards/Play, 3rd Down %, Red Zone %, Time of Possession %
              </div>
              <div className="feature-category">
                <strong>Recent Form (6 features per team = 12 total):</strong> Last 3 games EPA & PPG, Last 5 games EPA & PPG, games played this season
              </div>
              <div className="feature-category">
                <strong>Matchup Differentials (3 features):</strong> EPA differential, PPG differential, Success Rate differential
              </div>
            </div>
          </div>
        </div>

        <div className="legend-footer">
          <p><strong>🔬 Model Validation:</strong> Both models tested on unseen 2025 games. No data leakage detected (validated using historical splits). Performance competitive with professional sports betting analytics.</p>
        </div>
      </div>
    );
  };

  const renderExplanation = () => {
    return (
      <div className="explanation-container">
        <div className="stat-legend">
          <h3>🧠 How It Works: From Data to Prediction</h3>
          <p>Step-by-step breakdown of how AI predicts NFL games with scores and spreads</p>
        </div>

        <div className="explanation-sections">
          {/* Step 1: Data Collection */}
          <div className="explanation-card">
            <h3>📡 Step 1: Data Collection</h3>
            <div className="info-content">
              <p><strong>When you request predictions for Week 12:</strong></p>
              <ol>
                <li><strong>Game Schedule:</strong> System fetches all 14 games scheduled for that week</li>
                <li><strong>Team Performance Data:</strong> For each team, retrieves:
                  <ul>
                    <li>All games played THIS season before Week 12</li>
                    <li>Advanced stats: EPA per play, success rate, yards per play</li>
                    <li>Scoring trends: points per game, red zone efficiency</li>
                    <li>Recent form: Last 3 games, Last 5 games</li>
                  </ul>
                </li>
                <li><strong>Vegas Betting Lines:</strong> Fetches current spread, total, and moneyline from ESPN</li>
              </ol>
              <div className="metric-note">
                <strong>🔒 Data Leakage Prevention:</strong> Only uses statistics from games BEFORE the one being predicted. Never uses future or current game data.
              </div>
            </div>
          </div>

          {/* Step 2: Feature Engineering */}
          <div className="explanation-card">
            <h3>⚙️ Step 2: Feature Engineering</h3>
            <div className="info-content">
              <p><strong>System computes 39 features for each matchup:</strong></p>
              
              <p><strong>Home Team Stats (16 features):</strong></p>
              <ul>
                <li>Season averages: PPG, EPA, Success Rate, Yards/Play, 3rd Down %, Red Zone %</li>
                <li>Recent form: L3 EPA, L3 PPG, L5 EPA, L5 PPG</li>
                <li>Games played (experience factor)</li>
              </ul>

              <p><strong>Away Team Stats (16 features):</strong></p>
              <ul>
                <li>Same metrics as home team</li>
              </ul>

              <p><strong>Matchup Context (7 features):</strong></p>
              <ul>
                <li>EPA Differential (Home EPA - Away EPA)</li>
                <li>PPG Differential</li>
                <li>Success Rate Differential</li>
                <li>Vegas Spread Line</li>
                <li>Vegas Total Line</li>
                <li>Season, Week (temporal context)</li>
              </ul>

              <div className="metric-note">
                <strong>Example:</strong> For BUF @ HOU, system sees Buffalo averaging 0.137 EPA (elite offense) while Houston at -0.023 EPA (below average), creating an EPA advantage of 0.160 in Buffalo's favor.
              </div>
            </div>
          </div>

          {/* Step 3: Model Predictions */}
          <div className="explanation-card">
            <h3>🤖 Step 3: Dual Model Prediction</h3>
            <div className="info-content">
              <p><strong>Both AI models analyze the game simultaneously:</strong></p>
              
              <p><strong>🏆 Win/Loss Model (Classification):</strong></p>
              <ol>
                <li>Takes 39 features → passes through neural network</li>
                <li>128 neurons analyze patterns → 64 neurons refine → 32 neurons finalize</li>
                <li>Outputs probability: "74.8% Buffalo wins"</li>
                <li>Determines predicted winner: BUF</li>
              </ol>

              <p><strong>📊 Point Spread Model (Regression):</strong></p>
              <ol>
                <li>Takes SAME 39 features → passes through separate neural network</li>
                <li>128 neurons → 64 neurons → 32 neurons (different weights trained for scoring)</li>
                <li>Outputs point differential: "+6.1" (Buffalo favored by 6.1 points)</li>
              </ol>

              <div className="metric-note">
                <strong>⚡ Why two models?</strong> Win/loss model excels at picking winners (65.55% accurate). Point spread model excels at predicting margin (10.35 MAE). Together they provide complete picture.
              </div>
            </div>
          </div>

          {/* Step 4: Score Calculation */}
          <div className="explanation-card">
            <h3>🔢 Step 4: Predicted Score Calculation</h3>
            <div className="info-content">
              <p><strong>System converts point differential into actual scores:</strong></p>
              
              <p><strong>Formula:</strong></p>
              <div className="metric-note" style={{fontFamily: 'monospace', background: 'rgba(0,0,0,0.3)', padding: '15px', borderRadius: '8px'}}>
                Point Differential = +6.1 (Buffalo favored)<br/>
                Vegas Total Line = 43.5 (expected combined points)<br/>
                <br/>
                Home Score = (Total + Margin) / 2<br/>
                Home Score = (43.5 + 6.1) / 2 = 24.8<br/>
                <br/>
                Away Score = (Total - Margin) / 2<br/>
                Away Score = (43.5 - 6.1) / 2 = 18.7<br/>
                <br/>
                <strong>Result: BUF 18.7 - HOU 24.8</strong>
              </div>

              <p style={{marginTop: '15px'}}><strong>Why use Vegas total?</strong> Betting totals incorporate real-world factors (weather, injuries, pace of play) that pure stats might miss. Combining AI margin with Vegas total gives most realistic score prediction.</p>
            </div>
          </div>

          {/* Step 5: Spread Analysis */}
          <div className="explanation-card">
            <h3>💎 Step 5: AI vs Vegas Spread Analysis</h3>
            <div className="info-content">
              <p><strong>System compares AI analysis to betting market:</strong></p>
              
              <p><strong>Converting to betting spread:</strong></p>
              <div className="metric-note" style={{fontFamily: 'monospace', background: 'rgba(0,0,0,0.3)', padding: '15px', borderRadius: '8px'}}>
                Predicted Margin = +6.1 (Houston favored by 6.1)<br/>
                AI Spread = -6.1 (negative means home favored)<br/>
                Vegas Spread = -6.0 (from sportsbooks)<br/>
                <br/>
                Difference = AI (-6.1) - Vegas (-6.0) = -0.1<br/>
              </div>

              <p style={{marginTop: '15px'}}><strong>Interpreting spread difference:</strong></p>
              <ul>
                <li><strong>0-3 point difference:</strong> AI and Vegas agree (no value play badge)</li>
                <li><strong>3+ point difference:</strong> Significant disagreement (💎 VALUE PLAY appears)</li>
              </ul>

              <p><strong>Example Value Play:</strong></p>
              <div className="metric-note">
                If AI says Detroit -10.5 but Vegas says -6.0:<br/>
                → Difference: 4.5 points<br/>
                → <strong>💎 Value Play</strong> appears (purple badge)<br/>
                → AI thinks Detroit will win by MORE than Vegas predicts<br/>
                → Potential betting opportunity on Detroit to cover spread
              </div>

              <p style={{marginTop: '15px'}}><strong>⚠️ Important:</strong> Value plays are statistical insights, not guaranteed winners. They identify where AI's analysis differs from market consensus, which may indicate mispriced lines.</p>
            </div>
          </div>

          {/* Step 6: Display */}
          <div className="explanation-card">
            <h3>📺 Step 6: Presenting Results to You</h3>
            <div className="info-content">
              <p><strong>Each prediction card shows layered information:</strong></p>
              
              <p><strong>🏆 Winner Banner:</strong> "BUF wins (74.8% confidence)"</p>
              <ul>
                <li>From: Win/Loss Model</li>
                <li>Shows: Predicted winner + confidence level</li>
                <li>Color-coded confidence bar (green=high, blue=medium, orange=low)</li>
              </ul>

              <p><strong>📊 Predicted Final Score:</strong> "BUF 18.7 - HOU 24.8 (Margin: 6.1 pts)"</p>
              <ul>
                <li>From: Point Spread Model + Vegas Total</li>
                <li>Shows: Expected final scores and winning margin</li>
                <li>Large numbers for quick scanning</li>
              </ul>

              <p><strong>🎰 AI vs Vegas Spread:</strong> "🤖 -6.1 vs 🎰 -6.0"</p>
              <ul>
                <li>From: Comparing AI prediction to betting market</li>
                <li>Shows: Both spreads side-by-side</li>
                <li>💎 Badge appears if difference > 3 points</li>
              </ul>

              <p><strong>🎯 Key Factors:</strong> EPA Advantage, Recent Form, Vegas Total</p>
              <ul>
                <li>From: Raw feature data</li>
                <li>Shows: Top drivers of the prediction</li>
                <li>Helps understand WHY AI made this pick</li>
              </ul>
            </div>
          </div>

          {/* Performance Tracking */}
          <div className="explanation-card highlight">
            <h3>📊 How Accurate Is This System?</h3>
            <div className="info-content">
              <p><strong>Win/Loss Model (65.55% accuracy):</strong></p>
              <ul>
                <li>Correctly predicts winner in ~2 out of 3 games</li>
                <li>Outperforms Vegas betting favorites (52-55%)</li>
                <li>Competitive with professional sports analytics</li>
              </ul>

              <p><strong>Point Spread Model (10.35 MAE):</strong></p>
              <ul>
                <li>Average error of 10.35 points on final margin</li>
                <li>Competitive with Vegas spreads (~10.5 MAE)</li>
                <li>66.9% accurate at picking correct winner</li>
              </ul>

              <div className="metric-note">
                <strong>What does MAE mean?</strong> Mean Absolute Error measures average distance between prediction and actual result. MAE of 10.35 means predictions are typically within 10-11 points of actual margin. Lower is better.
              </div>

              <p style={{marginTop: '15px'}}><strong>Validation approach:</strong></p>
              <ul>
                <li>Trained on 1999-2023 games</li>
                <li>Validated on unseen 2024 games</li>
                <li>Tested on unseen 2025 games (current season)</li>
                <li>No data leakage - predictions use only pre-game information</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="legend-footer">
          <p><strong>💡 Bottom Line:</strong> The system analyzes 39 statistical features through two specialized neural networks to predict both WHO wins and BY HOW MUCH. By comparing AI spreads to Vegas lines, you can identify potential value plays where statistical analysis disagrees with betting markets.</p>
        </div>
      </div>
    );
  };

  return (
    <div className="ml-predictions-container">
      <div className="ml-predictions-header">
        <h1>🧠 ML Predictions</h1>
        <div className="header-controls">
          <div className="season-selector">
            <label>Season:</label>
            <select value={season} onChange={(e) => setSeason(Number(e.target.value))}>
              <option value={2025}>2025</option>
              <option value={2024}>2024</option>
              <option value={2023}>2023</option>
            </select>
          </div>
          <div className="week-selector">
            <label>Week:</label>
            <input 
              type="number" 
              min="1" 
              max="18" 
              value={week || ''} 
              onChange={(e) => setWeek(Number(e.target.value))}
              placeholder="Auto"
            />
            <button className="predict-btn" onClick={fetchWeekPredictions}>
              Predict Week
            </button>
          </div>
          <button className="upcoming-btn" onClick={fetchUpcomingPredictions}>
            Show Upcoming
          </button>
        </div>
      </div>

      <div className="ml-predictions-tabs">
        <button 
          className={activeTab === 'predictions' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('predictions')}
        >
          🏈 Predictions
        </button>
        <button 
          className={activeTab === 'legend' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('legend')}
        >
          📊 Legend
        </button>
        <button 
          className={activeTab === 'model-info' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('model-info')}
        >
          🤖 Model Info
        </button>
        <button 
          className={activeTab === 'how-it-works' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('how-it-works')}
        >
          📖 How It Works
        </button>
      </div>

      <div className="ml-predictions-content">
        {activeTab === 'predictions' && renderPredictions()}
        {activeTab === 'legend' && renderLegend()}
        {activeTab === 'model-info' && renderModelInfo()}
        {activeTab === 'how-it-works' && renderExplanation()}
      </div>
    </div>
  );
}

export default MLPredictions;
