import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SideMenu from './SideMenu';
import Homepage from './Homepage';
import GameStatistics from './GameStatistics';
import MatchupAnalyzer from './MatchupAnalyzer';
import TeamDetail from './TeamDetail';
import Analytics from './Analytics';
import MLPredictions from './MLPredictions';
import Admin from './Admin';
import './App.css';

const API_URL = 'https://api.aprilsykes.dev';

function App() {
  const [serverStatus, setServerStatus] = useState(null);

  useEffect(() => {
    testConnection();
  }, []);

  const testConnection = async () => {
    try {
      const response = await fetch(`${API_URL}/health`);
      const data = await response.json();
      setServerStatus(data);
    } catch (err) {
      console.error('Connection test failed:', err);
    }
  };

  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <img 
            src="https://a.espncdn.com/i/teamlogos/leagues/500/nfl.png" 
            alt="NFL Logo"
            className="nfl-logo"
          />
          <div className="fire-title">
            <h1>H.C. LOMBARDO</h1>
            <p className="fire-quote">" FOTTUTAMENTE INCREDIBILE!"</p>
          </div>
          <p className="subtitle">NFL Analytics</p>
        </header>

        <main className="App-main">
          <SideMenu />

          <Routes>
            <Route path="/" element={<Homepage />} />
            <Route path="/game-statistics" element={<GameStatistics />} />
            <Route path="/matchup-analyzer" element={<MatchupAnalyzer />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/ml-predictions" element={<MLPredictions />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="/team/:teamAbbr" element={<TeamDetail />} />
          </Routes>
        </main>

        <footer className="App-footer">
          <p>H.C. Lombardo NFL Analytics Platform  2025</p>
          <p className="footer-note">Production Environment | PWA Ready</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
