import React, { createContext, useContext, ReactNode } from 'react';

/**
 * Mock AuthContext for Feature 004 MVP
 *
 * This is a temporary mock until Feature 003-better-auth is fully integrated.
 * Replace this file with the actual AuthContext from Feature 003 when available.
 */

interface User {
  id: string;
  email: string;
  name?: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  // Mock user state (always unauthenticated for MVP testing)
  const user = null;
  const isAuthenticated = false;

  const login = async (email: string, password: string) => {
    // Mock login function
    console.log('Mock login called:', email);
  };

  const logout = () => {
    // Mock logout function
    console.log('Mock logout called');
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
