import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from '../lib/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Restore session from localStorage on mount
  const restoreSession = useCallback(async () => {
    const token = localStorage.getItem('sf_token');
    if (!token) {
      setLoading(false);
      return;
    }
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    try {
      const res = await api.get('/auth/me');
      setUser(res.data);
    } catch {
      // Token expired or invalid — clear it
      localStorage.removeItem('sf_token');
      delete api.defaults.headers.common['Authorization'];
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    restoreSession();
  }, [restoreSession]);

  const login = (tokenData) => {
    localStorage.setItem('sf_token', tokenData.access_token);
    api.defaults.headers.common['Authorization'] = `Bearer ${tokenData.access_token}`;
    setUser(tokenData.user);
  };

  const logout = () => {
    localStorage.removeItem('sf_token');
    delete api.defaults.headers.common['Authorization'];
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{ user, login, logout, isAuthenticated: !!user, loading }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
