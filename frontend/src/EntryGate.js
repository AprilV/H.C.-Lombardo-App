import React, { useState } from 'react';
import './EntryGate.css';

function EntryGate({ onEnter }) {
  const [logoUnavailable, setLogoUnavailable] = useState(false);

  return (
    <div
      className="entry-gate"
      style={{
        backgroundImage: `linear-gradient(155deg, rgba(3, 8, 28, 0.86), rgba(7, 18, 40, 0.78), rgba(6, 12, 24, 0.88)), url(${process.env.PUBLIC_URL}/entry-bg.jpg)`
      }}
    >
      <div className="entry-gate-overlay" aria-hidden="true"></div>

      <div className="entry-gate-content">
        {!logoUnavailable ? (
          <img
            src={`${process.env.PUBLIC_URL}/pics/gatehat.png`}
            alt="H.C. Lombardo"
            className="entry-gate-logo"
            onError={() => setLogoUnavailable(true)}
          />
        ) : (
          <h1 className="entry-gate-fallback-title">H.C. Lombardo</h1>
        )}

        <p className="entry-gate-tagline">AI-Powered NFL Predictions. Find the Edge.</p>
        <p className="entry-gate-age">You must be 21 or older to enter.</p>

        <button type="button" className="entry-gate-button" onClick={onEnter}>
          Enter - I'm 21+
        </button>
      </div>

      <p className="entry-gate-disclaimer">
        For educational and entertainment purposes only. Not affiliated with the NFL. Predictions and analysis should not be used for financial decisions.
      </p>
    </div>
  );
}

export default EntryGate;
