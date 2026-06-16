import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from './contexts/ThemeContext';
import './Homepage.css';
import LiveGamesTicker from './LiveGamesTicker';
import { getDefaultSeason } from './utils/season';

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

const formatMarketLine = (homeTeam, awayTeam, homeSpread) => {
  if (!homeTeam || !awayTeam || homeSpread === null || homeSpread === undefined || Number.isNaN(Number(homeSpread))) {
    return 'N/A';
  }

  const spread = Number(homeSpread);
  if (spread === 0) {
    return 'PK';
  }

  if (spread < 0) {
    return `${homeTeam} ${spread.toFixed(1)}`;
  }

  return `${awayTeam} -${Math.abs(spread).toFixed(1)}`;
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
  const [trackRecordSeason, setTrackRecordSeason] = useState(defaultSeason);
  const [showHowItWorks, setShowHowItWorks] = useState(false);
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
        setTrackRecordSeason(seasonToLoad);
      } else {
        setTrackRecord(null);
      }
    } catch (err) {
      setTrackRecord(null);
    } finally {
      setTrackRecordLoading(false);
    }
  };

  const rankBestBets = (predictions) => {
    const ranked = (predictions || []).map((prediction) => {
      const aiSpread = toNumber(prediction.ai_spread);
      const vegasSpread = toNumber(prediction.vegas_spread);
      const homeTeam = prediction.home_team;
      const awayTeam = prediction.away_team;

      if (aiSpread === null || vegasSpread === null || !homeTeam || !awayTeam) {
        return null;
      }

      let pickTeam = prediction.predicted_winner;
      if (pickTeam !== homeTeam && pickTeam !== awayTeam) {
        pickTeam = aiSpread <= 0 ? homeTeam : awayTeam;
      }

      const aiLineForPick = pickTeam === homeTeam ? aiSpread : -aiSpread;
      const vegasLineForPick = pickTeam === homeTeam ? vegasSpread : -vegasSpread;
      const lineGap = Number((vegasLineForPick - aiLineForPick).toFixed(1));
      const edgePoints = Math.abs(lineGap);

      let edgeStatement = `Biggest disagreement this week: ${pickTeam} by ${edgePoints.toFixed(1)} points.`;
      if (lineGap > 0) {
        edgeStatement = `AI sees ${pickTeam} as ${edgePoints.toFixed(1)} points better than the market line.`;
      } else if (lineGap < 0) {
        edgeStatement = `The market line is ${edgePoints.toFixed(1)} points stronger on ${pickTeam} than the AI line.`;
      }

      return {
        ...prediction,
        pickTeam,
        aiLineForPick,
        vegasLineForPick,
        edgePoints,
        edgeStatement,
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

      seasonForTrackRecord = season;
      setBestBetsSeason(season);
      setBestBetsWeek(week);
      setBestBets(rankBestBets(predictions));
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
                <div className="best-bet-rank">#{idx + 1} Edge</div>
                <h3>{bet.away_team} @ {bet.home_team}</h3>
                <p className="bet-pick">Pick: {bet.pickTeam} to cover</p>
                <p>AI line: {formatTeamLine(bet.pickTeam, bet.aiLineForPick)}</p>
                <p>Vegas line: {formatMarketLine(bet.home_team, bet.away_team, bet.vegas_spread)}</p>
                <p className="bet-edge-note">{bet.edgeStatement}</p>
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

      <div className="how-it-works-link-row">
        <button
          type="button"
          className="how-it-works-toggle"
          onClick={() => setShowHowItWorks((prev) => !prev)}
        >
          {showHowItWorks ? 'Hide how picks are made' : 'How picks are made'}
        </button>
      </div>

      {showHowItWorks && (
        <section className="how-it-works-panel">
          <h3>How Picks Are Built</h3>
          <ul>
            <li><strong>Team Power Ratings:</strong> We track team strength as results come in each week.</li>
            <li><strong>Game Matchup Read:</strong> We forecast each game score and expected spread.</li>
            <li><strong>Line Check:</strong> We compare our line to Vegas and flag the biggest gaps.</li>
          </ul>
          <p>Use this dashboard for spread edges first, then check line movement before placing a bet.</p>
        </section>
      )}


    </div>
  );
}

export default Homepage;
