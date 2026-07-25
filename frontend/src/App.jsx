import React, { useState } from 'react';
import axios from 'axios';
import Topbar from './components/Topbar';
import ChatInterface from './components/ChatInterface';
import Dashboard from './components/Dashboard';
import { AnimatedGridPattern } from './components/AnimatedGridPattern';
import './index.css';

function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: 'Hello! I am your Retail Bank Segmentation Agent. Ask me to segment your customers, explain segments, or recommend products based on our transactions data.',
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => Math.random().toString(36).substring(7));
  const [kpiData, setKpiData] = useState(null);

  React.useEffect(() => {
    const fetchKpi = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/kpi');
        setKpiData(response.data);
      } catch (err) {
        console.error("Failed to load KPI data", err);
      }
    };
    fetchKpi();
  }, []);

  const handleSendMessage = async (text) => {
    // Add user message to state
    const newMessages = [...messages, { role: 'user', content: text }];
    setMessages(newMessages);
    setIsLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/chat', {
        message: text,
        session_id: sessionId
      });

      // Add assistant message to state
      setMessages([...newMessages, { 
        role: 'assistant', 
        content: response.data.response,
        charts: response.data.charts
      }]);
    } catch (error) {
      console.error("Error calling API", error);
      setMessages([...newMessages, { 
        role: 'assistant', 
        content: `❌ **Error:** Could not connect to the backend API. Please ensure the FastAPI server is running on port 8000.\n\nDetails: ${error.message}`
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
  };

  // Only display charts from the most recent assistant message
  const lastAssistantMsg = [...messages].reverse().find(msg => msg.role === 'assistant');
  const activeCharts = lastAssistantMsg?.charts || [];

  return (
    <div className="app-layout">
      <div className="animated-grid-wrapper">
        <AnimatedGridPattern numSquares={40} maxOpacity={0.2} duration={3} />
      </div>
      <Topbar />
      <div className="main-content">
        <ChatInterface 
          messages={messages} 
          isLoading={isLoading} 
          onSendMessage={handleSendMessage} 
          onClearChat={handleClearChat}
        />
        <Dashboard charts={activeCharts} kpiData={kpiData} />
      </div>
    </div>
  );
}

export default App;
