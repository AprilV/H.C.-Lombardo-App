import React, { useEffect, useMemo, useState } from 'react';
import './ModelPerformance.css';
import { getDefaultSeason, getRecentSeasons } from './utils/season';

const API_URL = (typeof window !== 'undefined' && (window.location.hostname === 'hclombardo.com' || window.location.hostname === 'www.hclombardo.com' || window.location.hostname.endsWith('.netlify.app'))) ? '' : (process.env.REACT_APP_API_URL ?? '');

function toNumber(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : 0;
}

function winnerLabel(winner) {
  if (winner === 'hc_lombardo_ai') return 'HC Lombardo AI';
  if (winner === 'vegas_ai') return 'Vegas AI';
  return 'Tie';
}

function resultPillClass(result) {
  if (result === 'right') return 'result-pill right';
  if (result === 'wrong') return 'result-pill wrong';
  return 'result-pill push';
}

function formatPct(value) {
  return `${toNumber(value).toFixed(1)}%`;
}

function ModelPerformance() {
  const defaultSeason = getDefaultSeason();
  const seasonOptions = getRecentSeasons(25, 1999, defaultSeason);

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
          {seasonOptions.map((season) => (
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
        <h3>Season Winner ({selectedSeason})</h3>
        <p className="customer-answer-text">
          Best chance so far: <strong>{seasonWinner}</strong>
        </p>
        <div className="customer-answer-grid">
          <div className="customer-answer-card">
            <h4>HC Lombardo AI Right</h4>
            <p className="customer-answer-value">{toNumber(seasonSummary.ai_right)}</p>
            <p className="customer-answer-detail">{formatPct(seasonSummary.ai_pct)}</p>
          </div>
          <div className="customer-answer-card">
            <h4>Vegas AI Right</h4>
            <p className="customer-answer-value">{toNumber(seasonSummary.vegas_right)}</p>
            <p className="customer-answer-detail">{formatPct(seasonSummary.vegas_pct)}</p>
          </div>
          <div className="customer-answer-card">
            <h4>No Winner (Push)</h4>
            <p className="customer-answer-value">{toNumber(seasonSummary.pushes)}</p>
            <p className="customer-answer-detail">Games with no side winner</p>
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
                Week {week}: {wWinner}
              </button>
            );
          })}
        </div>

        {selectedWeekRow ? (
          <div className="customer-answer-grid" style={{ marginTop: 14 }}>
            <div className="customer-answer-card">
              <h4>Week {selectedWeekRow.week} Winner</h4>
              <p className="customer-answer-value">{winnerLabel(selectedWeekRow.week_winner)}</p>
              <p className="customer-answer-detail">Best chance this week</p>
            </div>
            <div className="customer-answer-card">
              <h4>HC Lombardo AI Right</h4>
              <p className="customer-answer-value">{toNumber(selectedWeekRow.ai_right)}</p>
              <p className="customer-answer-detail">{formatPct(selectedWeekRow.ai_pct)}</p>
            </div>
            <div className="customer-answer-card">
              <h4>Vegas AI Right</h4>
              <p className="customer-answer-value">{toNumber(selectedWeekRow.vegas_right)}</p>
              <p className="customer-answer-detail">{formatPct(selectedWeekRow.vegas_pct)}</p>
            </div>
          </div>
        ) : (
          <p className="customer-answer-text">No weekly rows available for this season yet.</p>
        )}
      </div>

      <div className="season-table-section">
        <h3>Week {selectedWeek || 'N/A'} Game Results</h3>
        <p className="season-trend-subtitle">
          Each game shows whether HC Lombardo AI was right or wrong compared to Vegas AI.
        </p>

        {selectedWeekRow && selectedWeekRow.details && selectedWeekRow.details.length > 0 ? (
          <div className="season-table-wrapper">
            <table className="season-results-table">
              <thead>
                <tr>
                  <th>Game</th>
                  <th>Final Score</th>
                  <th>HC Lombardo AI Pick Line</th>
                  <th>Vegas AI Line</th>
                  <th>HC Lombardo AI</th>
                  <th>Vegas AI</th>
                  <th>Winner</th>
                </tr>
              </thead>
              <tbody>
                {selectedWeekRow.details.map((g) => (
                  <tr key={g.game_id}>
                    <td>{g.away_team} @ {g.home_team}</td>
                    <td>{toNumber(g.away_score)} - {toNumber(g.home_score)}</td>
                    <td>{g.ai_spread}</td>
                    <td>{g.vegas_spread}</td>
                    <td><span className={resultPillClass(g.ai_result)}>{String(g.ai_result || '').toUpperCase()}</span></td>
                    <td><span className={resultPillClass(g.vegas_result)}>{String(g.vegas_result || '').toUpperCase()}</span></td>
                    <td>{winnerLabel(g.winner)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="customer-answer-text">No game rows available for this week.</p>
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
