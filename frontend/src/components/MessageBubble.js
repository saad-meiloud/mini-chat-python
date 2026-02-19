import React, { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Copy, Check, Image as ImageIcon } from 'lucide-react';
import './MessageBubble.css';

const MessageBubble = ({ message }) => {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';

  const copyToClipboard = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Detect code blocks
  const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
  const parts = [];
  let lastIndex = 0;
  let match;

  while ((match = codeBlockRegex.exec(message.content)) !== null) {
    // Add text before code block
    if (match.index > lastIndex) {
      parts.push({
        type: 'text',
        content: message.content.substring(lastIndex, match.index),
      });
    }
    // Add code block
    parts.push({
      type: 'code',
      language: match[1] || 'text',
      content: match[2],
    });
    lastIndex = match.index + match[0].length;
  }

  // Add remaining text
  if (lastIndex < message.content.length) {
    parts.push({
      type: 'text',
      content: message.content.substring(lastIndex),
    });
  }

  // If no code blocks found, treat entire message as text
  if (parts.length === 0) {
    parts.push({
      type: 'text',
      content: message.content,
    });
  }

  return (
    <div className={`message-bubble ${isUser ? 'user' : 'assistant'}`}>
      <div className="message-content">
        {message.image_path && (
          <div className="message-image">
            <img
              src={`http://localhost:8000/${message.image_path}`}
              alt="Uploaded"
              onError={(e) => {
                e.target.style.display = 'none';
              }}
            />
          </div>
        )}

        {parts.map((part, index) => {
          if (part.type === 'code') {
            return (
              <div key={index} className="code-block-wrapper">
                <div className="code-header">
                  <span className="code-language">{part.language}</span>
                  <button
                    className="copy-button"
                    onClick={copyToClipboard}
                    title="Copier"
                  >
                    {copied ? <Check size={14} /> : <Copy size={14} />}
                  </button>
                </div>
                <SyntaxHighlighter
                  language={part.language}
                  style={vscDarkPlus}
                  customStyle={{
                    margin: 0,
                    borderRadius: '0 0 8px 8px',
                  }}
                >
                  {part.content}
                </SyntaxHighlighter>
              </div>
            );
          } else {
            // Split text by newlines and render
            const lines = part.content.split('\n');
            return (
              <div key={index} className="message-text">
                {lines.map((line, lineIndex) => (
                  <React.Fragment key={lineIndex}>
                    {line}
                    {lineIndex < lines.length - 1 && <br />}
                  </React.Fragment>
                ))}
              </div>
            );
          }
        })}
      </div>
    </div>
  );
};

export default MessageBubble;
