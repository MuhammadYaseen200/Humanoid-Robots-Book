import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// Language type: English or Urdu
type Locale = 'en' | 'ur';

// Context interface
interface LanguageContextType {
  locale: Locale;
  setLocale: (locale: Locale) => void;
}

// Navbar translations (English ↔ Urdu)
export const navbarTranslations: Record<Locale, Record<string, string>> = {
  en: {
    home: 'Home',
    about: 'About',
    docs: 'Docs',
    signIn: 'Sign In',
    signUp: 'Sign Up',
    signOut: 'Sign Out',
    getStarted: 'Get Started',
    continueLearn: 'Continue Learning',
  },
  ur: {
    home: 'Ghar',
    about: 'Hamara Bare Main',
    docs: 'Kitabain',
    signIn: 'Dakhil Hon',
    signUp: 'Shamil Hon',
    signOut: 'Nikal Jayen',
    getStarted: 'Shuru Karein',
    continueLearn: 'Seekhna Jari Rakhein',
  },
};

// Create context
const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

// Provider component
export function LanguageProvider({ children }: { children: ReactNode }) {
  // Initialize locale from localStorage or default to English
  const [locale, setLocaleState] = useState<Locale>(() => {
    // Only access localStorage in browser (not during SSR)
    if (typeof window === 'undefined') {
      return 'en';
    }

    try {
      const saved = localStorage.getItem('locale');
      if (saved === 'en' || saved === 'ur') {
        return saved;
      }
    } catch (error) {
      console.warn('localStorage unavailable, defaulting to English', error);
    }
    return 'en';
  });

  // Update function that persists to localStorage
  const setLocale = (newLocale: Locale) => {
    setLocaleState(newLocale);

    // Persist to localStorage (graceful degradation if unavailable)
    if (typeof window !== 'undefined') {
      try {
        localStorage.setItem('locale', newLocale);
      } catch (error) {
        console.warn('Failed to persist language preference', error);
      }
    }
  };

  return (
    <LanguageContext.Provider value={{ locale, setLocale }}>
      {children}
    </LanguageContext.Provider>
  );
}

// Custom hook for consuming context
export function useLanguageContext() {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguageContext must be used within a LanguageProvider');
  }
  return context;
}
