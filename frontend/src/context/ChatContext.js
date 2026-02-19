import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const ChatContext = createContext();

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};

export const ChatProvider = ({ children }) => {
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
  }, []);

  // Load messages when conversation changes
  useEffect(() => {
    if (currentConversationId) {
      loadMessages(currentConversationId);
    } else {
      setMessages([]);
    }
  }, [currentConversationId]);

  const loadConversations = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/conversations`);
      setConversations(response.data);
    } catch (err) {
      console.error('Error loading conversations:', err);
      setError('Erreur lors du chargement des conversations');
    }
  };

  const loadMessages = async (conversationId) => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/conversations/${conversationId}/messages`
      );
      setMessages(response.data);
    } catch (err) {
      console.error('Error loading messages:', err);
      setError('Erreur lors du chargement des messages');
    }
  };

  const sendMessage = async (content, imageFile = null) => {
    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('content', content);
      if (currentConversationId) {
        formData.append('conversation_id', currentConversationId);
      }
      if (imageFile) {
        formData.append('image', imageFile);
      }

      const response = await axios.post(
        `${API_BASE_URL}/api/chat`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      // Add user message and bot response to messages
      const newMessages = [...messages];
      
      // Find user message (should be the last one before bot response)
      // Actually, we need to reload messages to get the complete conversation
      await loadMessages(response.data.conversation.id);
      
      // Update current conversation if it was a new one
      if (!currentConversationId) {
        setCurrentConversationId(response.data.conversation.id);
        await loadConversations();
      }

      setLoading(false);
    } catch (err) {
      console.error('Error sending message:', err);
      setError(err.response?.data?.detail || 'Erreur lors de l\'envoi du message');
      setLoading(false);
    }
  };

  const createNewConversation = async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/conversations/new`);
      setCurrentConversationId(response.data.id);
      setMessages([]);
      await loadConversations();
    } catch (err) {
      console.error('Error creating conversation:', err);
      setError('Erreur lors de la création de la conversation');
    }
  };

  const selectConversation = (conversationId) => {
    setCurrentConversationId(conversationId);
  };

  const deleteConversation = async (conversationId) => {
    try {
      await axios.delete(`${API_BASE_URL}/api/conversations/${conversationId}`);
      if (currentConversationId === conversationId) {
        setCurrentConversationId(null);
        setMessages([]);
      }
      await loadConversations();
    } catch (err) {
      console.error('Error deleting conversation:', err);
      setError('Erreur lors de la suppression de la conversation');
    }
  };

  const updateConversationTitle = async (conversationId, title) => {
    try {
      const formData = new FormData();
      formData.append('title', title);
      await axios.put(`${API_BASE_URL}/api/conversations/${conversationId}`, formData);
      await loadConversations();
    } catch (err) {
      console.error('Error updating conversation title:', err);
      setError('Erreur lors de la mise à jour du titre');
    }
  };

  const value = {
    conversations,
    currentConversationId,
    messages,
    loading,
    error,
    sendMessage,
    createNewConversation,
    selectConversation,
    deleteConversation,
    updateConversationTitle,
    loadConversations,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};
