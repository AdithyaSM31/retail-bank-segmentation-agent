import React, { useState } from 'react';
import { LayoutDashboard, Users, BarChart, PieChart, FileText, Bell, Database, Settings, Trash2, Building2 } from 'lucide-react';

const Sidebar = ({ onQuickAction, onClearChat }) => {
  const [activeTab, setActiveTab] = useState('Analytics');

  return (
    <div className="sidebar">
      <div className="brand-section">
        <div className="brand-icon">
          <Database size={28} />
        </div>
        <h1 className="brand-title">Analytics Agent</h1>
      </div>

      <div className="nav-section">
        <div className={`nav-item ${activeTab === 'Overview' ? 'active' : ''}`} onClick={() => setActiveTab('Overview')}>
          <LayoutDashboard size={18} />
          Overview
        </div>
        <div className={`nav-item ${activeTab === 'Customers' ? 'active' : ''}`} onClick={() => setActiveTab('Customers')}>
          <Users size={18} />
          Customers
        </div>
        <div className={`nav-item ${activeTab === 'Analytics' ? 'active' : ''}`} onClick={() => setActiveTab('Analytics')}>
          <BarChart size={18} />
          Analytics
        </div>
        <div className={`nav-item ${activeTab === 'Segments' ? 'active' : ''}`} onClick={() => setActiveTab('Segments')}>
          <PieChart size={18} />
          Segments
        </div>
        <div className={`nav-item ${activeTab === 'Reports' ? 'active' : ''}`} onClick={() => setActiveTab('Reports')}>
          <FileText size={18} />
          Reports
        </div>
        <div className={`nav-item ${activeTab === 'Alerts' ? 'active' : ''}`} onClick={() => setActiveTab('Alerts')}>
          <Bell size={18} />
          Alerts
        </div>
        <div className={`nav-item ${activeTab === 'Data Sources' ? 'active' : ''}`} onClick={() => setActiveTab('Data Sources')}>
          <Database size={18} />
          Data Sources
        </div>
        <div className={`nav-item ${activeTab === 'Settings' ? 'active' : ''}`} onClick={() => setActiveTab('Settings')}>
          <Settings size={18} />
          Settings
        </div>
      </div>

      <div className="sidebar-footer">
        <div className="company-icon">
          <Building2 size={18} />
        </div>
        <div className="company-info" style={{ flex: 1 }}>
          <h4>Global Bank</h4>
          <p>Enterprise Plan</p>
        </div>
        <button 
          onClick={onClearChat}
          style={{ background: 'transparent', border: 'none', color: '#ef4444', cursor: 'pointer', padding: '0.25rem' }}
          title="Clear Chat"
        >
          <Trash2 size={16} />
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
