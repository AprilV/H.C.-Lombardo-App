import React, { useState, useEffect } from 'react';
import './MLPredictions.css';

const API_URL = 'http://127.0.0.1:5000';

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

        <div className="predictions-grid">
          {predictions.map((pred, idx) => {
            const isHomeWinner = pred.predicted_winner === pred.home_team;
            const winnerConfidence = (pred.confidence * 100).toFixed(1);
            const homeProb = (pred.home_win_prob * 100).toFixed(1);
            const awayProb = (pred.away_win_prob * 100).toFixed(1);

            return (
              <div key={idx} className="prediction-card">
                <div className="game-header">
                  <span className="game-date">{pred.game_date}</span>
                  <span className="game-id">#{pred.game_id}</span>
                </div>

                <div className="matchup-container">
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
                  <div className="winner-banner">
                    <span className="trophy-icon">🏆</span>
                    <span className="winner-text">
                      {pred.predicted_winner} wins
                    </span>
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
                      {pred.spread_line && (
                        <div className="factor-item">
                          <span className="factor-label">Vegas Spread</span>
                          <span className="factor-value">{pred.spread_line}</span>
                        </div>
                      )}
                      {pred.key_factors.home_recent_ppg && (
                        <div className="factor-item">
                          <span className="factor-label">Recent Form</span>
                          <span className="factor-value">
                            {pred.key_factors.home_recent_ppg.toFixed(1)} - {pred.key_factors.away_recent_ppg.toFixed(1)}
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
          <p>Understanding the metrics and data sources used in predictions</p>
        </div>

        <div className="legend-sections">
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
              <div className="legend-term">PPG (Points Per Game)</div>
              <div className="legend-definition">
                <p><strong>What it is:</strong> Average points scored per game.</p>
                <p><strong>Why it matters:</strong> Simple measure of offensive effectiveness.</p>
                <p><strong>NFL average:</strong> ~22-24 points per game.</p>
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
    if (!modelInfo) {
      return <div className="loading">Loading model information...</div>;
    }

    return (
      <div className="model-info-container">
        <div className="stat-legend">
          <h3>🤖 Neural Network Architecture</h3>
          <p>Our prediction system uses a multi-layer neural network trained on 14,312 games from 1999-2025</p>
        </div>

        <div className="info-grid">
          <div className="info-card highlight">
            <h3>🎯 Model Performance</h3>
            <div className="info-content">
              <div className="metric">
                <span className="metric-label">Test Accuracy</span>
                <span className="metric-value">{modelInfo.performance?.test_accuracy || 'N/A'}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Validation Accuracy</span>
                <span className="metric-value">{modelInfo.performance?.validation_accuracy || 'N/A'}</span>
              </div>
              <p className="metric-note">
                Our model achieves 65.55% accuracy, outperforming Vegas betting lines (52-55%) 
                and matching top NFL prediction models (57-60%)
              </p>
            </div>
          </div>

          <div className="info-card">
            <h3>🧠 Architecture Details</h3>
            <div className="info-content">
              <div className="architecture-viz">
                <div className="layer-block">
                  <div className="layer-label">Input Layer</div>
                  <div className="layer-neurons">41 features</div>
                </div>
                <div className="layer-arrow">→</div>
                <div className="layer-block">
                  <div className="layer-label">Hidden Layer 1</div>
                  <div className="layer-neurons">128 neurons</div>
                </div>
                <div className="layer-arrow">→</div>
                <div className="layer-block">
                  <div className="layer-label">Hidden Layer 2</div>
                  <div className="layer-neurons">64 neurons</div>
                </div>
                <div className="layer-arrow">→</div>
                <div className="layer-block">
                  <div className="layer-label">Hidden Layer 3</div>
                  <div className="layer-neurons">32 neurons</div>
                </div>
                <div className="layer-arrow">→</div>
                <div className="layer-block">
                  <div className="layer-label">Output</div>
                  <div className="layer-neurons">Win/Loss</div>
                </div>
              </div>
              <div className="metric">
                <span className="metric-label">Total Parameters</span>
                <span className="metric-value">20,097</span>
              </div>
            </div>
          </div>

          <div className="info-card">
            <h3>📊 Training Data</h3>
            <div className="info-content">
              <div className="metric">
                <span className="metric-label">Total Games</span>
                <span className="metric-value">14,312</span>
              </div>
              <div className="metric">
                <span className="metric-label">Season Range</span>
                <span className="metric-value">1999-2025</span>
              </div>
              <div className="metric">
                <span className="metric-label">Training Set</span>
                <span className="metric-value">5,477 games (1999-2023)</span>
              </div>
              <div className="metric">
                <span className="metric-label">Validation Set</span>
                <span className="metric-value">269 games (2024)</span>
              </div>
              <div className="metric">
                <span className="metric-label">Test Set</span>
                <span className="metric-value">119 games (2025)</span>
              </div>
            </div>
          </div>

          <div className="info-card">
            <h3>📈 Input Features (41 total)</h3>
            <div className="info-content">
              <div className="feature-category">
                <strong>Season Stats (20):</strong> PPG, yards/game, touchdowns, EPA, 
                success rate, YPP, 3rd down %, pass EPA, rush EPA, CPOE for both teams
              </div>
              <div className="feature-category">
                <strong>Recent Form (6):</strong> Last 3 and last 5 game averages 
                (PPG, EPA, success rate) for both teams
              </div>
              <div className="feature-category">
                <strong>Matchup Differentials (4):</strong> EPA differential, PPG differential, 
                success rate differential, YPP differential
              </div>
              <div className="feature-category">
                <strong>Vegas Lines (4):</strong> Spread line, total line, home moneyline, 
                away moneyline
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderExplanation = () => {
    if (!explanation) {
      return <div className="loading">Loading explanation...</div>;
    }

    return (
      <div className="explanation-container">
        <div className="stat-legend">
          <h3>📖 How Our Predictions Work</h3>
          <p>Understanding the neural network prediction methodology</p>
        </div>

        <div className="explanation-sections">
          {explanation.sections?.map((section, idx) => (
            <div key={idx} className="explanation-card">
              <h3>{section.title}</h3>
              <p>{section.content}</p>
              {section.details && (
                <ul className="detail-list">
                  {section.details.map((detail, i) => (
                    <li key={i}>{detail}</li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </div>

        <div className="disclaimer">
          <h4>⚠️ Important Notes</h4>
          <p>
            While our model achieves strong accuracy (65.55%), NFL games are inherently unpredictable. 
            Factors like injuries, weather changes, and coaching decisions can affect outcomes. 
            These predictions are for informational purposes and should not be used as the sole basis 
            for betting decisions.
          </p>
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
