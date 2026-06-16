import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from './contexts/ThemeContext';
import './Homepage.css';
import LiveGamesTicker from './LiveGamesTicker';
import { getDefaultSeason } from './utils/season';
import { getSpreadConfidence } from './utils/predictionConfidence';

const API_URL = (typeof window !== 'undefined' && (window.location.hostname === 'hclombardo.com' || window.location.hostname === 'www.hclombardo.com' || window.location.hostname.endsWith('.netlify.app'))) ? '' : (process.env.REACT_APP_API_URL ?? '');

// Map team abbreviations to logo filenames
const teamLogoMap = {
  'WSH': 'was',  // Washington
  'WAS': 'was',  // Washington (alternate)
  'LAR': 'lar',  // LA Rams
  'LAC': 'lac',  // LA Chargers
};

const getTeamLogoName = (abbr) => {
  return (teamLogoMap[abbr] || abbr).toLowerCase();
};

const toNumber = (value) => {
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
};

const formatSpreadValue = (line) => {
  const numeric = toNumber(line);
  if (numeric === null) {
    return 'N/A';
  }

  if (numeric === 0) {
    return 'PK';
  }

  return `${numeric > 0 ? '+' : ''}${numeric.toFixed(1)}`;
};

const edgeToStars = (edgePoints) => {
  if (edgePoints >= 8) return 5;
  if (edgePoints >= 6) return 4;
  if (edgePoints >= 4) return 3;
  if (edgePoints >= 2) return 2;
  return 1;
};

const getModelResultMeta = (correct, label) => {
  if (correct === true) {
    return { className: 'correct', text: `${label} Covered`, icon: '✅' };
  }

  if (correct === false) {
    return { className: 'wrong', text: `${label} Missed`, icon: '❌' };
  }

  return { className: 'unknown', text: `${label} Pending`, icon: '⏳' };
};

const buildCoverOutcome = ({ gameStatus, actual, homeTeam, awayTeam, pickTeam, vegasSpread }) => {
  if (gameStatus !== 'final') {
    return {
      isFinal: false,
      finalScoreLine: '',
      resultLine: '',
      resultMeta: { className: 'unknown', text: 'Result Pending', icon: '⏳' }
    };
  }

  const homeScore = toNumber(actual?.home_score);
  const awayScore = toNumber(actual?.away_score);
  const marketSpread = toNumber(vegasSpread);

  const finalScoreLine = (homeScore !== null && awayScore !== null)
    ? `Final: ${awayTeam} ${awayScore} - ${homeTeam} ${homeScore}`
    : 'Final score unavailable';

  if (
    homeScore === null
    || awayScore === null
    || marketSpread === null
    || (pickTeam !== homeTeam && pickTeam !== awayTeam)
  ) {
    return {
      isFinal: true,
      finalScoreLine,
      resultLine: 'Result pending',
      resultMeta: getModelResultMeta(null, 'Pick')
    };
  }

  const homeAdjustedMargin = homeScore + marketSpread - awayScore;
  if (homeAdjustedMargin === 0) {
    return {
      isFinal: true,
      finalScoreLine,
      resultLine: `${pickTeam} pushed`,
      resultMeta: { className: 'unknown', text: 'Push', icon: '➖' }
    };
  }

  const pickCovered = pickTeam === homeTeam ? homeAdjustedMargin > 0 : homeAdjustedMargin < 0;
  return {
    isFinal: true,
    finalScoreLine,
    resultLine: `${pickTeam} ${pickCovered ? 'covered ✓' : 'missed ✗'}`,
    resultMeta: getModelResultMeta(pickCovered, 'Pick')
  };
};

const formatTeamLine = (team, line) => {
  if (!team || line === null || line === undefined || Number.isNaN(Number(line))) {
    return 'N/A';
  }

  const value = Number(line);
  if (value === 0) {
    return `${team} PK`;
  }

  return `${team} ${value > 0 ? '+' : ''}${value.toFixed(1)}`;
};

