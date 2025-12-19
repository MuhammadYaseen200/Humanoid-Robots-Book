/**
 * Authentication Context Provider
 * Feature: 003-better-auth
 *
 * Manages JWT authentication state and user profile with hardware specs.
 * Decodes JWT to extract gpu_type and ram_capacity for content personalization.
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

// ============================================================================
// Types
// ============================================================================

interface HardwareProfile {
  gpu_type: string;
  ram_capacity: string;
  coding_languages: string[];
  robotics_experience: string;
}

interface User {
  id: string;
  email: string;
  name: string;
  gpu_type: string;
  ram_capacity: string;
  coding_languages: string[];
  robotics_experience: string;
}

interface SignupData {
  email: string;
  password: string;
  name: string;
  gpu_type: string;
  ram_capacity: string;
  coding_languages: string[];
  robotics_experience: string;
}

interface SigninData {
  email: string;
  password: string;
}

interface AuthResponse {
  success: boolean;
  message: string;
  token: string;
  user: User;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  signup: (data: SignupData) => Promise<void>;
  signin: (data: SigninData) => Promise<void>;
  signout: () => void;
  hardwareProfile: HardwareProfile | null;
}

// ============================================================================
// Context Creation
// ============================================================================

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// API Base URL - hardcoded for browser safety (Docusaurus doesn't support process.env)
// Production: Update this to your deployed API URL
const API_BASE_URL = 'http://localhost:8000/api';

// ============================================================================
// JWT Decode Utility
// ============================================================================

/**
 * Decode JWT token and extract profile claims.
 *
 * **Critical**: Extracts gpu_type and ram_capacity for immediate content personalization.
 * Token format: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.PAYLOAD.SIGNATURE
 */
function decodeJWT(token: string): User | null {
  try {
    // JWT structure: header.payload.signature
    const parts = token.split('.');
    if (parts.length !== 3) {
      console.error('Invalid JWT format');
      return null;
    }

    // Decode payload (base64url)
    const payload = parts[1];
    const base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );

    const decoded = JSON.parse(jsonPayload);

    // Extract user profile with hardware specs
    return {
      id: decoded.user_id,
      email: decoded.email,
      name: decoded.name,
      gpu_type: decoded.gpu_type,
      ram_capacity: decoded.ram_capacity,
      coding_languages: decoded.coding_languages || [],
      robotics_experience: decoded.robotics_experience,
    };
  } catch (error) {
    console.error('JWT decode error:', error);
    return null;
  }
}

// ============================================================================
// Auth Provider Component
// ============================================================================

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Hardware profile derived from user
  const hardwareProfile: HardwareProfile | null = user
    ? {
        gpu_type: user.gpu_type,
        ram_capacity: user.ram_capacity,
        coding_languages: user.coding_languages,
        robotics_experience: user.robotics_experience,
      }
    : null;

  /**
   * Initialize auth state from localStorage on mount
   */
  useEffect(() => {
    const storedToken = localStorage.getItem('auth_token');
    if (storedToken) {
      const decoded = decodeJWT(storedToken);
      if (decoded) {
        setToken(storedToken);
        setUser(decoded);
      } else {
        // Invalid token, clear it
        localStorage.removeItem('auth_token');
      }
    }
    setLoading(false);
  }, []);

  /**
   * Signup: Create new account with hardware profiling
   */
  const signup = useCallback(async (data: SignupData): Promise<void> => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Signup failed');
      }

      const result: AuthResponse = await response.json();

      // Store token and decode user
      localStorage.setItem('auth_token', result.token);
      const decoded = decodeJWT(result.token);

      if (decoded) {
        setToken(result.token);
        setUser(decoded);
      }
    } catch (error) {
      console.error('Signup error:', error);
      throw error;
    }
  }, []);

  /**
   * Signin: Authenticate existing user
   */
  const signin = useCallback(async (data: SigninData): Promise<void> => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/signin`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Signin failed');
      }

      const result: AuthResponse = await response.json();

      // Store token and decode user
      localStorage.setItem('auth_token', result.token);
      const decoded = decodeJWT(result.token);

      if (decoded) {
        setToken(result.token);
        setUser(decoded);
      }
    } catch (error) {
      console.error('Signin error:', error);
      throw error;
    }
  }, []);

  /**
   * Signout: Clear auth state
   */
  const signout = useCallback(() => {
    localStorage.removeItem('auth_token');
    setToken(null);
    setUser(null);

    // Optional: Call backend signout endpoint for logging
    if (token) {
      fetch(`${API_BASE_URL}/auth/signout`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }).catch((err) => console.error('Signout logging error:', err));
    }
  }, [token]);

  const value: AuthContextType = {
    user,
    token,
    loading,
    signup,
    signin,
    signout,
    hardwareProfile,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// ============================================================================
// useAuth Hook
// ============================================================================

/**
 * Hook to access auth context.
 *
 * Usage:
 * ```tsx
 * const { user, hardwareProfile, signin, signout } = useAuth();
 *
 * if (hardwareProfile?.gpu_type === 'No GPU') {
 *   // Show cloud-based simulation guide
 * }
 * ```
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
