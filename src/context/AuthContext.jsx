import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { checkAuthStatus as apiCheckAuth, login as apiLogin, logout as apiLogout } from '../api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if a valid token exists in localStorage
    apiCheckAuth()
      .then(({ data }) => {
        setIsLoggedIn(data.logged_in || false);
      })
      .catch(() => setIsLoggedIn(false))
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (username, password) => {
    const result = await apiLogin(username, password);
    if (result.ok && result.data.token) {
      setIsLoggedIn(true);
    }
    return result;
  }, []);

  const logout = useCallback(async () => {
    await apiLogout();
    setIsLoggedIn(false);
  }, []);

  return (
    <AuthContext.Provider value={{ isLoggedIn, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