// NFL Divisions
const NFL_STRUCTURE = {
  AFC: {
    'AFC East': ['BUF', 'MIA', 'NYJ', 'NE'],
    'AFC North': ['BAL', 'CIN', 'CLE', 'PIT'],
    'AFC South': ['HOU', 'IND', 'JAX', 'TEN'],
    'AFC West': ['DEN', 'KC', 'LV', 'LAC']
  },
  NFC: {
    'NFC East': ['DAL', 'NYG', 'PHI', 'WAS'],
    'NFC North': ['CHI', 'DET', 'GB', 'MIN'],
    'NFC South': ['ATL', 'CAR', 'NO', 'TB'],
    'NFC West': ['ARI', 'LAR', 'SF', 'SEA']
  }
};

function Homepage() {
  const defaultSeason = getDefaultSeason();
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [bestBetsLoading, setBestBetsLoading] = useState(true);
  const [bestBetsError, setBestBetsError] = useState(null);
  const [bestBets, setBestBets] = useState([]);
  const [bestBetsSeason, setBestBetsSeason] = useState(defaultSeason);
  const [bestBetsWeek, setBestBetsWeek] = useState(null);
  const [trackRecordLoading, setTrackRecordLoading] = useState(true);
  const [trackRecord, setTrackRecord] = useState(null);
  const navigate = useNavigate();
  const { theme, changeTheme } = useTheme();

  useEffect(() => {
    fetchTeams();
    fetchBettorAnswers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchTeams = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/hcl/teams?season=${defaultSeason}`);
      const data = await response.json();
      setTeams(data.teams || []);
    } catch (err) {
      console.error('Failed to fetch teams:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchTrackRecord = async (seasonToLoad) => {
    setTrackRecordLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/ml/ai-vs-vegas-scoreboard/${seasonToLoad}`);
      const data = await response.json();

      if (data.success) {
        setTrackRecord(data.season_summary || null);
      } else {
        setTrackRecord(null);
      }
    } catch (err) {
      setTrackRecord(null);
    } finally {
      setTrackRecordLoading(false);
    }
  };

  const fetchCombinedGameMap = async (season, week) => {
    if (!season || !week) {
      return new Map();
    }

    try {
      const response = await fetch(`${API_URL}/api/predictions/combined/${season}/${week}`);
      const data = await response.json();
      if (!data.success || !Array.isArray(data.predictions)) {
        return new Map();
      }

      const gameMap = new Map();
      data.predictions.forEach((prediction) => {
        const gameId = prediction.game_id;
        const homeTeam = prediction.home_team;
        const awayTeam = prediction.away_team;
        const gameDetails = {
          agreement: prediction.agreement,
          gameStatus: prediction.game_status,
          actual: prediction.actual || null,
          vegasSpread: prediction.vegas_spread,
          xgbSpread: toNumber(prediction?.xgb?.spread),
          eloSpread: toNumber(prediction?.elo?.spread),
          xgbWinner: prediction?.xgb?.predicted_winner || null,
          eloWinner: prediction?.elo?.predicted_winner || null
        };

        if (gameId) {
          gameMap.set(String(gameId), gameDetails);
        }
        if (homeTeam && awayTeam) {
          gameMap.set(`${awayTeam}@${homeTeam}`, gameDetails);
        }
      });

      return gameMap;
    } catch (_err) {
      return new Map();
    }
  };

  const rankBestBets = (predictions, combinedGameMap = new Map()) => {
    const ranked = (predictions || []).map((prediction) => {
      const vegasSpread = toNumber(prediction.vegas_spread);
      const homeTeam = prediction.home_team;
      const awayTeam = prediction.away_team;

      const gameId = prediction.game_id ? String(prediction.game_id) : null;
      const matchupKey = `${awayTeam}@${homeTeam}`;
      const combinedGame = gameId && combinedGameMap.has(gameId)
        ? combinedGameMap.get(gameId)
        : combinedGameMap.get(matchupKey);

      const modelAiSpread = combinedGame?.xgbSpread ?? toNumber(prediction.ai_spread);
      const modelEloSpread = combinedGame?.eloSpread ?? null;

      let modelSpread = null;
      if (modelAiSpread !== null && modelEloSpread !== null) {
        modelSpread = Number(((modelAiSpread + modelEloSpread) / 2).toFixed(1));
      } else if (modelAiSpread !== null) {
        modelSpread = modelAiSpread;
      } else if (modelEloSpread !== null) {
        modelSpread = modelEloSpread;
      }

      if (modelSpread === null || vegasSpread === null || !homeTeam || !awayTeam) {
        return null;
      }

      let pickTeam = null;
      if (modelSpread < 0) {
        pickTeam = homeTeam;
      } else if (modelSpread > 0) {
        pickTeam = awayTeam;
      }

      const fallbackWinner = combinedGame?.xgbWinner || combinedGame?.eloWinner || prediction.predicted_winner;
      if (!pickTeam && (fallbackWinner === homeTeam || fallbackWinner === awayTeam)) {
        pickTeam = fallbackWinner;
      }

      if (!pickTeam) {
        return null;
      }

      const pickModelLine = pickTeam === homeTeam ? modelSpread : -modelSpread;
      const vegasLineForPick = pickTeam === homeTeam ? vegasSpread : -vegasSpread;
      const lineGap = Number((vegasLineForPick - pickModelLine).toFixed(1));
      const edgePoints = Math.abs(lineGap);

      const outcome = buildCoverOutcome({
        gameStatus: combinedGame?.gameStatus,
        actual: combinedGame?.actual,
        homeTeam,
        awayTeam,
        pickTeam,
        vegasSpread: combinedGame?.vegasSpread ?? vegasSpread
      });

      const stars = edgeToStars(edgePoints);
      const {
        confidenceLabel,
        confidenceDetail,
        confidenceTone
      } = getSpreadConfidence({
        homeTeam,
        pickTeam,
        eloSpread: modelEloSpread,
        aiSpread: modelAiSpread,
        edgePoints
      });
      const pickSpreadText = formatSpreadValue(vegasLineForPick);
      const actionText = `${pickTeam} to cover (${pickSpreadText})`;
      const whyLine = `Edge: ${formatTeamLine(pickTeam, pickModelLine)} vs Vegas ${formatTeamLine(pickTeam, vegasLineForPick)} (${edgePoints.toFixed(1)} pts).`;

      return {
        ...prediction,
        pickTeam,
        aiLineForPick: pickModelLine,
        vegasLineForPick,
        edgePoints,
        stars,
        confidenceLabel,
        confidenceDetail,
        confidenceTone,
        actionText,
        whyLine,
        outcome,
      };
    })
      .filter(Boolean)
      .sort((a, b) => b.edgePoints - a.edgePoints);

    return ranked.slice(0, 5);
  };

  const fetchBettorAnswers = async () => {
    setBestBetsLoading(true);
    setBestBetsError(null);

    let seasonForTrackRecord = defaultSeason;
    try {
      const response = await fetch(`${API_URL}/api/ml/predict-upcoming`);
      const data = await response.json();

      const season = toNumber(data?.season) || defaultSeason;
      const week = toNumber(data?.week);
      const predictions = Array.isArray(data?.predictions) ? data.predictions : [];
      const combinedGameMap = await fetchCombinedGameMap(season, week);

      seasonForTrackRecord = season;
      setBestBetsSeason(season);
      setBestBetsWeek(week);
      setBestBets(rankBestBets(predictions, combinedGameMap));
    } catch (err) {
      setBestBets([]);
      setBestBetsError('Could not load this week\'s picks right now.');
    } finally {
      setBestBetsLoading(false);
    }

    fetchTrackRecord(seasonForTrackRecord);
  };

  const getTeamByAbbr = (abbr) => {
    return teams.find(t => t.team === abbr) || { team_name: abbr, team: abbr, wins: 0, losses: 0, ties: 0 };
  };

  // Sort teams by NFL standings rules (simplified)
  const sortTeamsByStandings = (teamAbbrs) => {
    return teamAbbrs.map(abbr => getTeamByAbbr(abbr))
      .sort((a, b) => {
        // Calculate win percentage
        const aGames = a.wins + a.losses + (a.ties || 0);
        const bGames = b.wins + b.losses + (b.ties || 0);
        const aWinPct = aGames > 0 ? (a.wins + (a.ties || 0) * 0.5) / aGames : 0;
        const bWinPct = bGames > 0 ? (b.wins + (b.ties || 0) * 0.5) / bGames : 0;
        
        // Primary: Win percentage (descending)
        if (Math.abs(aWinPct - bWinPct) > 0.001) {
          return bWinPct - aWinPct;
        }
        
        // Secondary: Total wins (descending)
        if (a.wins !== b.wins) {
          return b.wins - a.wins;
        }
        
        // Tertiary: Alphabetical by team abbreviation
        return (a.team || '').localeCompare(b.team || '');
      })
      .map(team => team.team);
  };

  const handleTeamClick = (abbr) => {
    navigate(`/team/${abbr}`);
  };

  const buildTrackRecordLine = () => {
    if (!trackRecord) {
      return 'Track record updates when final scores are posted.';
    }

    const aiPct = toNumber(trackRecord.ai_pct);
    const vegasPct = toNumber(trackRecord.vegas_pct);
    const totalGames = toNumber(trackRecord.games) || 0;

    if (aiPct === null || vegasPct === null || totalGames === 0) {
      return 'Track record updates when enough final scores are in.';
    }

    return `HC Lombardo AI: ${aiPct.toFixed(1)}% against the spread this season — Vegas: ${vegasPct.toFixed(1)}%.`;
  };

  if (loading) {
    return (
      <div className="homepage-loading">
        <div className="loading-spinner"></div>
        <p>Loading NFL Teams...</p>
      </div>
    );
  }

  return (
    <div className="homepage">

      {/* Theme Selector */}
      <div className="theme-selector-bar">
        <span className="theme-selector-label">🎨 Theme:</span>
        <select
          className="theme-dropdown"
          value={theme}
          onChange={(e) => changeTheme(e.target.value)}
        >
          <option value="nfl">🏈 NFL</option>
          <option value="executive-dark">💼 Executive Dark</option>
          <option value="classic-light">☀️ Classic Light</option>
        </select>
      </div>

      {/* Live Games Ticker */}
      <LiveGamesTicker />

      <section className="dashboard-legend-panel" aria-labelledby="dashboard-legend-title">
        <div className="dashboard-legend-header">
          <h2 id="dashboard-legend-title">Legend Key</h2>
          <p>Quick reference for ticker rows and Best Bets terms.</p>
        </div>

        <div className="dashboard-legend-grid">
          <div className="dashboard-legend-item">
            <span className="symbol-chip legend-icon-chip">📊</span>
            <div className="dashboard-legend-copy">
              <h3>Power Rating Spread</h3>
              <p>Our team-strength system&apos;s predicted point margin.</p>
            </div>
          </div>
          <div className="dashboard-legend-item">
            <span className="symbol-chip legend-icon-chip">🏆</span>
            <div className="dashboard-legend-copy">
              <h3>Moneyline Pick</h3>
              <p>Straight-up winner pick used by both systems.</p>
            </div>
          </div>
          <div className="dashboard-legend-item">
            <span className="symbol-chip legend-icon-chip">🤖</span>
            <div className="dashboard-legend-copy">
              <h3>AI Model Spread</h3>
              <p>Our AI&apos;s predicted point margin.</p>
            </div>
          </div>
          <div className="dashboard-legend-item">
            <span className="symbol-chip legend-icon-chip">🎰</span>
            <div className="dashboard-legend-copy">
              <h3>Vegas Spread</h3>
              <p>The official sportsbook betting line.</p>
            </div>
          </div>
          <div className="dashboard-legend-item">
            <span className="symbol-chip success">✅ / ✓</span>
            <div className="dashboard-legend-copy">
              <h3>Covered</h3>
              <p>The pick beat the spread.</p>
            </div>
          </div>
          <div className="dashboard-legend-item">
            <span className="symbol-chip danger">❌ / ✗</span>
            <div className="dashboard-legend-copy">
              <h3>Missed</h3>
              <p>The pick did not cover the spread.</p>
            </div>
          </div>
          <div className="dashboard-legend-item">
            <span className="symbol-chip pending">⏳</span>
            <div className="dashboard-legend-copy">
              <h3>Result Pending</h3>
              <p>Game not played yet, so no grade yet.</p>
            </div>
          </div>
          <div className="dashboard-legend-item">
            <span className="symbol-chip legend-icon-chip">⭐</span>
            <div className="dashboard-legend-copy">
              <h3>Top Pick</h3>
              <p>Overall side recommendation from both systems.</p>
            </div>
          </div>
          <div className="dashboard-legend-item">
            <span className="symbol-chip legend-icon-chip strong-play">🥇</span>
            <div className="dashboard-legend-copy">
              <h3>Strong Play</h3>
              <p>Both our systems agree on this pick (higher-confidence play).</p>
            </div>
          </div>
          <div className="dashboard-legend-item">
            <span className="symbol-chip legend-icon-chip lean-play">🥈</span>
            <div className="dashboard-legend-copy">
              <h3>Lean</h3>
              <p>Our systems point the same way but do not fully agree (lower-confidence, close call).</p>
            </div>
          </div>
          <div className="dashboard-legend-item">
            <span className="symbol-chip legend-icon-chip">±</span>
            <div className="dashboard-legend-copy">
              <h3>Spread</h3>
              <p>Points handicap used to balance both teams.</p>
            </div>
          </div>
          <div className="dashboard-legend-item">
            <span className="symbol-chip legend-icon-chip">💵</span>
            <div className="dashboard-legend-copy">
              <h3>Moneyline</h3>
              <p>Straight pick on who wins the game.</p>
            </div>
          </div>
          <div className="dashboard-legend-item">
            <span className="symbol-chip legend-icon-chip">🛡️</span>
            <div className="dashboard-legend-copy">
              <h3>Cover</h3>
              <p>Your side beats the posted spread.</p>
            </div>
          </div>
          <div className="dashboard-legend-item">
            <span className="symbol-chip legend-icon-chip">🤝</span>
            <div className="dashboard-legend-copy">
              <h3>Push</h3>
              <p>Final margin lands exactly on the line.</p>
            </div>
          </div>
          <div className="dashboard-legend-item">
            <span className="symbol-chip legend-icon-chip">⚖️</span>
            <div className="dashboard-legend-copy">
              <h3>Favorite / Underdog</h3>
              <p>Favorite is negative, underdog is positive.</p>
            </div>
          </div>
          <div className="dashboard-legend-item">
            <span className="symbol-chip legend-icon-chip">Δ</span>
            <div className="dashboard-legend-copy">
              <h3>Edge</h3>
              <p>Gap between model spread and Vegas spread.</p>
            </div>
          </div>
          <div className="dashboard-legend-item">
            <span className="symbol-chip legend-icon-chip">↕️</span>
            <div className="dashboard-legend-copy">
              <h3>O/U</h3>
              <p>Total points line for over or under bets.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="best-bets-section">
        <div className="section-heading-row">
          <h2>This Week&apos;s Best Bets</h2>
          <span className="section-meta">
            {bestBetsWeek ? `Week ${bestBetsWeek} • ${bestBetsSeason}` : `${bestBetsSeason}`}
          </span>
        </div>

        {bestBetsLoading ? (
          <p className="best-bets-state">Loading this week&apos;s lines...</p>
        ) : bestBetsError ? (
          <p className="best-bets-state">{bestBetsError}</p>
        ) : bestBets.length === 0 ? (
          <p className="best-bets-state">No games this week - check back when the season&apos;s live.</p>
        ) : (
          <div className="best-bets-grid">
            {bestBets.map((bet, idx) => (
              <article key={bet.game_id || `${bet.home_team}-${bet.away_team}-${idx}`} className="best-bet-card">
                <div className="best-bet-top-row">
                  <div className="best-bet-stars" aria-label={`${bet.stars} of 5 stars`}>
                    <span className="stars-filled">{'★'.repeat(bet.stars)}</span>
                    <span className="stars-empty">{'☆'.repeat(5 - bet.stars)}</span>
                  </div>
                  <span className={`bet-confidence-badge ${bet.confidenceTone}`}>{bet.confidenceLabel}</span>
                </div>

                <div className="best-bet-matchup-row">
                  <img
                    src={`/images/teams/${getTeamLogoName(bet.away_team)}.png`}
                    alt={bet.away_team}
                    className="best-bet-logo"
                    onError={(e) => { e.currentTarget.style.display = 'none'; }}
                  />
                  <h3>{bet.away_team} @ {bet.home_team}</h3>
                  <img
                    src={`/images/teams/${getTeamLogoName(bet.home_team)}.png`}
                    alt={bet.home_team}
                    className="best-bet-logo"
                    onError={(e) => { e.currentTarget.style.display = 'none'; }}
                  />
                </div>

                <p className="bet-pick">Pick: {bet.actionText}</p>
                <p className="bet-edge-note">{bet.whyLine}</p>
                <p className={`bet-confidence-detail ${bet.confidenceTone}`}>{bet.confidenceDetail}</p>

                <div className={`best-bet-result-strip ${bet.outcome?.isFinal ? 'final' : 'scheduled'}`}>
                  {bet.outcome?.isFinal ? (
                    <>
                      <div className="best-bet-final-line">
                        {bet.outcome?.finalScoreLine || 'Final score unavailable'}
                      </div>
                      <div className="bet-results-line">
                        <span className={`bet-result-badge ${bet.outcome?.resultMeta?.className || 'unknown'}`}>
                          {bet.outcome?.resultMeta?.icon || '⏳'} {bet.outcome?.resultMeta?.text || 'Result Pending'}
                        </span>
                      </div>
                    </>
                  ) : (
                    <div className="bet-results-line">
                      <span className="bet-result-badge unknown">⏳ Result Pending</span>
                    </div>
                  )}
                </div>
              </article>
            ))}
          </div>
        )}
      </section>

      <section className="track-record-strip">
        <div>
          <h3>How&apos;s the AI Doing?</h3>
          <p>
            {trackRecordLoading ? 'Loading season track record...' : buildTrackRecordLine()}
          </p>
          {!trackRecordLoading && trackRecord && (toNumber(trackRecord.games) || 0) > 0 && (
            <p className="track-record-detail">
              Season sample: {trackRecord.games} games • AI ATS covers: {trackRecord.ai_wins} • Vegas ATS covers: {trackRecord.vegas_wins} • Pushes: {trackRecord.pushes}
            </p>
          )}
        </div>
        <button
          className="track-record-btn"
          type="button"
          onClick={() => navigate('/model-performance')}
        >
          See full track record
        </button>
      </section>

      {/* Standings Section Header */}
      <div className="homepage-header">
        <h1>NFL Standings</h1>
        <h2>{defaultSeason}</h2>
        <p className="season-subtitle">Division-by-division reference board</p>
      </div>

      {Object.entries(NFL_STRUCTURE).map(([conference, divisions]) => (
        <div key={conference} className={`conference-section ${conference.toLowerCase()}-section`}>
          <div className={`conference-header ${conference.toLowerCase()}`}>
            <img 
              src={`/images/${conference.toLowerCase()}.png`}
              alt={`${conference} Logo`}
              className="conference-logo-image"
            />
            <h2 className="conference-title">{conference}</h2>
          </div>
          
          <div className="divisions-grid">
            {Object.entries(divisions).map(([divisionName, teamAbbrs]) => {
              const sortedTeams = sortTeamsByStandings(teamAbbrs);
              return (
                <div key={divisionName} className="division-card">
                  <h3 className="division-title">{divisionName}</h3>
                  <div className="teams-list">
                    {sortedTeams.map(abbr => {
                      const team = getTeamByAbbr(abbr);
                      return (
                        <div 
                          key={abbr} 
                          className="team-row"
                          onClick={() => handleTeamClick(abbr)}
                        >
                          <img 
                            src={`/images/teams/${getTeamLogoName(abbr)}.png`}
                            alt={team.team_name || team.team || abbr}
                            className="team-logo-small"
                            onError={(e) => {e.target.style.display='none'}}
                          />
                          <span className="team-name-short">{team.team_name || team.team || abbr}</span>
                          <span className="team-record">
                            {team.wins}-{team.losses}{team.ties > 0 ? `-${team.ties}` : ''}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}

      <div className="homepage-footer">
        <button onClick={fetchTeams} className="refresh-btn-home">
          🔄 Refresh Standings
        </button>
      </div>

    </div>
  );
}

export default Homepage;
