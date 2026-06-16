import React, { useEffect, useMemo, useState } from 'react';
import './ModelPerformance.css';
import { getDefaultSeason } from './utils/season';

const API_URL = (typeof window !== 'undefined' && (window.location.hostname === 'hclombardo.com' || window.location.hostname === 'www.hclombardo.com' || window.location.hostname.endsWith('.netlify.app'))) ? '' : (process.env.REACT_APP_API_URL ?? '');

function toNumber(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : 0;
}

function winnerLabel(winner) {
  if (winner === 'hc_lombardo_ai') return 'HC Lombardo AI';
  if (winner === 'vegas_ai') return 'Vegas AI';
  if (winner === 'push') return 'Push';
  return 'Tie';
}

function winnerTone(winner) {
  if (winner === 'hc_lombardo_ai') return 'winner-ai';
  if (winner === 'vegas_ai') return 'winner-vegas';
  if (winner === 'push') return 'winner-push';
  return 'winner-tie';
}

function resultPillClass(result) {
  if (result === 'win' || result === 'right') return 'result-pill win';
  if (result === 'loss' || result === 'wrong') return 'result-pill loss';
  return 'result-pill push';
}

function formatPct(value) {
  return `${toNumber(value).toFixed(1)}%`;
}

function formatSpread(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return 'N/A';
  return `${n > 0 ? '+' : ''}${n.toFixed(1)}`;
}

