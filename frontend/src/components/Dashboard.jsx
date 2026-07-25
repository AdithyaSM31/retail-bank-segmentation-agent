import React from 'react';
import { Gem, User, Moon, BarChart2, Info } from 'lucide-react';
import PlotlyChart from './PlotlyChart';

const Dashboard = ({ charts, kpiData }) => {
  const formatNum = (num) => new Intl.NumberFormat('en-IN').format(num);

  if (!kpiData) {
    return (
      <div className="dashboard-container" style={{ justifyContent: 'center', alignItems: 'center' }}>
        <div style={{ opacity: 0.5 }}>Loading customer data...</div>
      </div>
    );
  }

  const stats = kpiData;

  return (
    <div className="dashboard-container">
      {/* KPI Cards Row */}
      <div className="kpi-row">
        {/* Priority Card */}
        <div className="kpi-card">
          <div className="kpi-header">
            <div className="kpi-title">
              <div className="kpi-icon" style={{ background: 'linear-gradient(135deg, #a855f7, #6366f1)' }}>
                <Gem size={18} />
              </div>
              Priority
            </div>
            <span className="kpi-badge" style={{ backgroundColor: '#f3e8ff', color: '#7e22ce' }}>High Value</span>
          </div>
          <div className="kpi-stats">
            <div className="stat-group">
              <div className="label">Customers</div>
              <div className="value">{formatNum(stats.priority.customers)}</div>
            </div>
            <div className="stat-group">
              <div className="label">Avg. Balance</div>
              <div className="value">₹{formatNum(stats.priority.avg_balance)}</div>
            </div>
          </div>
        </div>

        {/* Regular Card */}
        <div className="kpi-card">
          <div className="kpi-header">
            <div className="kpi-title">
              <div className="kpi-icon" style={{ background: '#10b981' }}>
                <User size={18} />
              </div>
              Regular
            </div>
            <span className="kpi-badge" style={{ backgroundColor: '#d1fae5', color: '#047857' }}>Mid Value</span>
          </div>
          <div className="kpi-stats">
            <div className="stat-group">
              <div className="label">Customers</div>
              <div className="value">{formatNum(stats.regular.customers)}</div>
            </div>
            <div className="stat-group">
              <div className="label">Avg. Balance</div>
              <div className="value">₹{formatNum(stats.regular.avg_balance)}</div>
            </div>
          </div>
        </div>

        {/* Dormant Card */}
        <div className="kpi-card">
          <div className="kpi-header">
            <div className="kpi-title">
              <div className="kpi-icon" style={{ background: '#f97316' }}>
                <Moon size={18} />
              </div>
              Dormant
            </div>
            <span className="kpi-badge" style={{ backgroundColor: '#ffedd5', color: '#c2410c' }}>Low Value</span>
          </div>
          <div className="kpi-stats">
            <div className="stat-group">
              <div className="label">Customers</div>
              <div className="value">{formatNum(stats.dormant.customers)}</div>
            </div>
            <div className="stat-group">
              <div className="label">Avg. Balance</div>
              <div className="value">₹{formatNum(stats.dormant.avg_balance)}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Dynamic Charts Area */}
      <div className="charts-row">
        {charts && charts.length > 0 ? (
          charts.map((chartJson, idx) => (
            <div className="chart-card" key={`dash-chart-${idx}`}>
              <div className="chart-header">
                <BarChart2 size={18} color="var(--accent-blue)" />
                <h3>Data Visualization</h3>
                <Info size={14} color="var(--text-muted)" style={{ marginLeft: 'auto' }} />
              </div>
              <div className="chart-body">
                <PlotlyChart chartJson={chartJson} />
              </div>
            </div>
          ))
        ) : (
          <div className="chart-card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '400px', color: 'var(--text-muted)' }}>
            <BarChart2 size={48} style={{ marginBottom: '1rem', opacity: 0.3 }} />
            <h3>No Active Visualizations</h3>
            <p style={{ fontSize: '0.9rem', marginTop: '0.5rem' }}>Ask the AI Assistant to segment customers or visualize data to see charts here.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
