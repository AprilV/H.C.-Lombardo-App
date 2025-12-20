import React, { useState, useEffect } from 'react';
import './MLPredictionsRedesign.css';

const API_URL = 'https://api.aprilsykes.dev';

function MLPredictionsRedesign() {
  const [season, setSeason] = useState(2025);
  const [week, setWeek] = useState(null);
  const [availableWeeks, setAvailableWeeks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [combinedData, setCombinedData] = useState([]);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('predictions');
  const [view, setView] = useState('winner-picks'); // 'winner-picks', 'spreads', 'detailed'

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
                          <span className="model-label">🤖 XGBoost:</span>
                          <span className="conf-value">{(xgbConf * 100).toFixed(0)}%</span>
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
                          <div className="split-model">🤖 XGBoost</div>
                          <div className="split-winner">
                            <img src={getTeamLogo(xgbWinner)} alt={xgbWinner} className="split-logo" />
                            <span>{xgbWinner}</span>
                          </div>
                          <div className="split-conf">{(xgbConf * 100).toFixed(0)}%</div>
                        </div>
                      </div>
                    </>
                  )}
                </div>

                {game.vegas_spread && (
                  <div className="pick-footer">
                    <span className="vegas-line">Vegas: {game.home_team} {game.vegas_spread > 0 ? '+' : ''}{game.vegas_spread.toFixed(1)}</span>
                  </div>
                )}
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
            <div className="col-spread">XGBoost Spread</div>
            <div className="col-spread">Vegas Line</div>
            <div className="col-edge">Edge</div>
          </div>

          {combinedData.map((game, idx) => {
            const eloSpread = game.elo?.spread || 0;
            const xgbSpread = game.xgb?.spread || 0;
            const vegasSpread = game.vegas_spread || 0;

            const eloEdge = Math.abs(eloSpread - vegasSpread);
            const xgbEdge = Math.abs(xgbSpread - vegasSpread);
            const maxEdge = Math.max(eloEdge, xgbEdge);

            const hasValue = maxEdge >= 3.0;

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
                    {game.home_team} {vegasSpread > 0 ? '+' : ''}{vegasSpread.toFixed(1)}
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

  const renderLegend = () => {
    return (
      <div className="legend-container">
        <div className="legend-header">
          <h2>📊 Legend & Terms</h2>
          <p>Understanding the predictions, spreads, and metrics</p>
        </div>

        <div className="legend-grid">
          {/* Elo Rating System */}
          <div className="legend-card">
            <h3>🏆 Elo Rating System</h3>
            <div className="legend-content">
              <p><strong>What it is:</strong> Chess-style ranking system adapted for NFL. Teams gain/lose rating points based on game outcomes and margin of victory.</p>
              <p><strong>How it works:</strong> Better teams beating weaker teams gains few points. Upsets cause large rating swings.</p>
              <p><strong>Current leader:</strong> Philadelphia Eagles (1768 rating)</p>
              <p><strong>Advantages:</strong> Simple, reliable, accounts for strength of opponent and margin of victory.</p>
              <p><strong>Win Confidence Range:</strong> 55-72% (realistic, conservative)</p>
              <p><strong>Spread:</strong> Based on rating differential + 65-point home field advantage</p>
            </div>
          </div>

          {/* XGBoost AI Model */}
          <div className="legend-card">
            <h3>🤖 XGBoost AI Model</h3>
            <div className="legend-content">
              <p><strong>What it is:</strong> Advanced machine learning model trained on 14,312 NFL games (1999-2025).</p>
              <p><strong>How it works:</strong> Analyzes 39 statistical features including EPA (Expected Points Added), success rate, yards per play, recent form, and Vegas lines.</p>
              <p><strong>Test Accuracy:</strong> 65.55% win prediction (2025 season)</p>
              <p><strong>Spread MAE:</strong> 10.35 points (competitive with Vegas)</p>
              <p><strong>Advantages:</strong> Incorporates advanced analytics (EPA), learns complex patterns, considers recent form.</p>
              <p><strong>Architecture:</strong> 3-layer neural network with 128→64→32 neurons</p>
            </div>
          </div>

          {/* Vegas Line */}
          <div className="legend-card">
            <h3>🎰 Vegas Line</h3>
            <div className="legend-content">
              <p><strong>What it is:</strong> Official betting spread from Las Vegas sportsbooks.</p>
              <p><strong>Source:</strong> ESPN aggregates odds from DraftKings, FanDuel, Caesars, BetMGM.</p>
              <p><strong>How to read:</strong> Negative number = home team favored. Example: -6.5 means home team favored by 6.5 points.</p>
              <p><strong>Why it matters:</strong> Vegas lines represent billions of dollars of market intelligence and sharp bettors.</p>
              <p><strong>Accuracy:</strong> ~10.5 point MAE historically</p>
              <p><strong>Note:</strong> Only available for past games. Future games show null until lines are published.</p>
            </div>
          </div>

          {/* Consensus vs Split */}
          <div className="legend-card">
            <h3>✅ Consensus vs ⚠️ Split</h3>
            <div className="legend-content">
              <p><strong>Consensus (Green):</strong> Both Elo and XGBoost predict the same winner.</p>
              <p><strong>Split (Orange):</strong> Models disagree on who will win.</p>
              <p><strong>Why it matters:</strong> Consensus picks have higher confidence. Splits indicate close/unpredictable games.</p>
              <p><strong>Combined Confidence:</strong> Average of both model confidences when they agree.</p>
            </div>
          </div>

          {/* Value Play */}
          <div className="legend-card">
            <h3>💎 Value Play</h3>
            <div className="legend-content">
              <p><strong>What it is:</strong> When AI spread differs from Vegas by 3+ points.</p>
              <p><strong>Why it matters:</strong> Indicates potential betting opportunities where AI analysis disagrees with market.</p>
              <p><strong>Example:</strong> AI: -10.5, Vegas: -6.0 → 4.5 point edge</p>
              <p><strong>Interpretation:</strong></p>
              <ul>
                <li>AI higher: AI thinks favorite wins by MORE than Vegas predicts</li>
                <li>AI lower: AI thinks game will be CLOSER than Vegas predicts</li>
              </ul>
            </div>
          </div>

          {/* Edge Analysis */}
          <div className="legend-card">
            <h3>📈 Edge Analysis</h3>
            <div className="legend-content">
              <p><strong>What it is:</strong> Absolute difference between AI spread and Vegas spread.</p>
              <p><strong>Calculation:</strong> |AI Spread - Vegas Spread|</p>
              <p><strong>3+ points:</strong> Highlighted as value play with gold badge</p>
              <p><strong>Use case:</strong> Helps identify games where statistical models suggest Vegas may have mispriced the line.</p>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderModelInfo = () => {
    return (
      <div className="model-info-container">
        <div className="model-header">
          <h2>🤖 Dual Prediction System</h2>
          <p>Two complementary approaches to NFL game prediction</p>
        </div>

        <div className="model-grid">
          {/* Elo System Details */}
          <div className="model-card highlight">
            <h3>🏆 Elo Rating System</h3>
            <div className="model-content">
              <div className="metric">
                <span className="metric-label">System Type</span>
                <span className="metric-value">FiveThirtyEight Methodology</span>
              </div>
              <div className="metric">
                <span className="metric-label">Historical Data</span>
                <span className="metric-value">6,214 games (2002-2024)</span>
              </div>
              <div className="metric">
                <span className="metric-label">Current Top Team</span>
                <span className="metric-value">PHI (1768 rating)</span>
              </div>
              <div className="metric">
                <span className="metric-label">Home Field Advantage</span>
                <span className="metric-value">65 Elo points</span>
              </div>
              <div className="metric">
                <span className="metric-label">K-Factor</span>
                <span className="metric-value">20 (win/loss impact)</span>
              </div>
              <div className="metric">
                <span className="metric-label">Mean Reversion</span>
                <span className="metric-value">1/3 regression to 1505</span>
              </div>
              <div className="metric-note">
                <strong>How it predicts spreads:</strong><br/>
                Spread = (Home Rating - Away Rating + 65) / 25<br/>
                <strong>Example:</strong> PHI (1768) vs NYG (1420) at PHI<br/>
                = (1768 - 1420 + 65) / 25 = 16.5 point spread
              </div>
            </div>
          </div>

          {/* XGBoost System Details */}
          <div className="model-card highlight">
            <h3>🤖 XGBoost Neural Network</h3>
            <div className="model-content">
              <div className="metric">
                <span className="metric-label">Model Type</span>
                <span className="metric-value">Deep Learning (Classification + Regression)</span>
              </div>
              <div className="metric">
                <span className="metric-label">Training Data</span>
                <span className="metric-value">14,312 games (1999-2025)</span>
              </div>
              <div className="metric">
                <span className="metric-label">Win Accuracy (2025)</span>
                <span className="metric-value">65.55%</span>
              </div>
              <div className="metric">
                <span className="metric-label">Spread MAE</span>
                <span className="metric-value">10.35 points</span>
              </div>
              <div className="metric">
                <span className="metric-label">Features Analyzed</span>
                <span className="metric-value">39 statistical inputs</span>
              </div>
              <div className="metric">
                <span className="metric-label">Architecture</span>
                <span className="metric-value">128→64→32 neurons (3 layers)</span>
              </div>
              <div className="metric-note">
                <strong>Key Features:</strong><br/>
                • EPA (Expected Points Added)<br/>
                • Success Rate, Yards Per Play<br/>
                • Recent Form (L3, L5 games)<br/>
                • Red Zone Efficiency<br/>
                • Vegas betting lines<br/>
                • Season/week context
              </div>
            </div>
          </div>
        </div>

        <div className="strengths-section">
          <h3>💪 Why We Use Both Systems</h3>
          
          <div className="strengths-grid">
            <div className="strength-card">
              <h4>🏆 Elo Rating Strengths</h4>
              <ul>
                <li><strong>Battle-tested reliability:</strong> Used successfully in chess, sports, and competitive games for decades</li>
                <li><strong>Long-term accuracy:</strong> Excellent at tracking team strength over entire seasons</li>
                <li><strong>Opponent-aware:</strong> Beating a strong team matters more than beating a weak team</li>
                <li><strong>Stable predictions:</strong> Doesn't overreact to single-game performances</li>
                <li><strong>Historical depth:</strong> Built on 6,214 games since 2002</li>
              </ul>
            </div>

            <div className="strength-card">
              <h4>🤖 XGBoost AI Strengths</h4>
              <ul>
                <li><strong>Advanced analytics:</strong> Uses EPA and modern stats that correlate strongly with winning</li>
                <li><strong>Momentum detection:</strong> Catches hot/cold streaks with L3/L5 game tracking</li>
                <li><strong>Deep learning:</strong> Finds complex patterns humans might miss across 14,312 games</li>
                <li><strong>Context-aware:</strong> Considers game situation, week, and betting market intelligence</li>
                <li><strong>Constantly improving:</strong> Retrains on latest data to adapt to modern NFL trends</li>
              </ul>
            </div>

            <div className="strength-card combined">
              <h4>⚡ Combined Power</h4>
              <ul>
                <li><strong>Consensus = Confidence:</strong> When both agree, accuracy increases significantly</li>
                <li><strong>Splits reveal toss-ups:</strong> Disagreement warns you of unpredictable games</li>
                <li><strong>Cross-validation:</strong> Two independent methodologies reduce bias</li>
                <li><strong>Best of both worlds:</strong> Elo's stability + XGBoost's advanced stats</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderHowItWorks = () => {
    return (
      <div className="how-it-works-container">
        <div className="how-header">
          <h2>📖 How It Works</h2>
          <p>From data to prediction: The complete process</p>
        </div>

        <div className="steps-container">
          {/* Step 1 */}
          <div className="step-card">
            <div className="step-number">1</div>
            <div className="step-content">
              <h3>📡 Data Collection</h3>
              <p><strong>When you select a week:</strong></p>
              <ul>
                <li>System fetches all scheduled games for that week</li>
                <li>Retrieves team performance data (only from games BEFORE this week)</li>
                <li>Loads current Elo ratings for all teams</li>
                <li>Fetches Vegas betting lines (if available)</li>
              </ul>
              <div className="step-note">
                🔒 <strong>Data Leakage Prevention:</strong> Never uses future or current game data
              </div>
            </div>
          </div>

          {/* Step 2 */}
          <div className="step-card">
            <div className="step-number">2</div>
            <div className="step-content">
              <h3>⚙️ Feature Engineering (XGBoost)</h3>
              <p><strong>System computes 39 features per matchup:</strong></p>
              <p><strong>Team Stats (32 features):</strong></p>
              <ul>
                <li>Season averages: PPG, EPA, Success Rate, YPP, 3rd Down %, Red Zone %</li>
                <li>Recent form: Last 3 games, Last 5 games</li>
                <li>Games played (experience factor)</li>
              </ul>
              <p><strong>Matchup Context (7 features):</strong></p>
              <ul>
                <li>EPA differential, PPG differential, Success rate differential</li>
                <li>Vegas spread, Vegas total</li>
                <li>Season, Week</li>
              </ul>
            </div>
          </div>

          {/* Step 3 */}
          <div className="step-card">
            <div className="step-number">3</div>
            <div className="step-content">
              <h3>🤖 Dual Model Prediction</h3>
              <p><strong>Elo Prediction:</strong></p>
              <ol>
                <li>Calculate rating differential: Home Rating - Away Rating</li>
                <li>Add 65-point home field advantage</li>
                <li>Convert to win probability and spread</li>
                <li>Apply margin of victory multiplier</li>
              </ol>
              <p><strong>XGBoost Prediction:</strong></p>
              <ol>
                <li>Pass 39 features through neural network</li>
                <li>Win/Loss model outputs probability (0-100%)</li>
                <li>Spread model outputs point differential</li>
                <li>Combine outputs for final prediction</li>
              </ol>
            </div>
          </div>

          {/* Step 4 */}
          <div className="step-card">
            <div className="step-number">4</div>
            <div className="step-content">
              <h3>🎯 Consensus Analysis</h3>
              <p><strong>Combining both models:</strong></p>
              <ul>
                <li><strong>Agreement Check:</strong> Do both models pick the same winner?</li>
                <li><strong>Consensus (Green):</strong> Both agree → Higher confidence</li>
                <li><strong>Split (Orange):</strong> Models disagree → Lower confidence, closer game</li>
                <li><strong>Spread Comparison:</strong> Compare AI spreads to Vegas line</li>
                <li><strong>Value Detection:</strong> Flag 3+ point differences as value plays</li>
              </ul>
            </div>
          </div>

          {/* Step 5 */}
          <div className="step-card">
            <div className="step-number">5</div>
            <div className="step-content">
              <h3>📊 Display Results</h3>
              <p><strong>Winner Picks View:</strong></p>
              <ul>
                <li>Shows WHO wins with confidence percentages</li>
                <li>Green badges for consensus, orange for splits</li>
                <li>Displays both model picks when they disagree</li>
              </ul>
              <p><strong>Point Spreads View:</strong></p>
              <ul>
                <li>Shows BY HOW MUCH each team will win/lose</li>
                <li>Compares Elo, XGBoost, and Vegas spreads side-by-side</li>
                <li>Highlights value plays with 💎 gold badges</li>
                <li>Shows edge analysis (difference from Vegas)</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="accuracy-section">
          <h3>🎯 Historical Accuracy</h3>
          <div className="accuracy-grid">
            <div className="accuracy-card">
              <div className="accuracy-label">XGBoost Win %</div>
              <div className="accuracy-value">65.55%</div>
              <div className="accuracy-note">2025 Test Set</div>
            </div>
            <div className="accuracy-card">
              <div className="accuracy-label">XGBoost Spread MAE</div>
              <div className="accuracy-value">10.35 pts</div>
              <div className="accuracy-note">Competitive with Vegas</div>
            </div>
            <div className="accuracy-card">
              <div className="accuracy-label">Vegas Spread MAE</div>
              <div className="accuracy-value">~10.5 pts</div>
              <div className="accuracy-note">Historical Average</div>
            </div>
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
        <h1>🧠 NFL Predictions</h1>
        <p className="subtitle">Dual AI System: Elo Ratings + XGBoost Machine Learning</p>
      </div>

      <div className="intro-panel">
        <div className="intro-content">
          <p><strong>🏆 Elo Rating System:</strong> Chess-style rankings tracking team strength over 6,214 historical games. Simple, reliable, accounts for opponent quality.</p>
          <p><strong>🤖 XGBoost AI:</strong> Advanced neural network trained on 14,312 games analyzing 39 features including EPA, success rate, and recent form.</p>
          <p><strong>🎰 Vegas Line:</strong> Official sportsbook spreads aggregated from DraftKings, FanDuel, Caesars, and BetMGM.</p>
          <p><strong>✅ Consensus:</strong> Both models agree on winner (higher confidence). <strong>⚠️ Split:</strong> Models disagree (toss-up game). <strong>💎 Value:</strong> 3+ point edge over Vegas.</p>
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

      {activeTab === 'predictions' && (
        <>
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
        </>
      )}

      {activeTab === 'legend' && renderLegend()}
      {activeTab === 'model-info' && renderModelInfo()}
      {activeTab === 'how-it-works' && renderHowItWorks()}
    </div>
  );
}

export default MLPredictionsRedesign;
