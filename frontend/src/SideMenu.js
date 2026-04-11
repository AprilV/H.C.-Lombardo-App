import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import './SideMenu.css';

function SideMenu() {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  const closeMenu = () => {
    setIsOpen(false);
  };

  const isActive = (path) => {
    return location.pathname === path ? 'active' : '';
  };

  return (
    <>
      {/* Hamburger Button */}
      <button className="hamburger-btn" onClick={toggleMenu} aria-label="Menu">
        <span className="hamburger-line"></span>
        <span className="hamburger-line"></span>
        <span className="hamburger-line"></span>
      </button>

      {/* Overlay */}
      {isOpen && <div className="menu-overlay" onClick={closeMenu}></div>}

      {/* Side Menu */}
      <nav className={`side-menu ${isOpen ? 'open' : ''}`}>
        <div className="menu-header">
          <img 
            src="https://a.espncdn.com/i/teamlogos/leagues/500/nfl.png"
            alt="NFL"
            className="menu-logo"
          />
          <h2>H.C. Lombardo</h2>
          <button className="close-btn" onClick={closeMenu} aria-label="Close Menu">
            ✕
          </button>
        </div>

        <div className="menu-content">
          <Link to="/" className={`menu-item ${isActive('/')}`} onClick={closeMenu}>
            <span className="menu-icon">🏈</span>
            <span className="menu-text">Dashboard</span>
          </Link>

          <div className="menu-divider"></div>

          <Link to="/team-stats" className={`menu-item ${isActive('/team-stats')}`} onClick={closeMenu}>
            <span className="menu-icon">📊</span>
            <span className="menu-text">Team Stats</span>
          </Link>

          <Link to="/team-comparison" className={`menu-item ${isActive('/team-comparison')}`} onClick={closeMenu}>
            <span className="menu-icon">⚖️</span>
            <span className="menu-text">Team Comparison</span>
          </Link>

          <Link to="/matchup-analyzer" className={`menu-item ${isActive('/matchup-analyzer')}`} onClick={closeMenu}>
            <span className="menu-icon">🎯</span>
            <span className="menu-text">Matchup Analyzer</span>
          </Link>

          <div className="menu-divider"></div>

          <Link to="/analytics" className={`menu-item ${isActive('/analytics')}`} onClick={closeMenu}>
            <span className="menu-icon">📈</span>
            <span className="menu-text">Advanced Analytics</span>
          </Link>

          <Link to="/game-statistics" className={`menu-item ${isActive('/game-statistics')}`} onClick={closeMenu}>
            <span className="menu-icon">🏟️</span>
            <span className="menu-text">Game Statistics</span>
          </Link>

          <Link to="/historical-data" className={`menu-item ${isActive('/historical-data')}`} onClick={closeMenu}>
            <span className="menu-icon">📚</span>
            <span className="menu-text">Historical Data</span>
          </Link>

          <div className="menu-divider"></div>

          <Link to="/ml-predictions" className={`menu-item ${isActive('/ml-predictions')}`} onClick={closeMenu}>
            <span className="menu-icon">🧠</span>
            <span className="menu-text">AI Predictions</span>
          </Link>

          <Link to="/model-performance" className={`menu-item ${isActive('/model-performance')}`} onClick={closeMenu}>
            <span className="menu-icon">📉</span>
            <span className="menu-text">Model Performance</span>
          </Link>

          <div className="menu-divider"></div>

          <Link to="/admin" className={`menu-item ${isActive('/admin')}`} onClick={closeMenu}>
            <span className="menu-icon">🔧</span>
            <span className="menu-text">Admin</span>
          </Link>

          <Link to="/settings" className={`menu-item ${isActive('/settings')}`} onClick={closeMenu}>
            <span className="menu-icon">⚙️</span>
            <span className="menu-text">Settings</span>
          </Link>
        </div>

        <div className="menu-footer">
          <p>© 2025 H.C. Lombardo</p>
          <p className="version">v1.0.0</p>
        </div>
      </nav>
    </>
  );
}

export default SideMenu;