function ModelPerformance() {
  const defaultSeason = getDefaultSeason();
  const fallbackSeasonOptions = useMemo(() => {
    const years = [];
    for (let year = defaultSeason; year >= 2020; year -= 1) {
      years.push(year);
    }
    return years;
  }, [defaultSeason]);

  const [seasonOptions, setSeasonOptions] = useState([]);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const [selectedSeason, setSelectedSeason] = useState(defaultSeason);
  const [selectedWeek, setSelectedWeek] = useState(null);
  const [scoreboard, setScoreboard] = useState(null);

  const fetchScoreboard = async () => {
    setRefreshing(true);
    try {
      const response = await fetch(`${API_URL}/api/ml/ai-vs-vegas-scoreboard/${selectedSeason}`);
      const data = await response.json();
      if (!data.success) {
        setError(data.error || 'Could not load scoreboard data.');
        setLoading(false);
        return;
      }

      setScoreboard(data);
      const weeks = data?.weekly || [];
      if (weeks.length > 0) {
        const maxWeek = Math.max(...weeks.map((w) => toNumber(w.week)));
        setSelectedWeek(maxWeek);
      } else {
        setSelectedWeek(null);
      }

      setLastUpdated(new Date());
      setError(null);
      setLoading(false);
    } catch (err) {
      setError('Unable to connect right now. Please retry.');
      setLoading(false);
    } finally {
      setRefreshing(false);
    }
  };

  const fetchSeasonOptions = async () => {
    try {
      const response = await fetch(`${API_URL}/api/ml/ai-vs-vegas-seasons`);
      const data = await response.json();
      if (!data.success) {
        return;
      }

      const seasons = (data.seasons || []).map((row) => Number(row.season)).filter(Number.isFinite);
      const sortedSeasons = [...new Set(seasons)].sort((a, b) => b - a);
      if (sortedSeasons.length > 0) {
        setSeasonOptions(sortedSeasons);
        if (!sortedSeasons.includes(selectedSeason)) {
          setSelectedSeason(sortedSeasons[0]);
        }
      }
    } catch (err) {
      // Keep current fallback if season list endpoint is unavailable.
    }
  };

  useEffect(() => {
    fetchSeasonOptions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    fetchScoreboard();
    return undefined;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedSeason]);

  const weeklyRows = useMemo(() => (scoreboard?.weekly || []), [scoreboard]);
  const weekOptions = weeklyRows.map((row) => toNumber(row.week)).sort((a, b) => a - b);
  const weeklyCards = useMemo(() => (
    [...weeklyRows].sort((a, b) => toNumber(a.week) - toNumber(b.week))
  ), [weeklyRows]);

  const selectedWeekRow = useMemo(() => (
    weeklyRows.find((row) => toNumber(row.week) === toNumber(selectedWeek)) || null
  ), [weeklyRows, selectedWeek]);

  const seasonSummary = scoreboard?.season_summary || {};
  const seasonWinner = winnerLabel(seasonSummary?.season_winner);
  const gameRows = scoreboard?.games || [];

  const displaySeasonOptions = seasonOptions.length > 0 ? seasonOptions : fallbackSeasonOptions;

  const formatLastUpdated = () => {
    if (!lastUpdated) return 'Waiting for first update';
    return `Last updated ${lastUpdated.toLocaleTimeString()}`;
  };

  if (loading) {
    return (
      <div className="model-performance-page">
        <div className="mp-loading-state">
          <div className="mp-spinner"></div>
          <p>Loading bettor scoreboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="model-performance-page">
        <div className="mp-error-state">
          <span className="mp-error-icon">!</span>
          <p>{error}</p>
          <button onClick={fetchScoreboard} className="mp-retry-button">Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="model-performance-page">
      <div className="mp-header">
        <h1>Should You Follow HC Lombardo AI Or Vegas AI?</h1>
        <p className="mp-subtitle">Season scoreboard and week-by-week winner tracker.</p>
      </div>

      <div className="mp-controls-bar">
        <div className="mp-select-group">
          <label htmlFor="model-season-select">Season</label>
          <select
            id="model-season-select"
            value={selectedSeason}
            onChange={(e) => setSelectedSeason(toNumber(e.target.value))}
          >
            {displaySeasonOptions.map((season) => (
              <option key={season} value={season}>{season}</option>
            ))}
          </select>
        </div>

        <div className="mp-select-group">
          <label htmlFor="model-week-select">Week</label>
          <select
            id="model-week-select"
            value={selectedWeek || ''}
            onChange={(e) => setSelectedWeek(toNumber(e.target.value))}
            disabled={weekOptions.length === 0}
          >
            {weekOptions.length === 0 && <option value="">No weeks available</option>}
            {weekOptions.map((week) => (
              <option key={week} value={week}>Week {week}</option>
            ))}
          </select>
        </div>

        <div className="mp-actions-group">
          <button
            className="mp-refresh-button"
            type="button"
            onClick={fetchScoreboard}
            disabled={refreshing}
          >
            {refreshing ? 'Refreshing...' : 'Refresh Now'}
          </button>
        </div>
      </div>

      <div className="mp-live-row">
        <div className="mp-live-text">Updates every 10 seconds | {formatLastUpdated()}</div>
        <div className="mp-live-meta">Season sample: {toNumber(seasonSummary.games)} games</div>
      </div>

      <section className="mp-summary-section">
        <div className="mp-section-heading">
          <h2>Season Verdict ({selectedSeason})</h2>
          <p className="mp-section-subtitle">AI-vs-Vegas scoreboard using ATS results from completed games.</p>
        </div>
        <p className="mp-verdict-line">
          <strong>{seasonSummary.verdict_text || seasonWinner}</strong>
        </p>
        <p className="mp-proof-line">{seasonSummary.proof_line || 'No data for this season yet.'}</p>

        <div className="mp-summary-grid">
          <div className="mp-insight-card highlight">
            <h3>Season Winner</h3>
            <div className="mp-insight-content">
              <div className="mp-stat-large">{seasonWinner}</div>
              <div className="mp-stat-label">AI-vs-Vegas verdict</div>
              <div className="mp-stat-detail">{seasonSummary.scoreline || 'No scoreline yet'}</div>
            </div>
          </div>
          <div className="mp-insight-card">
            <h3>AI ATS Covers</h3>
            <div className="mp-insight-content">
              <div className="mp-stat-large">{toNumber(seasonSummary.ai_wins)}</div>
              <div className="mp-stat-label">Against the spread wins</div>
              <div className="mp-stat-detail">{formatPct(seasonSummary.ai_pct)}</div>
            </div>
          </div>
          <div className="mp-insight-card">
            <h3>Vegas ATS Covers</h3>
            <div className="mp-insight-content">
              <div className="mp-stat-large">{toNumber(seasonSummary.vegas_wins)}</div>
              <div className="mp-stat-label">Against the spread wins</div>
              <div className="mp-stat-detail">{formatPct(seasonSummary.vegas_pct)}</div>
            </div>
          </div>
          <div className="mp-insight-card">
            <h3>True ATS Pushes</h3>
            <div className="mp-insight-content">
              <div className="mp-stat-large">{toNumber(seasonSummary.pushes)}</div>
              <div className="mp-stat-label">Line landed exactly</div>
              <div className="mp-stat-detail">No winner for those games</div>
            </div>
          </div>
          <div className="mp-insight-card">
            <h3>Total Games</h3>
            <div className="mp-insight-content">
              <div className="mp-stat-large">{toNumber(seasonSummary.games)}</div>
              <div className="mp-stat-label">Full played sample</div>
              <div className="mp-stat-detail">Completed regular-season/postseason games</div>
            </div>
          </div>
        </div>
      </section>

      <section className="mp-weekly-section">
        <div className="mp-section-heading">
          <h2>Week-By-Week Winner</h2>
          <p className="mp-section-subtitle">Scannable weekly cards show who won each week: HC Lombardo AI, Vegas AI, or Push.</p>
        </div>

        {selectedWeekRow ? (
          <div className="mp-summary-grid compact">
            <div className={`mp-insight-card ${winnerTone(selectedWeekRow.week_winner)}`}>
              <h3>Week {selectedWeekRow.week} Winner</h3>
              <div className="mp-insight-content">
                <div className="mp-stat-large">{winnerLabel(selectedWeekRow.week_winner)}</div>
                <div className="mp-stat-label">Weekly AI-vs-Vegas verdict</div>
                <div className="mp-stat-detail">{selectedWeekRow.scoreline || 'No scoreline yet'}</div>
              </div>
            </div>
            <div className="mp-insight-card">
              <h3>AI ATS Covers</h3>
              <div className="mp-insight-content">
                <div className="mp-stat-large">{toNumber(selectedWeekRow.ai_wins)}</div>
                <div className="mp-stat-label">Against the spread wins</div>
                <div className="mp-stat-detail">{formatPct(selectedWeekRow.ai_pct)}</div>
              </div>
            </div>
            <div className="mp-insight-card">
              <h3>Vegas ATS Covers</h3>
              <div className="mp-insight-content">
                <div className="mp-stat-large">{toNumber(selectedWeekRow.vegas_wins)}</div>
                <div className="mp-stat-label">Against the spread wins</div>
                <div className="mp-stat-detail">{formatPct(selectedWeekRow.vegas_pct)}</div>
              </div>
            </div>
            <div className="mp-insight-card">
              <h3>True ATS Pushes</h3>
              <div className="mp-insight-content">
                <div className="mp-stat-large">{toNumber(selectedWeekRow.pushes)}</div>
                <div className="mp-stat-label">Line landed exactly</div>
                <div className="mp-stat-detail">Push outcomes this week</div>
              </div>
            </div>
          </div>
        ) : (
          <p className="mp-empty-copy">No weekly rows available for this season yet.</p>
        )}

        <div className="mp-week-grid">
          {weeklyCards.map((row) => {
            const week = toNumber(row.week);
            const isActive = toNumber(selectedWeek) === week;
            return (
              <button
                key={week}
                className={`mp-week-card ${winnerTone(row.week_winner)} ${isActive ? 'active' : ''}`}
                onClick={() => setSelectedWeek(week)}
                type="button"
              >
                <div className="mp-week-card-top">
                  <span className="mp-week-chip">Week {week}</span>
                  <span className="mp-week-scoreline">{row.scoreline || 'No scoreline yet'}</span>
                </div>
                <div className="mp-week-winner">{winnerLabel(row.week_winner)}</div>
                <div className="mp-week-meta">
                  AI {toNumber(row.ai_wins)} ({formatPct(row.ai_pct)}) vs Vegas {toNumber(row.vegas_wins)} ({formatPct(row.vegas_pct)})
                </div>
              </button>
            );
          })}
        </div>
      </section>

      <section className="mp-games-section">
        <h3>Season Game-By-Game Results</h3>
        <p className="mp-games-subtitle">
          ATS outcomes use independent AI and Vegas cover results. Push means the game landed exactly on the line.
        </p>

        {gameRows.length > 0 ? (
          <div className="mp-games-table-wrapper">
            <table className="mp-games-table">
              <thead>
                <tr>
                  <th>Week</th>
                  <th>Game</th>
                  <th>Final Score</th>
                  <th>Vegas Closing Spread</th>
                  <th>AI ATS Pick</th>
                  <th>AI Result</th>
                  <th>Vegas ATS Pick</th>
                  <th>Vegas Result</th>
                  <th>Winner</th>
                </tr>
              </thead>
              <tbody>
                {gameRows.map((g) => (
                  <tr key={g.game_id}>
                    <td>{toNumber(g.week)}</td>
                    <td>{g.matchup}</td>
                    <td>{g.final_score}</td>
                    <td>{formatSpread(g.vegas_closing_spread ?? g.vegas_spread)}</td>
                    <td>{g.ai_pick_team || 'No edge'}</td>
                    <td><span className={resultPillClass(g.ai_result)}>{String(g.ai_result || 'push').toUpperCase()}</span></td>
                    <td>{g.vegas_pick_team || 'No edge'}</td>
                    <td><span className={resultPillClass(g.vegas_result)}>{String(g.vegas_result || 'push').toUpperCase()}</span></td>
                    <td><span className={resultPillClass(g.winner === 'hc_lombardo_ai' ? 'win' : (g.winner === 'vegas_ai' ? 'loss' : 'push'))}>{winnerLabel(g.winner)}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="mp-empty-copy">No game rows available for this season.</p>
        )}
      </section>

      <div className="mp-last-updated">
        Last updated: {new Date().toLocaleTimeString()}
        <span className="mp-auto-refresh">| Auto-refreshes every 30 seconds</span>
      </div>
    </div>
  );
}

export default ModelPerformance;
