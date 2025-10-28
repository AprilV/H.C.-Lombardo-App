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

  const getChartData = () => {
    if (!games || games.length === 0) return null;
    
    const sortedGames = [...games].sort((a, b) => a.week - b.week);
    
    return {
      labels: sortedGames.map(g => `Week ${g.week}`),
      datasets: [
        {
          label: 'EPA/Play',
          data: sortedGames.map(g => parseFloat(g.epa_per_play || 0)),
          borderColor: '#667eea',
          backgroundColor: 'rgba(102, 126, 234, 0.1)',
          tension: 0.4,
          fill: true
        },
        {
          label: 'Success Rate',
          data: sortedGames.map(g => parseFloat(g.success_rate || 0)),
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
        <button onClick={() => navigate('/historical')} className="back-btn">
          ← Back to Teams
        </button>
      </div>
    );
  }

  if (!teamData) {
    return null;
  }

  const stats = [
    { label: 'Record', value: `${teamData.wins}-${teamData.losses}` },
    { label: 'Games Played', value: teamData.games_played },
    { label: 'PPG', value: teamData.ppg },
    { label: 'EPA/Play', value: teamData.epa_per_play },
    { label: 'Success Rate', value: teamData.success_rate },
    { label: 'Yards/Play', value: teamData.yards_per_play },
    { label: 'Pass EPA', value: teamData.pass_epa || 'N/A' },
    { label: 'Rush EPA', value: teamData.rush_epa || 'N/A' }
  ];

  const chartData = getChartData();

  return (
    <div className="team-detail">
      <div className="header">
        <button onClick={() => navigate('/historical')} className="back-btn">
          ← Back to Teams
        </button>
        <div className="team-header">
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
              <th>EPA/Play</th>
              <th>Success Rate</th>
              <th>Yards/Play</th>
            </tr>
          </thead>
          <tbody>
            {games.map((game, index) => {
              const won = game.team_points > game.opponent_points;
              const resultClass = won ? 'win' : 'loss';
              const result = won ? 'W' : 'L';
              const location = game.is_home ? 'vs' : '@';
              
              return (
                <tr key={index}>
                  <td>{game.week}</td>
                  <td>{location} {game.opponent}</td>
                  <td className={resultClass}>{result}</td>
                  <td>{game.team_points}-{game.opponent_points}</td>
                  <td>{game.epa_per_play}</td>
                  <td>{game.success_rate}</td>
                  <td>{game.yards_per_play}</td>
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
