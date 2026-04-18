/**
 * Root Component Wrapper for Docusaurus
 * Provides AuthContext and injects ChatWidget globally across all pages
 */

import React from 'react';
import { AuthProvider } from '@site/src/context/AuthContext';
import ChatWidget from '@site/src/components/ChatWidget';
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
