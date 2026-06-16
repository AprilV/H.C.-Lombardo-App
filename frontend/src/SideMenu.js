import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import './SideMenu.css';

function SideMenu() {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  const navItems = [
    { path: '/', icon: '🏈', label: 'Dashboard' },
    { path: '/team-comparison', icon: '⚖️', label: 'Compare Teams' },
    { path: '/analytics', icon: '📈', label: 'Advanced Analytics' },
    { path: '/historical-data', icon: '📚', label: 'Historical Data' },
    { path: '/ml-predictions', icon: '🧠', label: 'AI Predictions' },
    { path: '/admin', icon: 'ℹ️', label: 'About' }
  ];

  useEffect(() => {
    setIsOpen(false);
  }, [location.pathname]);

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  const closeMenu = () => {
    setIsOpen(false);
  };

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <nav className="site-nav" aria-label="Primary">
      <div className="top-nav" role="menubar">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`top-nav-item ${isActive(item.path) ? 'active' : ''}`}
            role="menuitem"
          >
            <span className="menu-icon" aria-hidden="true">{item.icon}</span>
            <span className="menu-text">{item.label}</span>
          </Link>
        ))}
      </div>

      <button className="hamburger-btn" onClick={toggleMenu} aria-label="Open navigation menu" aria-expanded={isOpen}>
        <span className="hamburger-line"></span>
        <span className="hamburger-line"></span>
        <span className="hamburger-line"></span>
      </button>

      {isOpen && <div className="menu-overlay" onClick={closeMenu}></div>}

      <div className={`mobile-drawer ${isOpen ? 'open' : ''}`}>
        <div className="menu-header">
          <h2>Navigate</h2>
          <button className="close-btn" onClick={closeMenu} aria-label="Close navigation menu">
            x
          </button>
        </div>

        <div className="menu-content">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`menu-item ${isActive(item.path) ? 'active' : ''}`}
              onClick={closeMenu}
            >
              <span className="menu-icon" aria-hidden="true">{item.icon}</span>
              <span className="menu-text">{item.label}</span>
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}

export default SideMenu;
