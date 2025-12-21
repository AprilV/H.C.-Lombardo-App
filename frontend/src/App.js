import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import SideMenu from './SideMenu';
import Homepage from './Homepage';
import TeamComparison from './TeamComparison';
import TeamDetail from './TeamDetail';
import Analytics from './Analytics';
import MLPredictions from './MLPredictions';
import MLPredictionsRedesign from './MLPredictionsRedesign';
import Admin from './Admin';
import Settings from './Settings';
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
    <ThemeProvider>
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
            <Route path="/team-comparison" element={<TeamComparison />} />
            <Route path="/game-statistics" element={<TeamComparison />} />
            <Route path="/matchup-analyzer" element={<TeamComparison />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/ml-predictions" element={<MLPredictionsRedesign />} />
            <Route path="/ml-predictions-old" element={<MLPredictions />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="/team/:teamAbbr" element={<TeamDetail />} />
          </Routes>
        </main>

        <footer className="App-footer">
          <p>H.C. Lombardo NFL Analytics Platform 2025</p>
          <div className="footer-credits-combined">
            <span>Developed by </span>
            <a href="https://www.aprilsykes.com" target="_blank" rel="noopener noreferrer">
              April V. Sykes
            </a>
            <span> • Built with assistance from GitHub Copilot</span>
          </div>
          <p className="footer-note">This is for educational purposes only</p>
        </footer>
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
