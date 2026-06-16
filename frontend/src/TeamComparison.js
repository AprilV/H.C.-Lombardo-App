import React, { useState, useEffect } from 'react';
import './TeamComparison.css';
import { getDefaultSeason, MIN_NFL_SEASON } from './utils/season';

const API_URL = (typeof window !== 'undefined' && (window.location.hostname === 'hclombardo.com' || window.location.hostname === 'www.hclombardo.com' || window.location.hostname.endsWith('.netlify.app'))) ? '' : (process.env.REACT_APP_API_URL ?? '');

// All available statistics organized by category
const STAT_CATEGORIES = {
  'Record': [
    { key: 'games_played', label: 'Games Played', format: 'int' },
    { key: 'wins', label: 'Wins', format: 'int' },
    { key: 'losses', label: 'Losses', format: 'int' },
    { key: 'home_wins', label: 'Home Wins', format: 'int' },
    { key: 'away_wins', label: 'Away Wins', format: 'int' },
  ],
  'Scoring': [
    { key: 'ppg', label: 'Points Per Game', format: 'decimal' },
    { key: 'total_points', label: 'Total Points', format: 'int' },
    { key: 'ppg_home', label: 'PPG (Home)', format: 'decimal' },
    { key: 'ppg_away', label: 'PPG (Away)', format: 'decimal' },
    { key: 'touchdowns_per_game', label: 'TDs/Game', format: 'decimal' },
    { key: 'fg_per_game', label: 'FGs/Game', format: 'decimal' },
    { key: 'fg_att_per_game', label: 'FG Attempts/Game', format: 'decimal' },
  ],
  'Offense': [
    { key: 'total_yards_per_game', label: 'Total Yards/Game', format: 'decimal' },
    { key: 'passing_yards_per_game', label: 'Passing Yards/Game', format: 'decimal' },
    { key: 'rushing_yards_per_game', label: 'Rushing Yards/Game', format: 'decimal' },
    { key: 'plays_per_game', label: 'Plays/Game', format: 'decimal' },
    { key: 'yards_per_play', label: 'Yards Per Play', format: 'decimal' },
  ],
  'Passing': [
    { key: 'completions_per_game', label: 'Completions/Game', format: 'decimal' },
    { key: 'passing_att_per_game', label: 'Pass Attempts/Game', format: 'decimal' },
    { key: 'completion_pct', label: 'Completion %', format: 'percent' },
    { key: 'passing_tds_per_game', label: 'Pass TDs/Game', format: 'decimal' },
    { key: 'interceptions_per_game', label: 'INTs/Game', format: 'decimal' },
    { key: 'sacks_taken_per_game', label: 'Sacks Taken/Game', format: 'decimal' },
    { key: 'sack_yards_lost_per_game', label: 'Sack Yards Lost/Game', format: 'decimal' },
    { key: 'qb_rating', label: 'QB Rating', format: 'decimal' },
  ],
  'Rushing': [
    { key: 'rushing_att_per_game', label: 'Rush Attempts/Game', format: 'decimal' },
    { key: 'yards_per_carry', label: 'Yards Per Carry', format: 'decimal' },
    { key: 'rushing_tds_per_game', label: 'Rush TDs/Game', format: 'decimal' },
  ],
  'Efficiency': [
    { key: 'third_down_pct', label: 'Third Down %', format: 'percent' },
    { key: 'fourth_down_pct', label: 'Fourth Down %', format: 'percent' },
    { key: 'red_zone_pct', label: 'Red Zone %', format: 'percent' },
    { key: 'time_of_possession_pct', label: 'Time of Possession %', format: 'percent' },
    { key: 'early_down_success_rate', label: 'Early Down Success %', format: 'percent' },
  ],
  'Special Teams': [
    { key: 'punts_per_game', label: 'Punts/Game', format: 'decimal' },
    { key: 'punt_avg_yards', label: 'Punt Average', format: 'decimal' },
    { key: 'kickoff_return_yards_per_game', label: 'KR Yards/Game', format: 'decimal' },
    { key: 'punt_return_yards_per_game', label: 'PR Yards/Game', format: 'decimal' },
  ],
  'Turnovers': [
    { key: 'total_turnovers', label: 'Total Turnovers', format: 'int' },
    { key: 'turnovers_per_game', label: 'Turnovers/Game', format: 'decimal' },
    { key: 'fumbles_lost_per_game', label: 'Fumbles Lost/Game', format: 'decimal' },
  ],
  'Penalties': [
    { key: 'penalties_per_game', label: 'Penalties/Game', format: 'decimal' },
    { key: 'penalty_yards_per_game', label: 'Penalty Yards/Game', format: 'decimal' },
  ],
  'Advanced': [
    { key: 'drives_per_game', label: 'Drives/Game', format: 'decimal' },
    { key: 'starting_field_pos_yds', label: 'Avg Starting Field Position', format: 'decimal' },
  ],
};

