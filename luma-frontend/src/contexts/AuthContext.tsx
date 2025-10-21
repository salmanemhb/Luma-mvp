import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../lib/api';

interface User {
  id: string;
  email: string;
  company_id: string;
  company_name: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (data: { email: string; password: string; company_name: string; sector?: string }) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          const response = await authAPI.me();
          setUser(response.data);
        } catch (error) {
          localStorage.removeItem('token');
          setToken(null);
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, [token]);

  const login = async (email: string, password: string) => {
    const response = await authAPI.login(email, password);
    const { access_token, user_id, company_id } = response.data;
    
    localStorage.setItem('token', access_token);
    setToken(access_token);
    
    // Fetch full user data
    const userResponse = await authAPI.me();
    setUser(userResponse.data);
  };

  const signup = async (data: { email: string; password: string; company_name: string; sector?: string }) => {
    const response = await authAPI.signup(data);
    const { access_token } = response.data;
    
    localStorage.setItem('token', access_token);
    setToken(access_token);
    
    const userResponse = await authAPI.me();
    setUser(userResponse.data);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, signup, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
