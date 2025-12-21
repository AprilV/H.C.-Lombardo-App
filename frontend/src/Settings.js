import React from 'react';
import { useTheme } from './contexts/ThemeContext';
import './Settings.css';

function Settings() {
  const { theme, changeTheme } = useTheme();

  const themes = [
    {
      id: 'executive-dark',
      name: 'Executive Dark Mode',
      description: 'Professional cyan/blue analytics theme with dark background',
      icon: '💼'
    },
    {
      id: 'classic-light',
      name: 'Classic Light Mode',
      description: 'Clean light background with subtle accents',
      icon: '☀️'
    },
    {
      id: 'nfl-mode',
      name: 'NFL Mode',
      description: 'Vibrant NFL colors with red/blue gradient background',
      icon: '🏈'
    }
  ];

  return (
    <div className="settings-container">
      <div className="settings-header">
        <h1>⚙️ Settings</h1>
        <p className="settings-subtitle">Customize your H.C. Lombardo experience</p>
      </div>

      <div className="settings-section">
        <h2>🎨 Theme Selection</h2>
        <p className="section-description">Choose your preferred visual theme</p>

        <div className="theme-grid">
          {themes.map((themeOption) => (
            <div
              key={themeOption.id}
              className={`theme-card ${theme === themeOption.id ? 'active' : ''}`}
              onClick={() => changeTheme(themeOption.id)}
            >
              <div className="theme-icon">{themeOption.icon}</div>
              <h3>{themeOption.name}</h3>
              <p>{themeOption.description}</p>
              {theme === themeOption.id && (
                <div className="active-badge">✓ Active</div>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="settings-section">
        <h2>ℹ️ About Themes</h2>
        <div className="info-box">
          <p><strong>Executive Dark Mode:</strong> Our default professional theme with cyan highlights and dark backgrounds - perfect for extended analysis sessions.</p>
          <p><strong>Classic Light Mode:</strong> A traditional light interface for those who prefer bright backgrounds and high contrast.</p>
          <p><strong>NFL Mode:</strong> The original design with NFL-inspired red and blue gradient backgrounds for an energetic sports atmosphere.</p>
          <p className="note">Your theme preference is saved automatically and will persist across sessions.</p>
        </div>
      </div>
    </div>
  );
}

export default Settings;
