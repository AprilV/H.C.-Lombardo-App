import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Homepage.css';

const API_URL = 'http://127.0.0.1:5000';

// NFL Divisions
const NFL_STRUCTURE = {
  AFC: {
    'AFC East': ['BUF', 'MIA', 'NYJ', 'NE'],
    'AFC North': ['BAL', 'CIN', 'CLE', 'PIT'],
    'AFC South': ['HOU', 'IND', 'JAX', 'TEN'],
    'AFC West': ['DEN', 'KC', 'LV', 'LAC']
  },
  NFC: {
    'NFC East': ['DAL', 'NYG', 'PHI', 'WAS'],
    'NFC North': ['CHI', 'DET', 'GB', 'MIN'],
    'NFC South': ['ATL', 'CAR', 'NO', 'TB'],
    'NFC West': ['ARI', 'LAR', 'SF', 'SEA']
  }
};

function Homepage() {
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchTeams();
  }, []);

  const fetchTeams = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/teams`);
      const data = await response.json();
      setTeams(data.teams || []);
    } catch (err) {
      console.error('Failed to fetch teams:', err);
    } finally {
      setLoading(false);
    }
  };

  const getTeamByAbbr = (abbr) => {
    return teams.find(t => t.abbreviation === abbr) || { name: abbr, abbreviation: abbr, wins: 0, losses: 0, ties: 0 };
  };

  // Sort teams by NFL standings rules (simplified)
  const sortTeamsByStandings = (teamAbbrs) => {
    return teamAbbrs.map(abbr => getTeamByAbbr(abbr))
      .sort((a, b) => {
        // Calculate win percentage
        const aGames = a.wins + a.losses + (a.ties || 0);
        const bGames = b.wins + b.losses + (b.ties || 0);
        const aWinPct = aGames > 0 ? (a.wins + (a.ties || 0) * 0.5) / aGames : 0;
        const bWinPct = bGames > 0 ? (b.wins + (b.ties || 0) * 0.5) / bGames : 0;
        
        // Primary: Win percentage (descending)
        if (Math.abs(aWinPct - bWinPct) > 0.001) {
          return bWinPct - aWinPct;
        }
        
        // Secondary: Total wins (descending)
        if (a.wins !== b.wins) {
          return b.wins - a.wins;
        }
        
        // Tertiary: Alphabetical by team name
        return a.name.localeCompare(b.name);
      })
      .map(team => team.abbreviation);
  };

  const handleTeamClick = (abbr) => {
    navigate(`/team-stats?team=${abbr}`);
  };

  if (loading) {
    return (
      <div className="homepage-loading">
        <div className="loading-spinner"></div>
        <p>Loading NFL Teams...</p>
      </div>
    );
  }

  return (
    <div className="homepage">
      <div className="homepage-header">
        <h1>🏈 2025 NFL Season</h1>
        <p className="season-subtitle">Conference & Division Standings</p>
      </div>

      {Object.entries(NFL_STRUCTURE).map(([conference, divisions]) => (
        <div key={conference} className={`conference-section ${conference.toLowerCase()}-section`}>
          <div className={`conference-header ${conference.toLowerCase()}`}>
            <img 
              src={`/images/${conference.toLowerCase()}.png`}
              alt={`${conference} Logo`}
              className="conference-logo-image"
            />
            <h2 className="conference-title">{conference}</h2>
          </div>
          
          <div className="divisions-grid">
            {Object.entries(divisions).map(([divisionName, teamAbbrs]) => {
              const sortedTeams = sortTeamsByStandings(teamAbbrs);
              return (
                <div key={divisionName} className="division-card">
                  <h3 className="division-title">{divisionName}</h3>
                  <div className="teams-list">
                    {sortedTeams.map(abbr => {
                      const team = getTeamByAbbr(abbr);
                      return (
                        <div 
                          key={abbr} 
                          className="team-row"
                          onClick={() => handleTeamClick(abbr)}
                        >
                          <img 
                            src={`/images/teams/${abbr.toLowerCase()}.png`}
                            alt={team.name}
                            className="team-logo-small"
                            onError={(e) => {e.target.style.display='none'}}
                          />
                          <span className="team-name-short">{team.name}</span>
                          <span className="team-record">
                            {team.wins}-{team.losses}{team.ties > 0 ? `-${team.ties}` : ''}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}

      <div className="homepage-footer">
        <button onClick={fetchTeams} className="refresh-btn-home">
          🔄 Refresh Standings
        </button>
      </div>
    </div>
  );
}

export default Homepage;