const VALID_VIEW_MODES = new Set(['comparison', 'head-to-head', 'schedule', 'edge']);

function TeamComparison({ initialViewMode = 'comparison' }) {
  const currentSeason = getDefaultSeason();
  const normalizedInitialView = VALID_VIEW_MODES.has(initialViewMode) ? initialViewMode : 'comparison';

  // View Mode
  const [viewMode, setViewMode] = useState(normalizedInitialView);
  
  // Team A state
  const [seasonA, setSeasonA] = useState(String(currentSeason));
  const [teamAList, setTeamAList] = useState([]);
  const [selectedTeamA, setSelectedTeamA] = useState('');
  const [teamAData, setTeamAData] = useState(null);
  const [teamAResolvedSeason, setTeamAResolvedSeason] = useState(null);
  const [teamASchedule, setTeamASchedule] = useState([]);
  const [teamASos, setTeamASos] = useState(null);
  
  // Team B state
  const [seasonB, setSeasonB] = useState(String(currentSeason));
  const [teamBList, setTeamBList] = useState([]);
  const [selectedTeamB, setSelectedTeamB] = useState('');
  const [teamBData, setTeamBData] = useState(null);
  const [teamBResolvedSeason, setTeamBResolvedSeason] = useState(null);
  const [teamBSchedule, setTeamBSchedule] = useState([]);
  const [teamBSos, setTeamBSos] = useState(null);
  
  // UI state
  const [selectedStats, setSelectedStats] = useState(new Set([
    'ppg', 'total_yards_per_game', 'passing_yards_per_game', 'rushing_yards_per_game',
    'completion_pct', 'qb_rating', 'third_down_pct', 'turnovers_per_game'
  ]));
  const [showStatPicker, setShowStatPicker] = useState(false);
  const [, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expandedGameA, setExpandedGameA] = useState(null);
  const [expandedGameB, setExpandedGameB] = useState(null);

  // Generate season years from oldest supported season through current default season.
  const seasons = [];
  for (let year = currentSeason; year >= MIN_NFL_SEASON; year--) {
    seasons.push(year);
  }

  // Load teams when season changes
  useEffect(() => {
    if (seasonA) loadTeamsA();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [seasonA]);

  useEffect(() => {
    if (seasonB) loadTeamsB();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [seasonB]);

  // Load team data when selection changes
  useEffect(() => {
    if (selectedTeamA && seasonA) {
      if (viewMode === 'schedule') {
        loadTeamSchedule('A', selectedTeamA, seasonA);
        loadTeamSos('A', selectedTeamA, seasonA);
      } else {
        loadTeamData('A', selectedTeamA, seasonA);
      }
    } else {
      setTeamAData(null);
      setTeamAResolvedSeason(null);
      setTeamASos(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedTeamA, seasonA, viewMode]);

  useEffect(() => {
    if (selectedTeamB && seasonB) {
      if (viewMode === 'schedule') {
        loadTeamSchedule('B', selectedTeamB, seasonB);
        loadTeamSos('B', selectedTeamB, seasonB);
      } else {
        loadTeamData('B', selectedTeamB, seasonB);
      }
    } else {
      setTeamBData(null);
      setTeamBResolvedSeason(null);
      setTeamBSos(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedTeamB, seasonB, viewMode]);

  useEffect(() => {
    if (VALID_VIEW_MODES.has(initialViewMode)) {
      setViewMode(initialViewMode);
    }
  }, [initialViewMode]);

  const loadTeamsA = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/hcl/teams?season=${seasonA}`);
      const data = await response.json();
      if (data.success) {
        setTeamAList(data.teams.sort((a, b) => a.team.localeCompare(b.team)));
        setError(null);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadTeamsB = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/hcl/teams?season=${seasonB}`);
      const data = await response.json();
      if (data.success) {
        setTeamBList(data.teams.sort((a, b) => a.team.localeCompare(b.team)));
        setError(null);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadTeamData = async (team, abbr, season) => {
    const setTeamDataState = (payload, resolvedSeason) => {
      if (team === 'A') {
        setTeamAData(payload);
        setTeamAResolvedSeason(resolvedSeason);
      } else {
        setTeamBData(payload);
        setTeamBResolvedSeason(resolvedSeason);
      }
    };

    const tryLoadSeason = async (seasonToLoad) => {
      const response = await fetch(`${API_URL}/api/hcl/teams/${abbr}?season=${seasonToLoad}`);
      let data = {};

      try {
        data = await response.json();
      } catch {
        data = {};
      }

      if (!response.ok || !data.success || !data.team) {
        return null;
      }

      return data.team;
    };

    const getGamesPlayedForSeason = async (seasonToCheck) => {
      const listResponse = await fetch(`${API_URL}/api/hcl/teams?season=${seasonToCheck}`);
      let listData = {};

      try {
        listData = await listResponse.json();
      } catch {
        listData = {};
      }

      if (!listResponse.ok || !listData.success || !Array.isArray(listData.teams)) {
        return null;
      }

      const matchedTeam = listData.teams.find((candidate) => candidate.team === abbr);
      if (!matchedTeam) {
        return null;
      }

      return Number(matchedTeam.games_played || 0);
    };

    try {
      setLoading(true);

      const requestedSeason = Number(season);
      const gamesPlayed = await getGamesPlayedForSeason(requestedSeason);
      const shouldSkipRequestedSeason = requestedSeason >= currentSeason && gamesPlayed === 0;

      // Normal path: completed seasons resolve immediately via direct detail fetch.
      if (!shouldSkipRequestedSeason) {
        const requestedSeasonTeam = await tryLoadSeason(requestedSeason);
        if (requestedSeasonTeam) {
          setTeamDataState(requestedSeasonTeam, requestedSeason);
          setError(null);
          return;
        }
      }

      // Preseason fallback path (for example, 2026 -> 2025).
      for (let fallbackSeason = requestedSeason - 1; fallbackSeason >= MIN_NFL_SEASON; fallbackSeason -= 1) {
        const fallbackTeam = await tryLoadSeason(fallbackSeason);
        if (fallbackTeam) {
          setTeamDataState(fallbackTeam, fallbackSeason);
          setError(null);
          return;
        }
      }

      setTeamDataState(null, null);
      setError(null);
    } catch (err) {
      setTeamDataState(null, null);
      setError(null);
    } finally {
      setLoading(false);
    }
  };

  const loadTeamSchedule = async (team, abbr, season) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/hcl/teams/${abbr}/games?season=${season}&limit=50`);
      const data = await response.json();
      if (data.success) {
        const sortedGames = data.games.sort((a, b) => a.week - b.week);
        if (team === 'A') {
          setTeamASchedule(sortedGames);
        } else {
          setTeamBSchedule(sortedGames);
        }
        setError(null);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadTeamSos = async (team, abbr, season) => {
    const setSosState = (payload) => {
      if (team === 'A') {
        setTeamASos(payload);
      } else {
        setTeamBSos(payload);
      }
    };

    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/hcl/teams/${abbr}/sos?season=${season}`);
      let data = {};

      try {
        data = await response.json();
      } catch {
        data = {};
      }

      if (response.ok && data.success) {
        setSosState(data);
      } else {
        setSosState({
          success: true,
          team: abbr,
          season: Number(season),
          sos_type: data.sos_type || 'projected',
          based_on_season: data.based_on_season || (Number(season) - 1),
          sos: null,
          opponents_record: '0-0',
          games_counted: 0,
          opponent_breakdown: [],
          note: data.note || data.error || 'SOS unavailable right now. Try again after backend refresh.'
        });
      }
      setError(null);
    } catch (err) {
      setSosState({
        success: true,
        team: abbr,
        season: Number(season),
        sos_type: 'projected',
        based_on_season: Number(season) - 1,
        sos: null,
        opponents_record: '0-0',
        games_counted: 0,
        opponent_breakdown: [],
        note: `${season} not yet played — SOS available after games are played.`
      });
      setError(null);
    } finally {
      setLoading(false);
    }
  };

  const getTeamLogo = (teamAbbr) => {
    return `https://a.espncdn.com/i/teamlogos/nfl/500/${teamAbbr}.png`;
  };

  const formatValue = (value, format) => {
    if (value === null || value === undefined) return 'N/A';
    switch (format) {
      case 'int': return Math.round(value);
      case 'percent': return `${parseFloat(value).toFixed(1)}%`;
      case 'decimal': return parseFloat(value).toFixed(1);
      default: return value;
    }
  };

  const formatGameDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const formatSosValue = (sosValue) => {
    if (sosValue === null || sosValue === undefined) {
      return 'N/A';
    }
    const numeric = Number(sosValue);
    if (Number.isNaN(numeric)) {
      return 'N/A';
    }
    return numeric.toFixed(3).replace(/^0(?=\.)/, '');
  };

  const isProjectedSos = (sosData) => sosData?.sos_type === 'projected';

  const getSosMetricLabel = (sosData) => {
    if (isProjectedSos(sosData)) {
      return "projected opponents' win%";
    }
    return "opponents' win%";
  };

  const getSosTypeLabel = (sosData) => {
    if (isProjectedSos(sosData)) {
      return 'Projected SOS';
    }
    return 'Strength of Schedule';
  };

  const getProjectedBasisNote = (sosData) => {
    if (!isProjectedSos(sosData)) {
      return null;
    }
    return `Based on opponents' ${sosData.based_on_season} records (season not yet played).`;
  };

  const getSosVerdict = () => {
    if (!selectedTeamA || !selectedTeamB) {
      return 'Select both teams to compare schedule strength.';
    }

    if (!teamASos || !teamBSos) {
      return 'Loading SOS comparison...';
    }

    const sosA = teamASos.sos;
    const sosB = teamBSos.sos;

    const projectedComparison = isProjectedSos(teamASos) || isProjectedSos(teamBSos);

    if (sosA === null || sosB === null) {
      return projectedComparison
        ? 'Projected SOS verdict available after both teams have valid prior-season opponent records.'
        : 'SOS verdict available after both selected seasons have completed games.';
    }

    const difference = Number(sosA) - Number(sosB);
    if (Math.abs(difference) < 0.003) {
      return projectedComparison ? 'Even projected schedule strength.' : 'Even schedule strength.';
    }

    if (projectedComparison) {
      return difference > 0
        ? `${selectedTeamA} has the tougher projected schedule.`
        : `${selectedTeamB} has the tougher projected schedule.`;
    }

    return difference > 0
      ? `${selectedTeamA} faced the tougher schedule.`
      : `${selectedTeamB} faced the tougher schedule.`;
  };

  const getSeasonDisplayLabel = (requestedSeason, resolvedSeason) => {
    if (!resolvedSeason) {
      return `${requestedSeason} Season`;
    }

    const requestedNumeric = Number(requestedSeason);
    if (requestedNumeric === Number(resolvedSeason)) {
      return `${requestedSeason} Season`;
    }

    return `${resolvedSeason} Season (latest completed)`;
  };

  const calculateDifferential = (teamAVal, teamBVal, format) => {
    if (teamAVal === null || teamAVal === undefined || teamBVal === null || teamBVal === undefined) {
      return { diff: null, display: '---', better: 'none' };
    }
    const diff = teamAVal - teamBVal;
    const absDiff = Math.abs(diff);
    let display = '';
    if (format === 'percent') display = `${absDiff.toFixed(1)}%`;
    else if (format === 'decimal') display = absDiff.toFixed(1);
    else display = Math.round(absDiff).toString();
    const better = diff > 0 ? 'A' : diff < 0 ? 'B' : 'tie';
    return { diff, display, better };
  };

  const toggleStat = (statKey) => {
    const newSet = new Set(selectedStats);
    if (newSet.has(statKey)) {
      newSet.delete(statKey);
    } else {
      newSet.add(statKey);
    }
    setSelectedStats(newSet);
  };

  const getSelectedStatsArray = () => {
    const allStats = [];
    Object.entries(STAT_CATEGORIES).forEach(([category, stats]) => {
      stats.forEach(stat => {
        if (selectedStats.has(stat.key)) {
          allStats.push({ ...stat, category });
        }
      });
    });
    return allStats;
  };

  return (
    <div className="team-comparison">
      {/* Header */}
      <div className="comparison-header">
        <h1>Compare Teams Hub</h1>
        <p className="subtitle">One hub for season averages, head-to-head, strength of schedule, and edge analysis ({MIN_NFL_SEASON}-{currentSeason}).</p>
      </div>

      {error && (
        <div className="error-banner">⚠️ {error}</div>
      )}

      {/* View Mode Tabs */}
      <div className="view-tabs">
        <button 
          className={`tab-button ${viewMode === 'comparison' ? 'active' : ''}`}
          onClick={() => setViewMode('comparison')}
        >
          📊 Season Averages
        </button>
        <button 
          className={`tab-button ${viewMode === 'head-to-head' ? 'active' : ''}`}
          onClick={() => setViewMode('head-to-head')}
        >
          ⚔️ Head-to-Head
        </button>
        <button 
          className={`tab-button ${viewMode === 'schedule' ? 'active' : ''}`}
          onClick={() => setViewMode('schedule')}
        >
          📅 Strength of Schedule
        </button>
        <button
          className={`tab-button ${viewMode === 'edge' ? 'active' : ''}`}
          onClick={() => setViewMode('edge')}
        >
          ⚖️ Edge / Advantage
        </button>
      </div>

      {/* Team Selection Bar */}
      <div className="team-selection-bar">
        <div className="team-select-group">
          <label>Team A</label>
          <select value={seasonA} onChange={(e) => setSeasonA(e.target.value)} className="season-select">
            {seasons.map(year => <option key={year} value={year}>{year}</option>)}
          </select>
          <select 
            value={selectedTeamA} 
            onChange={(e) => setSelectedTeamA(e.target.value)}
            className="team-select"
          >
            <option value="">-- Select Team A --</option>
            {teamAList.map(team => (
              <option key={team.team} value={team.team}>
                {team.team} ({team.wins || 0}-{team.losses || 0})
              </option>
            ))}
          </select>
        </div>

        <div className="vs-divider">VS</div>

        <div className="team-select-group">
          <label>Team B</label>
          <select value={seasonB} onChange={(e) => setSeasonB(e.target.value)} className="season-select">
            {seasons.map(year => <option key={year} value={year}>{year}</option>)}
          </select>
          <select 
            value={selectedTeamB} 
            onChange={(e) => setSelectedTeamB(e.target.value)}
            className="team-select"
          >
            <option value="">-- Select Team B --</option>
            {teamBList.map(team => (
              <option key={team.team} value={team.team}>
                {team.team} ({team.wins || 0}-{team.losses || 0})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Stat Picker (for comparison view) */}
      {viewMode === 'comparison' && (
        <div className="stat-picker-section">
          <button 
            className="stat-picker-toggle-btn"
            onClick={() => setShowStatPicker(!showStatPicker)}
          >
            {showStatPicker ? '✖ Hide' : '⚙️ Customize'} Stats ({selectedStats.size} selected)
          </button>

          {showStatPicker && (
            <div className="stat-picker-panel">
              <div className="stat-picker-grid">
                {Object.entries(STAT_CATEGORIES).map(([category, stats]) => (
                  <div key={category} className="stat-category-box">
                    <h3>{category}</h3>
                    <div className="stat-checkboxes">
                      {stats.map(stat => (
                        <label key={stat.key} className="stat-checkbox-label">
                          <input 
                            type="checkbox"
                            checked={selectedStats.has(stat.key)}
                            onChange={() => toggleStat(stat.key)}
                          />
                          <span>{stat.label}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Content Area */}
      {viewMode === 'comparison' && (
        <div className="comparison-view">
          {(!selectedTeamA || !selectedTeamB) && (
            <div className="empty-state">Select both teams to compare their season averages</div>
          )}

          {selectedTeamA && selectedTeamB && teamAData && teamBData && (
            <div className="comparison-grid">
              {/* Team A Column */}
              <div className="team-column">
                <div className="team-header-card">
                  <img src={getTeamLogo(selectedTeamA)} alt={selectedTeamA} className="team-logo-large" />
                  <h2>{selectedTeamA}</h2>
                  <div className="team-record">{teamAData.wins}-{teamAData.losses}</div>
                  <div className="team-season">{getSeasonDisplayLabel(seasonA, teamAResolvedSeason)}</div>
                </div>
                <div className="stats-list">
                  {getSelectedStatsArray().map(stat => (
                    <div key={stat.key} className="stat-item">
                      <span className="stat-label">{stat.label}</span>
                      <span className="stat-value">{formatValue(teamAData[stat.key], stat.format)}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Differential Column */}
              <div className="differential-column">
                <div className="differential-header">
                  <h3>Advantage</h3>
                </div>
                <div className="stats-list">
                  {getSelectedStatsArray().map(stat => {
                    const diff = calculateDifferential(teamAData[stat.key], teamBData[stat.key], stat.format);
                    return (
                      <div key={stat.key} className={`stat-item differential-item ${diff.better}`}>
                        <span className="differential-value">{diff.display}</span>
                        <span className="differential-arrow">
                          {diff.better === 'A' ? '←' : diff.better === 'B' ? '→' : '='}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Team B Column */}
              <div className="team-column">
                <div className="team-header-card">
                  <img src={getTeamLogo(selectedTeamB)} alt={selectedTeamB} className="team-logo-large" />
                  <h2>{selectedTeamB}</h2>
                  <div className="team-record">{teamBData.wins}-{teamBData.losses}</div>
                  <div className="team-season">{getSeasonDisplayLabel(seasonB, teamBResolvedSeason)}</div>
                </div>
                <div className="stats-list">
                  {getSelectedStatsArray().map(stat => (
                    <div key={stat.key} className="stat-item">
                      <span className="stat-label">{stat.label}</span>
                      <span className="stat-value">{formatValue(teamBData[stat.key], stat.format)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {viewMode === 'head-to-head' && (
        <div className="head-to-head-view">
          {(!selectedTeamA || !selectedTeamB) && (
            <div className="empty-state">Select both teams for head-to-head analysis</div>
          )}

          {selectedTeamA && selectedTeamB && teamAData && teamBData && (
            <div className="head-to-head-grid">
              {Object.entries(STAT_CATEGORIES).map(([category, stats]) => (
                <div key={category} className="h2h-category-card">
                  <h3 className="h2h-category-title">{category}</h3>
                  <div className="h2h-stats-table">
                    <div className="h2h-table-header">
                      <div className="h2h-cell h2h-team">{selectedTeamA}</div>
                      <div className="h2h-cell h2h-stat">Statistic</div>
                      <div className="h2h-cell h2h-team">{selectedTeamB}</div>
                    </div>
                    {stats.map(stat => {
                      const diff = calculateDifferential(teamAData[stat.key], teamBData[stat.key], stat.format);
                      return (
                        <div key={stat.key} className="h2h-table-row">
                          <div className={`h2h-cell h2h-value ${diff.better === 'A' ? 'winner' : ''}`}>
                            {formatValue(teamAData[stat.key], stat.format)}
                          </div>
                          <div className="h2h-cell h2h-stat-label">{stat.label}</div>
                          <div className={`h2h-cell h2h-value ${diff.better === 'B' ? 'winner' : ''}`}>
                            {formatValue(teamBData[stat.key], stat.format)}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {viewMode === 'schedule' && (
        <div className="schedule-view">
          <div className="sos-summary-panel">
            {selectedTeamA && selectedTeamB ? (
              <>
                <div className="sos-summary-grid">
                  <article className="sos-team-card">
                    <h3>{selectedTeamA} ({seasonA})</h3>
                    {teamASos ? (
                      teamASos.sos !== null && teamASos.sos !== undefined ? (
                        <>
                          <div className="sos-type-label">{getSosTypeLabel(teamASos)}</div>
                          <div className="sos-value">{formatSosValue(teamASos.sos)}</div>
                          <div className="sos-caption">{getSosMetricLabel(teamASos)}</div>
                          <div className="sos-bar-track">
                            <div
                              className="sos-bar-fill"
                              style={{ width: `${Math.min(100, Math.max(6, Number(teamASos.sos) * 100))}%` }}
                            />
                          </div>
                          <div className="sos-meta">
                            {teamASos.opponents_record} opponents&apos; record ({teamASos.games_counted} games weighted)
                          </div>
                          {getProjectedBasisNote(teamASos) && (
                            <div className="sos-projection-note">{getProjectedBasisNote(teamASos)}</div>
                          )}
                          {teamASos.note && teamASos.note !== getProjectedBasisNote(teamASos) && (
                            <div className="sos-note">{teamASos.note}</div>
                          )}
                        </>
                      ) : (
                        <div className="sos-note">
                          {teamASos.note || `${seasonA} not yet played — SOS available after games are played.`}
                        </div>
                      )
                    ) : (
                      <div className="sos-note">Loading SOS...</div>
                    )}
                  </article>

                  <article className="sos-team-card">
                    <h3>{selectedTeamB} ({seasonB})</h3>
                    {teamBSos ? (
                      teamBSos.sos !== null && teamBSos.sos !== undefined ? (
                        <>
                          <div className="sos-type-label">{getSosTypeLabel(teamBSos)}</div>
                          <div className="sos-value">{formatSosValue(teamBSos.sos)}</div>
                          <div className="sos-caption">{getSosMetricLabel(teamBSos)}</div>
                          <div className="sos-bar-track">
                            <div
                              className="sos-bar-fill"
                              style={{ width: `${Math.min(100, Math.max(6, Number(teamBSos.sos) * 100))}%` }}
                            />
                          </div>
                          <div className="sos-meta">
                            {teamBSos.opponents_record} opponents&apos; record ({teamBSos.games_counted} games weighted)
                          </div>
                          {getProjectedBasisNote(teamBSos) && (
                            <div className="sos-projection-note">{getProjectedBasisNote(teamBSos)}</div>
                          )}
                          {teamBSos.note && teamBSos.note !== getProjectedBasisNote(teamBSos) && (
                            <div className="sos-note">{teamBSos.note}</div>
                          )}
                        </>
                      ) : (
                        <div className="sos-note">
                          {teamBSos.note || `${seasonB} not yet played — SOS available after games are played.`}
                        </div>
                      )
                    ) : (
                      <div className="sos-note">Loading SOS...</div>
                    )}
                  </article>
                </div>

                <div className="sos-verdict">{getSosVerdict()}</div>
              </>
            ) : (
              <div className="empty-state">Select both teams to compare strength of schedule.</div>
            )}
          </div>

          <div className="schedule-grid">
            {/* Team A Schedule */}
            <div className="schedule-column">
              <h3 className="schedule-column-title">
                {selectedTeamA ? `${selectedTeamA} - ${seasonA}` : 'Team A Schedule'}
              </h3>
              {selectedTeamA && teamASchedule.length > 0 ? (
                teamASchedule.map(game => (
                  <div key={game.game_id} className={`schedule-game-card ${game.result === 'W' ? 'win' : game.result === 'L' ? 'loss' : 'upcoming'}`}>
                    <div className="game-header" onClick={() => setExpandedGameA(expandedGameA === game.game_id ? null : game.game_id)}>
                      <div className="game-week-date">
                        <span className="game-week">Week {game.week}</span>
                        <span className="game-date">{formatGameDate(game.game_date)}</span>
                      </div>
                      <div className="game-matchup-info">
                        <span className="opponent-direction">{game.is_home ? 'vs' : '@'}</span>
                        <img src={getTeamLogo(game.opponent)} alt={game.opponent} className="opponent-logo-sm" />
                        <span className="opponent-name">{game.opponent}</span>
                      </div>
                      <div className="game-result-badge">
                        {game.result ? `${game.result} ${game.team_points}-${game.is_home ? game.away_score : game.home_score}` : 'TBD'}
                      </div>
                    </div>
                    {expandedGameA === game.game_id && (
                      <div className="game-details">
                        <div className="game-stats-row">
                          <div className="game-stat"><label>Total Yards</label><span>{game.total_yards || 'N/A'}</span></div>
                          <div className="game-stat"><label>Pass Yards</label><span>{game.passing_yards || 'N/A'}</span></div>
                          <div className="game-stat"><label>Rush Yards</label><span>{game.rushing_yards || 'N/A'}</span></div>
                          <div className="game-stat"><label>Turnovers</label><span>{game.turnovers ?? 'N/A'}</span></div>
                        </div>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="empty-state-small">Select Team A to view schedule</div>
              )}
            </div>

            {/* Team B Schedule */}
            <div className="schedule-column">
              <h3 className="schedule-column-title">
                {selectedTeamB ? `${selectedTeamB} - ${seasonB}` : 'Team B Schedule'}
              </h3>
              {selectedTeamB && teamBSchedule.length > 0 ? (
                teamBSchedule.map(game => (
                  <div key={game.game_id} className={`schedule-game-card ${game.result === 'W' ? 'win' : game.result === 'L' ? 'loss' : 'upcoming'}`}>
                    <div className="game-header" onClick={() => setExpandedGameB(expandedGameB === game.game_id ? null : game.game_id)}>
                      <div className="game-week-date">
                        <span className="game-week">Week {game.week}</span>
                        <span className="game-date">{formatGameDate(game.game_date)}</span>
                      </div>
                      <div className="game-matchup-info">
                        <span className="opponent-direction">{game.is_home ? 'vs' : '@'}</span>
                        <img src={getTeamLogo(game.opponent)} alt={game.opponent} className="opponent-logo-sm" />
                        <span className="opponent-name">{game.opponent}</span>
                      </div>
                      <div className="game-result-badge">
                        {game.result ? `${game.result} ${game.team_points}-${game.is_home ? game.away_score : game.home_score}` : 'TBD'}
                      </div>
                    </div>
                    {expandedGameB === game.game_id && (
                      <div className="game-details">
                        <div className="game-stats-row">
                          <div className="game-stat"><label>Total Yards</label><span>{game.total_yards || 'N/A'}</span></div>
                          <div className="game-stat"><label>Pass Yards</label><span>{game.passing_yards || 'N/A'}</span></div>
                          <div className="game-stat"><label>Rush Yards</label><span>{game.rushing_yards || 'N/A'}</span></div>
                          <div className="game-stat"><label>Turnovers</label><span>{game.turnovers ?? 'N/A'}</span></div>
                        </div>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="empty-state-small">Select Team B to view schedule</div>
              )}
            </div>
          </div>
        </div>
      )}

      {viewMode === 'edge' && (
        <div className="edge-view">
          {(!selectedTeamA || !selectedTeamB) && (
            <div className="empty-state">Select both teams to see the matchup edge.</div>
          )}

          {selectedTeamA && selectedTeamB && teamAData && teamBData && (
            <div className="edge-grid">
              {Object.entries(STAT_CATEGORIES).map(([category, stats]) => (
                <article key={category} className="edge-category-card">
                  <h3>{category}</h3>
                  <div className="edge-rows">
                    {stats.map((stat) => {
                      const { display, better } = calculateDifferential(
                        teamAData[stat.key],
                        teamBData[stat.key],
                        stat.format
                      );

                      let summary = 'No edge';
                      if (display !== '---') {
                        if (better === 'A') {
                          summary = `← ${selectedTeamA} +${display}`;
                        } else if (better === 'B') {
                          summary = `${selectedTeamB} +${display} →`;
                        } else {
                          summary = `Even ${display}`;
                        }
                      }

                      return (
                        <div key={stat.key} className={`edge-row ${better}`}>
                          <span className="edge-label">{stat.label}</span>
                          <span className="edge-value">{summary}</span>
                        </div>
                      );
                    })}
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default TeamComparison;
