import React, { useEffect, useRef } from 'react';
import Plot from 'react-plotly.js';

const PlotlyChart = ({ chartJson }) => {
  try {
    const data = JSON.parse(chartJson);
    if (!data.chart_json) return null;
    
    const parsedData = JSON.parse(data.chart_json);
    
    // Apply transparent background to match glassmorphism theme
    const layout = {
      ...parsedData.layout,
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
      font: {
        family: 'Inter, sans-serif',
        color: '#1f2937'
      }
    };

    return (
      <div style={{ marginTop: '1rem', marginBottom: '1rem', borderRadius: '12px', overflow: 'hidden', border: '1px solid rgba(255,255,255,0.1)' }}>
        <Plot
          data={parsedData.data}
          layout={layout}
          config={{ responsive: true, displayModeBar: false }}
          style={{ width: '100%', minHeight: '400px' }}
        />
      </div>
    );
  } catch (error) {
    console.error("Failed to parse chart JSON", error);
    return null;
  }
};

export default PlotlyChart;
