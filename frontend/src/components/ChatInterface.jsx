import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Send, Bot, User, Sparkles } from 'lucide-react';
import PlotlyChart from './PlotlyChart';

const ChatInterface = ({ messages, isLoading, onSendMessage }) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  return (
    <div className="chat-container glass-panel">
      <div className="chat-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Sparkles size={20} color="var(--accent-color)" />
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Analytics Assistant</h2>
        </div>
        <div className="header-status">
          <div className="status-dot"></div>
          Agent Online
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div style={{ 
            display: 'flex', flexDirection: 'column', alignItems: 'center', 
            justifyContent: 'center', height: '100%', opacity: 0.6 
          }}>
            <Bot size={48} style={{ marginBottom: '1rem' }} />
            <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>How can I help you today?</h3>
            <p>Try asking to segment customers or run EDA on the dataset.</p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <div className="avatar">
              {msg.role === 'user' ? <User size={20} /> : <Bot size={20} />}
            </div>
            <div className="message-content">
              <ReactMarkdown>{msg.content}</ReactMarkdown>
              
              {/* Render charts if present */}
              {msg.charts && msg.charts.map((chartJson, cIdx) => (
                <PlotlyChart key={`chart-${cIdx}`} chartJson={chartJson} />
              ))}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message assistant">
            <div className="avatar">
              <Bot size={20} />
            </div>
            <div className="message-content" style={{ padding: '1rem' }}>
              <div className="loading-dots">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        <form onSubmit={handleSubmit} className="input-wrapper">
          <input
            type="text"
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about the banking data..."
            disabled={isLoading}
          />
          <button type="submit" className="send-btn" disabled={!input.trim() || isLoading}>
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;
