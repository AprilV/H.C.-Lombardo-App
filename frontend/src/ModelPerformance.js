import React, { useEffect, useMemo, useState } from 'react';
import './ModelPerformance.css';
import { getDefaultSeason, getRecentSeasons } from './utils/season';

const API_URL = (typeof window !== 'undefined' && (window.location.hostname === 'hclombardo.com' || window.location.hostname === 'www.hclombardo.com' || window.location.hostname.endsWith('.netlify.app'))) ? '' : (process.env.REACT_APP_API_URL ?? '');
const CUSTOMER_SEASONS = [2020, 2021, 2022, 2023, 2024, 2025];
const STANDARD_WIN_PER_UNIT_RISKED = 100 / 110;
const BREAK_EVEN_WIN_RATE_PCT = (110 / 210) * 100;

function toNumber(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : 0;
}

function formatPct(value) {
  return `${toNumber(value).toFixed(1)}%`;
}

function normalizeSeasonRow(rawRow, season) {
  const aiWins = toNumber(rawRow?.ai_wins);
  const vegasWins = toNumber(rawRow?.vegas_wins);
  const pushes = toNumber(rawRow?.ties);
  const totalGames = toNumber(rawRow?.total_games);
  const decidedGames = aiWins + vegasWins;
  const aiPct = decidedGames > 0 ? (aiWins / decidedGames) * 100 : 0;
  const vegasPct = decidedGames > 0 ? (vegasWins / decidedGames) * 100 : 0;
  const edgePp = aiPct - vegasPct;
  const netUnits = (aiWins * STANDARD_WIN_PER_UNIT_RISKED) - vegasWins;
  const roiPct = decidedGames > 0 ? (netUnits / decidedGames) * 100 : 0;

  return {
    season,
    hasData: Boolean(rawRow?.success && totalGames > 0),
    aiWins,
    vegasWins,
    pushes,
    totalGames,
    decidedGames,
    aiPct,
    vegasPct,
    edgePp,
    netUnits,
    roiPct,
    vegasSource: rawRow?.vegas_spread_source || '',
    dataSource: rawRow?.data_source || ''
  };
}

function sourceLabel(sourceValue) {
  const source = String(sourceValue || '').toLowerCase();
  if (source.includes('closing_spread')) {
    return 'We use the closing betting line first. If missing, we use the stored game line, then the schedule line.';
  }
  if (source.includes('prediction_vegas_spread')) {
    return 'We use the stored game line first, then the schedule line.';
  }
  if (source.includes('spread_line')) {
    return 'We use the schedule spread line.';
  }
  return 'Line source details are not available right now.';
}

function dataSourceLabel(sourceValue) {
  const source = String(sourceValue || '').toLowerCase();
  if (source.includes('strict_pregame')) {
    return 'Only picks saved before kickoff are counted.';
  }
  if (source.includes('legacy_relaxed_pregame')) {
    return 'Older season records were used because full kickoff-time records were not available.';
  }
  if (source.includes('simulated_historical')) {
    return 'Backup season records were used because tracked rows were missing.';
  }
  if (source.includes('tracked_rows')) {
    return 'Tracked season rows were used.';
  }
  return 'Pick timing details are not available right now.';
}

