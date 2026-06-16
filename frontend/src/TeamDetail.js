import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import './TeamDetail.css';
import { getDefaultSeason } from './utils/season';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const API_URL = (typeof window !== 'undefined' && (window.location.hostname === 'hclombardo.com' || window.location.hostname === 'www.hclombardo.com' || window.location.hostname.endsWith('.netlify.app'))) ? '' : (process.env.REACT_APP_API_URL ?? '');
const MIN_NFL_SEASON = 1999;

// NFL Team Colors
const TEAM_COLORS = {
  'ARI': { primary: '#97233F', secondary: '#000000' },
  'ATL': { primary: '#A71930', secondary: '#000000' },
  'BAL': { primary: '#241773', secondary: '#000000' },
  'BUF': { primary: '#00338D', secondary: '#C60C30' },
  'CAR': { primary: '#0085CA', secondary: '#101820' },
  'CHI': { primary: '#C83803', secondary: '#0B162A' },
  'CIN': { primary: '#FB4F14', secondary: '#000000' },
  'CLE': { primary: '#311D00', secondary: '#FF3C00' },
  'DAL': { primary: '#003594', secondary: '#869397' },
  'DEN': { primary: '#FB4F14', secondary: '#002244' },
  'DET': { primary: '#0076B6', secondary: '#B0B7BC' },
  'GB': { primary: '#203731', secondary: '#FFB612' },
  'HOU': { primary: '#03202F', secondary: '#A71930' },
  'IND': { primary: '#002C5F', secondary: '#A2AAAD' },
  'JAX': { primary: '#006778', secondary: '#D7A22A' },
  'KC': { primary: '#E31837', secondary: '#FFB81C' },
  'LAC': { primary: '#0080C6', secondary: '#FFC20E' },
  'LAR': { primary: '#003594', secondary: '#FFA300' },
  'LV': { primary: '#000000', secondary: '#A5ACAF' },
  'MIA': { primary: '#008E97', secondary: '#FC4C02' },
  'MIN': { primary: '#4F2683', secondary: '#FFC62F' },
  'NE': { primary: '#002244', secondary: '#C60C30' },
  'NO': { primary: '#D3BC8D', secondary: '#101820' },
  'NYG': { primary: '#0B2265', secondary: '#A71930' },
  'NYJ': { primary: '#125740', secondary: '#000000' },
  'PHI': { primary: '#004C54', secondary: '#A5ACAF' },
  'PIT': { primary: '#FFB612', secondary: '#101820' },
  'SF': { primary: '#AA0000', secondary: '#B3995D' },
  'SEA': { primary: '#002244', secondary: '#69BE28' },
  'TB': { primary: '#D50A0A', secondary: '#34302B' },
  'TEN': { primary: '#0C2340', secondary: '#4B92DB' },
  'WAS': { primary: '#5A1414', secondary: '#FFB612' }
};

