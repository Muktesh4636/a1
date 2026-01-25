import React, { useState, useEffect } from 'react';
import Login from './components/Login';
import Register from './components/Register';
import Profile from './components/Profile';
import Game from './components/Game';
import BackendStatus from './components/BackendStatus';
import api from './services/api';

function App() {
  const [user, setUser] = useState(null);
  const [wallet, setWallet] = useState(null);
  const [showRegister, setShowRegister] = useState(false);
  const [currentView, setCurrentView] = useState('game'); // 'game' or 'profile'

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('access_token');
    if (token) {
      loadUser();
      loadWallet();
    }
  }, []);

  const loadUser = async () => {
    try {
      const userData = await api.getProfile();
      setUser(userData);
    } catch (err) {
      console.error('Failed to load user:', err);
      api.logout();
      setUser(null);
    }
  };

  const loadWallet = async () => {
    try {
      const walletData = await api.getWallet();
      setWallet(walletData);
    } catch (err) {
      console.error('Failed to load wallet:', err);
    }
  };

  const handleLogin = (userData) => {
    setUser(userData);
    loadWallet();
    setShowRegister(false);
  };

  const handleRegister = (userData) => {
    setUser(userData);
    loadWallet();
    setShowRegister(false);
  };

  const handleLogout = () => {
    api.logout();
    setUser(null);
    setWallet(null);
  };

  // Show login/register if not authenticated
  if (!user) {
    return (
      <div className="min-h-screen bg-[#004D4D] flex items-center justify-center p-6">
        <div className="w-full max-w-md">
          <BackendStatus />
          {showRegister ? (
            <Register
              onRegister={handleRegister}
              onSwitchToLogin={() => setShowRegister(false)}
            />
          ) : (
            <Login
              onLogin={handleLogin}
              onSwitchToRegister={() => setShowRegister(true)}
            />
          )}
        </div>
      </div>
    );
  }

  // Show game/profile interface if authenticated
  return (
    <div className="min-h-screen bg-[#004D4D]">
      {/* Header */}
      <div className="bg-white/10 backdrop-blur-sm border-b border-white/20">
        <div className="max-w-7xl mx-auto p-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-6">
              <h1 className="text-2xl font-bold text-white">🎲🎲 Gundu Ata</h1>
              <nav className="flex gap-4">
                <button
                  onClick={() => setCurrentView('game')}
                  className={`px-4 py-2 rounded transition-colors ${
                    currentView === 'game'
                      ? 'bg-yellow-500 text-black font-semibold'
                      : 'text-white/80 hover:text-white hover:bg-white/10'
                  }`}
                >
                  🎮 Game
                </button>
                <button
                  onClick={() => setCurrentView('profile')}
                  className={`px-4 py-2 rounded transition-colors ${
                    currentView === 'profile'
                      ? 'bg-yellow-500 text-black font-semibold'
                      : 'text-white/80 hover:text-white hover:bg-white/10'
                  }`}
                >
                  👤 Profile
                </button>
              </nav>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-white/80">Welcome, {user.username}!</span>
              <span className="text-green-400 font-bold">₹{wallet?.balance || '0.00'}</span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {currentView === 'game' ? (
          <Game
            user={user}
            wallet={wallet}
            onRefreshWallet={loadWallet}
          />
        ) : (
          <Profile
            user={user}
            wallet={wallet}
            onLogout={handleLogout}
            onRefreshWallet={loadWallet}
          />
        )}
      </div>
    </div>
  );
}

export default App;
