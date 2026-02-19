import React, { useState } from 'react';
import { useChat } from '../context/ChatContext';
import { Plus, Trash2, Moon, Sun, MessageSquare } from 'lucide-react';
import './Sidebar.css';

const Sidebar = ({ darkMode, setDarkMode }) => {
  const {
    conversations,
    currentConversationId,
    createNewConversation,
    selectConversation,
    deleteConversation,
    updateConversationTitle,
  } = useChat();

  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState('');

  const handleNewChat = () => {
    createNewConversation();
  };

  const handleConversationClick = (id) => {
    selectConversation(id);
  };

  const handleDelete = (e, id) => {
    e.stopPropagation();
    if (window.confirm('Êtes-vous sûr de vouloir supprimer cette conversation ?')) {
      deleteConversation(id);
    }
  };

  const handleEditStart = (e, conversation) => {
    e.stopPropagation();
    setEditingId(conversation.id);
    setEditTitle(conversation.title);
  };

  const handleEditSave = (e, id) => {
    e.stopPropagation();
    if (editTitle.trim()) {
      updateConversationTitle(id, editTitle.trim());
    }
    setEditingId(null);
    setEditTitle('');
  };

  const handleEditCancel = (e) => {
    e.stopPropagation();
    setEditingId(null);
    setEditTitle('');
  };

  return (
    <div className={`sidebar ${darkMode ? 'dark' : 'light'}`}>
      <div className="sidebar-header">
        <button className="new-chat-btn" onClick={handleNewChat}>
          <Plus size={18} />
          <span>Nouvelle discussion</span>
        </button>
        <button
          className="theme-toggle"
          onClick={() => setDarkMode(!darkMode)}
          title={darkMode ? 'Mode clair' : 'Mode sombre'}
        >
          {darkMode ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </div>

      <div className="conversations-list">
        {conversations.length === 0 ? (
          <div className="empty-state">
            <MessageSquare size={48} />
            <p>Aucune conversation</p>
            <p className="hint">Créez une nouvelle discussion pour commencer</p>
          </div>
        ) : (
          conversations.map((conversation) => (
            <div
              key={conversation.id}
              className={`conversation-item ${
                currentConversationId === conversation.id ? 'active' : ''
              }`}
              onClick={() => handleConversationClick(conversation.id)}
            >
              {editingId === conversation.id ? (
                <div className="edit-conversation" onClick={(e) => e.stopPropagation()}>
                  <input
                    type="text"
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        handleEditSave(e, conversation.id);
                      } else if (e.key === 'Escape') {
                        handleEditCancel(e);
                      }
                    }}
                    autoFocus
                    className="edit-input"
                  />
                  <div className="edit-actions">
                    <button
                      className="save-btn"
                      onClick={(e) => handleEditSave(e, conversation.id)}
                    >
                      ✓
                    </button>
                    <button className="cancel-btn" onClick={handleEditCancel}>
                      ✕
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <div className="conversation-title">
                    <MessageSquare size={16} />
                    <span>{conversation.title}</span>
                  </div>
                  <div className="conversation-actions">
                    <button
                      className="edit-btn"
                      onClick={(e) => handleEditStart(e, conversation)}
                      title="Renommer"
                    >
                      ✏️
                    </button>
                    <button
                      className="delete-btn"
                      onClick={(e) => handleDelete(e, conversation.id)}
                      title="Supprimer"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Sidebar;
