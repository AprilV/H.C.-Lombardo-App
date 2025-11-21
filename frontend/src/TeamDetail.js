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

const API_URL = 'http://127.0.0.1:5000';

function TeamDetail() {
  const { teamAbbr } = useParams();
  const navigate = useNavigate();
  const [teamData, setTeamData] = useState(null);
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadTeamData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [teamAbbr]);

  const loadTeamData = async () => {
    try {
      setLoading(true);
      
      // Load team details
      const detailsResponse = await fetch(`${API_URL}/api/hcl/teams/${teamAbbr}?season=2025`);
      const detailsData = await detailsResponse.json();
      
      if (!detailsData.success) {
        throw new Error(detailsData.error || 'Failed to load team details');
      }
      
      // Load games
      const gamesResponse = await fetch(`${API_URL}/api/hcl/teams/${teamAbbr}/games?season=2025`);
      const gamesData = await gamesResponse.json();
      
      if (!gamesData.success) {
        throw new Error(gamesData.error || 'Failed to load games');
      }
      
      setTeamData(detailsData.team);
      setGames(gamesData.games);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getTeamLogo = (abbr) => {
    return `https://a.espncdn.com/i/teamlogos/nfl/500/${abbr}.png`;
  };

  const getChartData = () => {
    if (!games || games.length === 0) return null;
    
    const sortedGames = [...games].sort((a, b) => a.week - b.week);
    
    return {
      labels: sortedGames.map(g => `Week ${g.week}`),
      datasets: [
        {
          label: 'Total Yards',
          data: sortedGames.map(g => parseFloat(g.total_yards || 0)),
          borderColor: '#667eea',
          backgroundColor: 'rgba(102, 126, 234, 0.1)',
          tension: 0.4,
          fill: true
        },
        {
          label: 'Points Scored',
          data: sortedGames.map(g => parseFloat(g.team_points || 0)),
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
    { label: 'Completion %', value: `${teamData.completion_pct}%` },
    { label: '3rd Down %', value: `${teamData.third_down_pct}%` }
  ];

  const chartData = getChartData();

  return (
    <div className="team-detail">
      <div className="header">
        <button onClick={() => navigate('/')} className="back-btn">
          ← Back to Teams
        </button>
        <div className="team-header">
          <img 
            src={getTeamLogo(teamAbbr)} 
            alt={teamAbbr}
            className="team-logo-large"
          />
          <div>
            <h1 className="team-name">{teamAbbr}</h1>
          </div>
          <span className="badge">2025 SEASON</span>
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

      <div className="games-table">
        <h2>Game History</h2>
        <table>
          <thead>
            <tr>
              <th>Week</th>
              <th>Opponent</th>
              <th>Result</th>
              <th>Score</th>
              <th>Total Yards</th>
              <th>Pass Yds</th>
              <th>Rush Yds</th>
            </tr>
          </thead>
          <tbody>
            {games.map((game, index) => {
              const won = game.result === 'W';
              const resultClass = won ? 'win' : 'loss';
              const location = game.is_home ? 'vs' : '@';
              
              return (
                <tr key={index}>
                  <td>{game.week}</td>
                  <td>
                    <div className="opponent-cell">
                      <img 
                        src={getTeamLogo(game.opponent)} 
                        alt={game.opponent}
                        className="opponent-logo"
                      />
                      {location} {game.opponent}
                      {game.is_divisional_game && <span className="division-badge">DIV</span>}
                    </div>
                  </td>
                  <td className={resultClass}>{game.result}</td>
                  <td>
                    {game.team_points != null ? game.team_points : '-'}-
                    {(() => {
                      // Opponent score is home_score if team is away, away_score if team is home
                      const oppScore = game.is_home ? game.away_score : game.home_score;
                      return oppScore != null ? oppScore : '-';
                    })()}
                  </td>
                  <td>{game.total_yards != null ? game.total_yards : '-'}</td>
                  <td>{game.passing_yards != null ? game.passing_yards : '-'}</td>
                  <td>{game.rushing_yards != null ? game.rushing_yards : '-'}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default TeamDetail;
