import React, { useState, useEffect } from 'react';
import './LiveGamesTicker.css';

const API_URL = 'http://34.198.25.249:5000';

function LiveGamesTicker() {
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isPaused, setIsPaused] = useState(false);
  const scrollContainerRef = React.useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [startX, setStartX] = useState(0);
  const [scrollLeft, setScrollLeft] = useState(0);

  useEffect(() => {
    fetchGames();
    const interval = setInterval(fetchGames, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const handleMouseDown = (e) => {
    setIsDragging(true);
    setIsPaused(true);
    setStartX(e.pageX - scrollContainerRef.current.offsetLeft);
    setScrollLeft(scrollContainerRef.current.scrollLeft);
  };

  const handleMouseUp = () => {
    setIsDragging(false);
    setTimeout(() => setIsPaused(false), 3000); // Resume auto-scroll after 3 seconds
  };

  const handleMouseMove = (e) => {
    if (!isDragging) return;
    e.preventDefault();
    const x = e.pageX - scrollContainerRef.current.offsetLeft;
    const walk = (x - startX) * 2; // Multiply by 2 for faster scroll
    scrollContainerRef.current.scrollLeft = scrollLeft - walk;
  };

  const handleTouchStart = (e) => {
    setIsDragging(true);
    setIsPaused(true);
    setStartX(e.touches[0].pageX - scrollContainerRef.current.offsetLeft);
    setScrollLeft(scrollContainerRef.current.scrollLeft);
  };

  const handleTouchMove = (e) => {
    if (!isDragging) return;
    const x = e.touches[0].pageX - scrollContainerRef.current.offsetLeft;
    const walk = (x - startX) * 2;
    scrollContainerRef.current.scrollLeft = scrollLeft - walk;
  };

  const handleTouchEnd = () => {
    setIsDragging(false);
    setTimeout(() => setIsPaused(false), 3000);
  };

  const scrollLeftBtn = () => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollBy({ left: -300, behavior: 'smooth' });
      setIsPaused(true);
      setTimeout(() => setIsPaused(false), 3000);
    }
  };

  const scrollRightBtn = () => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollBy({ left: 300, behavior: 'smooth' });
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

  return (
    <div className="live-games-ticker">
      <div className="ticker-header-bar">
        <div className="ticker-label">
          <span className="live-dot"></span>
          LIVE SCORES • AI PREDICTIONS • VEGAS LINES
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
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onMouseMove={handleMouseMove}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
      >
        <div className={`ticker-content ${isPaused ? 'paused' : ''}`}>
          {/* Duplicate for seamless loop */}
          {[...games, ...games].map((game, index) => (
            <div key={`${game.game_id}-${index}`} className={`game-ticker-card ${game.status}`}>
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
                    src={`/images/teams/${game.away_team.toLowerCase()}.png`} 
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
                    src={`/images/teams/${game.home_team.toLowerCase()}.png`} 
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
              {game.ai_prediction && (
                <div className="ticker-predictions">
                  <div className="pred-line">
                    <div className="pred-left">
                      <span className="pred-icon">🤖</span>
                      <span className="pred-text">
                        AI: {game.ai_spread < 0 ? game.home_team : game.away_team} by {Math.abs(game.ai_spread)}
                      </span>
                    </div>
                    {game.status === 'final' && (
                      <span className={`pred-check ${
                        game.ai_spread_covered === 'push' ? 'push' : 
                        game.ai_spread_covered ? 'correct' : 'wrong'
                      }`}>
                        {game.ai_spread_covered === 'push' ? 'PUSH' : game.ai_spread_covered ? '✓' : '✗'}
                      </span>
                    )}
                  </div>
                  {game.vegas_spread && (
                    <div className="pred-line">
                      <div className="pred-left">
                        <span className="pred-icon">🎰</span>
                        <span className="pred-text">
                          Vegas: {game.vegas_spread < 0 ? game.home_team : game.away_team} by {Math.abs(game.vegas_spread)}
                        </span>
                      </div>
                      {game.status === 'final' && (
                        <span className={`pred-check ${
                          game.vegas_covered === 'push' ? 'push' : 
                          game.vegas_covered ? 'correct' : 'wrong'
                        }`}>
                          {game.vegas_covered === 'push' ? 'PUSH' : game.vegas_covered ? '✓' : '✗'}
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
