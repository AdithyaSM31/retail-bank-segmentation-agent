import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Send, Sparkles, Trash2 } from 'lucide-react';

const ChatInterface = ({ messages, isLoading, onSendMessage, onClearChat }) => {
  const [input, setInput] = useState('');
  const chatMessagesRef = useRef(null);

  const scrollToBottom = () => {
    if (chatMessagesRef.current) {
      chatMessagesRef.current.scrollTo({
        top: chatMessagesRef.current.scrollHeight,
        behavior: 'smooth'
      });
    }
  };

  useEffect(() => {
    if (isLoading) {
      scrollToBottom();
    }
  }, [isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="header-title">
          <Sparkles size={20} color="var(--accent-blue)" />
          AI Assistant
          <div className="header-status" style={{ marginLeft: '0.5rem' }}>
            <div className="status-dot"></div>
            Online
          </div>
        </div>
        <div style={{ display: 'flex', gap: '1rem', color: 'var(--text-muted)' }}>
          <Trash2 size={18} style={{ cursor: 'pointer' }} onClick={onClearChat} title="Clear Chat" />
        </div>
      </div>

      <div className="chat-messages" ref={chatMessagesRef}>
        {messages.length === 0 && (
          <div style={{ 
            display: 'flex', flexDirection: 'column', alignItems: 'center', 
            justifyContent: 'center', height: '100%', opacity: 0.6 
          }}>
            <Sparkles size={48} color="var(--accent-blue)" style={{ marginBottom: '1rem' }} />
            <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>Hello! I'm your AI data assistant.</h3>
            <p>How can I help you today?</p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <div className="avatar">
              <Sparkles size={16} />
            </div>
            <div className="message-content">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message assistant">
            <div className="avatar">
              <Sparkles size={16} />
            </div>
            <div className="message-content">
              Analyzing data...
            </div>
          </div>
        )}
      </div>

      <div className="input-area">
        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Try asking</div>
        <div className="suggestion-chips">
          <div className="chip" onClick={() => onSendMessage("Top 10 high value customers")}>Top 10 high value customers</div>
          <div className="chip" onClick={() => onSendMessage("Churn risk analysis")}>Churn risk analysis</div>
          <div className="chip" onClick={() => onSendMessage("Monthly trends")}>Monthly trends</div>
          <div className="chip" onClick={() => onSendMessage("Segment customers by balance and transaction frequency")}>Segment customers</div>
        </div>
        
        <form onSubmit={handleSubmit} className="input-wrapper">
          <Sparkles size={18} color="var(--accent-blue)" style={{ margin: '0 0.25rem' }} />
          <input
            type="text"
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your data..."
            disabled={isLoading}
          />
          <button type="submit" className="send-btn" disabled={!input.trim() || isLoading}>
            <Send size={16} />
          </button>
        </form>
        <div style={{ textAlign: 'center', fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.75rem' }}>
          AI responses may contain inaccuracies. Verify important information.
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
