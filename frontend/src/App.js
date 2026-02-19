import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import InputArea from './components/InputArea';
import { ChatProvider } from './context/ChatContext';
import './App.css';

function App() {
  const [darkMode, setDarkMode] = useState(true);

  useEffect(() => {
    // Load dark mode preference from localStorage
    const savedDarkMode = localStorage.getItem('darkMode');
    if (savedDarkMode !== null) {
      setDarkMode(savedDarkMode === 'true');
    }
  }, []);

  useEffect(() => {
    // Apply dark mode class
    document.body.className = darkMode ? 'dark-mode' : 'light-mode';
    localStorage.setItem('darkMode', darkMode);
  }, [darkMode]);

  return (
    <ChatProvider>
      <div className={`app ${darkMode ? 'dark' : 'light'}`}>
        <Sidebar darkMode={darkMode} setDarkMode={setDarkMode} />
        <div className="main-content">
          <ChatArea />
          <InputArea />
        </div>
      </div>
    </ChatProvider>
  );
}

export default App;
