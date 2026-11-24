import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';

const RoleContext = createContext(null);

export function RoleProvider({ children }) {
  const [token, setToken] = useState(() => {
    return typeof window !== 'undefined' ? sessionStorage.getItem('linkshield_token') : null;
  });
  const [user, setUser] = useState(() => {
    try {
      const stored = typeof window !== 'undefined' ? sessionStorage.getItem('linkshield_user') : null;
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  });
  const [loading, setLoading] = useState(true);

  // Validate or restore session on mount
  useEffect(() => {
    let isMounted = true;
    const verifySession = async () => {
      const storedToken = sessionStorage.getItem('linkshield_token');
      if (!storedToken) {
        if (isMounted) {
          setUser(null);
          setToken(null);
          setLoading(false);
        }
        return;
      }

      try {
        const profile = await api.getMe();
        if (isMounted) {
          setUser(profile);
          sessionStorage.setItem('linkshield_user', JSON.stringify(profile));
          setToken(storedToken);
        }
      } catch (err) {
        console.warn('Session verification failed, clearing credentials:', err);
        if (isMounted) {
          sessionStorage.removeItem('linkshield_token');
          sessionStorage.removeItem('linkshield_user');
          setUser(null);
          setToken(null);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    verifySession();
    return () => {
      isMounted = false;
    };
  }, []);

  const login = useCallback(async (username, password) => {
    const res = await api.login(username, password);
    sessionStorage.setItem('linkshield_token', res.access_token);
    sessionStorage.setItem('linkshield_user', JSON.stringify(res.user));
    setToken(res.access_token);
    setUser(res.user);
    return res.user;
  }, []);

  const register = useCallback(async (username, password, displayName) => {
    const res = await api.register(username, password, displayName);
    sessionStorage.setItem('linkshield_token', res.access_token);
    sessionStorage.setItem('linkshield_user', JSON.stringify(res.user));
    setToken(res.access_token);
    setUser(res.user);
    return res.user;
  }, []);

  const logout = useCallback(async () => {
    try {
      await api.logout();
    } catch {
      // Continue client cleanup even if backend network call fails
    }
    sessionStorage.removeItem('linkshield_token');
    sessionStorage.removeItem('linkshield_user');
    setToken(null);
    setUser(null);
  }, []);

  const role = user?.role || null;
  const isOfficer = role === 'officer';
  const isCitizen = role === 'citizen';
  const isAuthenticated = Boolean(user && token);

  return (
    <RoleContext.Provider
      value={{
        token,
        user,
        role,
        loading,
        isAuthenticated,
        isOfficer,
        isCitizen,
        login,
        register,
        logout,
      }}
    >
      {children}
    </RoleContext.Provider>
  );
}

export function useRole() {
  const context = useContext(RoleContext);
  if (!context) {
    throw new Error('useRole must be used within a RoleProvider');
  }
  return context;
}
