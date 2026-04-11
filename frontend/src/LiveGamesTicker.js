import React, { useState, useEffect, useRef } from 'react';
import './LiveGamesTicker.css';

const API_URL = process.env.REACT_APP_API_URL || 'https://api.aprilsykes.dev';

// Map team abbreviations to logo filenames
const teamLogoMap = {
  'WSH': 'was',  // Washington
  'LAR': 'lar',  // LA Rams
  'LAC': 'lac',  // LA Chargers
  'LA': 'lar',   // LA fallback to Rams
};

const getTeamLogoName = (abbr) => {
  return (teamLogoMap[abbr] || abbr).toLowerCase();
};

function LiveGamesTicker() {
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isPaused, setIsPaused] = useState(false);
  const scrollContainerRef = useRef(null);
  const isPausedRef = useRef(false);
  const scrollIntervalRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStartX, setDragStartX] = useState(0);
  const [dragScrollLeft, setDragScrollLeft] = useState(0);

  useEffect(() => {
    fetchGames();
    const interval = setInterval(fetchGames, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  // Keep ref in sync with state so the scroll interval reads the latest value
  useEffect(() => {
    isPausedRef.current = isPaused;
  }, [isPaused]);

  // Start JS-based auto-scroll only when there are enough games to fill the ticker
  useEffect(() => {
    if (games.length < 4) return;
    startAutoScroll();
    return () => stopAutoScroll();
  }, [games]); // eslint-disable-line react-hooks/exhaustive-deps

  const startAutoScroll = () => {
    stopAutoScroll();
    scrollIntervalRef.current = setInterval(() => {
      if (isPausedRef.current || !scrollContainerRef.current) return;
      const container = scrollContainerRef.current;
      container.scrollLeft += 1;
      // Seamless loop: when we've scrolled through the first set, reset to 0
      if (container.scrollLeft >= container.scrollWidth / 2) {
        container.scrollLeft = 0;
      }
    }, 16); // ~60fps
  };

  const stopAutoScroll = () => {
    if (scrollIntervalRef.current) {
      clearInterval(scrollIntervalRef.current);
      scrollIntervalRef.current = null;
    }
  };

  const handleMouseDown = (e) => {
    e.preventDefault();
    setIsDragging(true);
    setIsPaused(true);
    const container = scrollContainerRef.current;
    setDragStartX(e.pageX);
    setDragScrollLeft(container.scrollLeft);
  };

  const handleMouseUp = () => {
    setIsDragging(false);
    setTimeout(() => setIsPaused(false), 3000);
  };

  const handleMouseMove = (e) => {
    if (!isDragging) return;
    e.preventDefault();
    const container = scrollContainerRef.current;
    const walk = dragStartX - e.pageX;
    container.scrollLeft = dragScrollLeft + walk;
  };

  const handleTouchStart = (e) => {
    setIsDragging(true);
    setIsPaused(true);
    const container = scrollContainerRef.current;
    setDragStartX(e.touches[0].pageX);
    setDragScrollLeft(container.scrollLeft);
  };

  const handleTouchMove = (e) => {
    if (!isDragging) return;
    e.preventDefault();
    const container = scrollContainerRef.current;
    const walk = dragStartX - e.touches[0].pageX;
    container.scrollLeft = dragScrollLeft + walk;
  };

  const handleTouchEnd = () => {
    setIsDragging(false);
    setTimeout(() => setIsPaused(false), 3000);
  };

  const scrollLeftBtn = () => {
    if (scrollContainerRef.current) {
      const container = scrollContainerRef.current;
      container.scrollLeft = Math.max(0, container.scrollLeft - 300);
      setIsPaused(true);
      setTimeout(() => setIsPaused(false), 3000);
    }
  };

  const scrollRightBtn = () => {
    if (scrollContainerRef.current) {
      const container = scrollContainerRef.current;
      const halfWidth = container.scrollWidth / 2;
      container.scrollLeft = Math.min(halfWidth - 1, container.scrollLeft + 300);
      setIsPaused(true);
      setTimeout(() => setIsPaused(false), 3000);
    }
  };

  const convertToPacific = (etTime, etDate) => {
    if (!etTime) return { date: etDate || '', time: '' };
    
    // Parse ET time (e.g., "06:00 PM ET")
    const match = etTime.match(/(\d{1,2}):(\d{2})\s*(AM|PM)/i);
    if (!match) return { date: etDate || '', time: etTime };
    
    let hours = parseInt(match[1]);
    const minutes = match[2];
    const period = match[3].toUpperCase();
    
    // Convert to 24-hour
    if (period === 'PM' && hours !== 12) hours += 12;
    if (period === 'AM' && hours === 12) hours = 0;
    
    // Subtract 3 hours for Pacific
    let ptHours = hours - 3;
    let dayAdjust = 0;
    
    if (ptHours < 0) {
      ptHours += 24;
      dayAdjust = -1; // Previous day
    }
    
    // Convert back to 12-hour
    const newPeriod = ptHours >= 12 ? 'PM' : 'AM';
    const displayHours = ptHours === 0 ? 12 : ptHours > 12 ? ptHours - 12 : ptHours;
    
    // Use the date from API
    let displayDate = etDate || '';
    
    return {
      date: displayDate,
      time: `${displayHours}:${minutes} ${newPeriod} PT`
    };
  };

  const fetchGames = async () => {
    try {
      const response = await fetch(`${API_URL}/api/live-scores`);
      const data = await response.json();
      
      if (data.success && data.games) {
        // Convert times to Pacific with dates
        const gamesWithPacificTime = data.games.map(game => {
          // Only convert scheduled games, keep others as-is
          if (game.status === 'scheduled' && game.time) {
            const { date, time } = convertToPacific(game.time, game.game_date);
            return {
              ...game,
              game_date: date,
              time: time
            };
          }
          return game;
        });
        setGames(gamesWithPacificTime);
      }
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch live games:', err);
      setLoading(false);
    }
  };

  if (loading || games.length === 0) return null;

  // Ticker scroll only makes sense with enough games to fill the viewport.
  // Each card is ~355px wide (340px + 15px gap). Viewport ~1400px = ~4 unique games needed.
  const cardWidth = 355;
  const useScroller = games.length >= 4;

  // For the infinite scroll build enough copies to fill 2× the container width.
  const minCardsPerSet = Math.max(5, Math.ceil(1600 / (cardWidth * games.length)));
  const setA = Array.from({ length: minCardsPerSet }, () => games).flat();
  const displayGames = useScroller ? [...setA, ...setA] : games;

  return (
    <div className="live-games-ticker">
      <div className="ticker-header-bar">
        <div className="ticker-label">
          <span className="live-dot"></span>
          LIVE SCORES • ELO • AI (XGBoost) • VEGAS LINES
        </div>
        <div className="ticker-info" title="Two independent prediction systems: ELO ratings and XGBoost machine learning, compared against Vegas spreads">
          ℹ️
        </div>
        <div className="ticker-controls">
          <button className="scroll-btn" onClick={scrollLeftBtn} title="Scroll Left">
            ◀
          </button>
          <button className="scroll-btn" onClick={scrollRightBtn} title="Scroll Right">
            ▶
          </button>
        </div>
      </div>
      <div
        className="ticker-scroll"
        ref={scrollContainerRef}
        onMouseDown={useScroller ? handleMouseDown : undefined}
        onMouseUp={useScroller ? handleMouseUp : undefined}
        onMouseLeave={useScroller ? handleMouseUp : undefined}
        onMouseMove={useScroller ? handleMouseMove : undefined}
        onTouchStart={useScroller ? handleTouchStart : undefined}
        onTouchMove={useScroller ? handleTouchMove : undefined}
        onTouchEnd={useScroller ? handleTouchEnd : undefined}
        style={{ cursor: useScroller ? (isDragging ? 'grabbing' : 'grab') : 'default' }}
      >
        <div className={`ticker-content ${!useScroller ? 'ticker-static' : ''}`}>
          {displayGames.map((game, index) => (
            <div key={index} className={`game-ticker-card ${game.status}`}>
              {/* Status indicator */}
              {game.status === 'in_progress' && (
                <div className="status-live">LIVE</div>
              )}
              {game.status === 'final' && (
                <div className="status-final">FINAL</div>
              )}
              
              {/* Game info */}
              <div className="ticker-matchup">
                <div className={`ticker-team ${game.away_score > game.home_score && game.status === 'final' ? 'winner' : ''}`}>
                  <img 
                    src={`/images/teams/${getTeamLogoName(game.away_team)}.png`} 
                    alt={game.away_team}
                    className="team-logo"
                    onError={(e) => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'block'; }}
                  />
                  <span className="team-abbr" style={{display: 'none'}}>{game.away_team}</span>
                  <span className="team-score">{game.status !== 'scheduled' ? game.away_score : '-'}</span>
                </div>
                <div className="ticker-vs">@</div>
                <div className={`ticker-team ${game.home_score > game.away_score && game.status === 'final' ? 'winner' : ''}`}>
                  <img 
                    src={`/images/teams/${getTeamLogoName(game.home_team)}.png`} 
                    alt={game.home_team}
                    className="team-logo"
                    onError={(e) => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'block'; }}
                  />
                  <span className="team-abbr" style={{display: 'none'}}>{game.home_team}</span>
                  <span className="team-score">{game.status !== 'scheduled' ? game.home_score : '-'}</span>
                </div>
              </div>

              {/* Game details */}
              <div className="ticker-details">
                {game.status === 'in_progress' && (
                  <span className="time-info">{game.period} {game.clock}</span>
                )}
                {game.status === 'scheduled' && (
                  <>
                    {game.game_date && <span className="game-date">{game.game_date}</span>}
                    <span className="time-info">{game.time || 'TBD'}</span>
                  </>
                )}
                {game.status === 'halftime' && (
                  <span className="time-info">HALFTIME</span>
                )}
              </div>

              {/* Final Score Result */}
              {game.status === 'final' && (
                <div className="ticker-final-result">
                  <span className="final-label">Final:</span>
                  <span className="final-result">
                    {game.home_score > game.away_score 
                      ? `${game.home_team} won by ${game.home_score - game.away_score}`
                      : `${game.away_team} won by ${game.away_score - game.home_score}`}
                  </span>
                </div>
              )}

              {/* Predictions (if available) */}
              {(game.elo_spread || game.ai_spread || game.vegas_spread) && (
                <div className="ticker-predictions">
                  {game.elo_spread && (
                    <div className="pred-line">
                      <div className="pred-left">
                        <span className="pred-icon">📊</span>
                        <span className="pred-text" title="ELO Spread Prediction - For betting against the spread">
                          ELO Spread: {(() => {
                            const rounded = Math.round(game.elo_spread * 2) / 2;
                            return rounded < 0 ? `${game.home_team} ${rounded}` : `${game.away_team} +${rounded}`;
                          })()}
                        </span>
                      </div>
                      {game.status === 'final' && (
                        <span className={`pred-check ${
                          game.elo_spread_covered === 'push' ? 'push' : 
                          game.elo_spread_covered === 'yes' ? 'correct' : 'wrong'
                        }`}>
                          {game.elo_spread_covered === 'push' ? 'PUSH' : game.elo_spread_covered === 'yes' ? '✓' : '✗'}
                        </span>
                      )}
                    </div>
                  )}
                  {game.elo_prediction && (
                    <div className="pred-line pred-winner">
                      <div className="pred-left">
                        <span className="pred-icon">🏆</span>
                        <span className="pred-text" title="ELO Moneyline Prediction - For moneyline betting">
                          ELO Moneyline: {game.elo_prediction}
                        </span>
                      </div>
                      {game.status === 'final' && game.elo_correct !== null && (
                        <span className={`pred-check ${game.elo_correct ? 'correct' : 'wrong'}`}>
                          {game.elo_correct ? '✓' : '✗'}
                        </span>
                      )}
                    </div>
                  )}
                  {game.ai_spread && (
                    <div className="pred-line">
                      <div className="pred-left">
                        <span className="pred-icon">🤖</span>
                        <span className="pred-text" title="XGBoost Spread Prediction - For betting against the spread">
                          AI Spread: {(() => {
                            const rounded = Math.round(game.ai_spread * 2) / 2;
                            return rounded < 0 ? `${game.home_team} ${rounded}` : `${game.away_team} +${rounded}`;
                          })()}
                        </span>
                      </div>
                      {game.status === 'final' && (
                        <span className={`pred-check ${
                          game.ai_spread_covered === 'push' ? 'push' : 
                          game.ai_spread_covered === 'yes' ? 'correct' : 'wrong'
                        }`}>
                          {game.ai_spread_covered === 'push' ? 'PUSH' : game.ai_spread_covered === 'yes' ? '✓' : '✗'}
                        </span>
                      )}
                    </div>
                  )}
                  {game.ai_prediction && (
                    <div className="pred-line pred-winner">
                      <div className="pred-left">
                        <span className="pred-icon">🏆</span>
                        <span className="pred-text" title="XGBoost Moneyline Prediction - For moneyline betting">
                          AI Moneyline: {game.ai_prediction}
                        </span>
                      </div>
                      {game.status === 'final' && game.ai_correct !== null && (
                        <span className={`pred-check ${game.ai_correct ? 'correct' : 'wrong'}`}>
                          {game.ai_correct ? '✓' : '✗'}
                        </span>
                      )}
                    </div>
                  )}
                  {game.vegas_spread && (
                    <div className="pred-line">
                      <div className="pred-left">
                        <span className="pred-icon">🎰</span>
                        <span className="pred-text" title="Vegas Spread - Official betting line">
                          Vegas Spread: {(() => {
                            const rounded = Math.round(game.vegas_spread * 2) / 2;
                            return rounded < 0 ? `${game.home_team} ${rounded}` : `${game.away_team} +${rounded}`;
                          })()}
                        </span>
                      </div>
                      {game.status === 'final' && (
                        <span className={`pred-check ${
                          game.vegas_covered === 'push' ? 'push' : 
                          game.vegas_covered === 'yes' ? 'correct' : 'wrong'
                        }`}>
                          {game.vegas_covered === 'push' ? 'PUSH' : game.vegas_covered === 'yes' ? '✓' : '✗'}
                        </span>
                      )}
                    </div>
                  )}
                  {game.vegas_total && (
                    <div className="pred-line">
                      <span className="pred-text">O/U: {game.vegas_total}</span>
                      {game.status === 'final' && (
                        <span className="ou-badge">
                          {game.home_score + game.away_score > game.vegas_total ? 'OVER' : 'UNDER'}
                        </span>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default LiveGamesTicker;
