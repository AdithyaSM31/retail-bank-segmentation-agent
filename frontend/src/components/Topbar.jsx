import React from 'react';
import { Sparkles } from 'lucide-react';

const Topbar = () => {
  return (
    <div className="topbar">
      <div className="brand-section">
        <div className="brand-icon">
          <Sparkles size={24} />
        </div>
        <h1 className="brand-title">Retail Bank Segmentation Agent</h1>
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