function TeamDetail() {
  const { teamAbbr } = useParams();
  const navigate = useNavigate();
  const [season, setSeason] = useState(getDefaultSeason());
  const [teamData, setTeamData] = useState(null);
  const [teamName, setTeamName] = useState('');
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const currentSeason = getDefaultSeason();
    setSeason(currentSeason);
    loadTeamData(currentSeason);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [teamAbbr]);

  const fetchJson = async (url) => {
    const response = await fetch(url);
    let data = {};

    try {
      data = await response.json();
    } catch {
      data = {};
    }

    return { response, data };
  };

  const getTeamSummaryForSeason = async (targetSeason) => {
    const { response, data } = await fetchJson(`${API_URL}/api/hcl/teams?season=${targetSeason}`);

    if (!response.ok || !data.success || !Array.isArray(data.teams)) {
      return null;
    }

    return data.teams.find((team) => (
      team.team === teamAbbr || team.abbreviation === teamAbbr || team.abbr === teamAbbr
    )) || null;
  };

  const loadTeamData = async (startSeason) => {
    try {
      setLoading(true);
      setError(null);
      const initialSeason = startSeason ?? getDefaultSeason();

      let candidateSeason = initialSeason;
      let resolvedTeamName = teamAbbr;

      // Pre-resolve a season that has completed team stats to avoid expected preseason 404s.
      for (let checkSeason = initialSeason; checkSeason >= MIN_NFL_SEASON; checkSeason -= 1) {
        const teamSummary = await getTeamSummaryForSeason(checkSeason);

        if (!teamSummary) {
          continue;
        }

        if (teamSummary.team_name) {
          resolvedTeamName = teamSummary.team_name;
        }

        if (Number(teamSummary.games_played ?? 0) > 0) {
          candidateSeason = checkSeason;
          break;
        }
      }

      setTeamName(resolvedTeamName);

      // Try the best candidate season first, then walk backward until team stats exist.
      for (let fallbackSeason = candidateSeason; fallbackSeason >= MIN_NFL_SEASON; fallbackSeason -= 1) {
        const { response: detailsResponse, data: detailsData } = await fetchJson(
          `${API_URL}/api/hcl/teams/${teamAbbr}?season=${fallbackSeason}`
        );

        if (!detailsResponse.ok || !detailsData.success || !detailsData.team) {
          continue;
        }

        const { response: gamesResponse, data: gamesData } = await fetchJson(
          `${API_URL}/api/hcl/teams/${teamAbbr}/games?season=${fallbackSeason}`
        );

        if (!gamesResponse.ok || !gamesData.success || !Array.isArray(gamesData.games)) {
          continue;
        }

        setTeamData(detailsData.team);
        setGames(gamesData.games);
        setSeason(fallbackSeason);
        return;
      }

      throw new Error(
        `Team ${teamAbbr} not found from ${initialSeason} back to ${MIN_NFL_SEASON}`
      );
    } catch (err) {
      setTeamData(null);
      setGames([]);
      setError(err?.message || 'Failed to load team data');
    } finally {
      setLoading(false);
    }
  };

  const getTeamLogo = (abbr) => {
    return `https://a.espncdn.com/i/teamlogos/nfl/500/${abbr}.png`;
  };

  const getTeamColors = () => {
    return TEAM_COLORS[teamAbbr] || { primary: '#013369', secondary: '#D50A0A' };
  };

  const formatGameDate = (gameDate) => {
    if (!gameDate) return 'Date TBD';

    const parsed = new Date(gameDate);
    if (Number.isNaN(parsed.getTime())) {
      return gameDate;
    }

    return parsed.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getOpponentScore = (game) => {
    return game.is_home ? game.away_score : game.home_score;
  };

  const getScheduleResult = (game) => {
    const opponentScore = getOpponentScore(game);

    if (game.result === 'W' || game.result === 'L' || game.result === 'T') {
      if (game.team_points != null && opponentScore != null) {
        return `${game.result} ${game.team_points}-${opponentScore}`;
      }
      return game.result;
    }

    return 'TBD';
  };

  const getScheduleClass = (game) => {
    if (game.result === 'W') return 'win';
    if (game.result === 'L') return 'loss';
    return 'upcoming';
  };

  const getChartData = () => {
    if (!games || games.length === 0) return null;
    
    // Only include games that have been played (have stats)
    const completedGames = games.filter(g => g.total_yards != null);
    
    if (completedGames.length === 0) return null;
    
    const sortedGames = [...completedGames].sort((a, b) => a.week - b.week);
    
    return {
      labels: sortedGames.map(g => `Week ${g.week}`),
      datasets: [
        {
          label: 'Total Yards',
          data: sortedGames.map(g => parseFloat(g.total_yards)),
          borderColor: '#667eea',
          backgroundColor: 'rgba(102, 126, 234, 0.1)',
          tension: 0.4,
          fill: true
        },
        {
          label: 'Points Scored',
          data: sortedGames.map(g => parseFloat(g.team_points)),
          borderColor: '#4CAF50',
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
          tension: 0.4,
          fill: true
        }
      ]
    };
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        display: true,
        position: 'top'
      },
      title: {
        display: false
      }
    },
    scales: {
      y: {
        beginAtZero: false
      }
    }
  };

  if (loading) {
    return (
      <div className="team-detail">
        <div className="loading">Loading team data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="team-detail">
        <div className="error">Error: {error}</div>
        <button onClick={() => navigate('/')} className="back-btn">
          ← Back to Teams
        </button>
      </div>
    );
  }

  if (!teamData) {
    return null;
  }

  const stats = [
    { label: 'Record', value: `${teamData.wins}-${teamData.losses}${(teamData.ties || 0) > 0 ? `-${teamData.ties}` : ''}` },
    { label: 'Games Played', value: teamData.games_played },
    { label: 'PPG', value: teamData.ppg },
    { label: 'Total Yards/Game', value: teamData.total_yards_per_game },
    { label: 'Pass Yards/Game', value: teamData.passing_yards_per_game },
    { label: 'Rush Yards/Game', value: teamData.rushing_yards_per_game },
    { label: 'Completion %', value: teamData.completion_pct ? `${teamData.completion_pct}%` : 'N/A' },
    { label: 'QB Rating', value: teamData.qb_rating || 'N/A' },
    { label: 'Sack Yards Lost/Game', value: teamData.sack_yards_lost_per_game || 'N/A' },
    { label: '3rd Down %', value: teamData.third_down_pct ? `${teamData.third_down_pct}%` : 'N/A' }
  ];

  const chartData = getChartData();
  const sortedGames = [...games].sort((a, b) => (a.week ?? 999) - (b.week ?? 999));
  
  // Get team colors for header
  const colors = getTeamColors();

  return (
    <div className="team-detail">
      <div className="team-detail-header" style={{
        background: `linear-gradient(135deg, ${colors.primary} 0%, ${colors.secondary} 100%)`,
        backgroundColor: colors.primary
      }}>
        <button onClick={() => navigate('/')} className="back-btn">
          ← Back to Teams
        </button>
        <div className="team-header">
          <img 
            src={getTeamLogo(teamAbbr)} 
            alt={teamName}
            className="team-logo-large"
          />
          <div>
            <h1 className="team-name">{teamName}</h1>
          </div>
          <span className="badge">{season} SEASON</span>
        </div>
      </div>

      <div className="stats-overview">
        <h2>Season Overview</h2>
        <div className="stats-grid">
          {stats.map((stat, index) => (
            <div key={index} className="stat-box">
              <div className="stat-label">{stat.label}</div>
              <div className="stat-value">{stat.value}</div>
            </div>
          ))}
        </div>
      </div>

      {chartData && (
        <div className="chart-container">
          <h2>Performance Trends</h2>
          <Line data={chartData} options={chartOptions} />
        </div>
      )}

      <div className="team-schedule-section">
        <h2>Season Schedule</h2>
        {sortedGames.length > 0 ? (
          <div className="team-schedule-list">
            {sortedGames.map((game, index) => {
              const location = game.is_home ? 'vs' : '@';
              const cardClass = getScheduleClass(game);

              return (
                <div key={`${game.game_id || 'game'}-${index}`} className={`team-schedule-card ${cardClass}`}>
                  <div className="team-schedule-header-row">
                    <div className="game-week-date">
                      <span className="game-week">Week {game.week ?? '-'}</span>
                      <span className="game-date">{formatGameDate(game.game_date)}</span>
                    </div>
                    <div className="game-matchup-info">
                      <span className="opponent-name">{location} {game.opponent}</span>
                      {game.is_divisional_game && <span className="division-badge">DIV</span>}
                    </div>
                    <div className="game-result-badge">{getScheduleResult(game)}</div>
                  </div>

                  <div className="team-schedule-stats-row">
                    <div className="team-schedule-stat">
                      <label>Total Yards</label>
                      <span>{game.total_yards != null ? game.total_yards : 'TBD'}</span>
                    </div>
                    <div className="team-schedule-stat">
                      <label>Pass Yards</label>
                      <span>{game.passing_yards != null ? game.passing_yards : 'TBD'}</span>
                    </div>
                    <div className="team-schedule-stat">
                      <label>Rush Yards</label>
                      <span>{game.rushing_yards != null ? game.rushing_yards : 'TBD'}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="empty-state-small">No schedule available for {season}</div>
        )}
      </div>
    </div>
  );
}

export default TeamDetail;
