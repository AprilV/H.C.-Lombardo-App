import React, { useState, useEffect } from 'react';
import './LiveScores.css';

const API_URL = '';

function LiveScores() {
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [weekInfo, setWeekInfo] = useState(null);

  useEffect(() => {
    fetchLiveScores();
    // Refresh every 30 seconds during game days
    const interval = setInterval(fetchLiveScores, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchLiveScores = async () => {
    try {
      const response = await fetch(`${API_URL}/api/live-scores`);
      const data = await response.json();
      
      if (data.success) {
        setGames(data.games);
        setWeekInfo(data.week_info);
        setError(null);
      } else {
        setError(data.error || 'Failed to load live scores');
      }
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch live scores:', err);
      setError('Unable to connect to API');
      setLoading(false);
    }
  };

  const getGameStatus = (game) => {
    const status = game.status;
    
    if (status === 'in_progress') {
      return {
        text: `${game.period} - ${game.clock}`,
        class: 'live',
        icon: '🔴'
      };
    } else if (status === 'final') {
      return {
        text: 'FINAL',
        class: 'final',
        icon: '✓'
      };
    } else if (status === 'scheduled') {
      return {
        text: game.time,
        class: 'scheduled',
        icon: '🕐'
      };
    } else if (status === 'halftime') {
      return {
        text: 'HALFTIME',
        class: 'halftime',
        icon: '⏸️'
      };
    }
    
    return { text: status, class: 'unknown', icon: '' };
  };

  const getScoreClass = (teamScore, opponentScore, isFinal) => {
    if (!isFinal) return '';
    return teamScore > opponentScore ? 'winning' : 'losing';
  };

  // Calculate live differential vs predictions
  const getDifferentialInfo = (game) => {
    if (game.status === 'scheduled' || !game.home_score) return null;
    
    // Current score differential (positive = home team winning)
    const currentDiff = game.home_score - game.away_score;
    
    const info = {
      currentDiff,
      ai: null,
      vegas: null
    };
    
    // Compare to AI prediction (if available)
    if (game.ai_spread !== undefined && game.ai_spread !== null) {
      // AI spread is from home team perspective (negative = home underdog)
      // Differential vs AI = current - predicted
      info.ai = {
        predicted: game.ai_spread,
        diff: currentDiff - game.ai_spread,
        beating: currentDiff > game.ai_spread
      };
    }
    
    // Compare to Vegas line (if available)
    if (game.vegas_spread !== undefined && game.vegas_spread !== null) {
      // Vegas spread is from home team perspective (negative = home underdog)
      info.vegas = {
        predicted: game.vegas_spread,
        diff: currentDiff - game.vegas_spread,
        beating: currentDiff > game.vegas_spread,
        covering: game.status === 'final' ? currentDiff + game.vegas_spread > 0 : null
      };
    }
    
    return info;
  };

  const formatSpread = (spread) => {
    if (spread === 0) return 'PK';
    return spread > 0 ? `+${spread}` : spread.toString();
  };

  if (loading) {
    return (
      <div className="live-scores-container">
        <div className="loading-message">
          <div className="spinner"></div>
          <p>Loading live scores...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="live-scores-container">
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          <p>{error}</p>
          <button onClick={fetchLiveScores} className="retry-button">Retry</button>
        </div>
      </div>
    );
  }

  if (!games || games.length === 0) {
    return (
      <div className="live-scores-container">
        <div className="no-games-message">
          <span className="info-icon">📅</span>
          <h3>No Games Today</h3>
          <p>Check back on game days for live scores!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="live-scores-container">
      <div className="live-scores-header">
        <h2>🏈 Live Scores</h2>
        {weekInfo && (
          <div className="week-info">
            <span className="season-text">2025 Season</span>
            <span className="week-text">Week {weekInfo.week}</span>
          </div>
        )}
      </div>

      <div className="games-grid">
        {games.map((game, index) => {
          const status = getGameStatus(game);
          const isFinal = game.status === 'final';
          const isLive = game.status === 'in_progress';
          const diffInfo = getDifferentialInfo(game);
          
          return (
            <div key={index} className={`game-card ${status.class}`}>
              {/* Status Badge */}
              <div className={`status-badge ${status.class}`}>
                {status.icon} {status.text}
              </div>

              {/* Teams and Scores */}
              <div className="game-content">
                {/* Away Team */}
                <div className={`team-row ${getScoreClass(game.away_score, game.home_score, isFinal)}`}>
                  <div className="team-info">
                    <img 
                      src={`/team-logos/${game.away_team}.png`} 
                      alt={game.away_team}
                      className="team-logo"
                      onError={(e) => e.target.style.display = 'none'}
                    />
                    <span className="team-name">{game.away_team}</span>
                  </div>
                  <div className="team-score">
                    {game.status !== 'scheduled' ? game.away_score : '-'}
                  </div>
                </div>

                {/* Home Team */}
                <div className={`team-row ${getScoreClass(game.home_score, game.away_score, isFinal)}`}>
                  <div className="team-info">
                    <img 
                      src={`/team-logos/${game.home_team}.png`} 
                      alt={game.home_team}
                      className="team-logo"
                      onError={(e) => e.target.style.display = 'none'}
                    />
                    <span className="team-name">{game.home_team}</span>
                  </div>
                  <div className="team-score">
                    {game.status !== 'scheduled' ? game.home_score : '-'}
                  </div>
                </div>
              </div>

              {/* Live Differential Tracker */}
              {diffInfo && (diffInfo.ai || diffInfo.vegas) && (
                <div className="differential-tracker">
                  <div className="diff-header">
                    <span className="current-diff">
                      Current: {game.home_team} {diffInfo.currentDiff > 0 ? '+' : ''}{diffInfo.currentDiff}
                    </span>
                  </div>
                  <div className="diff-comparisons">
                    {diffInfo.ai && (
                      <div className={`diff-item ai ${diffInfo.ai.beating ? 'beating' : 'trailing'}`}>
                        <div className="diff-label">
                          <span className="label-text">🤖 AI Line:</span>
                          <span className="line-value">{formatSpread(diffInfo.ai.predicted)}</span>
                        </div>
                        <div className="diff-status">
                          {diffInfo.ai.beating ? '✓ Beating' : '✗ Below'}
                          <span className="diff-value">({diffInfo.ai.diff > 0 ? '+' : ''}{diffInfo.ai.diff.toFixed(1)})</span>
                        </div>
                      </div>
                    )}
                    {diffInfo.vegas && (
                      <div className={`diff-item vegas ${diffInfo.vegas.beating ? 'beating' : 'trailing'}`}>
                        <div className="diff-label">
                          <span className="label-text">🎰 Vegas:</span>
                          <span className="line-value">{formatSpread(diffInfo.vegas.predicted)}</span>
                        </div>
                        <div className="diff-status">
                          {isFinal 
                            ? (diffInfo.vegas.covering ? '✓ Covered' : '✗ Failed') 
                            : (diffInfo.vegas.beating ? '✓ Beating' : '✗ Below')}
                          <span className="diff-value">({diffInfo.vegas.diff > 0 ? '+' : ''}{diffInfo.vegas.diff.toFixed(1)})</span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* AI Prediction (if available) */}
              {game.ai_prediction && (
                <div className="ai-prediction">
                  <span className="prediction-label">AI Pick:</span>
                  <span className={`prediction-team ${game.ai_correct === true ? 'correct' : game.ai_correct === false ? 'wrong' : ''}`}>
                    {game.ai_prediction}
                    {game.ai_correct === true && ' ✅'}
                    {game.ai_correct === false && ' ❌'}
                  </span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Live Update Indicator */}
      {games.some(g => g.status === 'in_progress') && (
        <div className="auto-refresh-notice">
          <span className="pulse-dot"></span>
          Auto-updating every 30 seconds
        </div>
      )}
    </div>
  );
}

export default LiveScores;
