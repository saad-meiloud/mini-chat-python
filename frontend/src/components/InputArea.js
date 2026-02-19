import React, { useState, useRef, useEffect } from 'react';
import { useChat } from '../context/ChatContext';
import { Send, Image as ImageIcon, X } from 'lucide-react';
import './InputArea.css';

const InputArea = () => {
  const { sendMessage, loading, currentConversationId } = useChat();
  const [input, setInput] = useState('');
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  const handleSend = async () => {
    if ((!input.trim() && !selectedImage) || loading) return;

    await sendMessage(input.trim(), selectedImage);
    setInput('');
    setSelectedImage(null);
    setImagePreview(null);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleImageSelect = (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const removeImage = () => {
    setSelectedImage(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="input-area">
      {imagePreview && (
        <div className="image-preview">
          <img src={imagePreview} alt="Preview" />
          <button className="remove-image" onClick={removeImage}>
            <X size={16} />
          </button>
        </div>
      )}

      <div className="input-container">
        <div className="input-wrapper">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={
              currentConversationId
                ? "Tapez votre message..."
                : "Commencez une nouvelle conversation..."
            }
            rows={1}
            className="message-input"
            disabled={loading}
          />
          <div className="input-actions">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleImageSelect}
              className="file-input"
              id="image-upload"
              disabled={loading}
            />
            <label htmlFor="image-upload" className="image-button" title="Téléverser une image">
              <ImageIcon size={20} />
            </label>
            <button
              onClick={handleSend}
              disabled={(!input.trim() && !selectedImage) || loading}
              className="send-button"
              title="Envoyer (Entrée)"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InputArea;
