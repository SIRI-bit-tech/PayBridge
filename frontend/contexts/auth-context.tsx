"use client"

import { createContext, useContext, ReactNode, useState } from 'react';

interface AuthContextType {
  auth: any;
  setAuth: (auth: any) => void;
  clearAuth: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [auth, setAuthState] = useState<any>(null);

  const setAuth = (authData: any) => {
    setAuthState(authData);
    // Optionally save to localStorage if you want to persist auth
    if (typeof window !== 'undefined') {
      if (authData) {
        localStorage.setItem('auth', JSON.stringify(authData));
      } else {
        localStorage.removeItem('auth');
      }
    }
  };

  const clearAuth = () => {
    setAuthState(null);
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth');
    }
  };

  return (
    <AuthContext.Provider value={{ auth, setAuth, clearAuth }}>
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
