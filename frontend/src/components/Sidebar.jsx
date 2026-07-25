import React from 'react';
import { Database, Users, LayoutDashboard, PieChart, Info, Download, Trash2 } from 'lucide-react';

const Sidebar = ({ onQuickAction, onClearChat }) => {
  return (
    <div className="sidebar glass-panel">
      <div className="brand-section">
        <div className="brand-icon">
          <Database size={40} strokeWidth={1.5} />
        </div>
        <h1 className="brand-title">Analytics Agent</h1>
        <p className="brand-subtitle">Customer Segmentation</p>
      </div>

      <div className="nav-section">
        <h3 className="nav-title">Quick Actions</h3>
        <button 
          className="action-btn"
          onClick={() => onQuickAction("Run a comprehensive exploratory data analysis on the dataset")}
        >
          <LayoutDashboard size={18} />
          Run EDA
        </button>
        <button 
          className="action-btn"
          onClick={() => onQuickAction("Segment customers into Priority, Regular, and Dormant based on balance and transaction frequency")}
        >
          <Users size={18} />
          Segment Customers
        </button>
        <button 
          className="action-btn"
          onClick={() => onQuickAction("Create visualizations showing segment distribution")}
        >
          <PieChart size={18} />
          Visualize Data
        </button>
        <button 
          className="action-btn"
          onClick={() => onQuickAction("Explain the characteristics of each customer segment")}
        >
          <Info size={18} />
          Explain Segments
        </button>
      </div>

      <div className="nav-section">
        <h3 className="nav-title">Dataset</h3>
        <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.5rem', padding: '0 0.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            <span>Rows:</span>
            <span style={{ color: 'white', fontWeight: 500 }}>1,048,567</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>Customers:</span>
            <span style={{ color: 'white', fontWeight: 500 }}>885,112</span>
          </div>
        </div>
      </div>

      <div style={{ marginTop: 'auto' }}>
        <button 
          className="action-btn" 
          onClick={onClearChat}
          style={{ color: '#ef4444', justifyContent: 'center' }}
        >
          <Trash2 size={16} />
          Clear Chat
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
