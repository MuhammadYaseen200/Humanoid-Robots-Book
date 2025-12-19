/**
 * Root Component Wrapper for Docusaurus
 * Injects AuthProvider and ChatWidget globally across all pages
 */

import React from 'react';
import ChatWidget from '@site/src/components/ChatWidget';
import { AuthProvider } from '@site/src/context/AuthContext';

// ExecutionEnvironment is used to detect if we're running in browser
// This prevents SSR issues during build
import ExecutionEnvironment from '@docusaurus/ExecutionEnvironment';

interface RootProps {
  children: React.ReactNode;
}

const Root: React.FC<RootProps> = ({ children }) => {
  return (
    <AuthProvider>
      {children}
      {/* Only render ChatWidget on client-side (browser) */}
      {ExecutionEnvironment.canUseDOM && <ChatWidget />}
    </AuthProvider>
  );
};

export default Root;
