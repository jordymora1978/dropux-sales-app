import React, { useState, useEffect } from 'react';
import Login from './Login';
import SalesDashboard from '../App';
import apiService from '../services/api';

const AuthWrapper = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);

  useEffect(() => {
    checkAuthentication();
  }, []);

  const checkAuthentication = async () => {
    if (apiService.isAuthenticated()) {
      try {
        const response = await apiService.verifyToken();
        setUser(response.user);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Token verification failed:', error);
        setIsAuthenticated(false);
      }
    }
    setLoading(false);
  };

  const handleLoginSuccess = (loginResponse) => {
    setUser(loginResponse.user);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    apiService.logout();
    setUser(null);
    setIsAuthenticated(false);
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Verificando sesión...</p>
        
        <style jsx>{`
          .loading-container {
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: #f8f9fa;
          }

          .loading-spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #e1e5e9;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 16px;
          }

          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }

          p {
            color: #666;
            margin: 0;
          }
        `}</style>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  return <SalesDashboard user={user} onLogout={handleLogout} />;
};

export default AuthWrapper;