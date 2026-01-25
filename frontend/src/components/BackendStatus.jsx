import React, { useState, useEffect } from 'react';
import api from '../services/api';

export default function BackendStatus() {
  const [isConnected, setIsConnected] = useState(false);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    checkBackend();
    const interval = setInterval(checkBackend, 5000); // Check every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const checkBackend = async () => {
    try {
      // Use the API endpoint through the Vite proxy
      const apiUrl = import.meta.env.VITE_API_URL || '/api';
      const response = await fetch(`${apiUrl}/auth/login/`, {
        method: 'OPTIONS',
        mode: 'cors',
      });
      // 200, 204, or 405 are all OK - they mean the server is responding
      if (response.ok || response.status === 200 || response.status === 204 || response.status === 405) {
        setIsConnected(true);
        setChecking(false);
        return;
      }
    } catch (err) {
      console.error('Backend check error:', err);
    }
    setIsConnected(false);
    setChecking(false);
  };

  if (checking) {
    return null;
  }

  if (!isConnected) {
    return (
      <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-4 mb-4">
        <div className="flex items-center gap-2">
          <span className="text-red-400 text-xl">⚠️</span>
          <div>
            <p className="text-red-200 font-semibold">Backend Server Not Running</p>
            <p className="text-red-300 text-sm mt-1">
              Please start the Django backend server:
            </p>
            <div className="mt-2 bg-black/30 rounded p-2 text-xs text-red-100 font-mono">
              <p>cd backend</p>
              <p>python manage.py runserver</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-green-500/20 border border-green-500/50 rounded-lg p-2 mb-4">
      <div className="flex items-center gap-2">
        <span className="text-green-400">✅</span>
        <p className="text-green-200 text-sm">Backend server is running</p>
      </div>
    </div>
  );
}





