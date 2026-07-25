import React, { useState } from 'react';
import axios from 'axios';
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import './index.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => Math.random().toString(36).substring(7));

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

  return (
    <div className="app-container">
      <Sidebar 
        onQuickAction={handleSendMessage} 
        onClearChat={handleClearChat} 
      />
      <ChatInterface 
        messages={messages} 
        isLoading={isLoading} 
        onSendMessage={handleSendMessage} 
      />
    </div>
  );
}

export default App;
