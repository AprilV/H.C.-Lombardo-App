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
          <Link 
            to="/" 
            className={`menu-item ${isActive('/')}`}
            onClick={closeMenu}
          >
            <span className="menu-icon">🏈</span>
            <span className="menu-text">Dashboard</span>
          </Link>

          <Link 
            to="/team-comparison" 
            className={`menu-item ${isActive('/team-comparison')}`}
            onClick={closeMenu}
          >
            <span className="menu-icon">📊</span>
            <span className="menu-text">Team Comparison</span>
          </Link>

          <Link 
            to="/analytics" 
            className={`menu-item ${isActive('/analytics')}`}
            onClick={closeMenu}
          >
            <span className="menu-icon">📈</span>
            <span className="menu-text">Advanced Analytics</span>
          </Link>

          <Link 
            to="/ml-predictions" 
            className={`menu-item ${isActive('/ml-predictions')}`}
            onClick={closeMenu}
          >
            <span className="menu-icon">🧠</span>
            <span className="menu-text">AI Predictions</span>
          </Link>

          <div className="menu-divider"></div>

          <Link 
            to="/admin" 
            className={`menu-item ${isActive('/admin')}`}
            onClick={closeMenu}
          >
            <span className="menu-icon">🔧</span>
            <span className="menu-text">Admin</span>
          </Link>

          <div className="menu-divider"></div>

          <Link 
            to="/settings" 
            className={`menu-item ${isActive('/settings')}`}
            onClick={closeMenu}
          >
            <span className="menu-icon">⚙️</span>
            <span className="menu-text">Settings</span>
          </Link>

          <div className="menu-item disabled">
            <span className="menu-icon">ℹ️</span>
            <span className="menu-text">About</span>
          </div>
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
