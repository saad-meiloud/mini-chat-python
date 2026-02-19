import React, { useEffect, useRef } from 'react';
import { useChat } from '../context/ChatContext';
import MessageBubble from './MessageBubble';
import { Loader } from 'lucide-react';
import './ChatArea.css';

const ChatArea = () => {
  const { messages, loading, currentConversationId } = useChat();
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  return (
    <div className="chat-area">
      {messages.length === 0 && !loading && (
        <div className="empty-chat">
          <h1>Mini Chatbot</h1>
          <p>Commencez une nouvelle conversation en envoyant un message</p>
          <div className="features">
            <div className="feature">
              <span>💬</span>
              <p>Chat intelligent multilingue</p>
            </div>
            <div className="feature">
              <span>🖼️</span>
              <p>Analyse d'images</p>
            </div>
            <div className="feature">
              <span>📝</span>
              <p>Historique des conversations</p>
            </div>
          </div>
        </div>
      )}

      <div className="messages-container">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        {loading && (
          <div className="loading-indicator">
            <Loader className="spinner" size={20} />
            <span>Le bot est en train d'écrire...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default ChatArea;