function ModelPerformance() {
  const defaultSeason = getDefaultSeason();
  const seasonOptions = getRecentSeasons(6, 1999, defaultSeason);

  const [performanceData, setPerformanceData] = useState(null);
  const [seasonVsVegas, setSeasonVsVegas] = useState(null);
  const [seasonRows, setSeasonRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [error, setError] = useState(null);
  const [selectedSeason, setSelectedSeason] = useState(defaultSeason);

  useEffect(() => {
    fetchPerformance();
    return undefined;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedSeason]);

  const fetchPerformanceForSeason = async (season) => {
    const response = await fetch(`${API_URL}/api/ml/performance-stats?season=${season}&include_trend=false&include_coverage_contract=false&include_integrity=false&allow_simulated_recompute=false`);
    return response.json();
  };

  const fetchSeasonVsVegas = async (season) => {
    const response = await fetch(`${API_URL}/api/ml/season-ai-vs-vegas/${season}?allow_simulated_fallback=false`);
    return response.json();
  };

  const fetchPerformance = async () => {
    setRefreshing(true);
    try {
      const [data, multiSeasonRaw] = await Promise.all([
        fetchPerformanceForSeason(selectedSeason),
        Promise.all(CUSTOMER_SEASONS.map((season) => fetchSeasonVsVegas(season)))
      ]);

      const normalizedSeasonRows = CUSTOMER_SEASONS.map((season, index) => normalizeSeasonRow(multiSeasonRaw[index], season));
      setSeasonRows(normalizedSeasonRows);

      if (!data.success) {
        setError(data.error || 'Failed to load customer performance data.');
        setLoading(false);
        return;
      }

      setPerformanceData(data);

      const spreadH2h = data?.model_breakdown?.spread_h2h;
      const selectedFromSeasonTable = normalizedSeasonRows.find((row) => row.season === selectedSeason && row.hasData);

      if (spreadH2h && toNumber(spreadH2h.total_games) > 0) {
        setSeasonVsVegas(normalizeSeasonRow({
          success: true,
          ai_wins: spreadH2h.ai_wins,
          vegas_wins: spreadH2h.vegas_wins,
          ties: spreadH2h.ties,
          total_games: spreadH2h.total_games,
          vegas_spread_source: spreadH2h.vegas_spread_source,
          data_source: spreadH2h.data_source
        }, selectedSeason));
      } else if (selectedFromSeasonTable) {
        setSeasonVsVegas(selectedFromSeasonTable);
      } else {
        setSeasonVsVegas(normalizeSeasonRow({ success: false }, selectedSeason));
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

  const formatLastUpdated = () => {
    if (!lastUpdated) {
      return 'Waiting for first update';
    }
    return `Last updated ${lastUpdated.toLocaleTimeString()}`;
  };

  const modelBreakdown = performanceData?.model_breakdown || {};
  const xgbSummary = modelBreakdown?.xgb || {};
  const eloSummary = modelBreakdown?.elo || {};
  const xgbScored = toNumber(xgbSummary?.scored_games);
  const eloScored = toNumber(eloSummary?.scored_games);
  const primarySummary = eloScored > xgbScored ? eloSummary : xgbSummary;
  const winnerAccuracy = toNumber(primarySummary?.win_accuracy);
  const winnerCorrect = toNumber(primarySummary?.correct_predictions);
  const winnerScored = toNumber(primarySummary?.scored_games);

  const hasAtsData = Boolean(seasonVsVegas?.hasData && toNumber(seasonVsVegas?.totalGames) > 0);
  const aiWins = hasAtsData ? toNumber(seasonVsVegas.aiWins) : 0;
  const vegasWins = hasAtsData ? toNumber(seasonVsVegas.vegasWins) : 0;
  const pushes = hasAtsData ? toNumber(seasonVsVegas.pushes) : 0;
  const totalGames = hasAtsData ? toNumber(seasonVsVegas.totalGames) : 0;
  const decidedGames = hasAtsData ? toNumber(seasonVsVegas.decidedGames) : 0;
  const aiPct = hasAtsData ? toNumber(seasonVsVegas.aiPct) : 0;
  const vegasPct = hasAtsData ? toNumber(seasonVsVegas.vegasPct) : 0;
  const edgePp = hasAtsData ? toNumber(seasonVsVegas.edgePp) : 0;
  const netUnits = hasAtsData ? toNumber(seasonVsVegas.netUnits) : 0;
  const roiPct = hasAtsData ? toNumber(seasonVsVegas.roiPct) : 0;
  const vegasNetUnits = hasAtsData ? ((vegasWins * STANDARD_WIN_PER_UNIT_RISKED) - aiWins) : 0;
  const vegasRoiPct = hasAtsData && decidedGames > 0 ? (vegasNetUnits / decidedGames) * 100 : 0;
  const netDifference = hasAtsData ? (netUnits - vegasNetUnits) : 0;

  const selectedSeasonRow = useMemo(() => (
    seasonRows.find((row) => row.season === selectedSeason)
  ), [seasonRows, selectedSeason]);

  if (loading) {
    return (
      <div className="performance-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading customer performance page...</p>
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
          <button onClick={fetchPerformance} className="retry-button">Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="performance-container">
      <div className="season-selector-container">
        <h2 className="page-title">HC Lombardo AI vs Vegas AI</h2>
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
          <div className="live-status-text">
            Updates every 10 seconds | {formatLastUpdated()}
          </div>
          <button
            className="refresh-now-btn"
            type="button"
            onClick={fetchPerformance}
            disabled={refreshing}
          >
            {refreshing ? 'Refreshing...' : 'Refresh Now'}
          </button>
        </div>
      </div>

      <div className="vegas-hero">
        <h2 className="hero-title">{selectedSeason} Season: HC Lombardo AI vs Vegas AI</h2>
        <p className="season-trend-subtitle">
          Win rates below use games with a winner only. No Winner (Push) games are shown separately.
        </p>
        <div className="hero-comparison">
          <div className="comparison-side ai-side">
            <div className="side-label">HC Lombardo AI</div>
            <div className="side-number ai-number">{hasAtsData ? formatPct(aiPct) : 'N/A'}</div>
            <div className="side-detail">Wins: {aiWins} | Games With Winner: {decidedGames}</div>
            <div className="side-tier">Game winner picks: {formatPct(winnerAccuracy)} ({winnerCorrect}/{winnerScored})</div>
          </div>

          <div className="comparison-middle">
            <div className={`delta-badge ${hasAtsData && edgePp >= 0 ? 'beating' : 'below'}`}>
              <div className="delta-number">{hasAtsData ? `${edgePp >= 0 ? '+' : ''}${edgePp.toFixed(1)}` : 'N/A'}</div>
              <div className="delta-label">HC LOMBARDO AI LEAD</div>
            </div>
            {hasAtsData && decidedGames < 30 && (
              <div className="winning-streak">Small sample: {decidedGames} games with a winner</div>
            )}
          </div>

          <div className="comparison-side vegas-side">
            <div className="side-label">Vegas AI</div>
            <div className="side-number vegas-number">{hasAtsData ? formatPct(vegasPct) : 'N/A'}</div>
            <div className="side-detail">Wins: {vegasWins} | No Winner (Push): {pushes}</div>
            <div className="side-tier">Compared games: {totalGames}</div>
          </div>
        </div>
      </div>

      <div className="customer-answer-section">
        <h3>Quick Customer Answer</h3>
        {hasAtsData ? (
          <>
            <p className="customer-answer-text">
              {netUnits >= 0
                ? `If you followed HC Lombardo AI this season, you would be up ${netUnits.toFixed(2)} units so far.`
                : `If you followed HC Lombardo AI this season, you would be down ${Math.abs(netUnits).toFixed(2)} units so far.`}
            </p>
            <div className="customer-answer-grid">
              <div className="customer-answer-card">
                <h4>HC Lombardo AI Result</h4>
                <p className="customer-answer-value">{netUnits >= 0 ? '+' : ''}{netUnits.toFixed(2)} units</p>
                <p className="customer-answer-detail">Return: {formatPct(roiPct)}</p>
              </div>
              <div className="customer-answer-card">
                <h4>Vegas AI Result</h4>
                <p className="customer-answer-value">{vegasNetUnits >= 0 ? '+' : ''}{vegasNetUnits.toFixed(2)} units</p>
                <p className="customer-answer-detail">Return: {formatPct(vegasRoiPct)}</p>
              </div>
              <div className="customer-answer-card">
                <h4>Bottom Line</h4>
                <p className="customer-answer-value">{netDifference >= 0 ? '+' : ''}{netDifference.toFixed(2)} units</p>
                <p className="customer-answer-detail">HC Lombardo AI minus Vegas AI</p>
              </div>
            </div>
          </>
        ) : (
          <p className="customer-answer-text">
            Not enough game results are available yet for a clear customer answer.
          </p>
        )}
      </div>

      <div className="quick-stats">
        <div className="quick-stat">
          <div className="stat-value-big">{totalGames}</div>
          <div className="stat-label-small">Compared Games</div>
        </div>
        <div className="quick-stat">
          <div className="stat-value-big">{decidedGames}</div>
          <div className="stat-label-small">Games With Winner</div>
        </div>
        <div className="quick-stat">
          <div className="stat-value-big">{aiWins}</div>
          <div className="stat-label-small">HC Lombardo AI Wins</div>
        </div>
        <div className="quick-stat">
          <div className="stat-value-big">{pushes}</div>
          <div className="stat-label-small">No Winner (Push)</div>
        </div>
      </div>

      <div className="performance-insights">
        <h3>How To Read This Page</h3>
        <div className="insights-grid">
          <div className="insight-card">
            <div className="insight-content">
              <h4>Win Rate</h4>
              <p>Win rate uses games with a winner only. Pushes are not counted as wins or losses.</p>
            </div>
          </div>
          <div className="insight-card">
            <div className="insight-content">
              <h4>Edge</h4>
              <p>Edge is the HC Lombardo AI win rate minus the Vegas AI win rate.</p>
            </div>
          </div>
          <div className="insight-card">
            <div className="insight-content">
              <h4>Sample Size</h4>
              <p>Larger decided game counts usually mean more stable results.</p>
            </div>
          </div>
        </div>
      </div>

      <div className="season-table-section">
        <h3>2020-2025 Season Results</h3>
        <p className="season-trend-subtitle">
          Customer view: HC Lombardo AI and Vegas AI compared season by season.
        </p>
        <div className="season-table-wrapper">
          <table className="season-results-table">
            <thead>
              <tr>
                <th>Season</th>
                <th>HC Lombardo AI Win Rate</th>
                <th>Vegas AI Win Rate</th>
                <th>HC Lombardo AI Edge</th>
                <th>Games With Winner</th>
                <th>No Winner (Push)</th>
                <th>Win/Loss Units</th>
                <th>Return %</th>
              </tr>
            </thead>
            <tbody>
              {CUSTOMER_SEASONS.map((season) => {
                const row = seasonRows.find((r) => r.season === season) || normalizeSeasonRow({ success: false }, season);
                return (
                  <tr key={season}>
                    <td>{season}</td>
                    <td>{row.hasData ? formatPct(row.aiPct) : 'N/A'}</td>
                    <td>{row.hasData ? formatPct(row.vegasPct) : 'N/A'}</td>
                    <td className={row.edgePp >= 0 ? 'positive-cell' : 'negative-cell'}>
                      {row.hasData ? `${row.edgePp >= 0 ? '+' : ''}${row.edgePp.toFixed(1)} pts` : 'N/A'}
                    </td>
                    <td>{row.decidedGames}</td>
                    <td>{row.pushes}</td>
                    <td>{row.hasData ? `${row.netUnits >= 0 ? '+' : ''}${row.netUnits.toFixed(2)}` : 'N/A'}</td>
                    <td>{row.hasData ? formatPct(row.roiPct) : 'N/A'}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      <div className="performance-insights">
        <h3>If You Bet Every Game (Selected Season)</h3>
        <div className="insights-grid">
          <div className="insight-card">
            <div className="insight-content">
              <h4>Simple Bet Example</h4>
              <p>
                If you bet 1 unit on HC Lombardo AI each game with a winner: {hasAtsData ? `${netUnits >= 0 ? '+' : ''}${netUnits.toFixed(2)} units` : 'N/A'}.
              </p>
            </div>
          </div>
          <div className="insight-card">
            <div className="insight-content">
              <h4>Return</h4>
              <p>
                Selected season return: {hasAtsData ? formatPct(roiPct) : 'N/A'}.
              </p>
            </div>
          </div>
          <div className="insight-card">
            <div className="insight-content">
              <h4>Break-Even Point</h4>
              <p>
                At standard odds, you usually need about {BREAK_EVEN_WIN_RATE_PCT.toFixed(1)}% wins to break even.
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="performance-insights">
        <h3>Where The Numbers Come From</h3>
        <div className="insights-grid">
          <div className="insight-card">
            <div className="insight-content">
              <h4>Which Betting Line We Use</h4>
              <p>{sourceLabel(seasonVsVegas?.vegasSource)}</p>
            </div>
          </div>
          <div className="insight-card">
            <div className="insight-content">
              <h4>When Picks Are Counted</h4>
              <p>{dataSourceLabel(seasonVsVegas?.dataSource)}</p>
            </div>
          </div>
          <div className="insight-card">
            <div className="insight-content">
              <h4>Selected Season Snapshot</h4>
              <p>
                {selectedSeasonRow?.hasData
                  ? `${selectedSeason}: ${selectedSeasonRow.decidedGames} games with a winner, ${selectedSeasonRow.pushes} No Winner (Push).`
                  : `${selectedSeason}: no season comparison rows available.`}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="last-updated">
        Last updated: {new Date().toLocaleTimeString()}
        <span className="auto-refresh">| Auto-refreshes every 30 seconds</span>
      </div>
    </div>
  );
}

export default ModelPerformance;
