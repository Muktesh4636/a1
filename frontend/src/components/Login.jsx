import React, { useState } from 'react';
import api from '../services/api';

export default function Login({ onLogin, onSwitchToRegister }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await api.login(username, password);
      if (data.user && data.access) {
        onLogin(data.user);
      }
    } catch (err) {
      console.error('Login error:', err);
      setError(err.message || 'Login failed. Please check if the backend server is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto bg-white/10 rounded-lg p-6 backdrop-blur-sm">
      <h2 className="text-2xl font-bold text-white mb-4">Login</h2>
      {error && (
        <div className="bg-red-500/20 text-red-200 px-4 py-2 rounded mb-4">
          {error}
        </div>
      )}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-white mb-2">Username</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-4 py-2 rounded bg-white/20 text-white placeholder-white/50 border border-white/30 focus:outline-none focus:border-white/50"
            placeholder="Enter username"
            required
          />
        </div>
        <div>
          <label className="block text-white mb-2">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-2 rounded bg-white/20 text-white placeholder-white/50 border border-white/30 focus:outline-none focus:border-white/50"
            placeholder="Enter password"
            required
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
      <p className="text-white/80 text-center mt-4">
        Don't have an account?{' '}
        <button
          onClick={onSwitchToRegister}
          className="text-indigo-300 hover:text-indigo-200 underline"
        >
          Register
        </button>
      </p>
    </div>
  );
}

