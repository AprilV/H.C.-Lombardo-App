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
      <div className="performance-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading bettor scoreboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="performance-container">
        <div className="error-message">
          <span className="error-icon">!</span>
          <p>{error}</p>
          <button onClick={fetchScoreboard} className="retry-button">Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="performance-container">
      <div className="season-selector-container">
        <h2 className="page-title">Should You Follow HC Lombardo AI Or Vegas AI?</h2>
        <div className="season-selector">
          {displaySeasonOptions.map((season) => (
            <button
              key={season}
              className={`season-btn ${selectedSeason === season ? 'active' : ''}`}
              onClick={() => setSelectedSeason(season)}
            >
              {season} Season
            </button>
          ))}
        </div>
        <div className="live-status-row">
          <div className="live-status-text">Updates every 10 seconds | {formatLastUpdated()}</div>
          <button
            className="refresh-now-btn"
            type="button"
            onClick={fetchScoreboard}
            disabled={refreshing}
          >
            {refreshing ? 'Refreshing...' : 'Refresh Now'}
          </button>
        </div>
      </div>

      <div className="customer-answer-section">
        <h3>Season Verdict ({selectedSeason})</h3>
        <p className="customer-answer-text">
          <strong>{seasonSummary.verdict_text || seasonWinner}</strong>
        </p>
        <p className="customer-answer-text">{seasonSummary.proof_line || 'No data for this season yet.'}</p>
        <div className="customer-answer-grid">
          <div className="customer-answer-card">
            <h4>AI ATS Wins</h4>
            <p className="customer-answer-value">{toNumber(seasonSummary.ai_wins)}</p>
            <p className="customer-answer-detail">{formatPct(seasonSummary.ai_pct)}</p>
          </div>
          <div className="customer-answer-card">
            <h4>Vegas ATS Wins</h4>
            <p className="customer-answer-value">{toNumber(seasonSummary.vegas_wins)}</p>
            <p className="customer-answer-detail">{formatPct(seasonSummary.vegas_pct)}</p>
          </div>
          <div className="customer-answer-card">
            <h4>Pushes</h4>
            <p className="customer-answer-value">{toNumber(seasonSummary.pushes)}</p>
            <p className="customer-answer-detail">Shown, not counted for either side</p>
          </div>
          <div className="customer-answer-card">
            <h4>Total Games</h4>
            <p className="customer-answer-value">{toNumber(seasonSummary.games)}</p>
            <p className="customer-answer-detail">Full played sample</p>
          </div>
        </div>
      </div>

      <div className="performance-insights">
        <h3>Week-By-Week Winner</h3>
        <div className="season-selector">
          {weekOptions.map((week) => {
            const row = weeklyRows.find((w) => toNumber(w.week) === week);
            const wWinner = winnerLabel(row?.week_winner);
            return (
              <button
                key={week}
                className={`season-btn ${toNumber(selectedWeek) === week ? 'active' : ''}`}
                onClick={() => setSelectedWeek(week)}
              >
                Week {week}: {wWinner} ({row?.scoreline || 'No scoreline yet'})
              </button>
            );
          })}
        </div>

        {selectedWeekRow ? (
          <div className="customer-answer-grid" style={{ marginTop: 14 }}>
            <div className="customer-answer-card">
              <h4>Week {selectedWeekRow.week} Winner</h4>
              <p className="customer-answer-value">{winnerLabel(selectedWeekRow.week_winner)}</p>
              <p className="customer-answer-detail">{selectedWeekRow.scoreline}</p>
            </div>
            <div className="customer-answer-card">
              <h4>AI ATS Wins</h4>
              <p className="customer-answer-value">{toNumber(selectedWeekRow.ai_wins)}</p>
              <p className="customer-answer-detail">{formatPct(selectedWeekRow.ai_pct)}</p>
            </div>
            <div className="customer-answer-card">
              <h4>Vegas ATS Wins</h4>
              <p className="customer-answer-value">{toNumber(selectedWeekRow.vegas_wins)}</p>
              <p className="customer-answer-detail">{formatPct(selectedWeekRow.vegas_pct)}</p>
            </div>
            <div className="customer-answer-card">
              <h4>Pushes</h4>
              <p className="customer-answer-value">{toNumber(selectedWeekRow.pushes)}</p>
              <p className="customer-answer-detail">Week ties on error distance</p>
            </div>
          </div>
        ) : (
          <p className="customer-answer-text">No weekly rows available for this season yet.</p>
        )}
      </div>

      <div className="season-table-section">
        <h3>Season Game-By-Game Results</h3>
        <p className="season-trend-subtitle">
          ATS winner is determined by final score versus Vegas closing spread.
        </p>

        {gameRows.length > 0 ? (
          <div className="season-table-wrapper">
            <table className="season-results-table">
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
          <p className="customer-answer-text">No game rows available for this season.</p>
        )}
      </div>

      <div className="last-updated">
        Last updated: {new Date().toLocaleTimeString()}
        <span className="auto-refresh">| Auto-refreshes every 30 seconds</span>
      </div>
    </div>
  );
}

export default ModelPerformance;
