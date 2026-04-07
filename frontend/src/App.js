import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import SideMenu from './SideMenu';
import Homepage from './Homepage';
import LiveScores from './LiveScores';
import TeamStats from './TeamStats';
import TeamComparison from './TeamComparison';
import TeamDetail from './TeamDetail';
import MatchupAnalyzer from './MatchupAnalyzer';
import Analytics from './Analytics';
import GameStatistics from './GameStatistics';
import HistoricalData from './HistoricalData';
import MLPredictions from './MLPredictions';
import MLPredictionsRedesign from './MLPredictionsRedesign';
import ModelPerformance from './ModelPerformance';
import Admin from './Admin';
import Settings from './Settings';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || 'https://api.aprilsykes.dev';

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
            <Route path="/live-scores" element={<LiveScores />} />
            <Route path="/team-stats" element={<TeamStats />} />
            <Route path="/team-comparison" element={<TeamComparison />} />
            <Route path="/team/:teamAbbr" element={<TeamDetail />} />
            <Route path="/matchup-analyzer" element={<MatchupAnalyzer />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/game-statistics" element={<GameStatistics />} />
            <Route path="/historical-data" element={<HistoricalData />} />
            <Route path="/ml-predictions" element={<MLPredictionsRedesign />} />
            <Route path="/ml-predictions-redesign" element={<MLPredictionsRedesign />} />
            <Route path="/ml-predictions-old" element={<MLPredictions />} />
            <Route path="/model-performance" element={<ModelPerformance />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/admin" element={<Admin />} />
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
