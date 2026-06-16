import React, { useEffect, useMemo, useState } from 'react';
import './MLPredictionsRedesign.css';
import { getDefaultSeason, getRecentSeasons } from './utils/season';
import { getSpreadConfidence } from './utils/predictionConfidence';

const API_URL = (typeof window !== 'undefined' && (window.location.hostname === 'hclombardo.com' || window.location.hostname === 'www.hclombardo.com' || window.location.hostname.endsWith('.netlify.app'))) ? '' : (process.env.REACT_APP_API_URL ?? '');
const FALLBACK_WEEKS = Array.from({ length: 18 }, (_, idx) => idx + 1);

const toNumber = (value) => {
  const num = Number(value);
  return Number.isFinite(num) ? num : null;
};

const roundToTenth = (value) => Math.round(value * 10) / 10;

const edgeToStars = (edgePoints) => {
  if (edgePoints >= 8) return 5;
  if (edgePoints >= 6) return 4;
  if (edgePoints >= 4) return 3;
  if (edgePoints >= 2) return 2;
  return 1;
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

const formatSpreadForHome = (homeTeam, spread) => {
  const value = toNumber(spread);
  if (!homeTeam || value === null) {
    return 'N/A';
  }

  if (value === 0) {
    return `${homeTeam} PK`;
  }

  return `${homeTeam} ${value > 0 ? '+' : ''}${value.toFixed(1)}`;
};

const formatTeamLine = (team, line) => {
  const value = toNumber(line);
  if (!team || value === null) {
    return 'N/A';
  }

  if (value === 0) {
    return `${team} PK`;
  }

  return `${team} ${value > 0 ? '+' : ''}${value.toFixed(1)}`;
};

const getModelResultMeta = (correct, label) => {
  if (correct === true) {
    return { className: 'correct', text: `${label} Covered`, icon: '✅' };
  }

  if (correct === false) {
    return { className: 'wrong', text: `${label} Missed`, icon: '❌' };
  }

  if (correct === 'push') {
    return { className: 'unknown', text: `${label} Push`, icon: '➖' };
  }

  return { className: 'unknown', text: `${label} Pending`, icon: '⏳' };
};

const buildCoverOutcome = ({ gameStatus, actual, homeTeam, awayTeam, pickTeam, vegasSpread }) => {
  if (gameStatus !== 'final') {
    return {
      isFinal: false,
      finalScoreLine: '',
      resultLine: 'Result pending',
      resultMeta: getModelResultMeta(null, 'Pick')
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
      resultMeta: getModelResultMeta('push', 'Pick')
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

const LEGEND_ITEMS = [
  {
    icon: '⭐',
    chipClass: 'legend-icon-chip',
    title: 'Star Rating',
    description: 'Bigger edge vs Vegas = more stars (1-5). 5 stars = biggest disagreement with the Vegas line.'
  },
  {
    icon: '🥇',
    chipClass: 'legend-icon-chip strong-play',
    title: 'Strong Play',
    description: 'Both our systems agree on the same side and there\'s a meaningful edge (3+ pts). Higher confidence.'
  },
  {
    icon: '🥈',
    chipClass: 'legend-icon-chip lean-play',
    title: 'Lean',
    description: 'Lower confidence: the systems do not fully agree on the side, or the edge is small. Close call.'
  },
  {
    icon: '🛡️',
    chipClass: 'legend-icon-chip',
    title: 'Pick / Cover',
    description: 'The side we recommend. "Cover" means that team beats the spread (wins, or loses by less than the spread).'
  },
  {
    icon: 'Δ',
    chipClass: 'legend-icon-chip',
    title: 'Edge',
    description: 'Gap between model spread and Vegas spread. Bigger gaps mean more perceived value.'
  },
  {
    icon: '📊',
    chipClass: 'legend-icon-chip',
    title: 'Power Rating Spread',
    description: 'Our team-strength system\'s predicted point margin.'
  },
  {
    icon: '🤖',
    chipClass: 'legend-icon-chip',
    title: 'AI Model Spread',
    description: 'Our AI\'s predicted point margin.'
  },
  {
    icon: '🎰',
    chipClass: 'legend-icon-chip',
    title: 'Vegas Spread',
    description: 'The official sportsbook betting line.'
  },
  {
    icon: '✓ / ✗ / ⏳',
    chipClass: 'legend-icon-chip',
    title: '✓ Covered / ✗ Missed / ⏳ Pending',
    description: 'Whether the pick beat the spread once the game is final (pending until played).'
  }
];

function MLPredictionsRedesign() {
  const defaultSeason = getDefaultSeason();
  const seasonOptions = getRecentSeasons(7, 2020, defaultSeason);

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

  const weekOptions = useMemo(() => {
    const fromApi = Array.from(new Set(
      availableWeeks
        .filter((item) => Number(item.season) === Number(season))
        .map((item) => Number(item.week))
        .filter((value) => Number.isFinite(value))
    )).sort((a, b) => a - b);

    return fromApi.length > 0 ? fromApi : FALLBACK_WEEKS;
  }, [availableWeeks, season]);

  useEffect(() => {
    initializePage();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (week && season) {
      fetchCombinedPredictions();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [week, season]);

  useEffect(() => {
    if (season) {
      fetchSeasonStats(season);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [season]);

  useEffect(() => {
    if (weekOptions.length === 0) {
      return;
    }

    if (!week || !weekOptions.includes(Number(week))) {
      setWeek(weekOptions[weekOptions.length - 1]);
    }
  }, [weekOptions, week]);

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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [season, week]);

  const initializePage = async () => {
    await fetchAvailableWeeks();
    await fetchUpcomingPredictions();
  };

  const fetchAvailableWeeks = async () => {
    try {
      const response = await fetch(`${API_URL}/api/ml/available-weeks`);
      const data = await response.json();
      if (data.success) {
        setAvailableWeeks(data.weeks || []);
      }
    } catch {
      setAvailableWeeks([]);
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
    } catch {
      setError('Failed to load upcoming predictions');
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
      const response = await fetch(`${API_URL}/api/predictions/combined/${season}/${week}`);
      const data = await response.json();
      
      if (data.success) {
        setCombinedData(data.predictions || []);
        setLastUpdated(new Date());
      } else {
        setCombinedData([]);
        setError(data.message || 'No predictions available');
      }
    } catch {
      if (!silent) {
        setCombinedData([]);
        setError('Failed to load predictions');
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
      const response = await fetch(`${API_URL}/api/ml/ai-vs-vegas-scoreboard/${selectedSeason}`);
      const data = await response.json();

      if (data.success) {
        setSeasonStats(data);
        setLastUpdated(new Date());
      } else {
        setSeasonStats(null);
      }
    } catch {
      if (!silent) {
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
    if (!team) return '';
    return `https://a.espncdn.com/i/teamlogos/nfl/500/${team}.png`;
  };

  const weeklyCards = useMemo(() => {
    if (!combinedData || combinedData.length === 0) {
      return [];
    }

    return combinedData
      .map((game) => {
        const homeTeam = game.home_team;
        const awayTeam = game.away_team;

        const eloSpread = toNumber(game.elo?.spread);
        const aiSpread = toNumber(game.xgb?.spread);
        const vegasSpread = toNumber(game.vegas_spread);

        let modelSpread = null;
        if (eloSpread !== null && aiSpread !== null) {
          modelSpread = roundToTenth((eloSpread + aiSpread) / 2);
        } else if (aiSpread !== null) {
          modelSpread = aiSpread;
        } else if (eloSpread !== null) {
          modelSpread = eloSpread;
        }

        const fallbackWinner = game.xgb?.predicted_winner || game.elo?.predicted_winner || null;
        let pickTeam = null;
        if (modelSpread !== null) {
          if (modelSpread < 0) {
            pickTeam = homeTeam;
          } else if (modelSpread > 0) {
            pickTeam = awayTeam;
          }
        }

        if (!pickTeam && (fallbackWinner === homeTeam || fallbackWinner === awayTeam)) {
          pickTeam = fallbackWinner;
        }

        const pickModelLine = (pickTeam && modelSpread !== null)
          ? (pickTeam === homeTeam ? modelSpread : -modelSpread)
          : null;

        const pickVegasLine = (pickTeam && vegasSpread !== null)
          ? (pickTeam === homeTeam ? vegasSpread : -vegasSpread)
          : null;

        const edgePoints = (pickModelLine !== null && pickVegasLine !== null)
          ? Math.abs(pickVegasLine - pickModelLine)
          : 0;

        const {
          confidenceLabel,
          confidenceDetail,
          confidenceTone
        } = getSpreadConfidence({
          homeTeam,
          pickTeam,
          eloSpread,
          aiSpread,
          edgePoints
        });

        const actionText = pickTeam
          ? `${pickTeam} to cover (${formatSpreadValue(pickVegasLine)})`
          : 'No clear side to cover';

        let verdictLine = 'Spread edge unavailable for this matchup right now.';
        if (pickTeam && pickModelLine !== null && pickVegasLine !== null) {
          verdictLine = `Our model: ${formatTeamLine(pickTeam, pickModelLine)} vs Vegas ${formatTeamLine(pickTeam, pickVegasLine)} - ${edgePoints.toFixed(1)} pt edge.`;
        } else if (pickTeam && pickModelLine !== null) {
          verdictLine = `Our model: ${formatTeamLine(pickTeam, pickModelLine)} - Vegas line unavailable.`;
        }

        const outcome = buildCoverOutcome({
          gameStatus: game.game_status,
          actual: game.actual,
          homeTeam,
          awayTeam,
          pickTeam,
          vegasSpread
        });

        return {
          ...game,
          edgePoints,
          stars: edgeToStars(edgePoints),
          confidenceLabel,
          confidenceDetail,
          confidenceTone,
          actionText,
          verdictLine,
          pickTeam,
          pickLogo: getTeamLogo(pickTeam),
          powerSpreadDisplay: formatSpreadForHome(homeTeam, eloSpread),
          aiSpreadDisplay: formatSpreadForHome(homeTeam, aiSpread),
          vegasSpreadDisplay: formatSpreadForHome(homeTeam, vegasSpread),
          outcome
        };
      })
      .sort((a, b) => b.edgePoints - a.edgePoints);
  }, [combinedData]);

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
        <h1>AI Predictions</h1>
        <p className="subtitle">Any week. Any season. Full bettor card board with pick, edge, and result grading.</p>
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
            {weekOptions.map((optionWeek) => (
              <option key={optionWeek} value={optionWeek}>Week {optionWeek}</option>
            ))}
          </select>
        </div>

        <button className="load-btn" onClick={() => fetchCombinedPredictions()}>
          Load Week
        </button>
      </div>

      <section className="dashboard-legend-panel" aria-labelledby="predictions-legend-title">
        <div className="dashboard-legend-header">
          <h2 id="predictions-legend-title">Legend Key</h2>
          <p>Quick reference for bettor cards and spread terms.</p>
        </div>
        <div className="dashboard-legend-grid">
          {LEGEND_ITEMS.map((item) => (
            <div className="dashboard-legend-item" key={item.title}>
              <span className={`symbol-chip ${item.chipClass}`}>{item.icon}</span>
              <div className="dashboard-legend-copy">
                <h3>{item.title}</h3>
                <p>{item.description}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

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
          <h3>Season Verdict - {season}</h3>
          <p>
            {seasonStats?.season_summary?.verdict_text || 'No played games yet'}
          </p>
        </div>

        {seasonStatsLoading ? (
          <div className="season-benchmark-loading">Updating season benchmark...</div>
        ) : (
          <>
            <div className="season-benchmark-grid">
              <div className="benchmark-tile ai">
                <div className="benchmark-label">AI ATS Wins</div>
                <div className="benchmark-value">
                  {seasonStats ? Number(seasonStats?.season_summary?.ai_wins || 0) : 0}
                </div>
              </div>

              <div className="benchmark-tile vegas">
                <div className="benchmark-label">Vegas ATS Wins</div>
                <div className="benchmark-value">
                  {seasonStats ? Number(seasonStats?.season_summary?.vegas_wins || 0) : 0}
                </div>
              </div>

              <div className="benchmark-tile delta positive">
                <div className="benchmark-label">Pushes</div>
                <div className="benchmark-value">
                  {seasonStats ? Number(seasonStats?.season_summary?.pushes || 0) : 0}
                </div>
              </div>

              <div className="benchmark-tile delta negative">
                <div className="benchmark-label">Total Games</div>
                <div className="benchmark-value">
                  {seasonStats ? Number(seasonStats?.season_summary?.games || 0) : 0}
                </div>
              </div>
            </div>

            <div className="season-benchmark-detail">
              {seasonStats
                ? (seasonStats?.season_summary?.proof_line || 'No played games yet for this season.')
                : 'Season benchmark data unavailable'}
            </div>

            {seasonStats && (
              <div className="season-benchmark-detail">
                Full sample: AI {Number(seasonStats?.season_summary?.ai_pct || 0).toFixed(1)}% vs Vegas {Number(seasonStats?.season_summary?.vegas_pct || 0).toFixed(1)}%
              </div>
            )}
          </>
        )}
      </div>

      {error && (
        <div className="error-message">
          <p>{error}</p>
        </div>
      )}

      <div className="content-area">
        <div className="section-header">
          <h2>Week {week} Bettor Cards</h2>
          <p>All games for the selected week, ordered by model-vs-market edge.</p>
        </div>

        {weeklyCards.length === 0 ? (
          <div className="empty-state">No prediction cards available for this week yet.</div>
        ) : (
          <div className="prediction-cards-grid">
            {weeklyCards.map((game, idx) => (
              <article key={game.game_id || `${game.home_team}-${game.away_team}-${idx}`} className="prediction-card">
                <div className="prediction-top-row">
                  <div className="prediction-stars" aria-label={`${game.stars} of 5 stars`}>
                    <span className="stars-filled">{'★'.repeat(game.stars)}</span>
                    <span className="stars-empty">{'☆'.repeat(5 - game.stars)}</span>
                  </div>
                  <span className={`prediction-confidence-badge ${game.confidenceTone}`}>{game.confidenceLabel}</span>
                </div>

                <div className="prediction-matchup-row">
                  <img src={getTeamLogo(game.away_team)} alt={game.away_team} className="prediction-team-logo" />
                  <h3>{game.away_team} @ {game.home_team}</h3>
                  <img src={getTeamLogo(game.home_team)} alt={game.home_team} className="prediction-team-logo" />
                </div>

                <div className="prediction-pick-row">
                  {game.pickTeam && (
                    <img src={game.pickLogo} alt={game.pickTeam} className="prediction-pick-logo" />
                  )}
                  <div className="prediction-pick-copy">
                    <p className="prediction-pick-title">Pick: {game.actionText}</p>
                    <p className={`prediction-confidence-detail ${game.confidenceTone}`}>{game.confidenceDetail}</p>
                  </div>
                </div>

                <p className="prediction-edge-line">{game.verdictLine}</p>

                <div className={`prediction-result-strip ${game.outcome.isFinal ? 'final' : 'scheduled'}`}>
                  {game.outcome.isFinal ? (
                    <>
                      <div className="prediction-final-line">{game.outcome.finalScoreLine}</div>
                      <div className="prediction-results-line">
                        <span className={`prediction-result-badge ${game.outcome.resultMeta.className}`}>
                          {game.outcome.resultMeta.icon} {game.outcome.resultMeta.text}
                        </span>
                        <span className="prediction-result-text">{game.outcome.resultLine}</span>
                      </div>
                    </>
                  ) : (
                    <div className="prediction-results-line">
                      <span className="prediction-result-badge unknown">⏳ Pick Result Pending</span>
                    </div>
                  )}
                </div>

                <details className="prediction-lines-panel">
                  <summary>Show model lines</summary>
                  <div className="prediction-lines-grid">
                    <div className="prediction-line-item">
                      <span>Power Rating Spread</span>
                      <strong>{game.powerSpreadDisplay}</strong>
                    </div>
                    <div className="prediction-line-item">
                      <span>AI Model Spread</span>
                      <strong>{game.aiSpreadDisplay}</strong>
                    </div>
                    <div className="prediction-line-item">
                      <span>Vegas Spread</span>
                      <strong>{game.vegasSpreadDisplay}</strong>
                    </div>
                  </div>
                </details>
              </article>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default MLPredictionsRedesign;
