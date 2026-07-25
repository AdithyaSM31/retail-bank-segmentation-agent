import React from 'react';
import { KineticText } from './KineticText';

const Topbar = () => {
  return (
    <div className="topbar">
      <div className="brand-section">
        <KineticText text="Retail Bank Segmentation Agent" className="brand-title" style={{ fontSize: '1.25rem' }} />
      </div>

      <div className="topbar-center">
      </div>

      <div className="topbar-right">
        <div className="user-profile">
          <div className="user-avatar">U</div>
          <div className="user-info">
            <h4>User</h4>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Topbar;
