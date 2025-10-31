import React, { useState, useEffect } from 'react';
import './Analytics.css';

const API_URL = 'http://127.0.0.1:5000';

function Analytics() {
  const [activeTab, setActiveTab] = useState('summary');
  const [season, setSeason] = useState(2025);
  const [loading, setLoading] = useState(false);
  
  // Data states
  const [summary, setSummary] = useState(null);
  const [bettingData, setBettingData] = useState([]);
  const [weatherData, setWeatherData] = useState([]);
  const [restData, setRestData] = useState([]);
  const [refereeData, setRefereeData] = useState([]);
  
  // Custom stat builder states
  const [selectedTeam, setSelectedTeam] = useState('');
  const [selectedStats, setSelectedStats] = useState([]);
  const [teams, setTeams] = useState([]);

  // Available stats for à la carte selection
  const availableStats = [
    { id: 'ats_record', name: 'Against The Spread Record', category: 'betting' },
    { id: 'ats_win_pct', name: 'ATS Win %', category: 'betting' },
    { id: 'over_under', name: 'Over/Under Record', category: 'betting' },
    { id: 'favorite_record', name: 'Record As Favorite', category: 'betting' },
    { id: 'underdog_record', name: 'Record As Underdog', category: 'betting' },
    { id: 'dome_scoring', name: 'Dome Scoring Average', category: 'weather' },
    { id: 'outdoor_scoring', name: 'Outdoor Scoring Average', category: 'weather' },
    { id: 'cold_weather', name: 'Cold Weather Performance', category: 'weather' },
    { id: 'wind_impact', name: 'High Wind Games', category: 'weather' },
    { id: 'rest_advantage', name: 'Bye Week Performance', category: 'rest' },
    { id: 'short_week', name: 'Short Week Performance', category: 'rest' },
    { id: 'normal_rest', name: 'Normal Rest Performance', category: 'rest' },
  ];

  useEffect(() => {
    fetchSummary();
    fetchTeams();
  }, [season]);

  useEffect(() => {
    if (activeTab === 'betting') fetchBettingData();
    if (activeTab === 'weather') fetchWeatherData();
    if (activeTab === 'rest') fetchRestData();
    if (activeTab === 'referees') fetchRefereeData();
  }, [activeTab, season]);

  const fetchSummary = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/hcl/analytics/summary?season=${season}`);
      const data = await response.json();
      if (data.success) {
        setSummary(data.summary);
      }
    } catch (err) {
      console.error('Error fetching summary:', err);
    }
    setLoading(false);
  };

  const fetchBettingData = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/hcl/analytics/betting?season=${season}`);
      const data = await response.json();
      if (data.success) {
        setBettingData(data.teams);
      }
    } catch (err) {
      console.error('Error fetching betting data:', err);
    }
    setLoading(false);
  };

  const fetchWeatherData = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/hcl/analytics/weather?season=${season}`);
      const data = await response.json();
      if (data.success) {
        setWeatherData(data.conditions);
      }
    } catch (err) {
      console.error('Error fetching weather data:', err);
    }
    setLoading(false);
  };

  const fetchRestData = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/hcl/analytics/rest?season=${season}`);
      const data = await response.json();
      if (data.success) {
        setRestData(data.rest_categories);
      }
    } catch (err) {
      console.error('Error fetching rest data:', err);
    }
    setLoading(false);
  };

  const fetchRefereeData = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/hcl/analytics/referees?season=${season}`);
      const data = await response.json();
      if (data.success) {
        setRefereeData(data.referees);
      }
    } catch (err) {
      console.error('Error fetching referee data:', err);
    }
    setLoading(false);
  };

  const fetchTeams = async () => {
    try {
      const response = await fetch(`${API_URL}/api/hcl/teams`);
      const data = await response.json();
      if (data.success) {
        setTeams(data.teams);
      }
    } catch (err) {
      console.error('Error fetching teams:', err);
    }
  };

  const toggleStat = (statId) => {
    setSelectedStats(prev => 
      prev.includes(statId) 
        ? prev.filter(id => id !== statId)
        : [...prev, statId]
    );
  };

  const renderSummary = () => {
    if (!summary) return <div>Loading summary...</div>;

    return (
      <>
        <div className="stat-legend">
          <h3>📖 Summary Overview</h3>
          <p><strong>ATS (Against The Spread):</strong> How often a team covers the betting spread</p>
          <p><strong>PPG (Points Per Game):</strong> Average points scored per game</p>
          <p><strong>Rest Advantage:</strong> Win percentage based on days of rest (bye week, short week, normal)</p>
        </div>
        
        <div className="summary-grid">
          <div className="insight-card highlight">
            <h3>🎯 Best Betting Team</h3>
            {summary.best_ats_team && (
              <div className="insight-content">
                <div className="team-name">{summary.best_ats_team.team}</div>
                <div className="stat-large">{summary.best_ats_team.ats_win_pct}%</div>
                <div className="stat-label">ATS Win Rate</div>
                <div className="record">{summary.best_ats_team.ats_wins}-{summary.best_ats_team.ats_losses}</div>
              </div>
            )}
          </div>

          <div className="insight-card">
            <h3>🌤️ Weather Impact</h3>
            {summary.weather_impact && summary.weather_impact.length > 0 && (
              <div className="insight-content">
                <div className="weather-comparison">
                  {summary.weather_impact.map((w, i) => (
                    <div key={i} className="weather-item">
                      <span className="roof-type">{w.roof}</span>
                      <span className="ppg">{w.avg_ppg} PPG</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="insight-card">
            <h3>😴 Rest Advantage</h3>
            {summary.best_rest_advantage && (
              <div className="insight-content">
                <div className="stat-large">{summary.best_rest_advantage.avg_win_pct}%</div>
                <div className="stat-label">{summary.best_rest_advantage.rest_category}</div>
                <div className="stat-small">{summary.best_rest_advantage.games} games</div>
              </div>
            )}
          </div>

          <div className="insight-card">
            <h3>👔 Top Referee</h3>
            {summary.most_games_referee && (
              <div className="insight-content">
                <div className="referee-name">{summary.most_games_referee.referee}</div>
                <div className="stat-medium">{summary.most_games_referee.total_games} games</div>
                <div className="stat-small">Home Win: {summary.most_games_referee.home_win_pct}%</div>
              </div>
            )}
          </div>
        </div>
      </>
    );
  };

  const renderBettingTable = () => {
    return (
      <div className="data-table-container">
        <div className="stat-legend">
          <h3>📖 Betting Stats Explained</h3>
          <p><strong>ATS Record:</strong> Against The Spread wins-losses (did team beat the betting line?)</p>
          <p><strong>ATS %:</strong> Percentage of games where team covered the spread</p>
          <p><strong>O/U Record:</strong> Over/Under wins-losses (did total points exceed the betting line?)</p>
          <p><strong>Over %:</strong> Percentage of games that went over the total</p>
          <p><strong>As Favorite:</strong> Record when team was favored to win</p>
          <p><strong>As Underdog:</strong> Record when team was the underdog</p>
        </div>
        
        <h2>📊 Team Betting Performance</h2>
        <table className="data-table">
          <thead>
            <tr>
              <th>Team</th>
              <th>Games</th>
              <th>ATS Record</th>
              <th>ATS %</th>
              <th>O/U Record</th>
              <th>Over %</th>
              <th>As Favorite</th>
              <th>As Underdog</th>
            </tr>
          </thead>
          <tbody>
            {bettingData.map((team, i) => (
              <tr key={i} className={i < 5 ? 'highlight-row' : ''}>
                <td className="team-cell">{team.team}</td>
                <td>{team.total_games}</td>
                <td className="record-cell">{team.ats_wins}-{team.ats_losses}-{team.ats_pushes}</td>
                <td className={team.ats_win_pct >= 55 ? 'good' : team.ats_win_pct <= 45 ? 'bad' : ''}>
                  {team.ats_win_pct}%
                </td>
                <td className="record-cell">{team.games_over}-{team.games_under}</td>
                <td>{team.over_pct}%</td>
                <td className="record-cell">{team.wins_as_favorite}/{team.games_as_favorite}</td>
                <td className="record-cell">{team.wins_as_underdog}/{team.games_as_underdog}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderWeatherTable = () => {
    return (
      <div className="data-table-container">
        <div className="stat-legend">
          <h3>📖 Weather Stats Explained</h3>
          <p><strong>Roof Types:</strong> Dome (indoor), Retractable (can open/close), Outdoor (open air)</p>
          <p><strong>Temp Range:</strong> Temperature categories affecting gameplay (cold affects passing, etc.)</p>
          <p><strong>Wind Range:</strong> Wind speed categories (high wind reduces passing yards)</p>
          <p><strong>PPG:</strong> Points Per Game - higher scoring in controlled environments (domes)</p>
          <p><strong>Pass/Rush Yards:</strong> Average passing and rushing yards per game under these conditions</p>
          <p><strong>Over %:</strong> Percentage of games that went over the betting total</p>
        </div>
        
        <h2>🌤️ Weather Impact Analysis</h2>
        <table className="data-table">
          <thead>
            <tr>
              <th>Roof</th>
              <th>Temp Range</th>
              <th>Wind Range</th>
              <th>Games</th>
              <th>Avg PPG</th>
              <th>Avg Yards</th>
              <th>Pass Yards</th>
              <th>Rush Yards</th>
              <th>Over %</th>
            </tr>
          </thead>
          <tbody>
            {weatherData.map((condition, i) => (
              <tr key={i}>
                <td>{condition.roof}</td>
                <td>{condition.temp_range}</td>
                <td>{condition.wind_range}</td>
                <td>{condition.total_games}</td>
                <td className="highlight-cell">{condition.avg_total_points}</td>
                <td>{condition.avg_total_yards}</td>
                <td>{condition.avg_passing_yards}</td>
                <td>{condition.avg_rushing_yards}</td>
                <td>{condition.over_pct}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderRestTable = () => {
    return (
      <div className="data-table-container">
        <div className="stat-legend">
          <h3>📖 Rest Advantage Explained</h3>
          <p><strong>Bye Week:</strong> Team had 14+ days rest (full week off between games)</p>
          <p><strong>Extra Rest:</strong> Team had 8-13 days rest (typically after Monday/Thursday games)</p>
          <p><strong>Normal Rest:</strong> Team had 6-7 days rest (standard weekly schedule)</p>
          <p><strong>Short Week:</strong> Team had 5 or fewer days rest (Thursday night games)</p>
          <p><strong>Win %:</strong> Winning percentage with this amount of rest</p>
          <p><strong>ATS %:</strong> Percentage of games where teams covered the spread with this rest</p>
          <p><em>Teams generally perform better with more rest, especially after bye weeks</em></p>
        </div>
        
        <h2>😴 Rest Advantage Analysis</h2>
        <table className="data-table">
          <thead>
            <tr>
              <th>Rest Category</th>
              <th>Days</th>
              <th>Games</th>
              <th>Record</th>
              <th>Win %</th>
              <th>Avg Points</th>
              <th>Home Win %</th>
              <th>Away Win %</th>
            </tr>
          </thead>
          <tbody>
            {restData.map((rest, i) => (
              <tr key={i} className={rest.rest_category.includes('Bye') ? 'highlight-row' : ''}>
                <td>{rest.rest_category}</td>
                <td>{rest.rest_days}</td>
                <td>{rest.total_games}</td>
                <td className="record-cell">{rest.wins}-{rest.losses}</td>
                <td className={rest.win_pct >= 55 ? 'good' : rest.win_pct <= 45 ? 'bad' : ''}>
                  {rest.win_pct}%
                </td>
                <td>{rest.avg_points_scored}</td>
                <td>{rest.home_win_pct}%</td>
                <td>{rest.away_win_pct}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderRefereeTable = () => {
    return (
      <div className="data-table-container">
        <div className="stat-legend">
          <h3>📖 Referee Stats Explained</h3>
          <p><strong>Home Win %:</strong> Percentage of games where home team won under this referee</p>
          <p className="legend-note">⚠️ <em>Values significantly different from 50% (±10%) may indicate home field bias</em></p>
          <p><strong>Avg PPG:</strong> Average total points scored in games this referee worked</p>
          <p><strong>OT Games:</strong> Number and percentage of games that went to overtime</p>
          <p><strong>Avg Turnovers:</strong> Average turnovers per game (fumbles + interceptions)</p>
          <p><strong>Over %:</strong> Percentage of games that went over the betting total</p>
          <p><em>Some referees call tighter games (more penalties/turnovers), others let teams play</em></p>
        </div>
        
        <h2>👔 Referee Tendencies</h2>
        <table className="data-table">
          <thead>
            <tr>
              <th>Referee</th>
              <th>Games</th>
              <th>Home Win %</th>
              <th>Avg PPG</th>
              <th>OT Games</th>
              <th>Avg Turnovers</th>
              <th>Over %</th>
            </tr>
          </thead>
          <tbody>
            {refereeData.map((ref, i) => (
              <tr key={i}>
                <td className="referee-cell">{ref.referee}</td>
                <td>{ref.total_games}</td>
                <td className={Math.abs(ref.home_win_pct - 50) > 10 ? 'warning' : ''}>
                  {ref.home_win_pct}%
                </td>
                <td>{ref.avg_total_points}</td>
                <td>{ref.overtime_games} ({ref.overtime_pct}%)</td>
                <td>{ref.avg_turnovers_per_game}</td>
                <td>{ref.over_pct}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderCustomBuilder = () => {
    return (
      <div className="custom-builder">
        <div className="stat-legend">
          <h3>📖 À La Carte Stats Builder</h3>
          <p><strong>How to use:</strong> Select a team (or leave blank for all teams), then check the specific stats you want to see.</p>
          <p><strong>Betting Stats:</strong> Spread performance, over/under records, favorite/underdog splits</p>
          <p><strong>Weather Stats:</strong> Dome vs outdoor performance, cold weather impact, wind effects</p>
          <p><strong>Rest Stats:</strong> Performance after bye weeks, short weeks, and normal rest</p>
          <p><em>Build your own custom analytics dashboard by mixing and matching any stats!</em></p>
        </div>
        
        <h2>🎯 Custom Stat Builder</h2>
        <div className="builder-controls">
          <div className="control-group">
            <label>Select Team:</label>
            <select value={selectedTeam} onChange={(e) => setSelectedTeam(e.target.value)}>
              <option value="">-- All Teams --</option>
              {teams.map(team => (
                <option key={team.team} value={team.team}>{team.team}</option>
              ))}
            </select>
          </div>
          
          <div className="stat-selector">
            <h3>Select Stats to Display:</h3>
            <div className="stat-categories">
              <div className="stat-category">
                <h4>🎯 Betting Stats</h4>
                {availableStats.filter(s => s.category === 'betting').map(stat => (
                  <label key={stat.id} className="stat-checkbox">
                    <input 
                      type="checkbox" 
                      checked={selectedStats.includes(stat.id)}
                      onChange={() => toggleStat(stat.id)}
                    />
                    {stat.name}
                  </label>
                ))}
              </div>

              <div className="stat-category">
                <h4>🌤️ Weather Stats</h4>
                {availableStats.filter(s => s.category === 'weather').map(stat => (
                  <label key={stat.id} className="stat-checkbox">
                    <input 
                      type="checkbox" 
                      checked={selectedStats.includes(stat.id)}
                      onChange={() => toggleStat(stat.id)}
                    />
                    {stat.name}
                  </label>
                ))}
              </div>

              <div className="stat-category">
                <h4>😴 Rest Stats</h4>
                {availableStats.filter(s => s.category === 'rest').map(stat => (
                  <label key={stat.id} className="stat-checkbox">
                    <input 
                      type="checkbox" 
                      checked={selectedStats.includes(stat.id)}
                      onChange={() => toggleStat(stat.id)}
                    />
                    {stat.name}
                  </label>
                ))}
              </div>
            </div>
          </div>

          {selectedStats.length > 0 && (
            <div className="selected-stats-display">
              <h3>Your Custom Stats View:</h3>
              <div className="custom-stats-grid">
                {selectedStats.map(statId => {
                  const stat = availableStats.find(s => s.id === statId);
                  return (
                    <div key={statId} className="custom-stat-card">
                      <div className="stat-name">{stat.name}</div>
                      <div className="stat-value">Coming Soon</div>
                      <button onClick={() => toggleStat(statId)} className="remove-stat">×</button>
                    </div>
                  );
                })}
              </div>
              <p className="builder-note">
                💡 This custom builder lets you pick exactly which stats you want to see.
                Select a team above to filter, or leave blank for league-wide stats.
              </p>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="analytics-container">
      <div className="analytics-header">
        <h1>📊 Advanced Analytics Dashboard</h1>
        <div className="season-selector">
          <label>Season:</label>
          <select value={season} onChange={(e) => setSeason(Number(e.target.value))}>
            <option value={2025}>2025</option>
            <option value={2024}>2024</option>
            <option value={2023}>2023</option>
            <option value={2022}>2022</option>
          </select>
        </div>
      </div>

      <div className="analytics-tabs">
        <button 
          className={activeTab === 'summary' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('summary')}
        >
          📈 Summary
        </button>
        <button 
          className={activeTab === 'betting' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('betting')}
        >
          🎯 Betting
        </button>
        <button 
          className={activeTab === 'weather' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('weather')}
        >
          🌤️ Weather
        </button>
        <button 
          className={activeTab === 'rest' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('rest')}
        >
          😴 Rest
        </button>
        <button 
          className={activeTab === 'referees' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('referees')}
        >
          👔 Referees
        </button>
        <button 
          className={activeTab === 'custom' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('custom')}
        >
          🎯 Custom Builder
        </button>
      </div>

      <div className="analytics-content">
        {loading && <div className="loading">Loading data...</div>}
        {!loading && activeTab === 'summary' && renderSummary()}
        {!loading && activeTab === 'betting' && renderBettingTable()}
        {!loading && activeTab === 'weather' && renderWeatherTable()}
        {!loading && activeTab === 'rest' && renderRestTable()}
        {!loading && activeTab === 'referees' && renderRefereeTable()}
        {!loading && activeTab === 'custom' && renderCustomBuilder()}
      </div>
    </div>
  );
}

export default Analytics;
