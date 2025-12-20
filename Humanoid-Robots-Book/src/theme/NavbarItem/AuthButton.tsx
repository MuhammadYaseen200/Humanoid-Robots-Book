/**
 * AuthButton Component
 * Feature: 003-better-auth
 *
 * Displays authentication controls in the navbar.
 * - When unauthenticated: Shows "Sign In" and "Sign Up" buttons
 * - When authenticated: Shows user name, GPU type, and "Sign Out" button
 */

import React, { useState } from 'react';
import { useAuth } from '@site/src/context/AuthContext';
import SignupModal from '@site/src/components/Auth/SignupModal';
import SigninModal from '@site/src/components/Auth/SigninModal';
import { User, LogOut } from 'lucide-react';

export default function AuthButton(): JSX.Element {
  const { user, signout } = useAuth();
  const [showSignup, setShowSignup] = useState(false);
  const [showSignin, setShowSignin] = useState(false);

  const handleSignout = () => {
    signout();
  };

  // Authenticated state - show user profile and signout
  if (user) {
    return (
      <div className="flex items-center gap-3">
        {/* User profile info - hidden on mobile */}
        <div className="hidden md:flex flex-col items-end">
          <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
            {user.name}
          </span>
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {user.gpu_type}
          </span>
        </div>

        {/* Profile icon */}
        <button
          className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          aria-label="My Profile"
          title="My Profile"
        >
          <User size={20} className="text-gray-700 dark:text-gray-300" />
        </button>

        {/* Sign out button */}
        <button
          onClick={handleSignout}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors text-sm font-medium"
          aria-label="Sign Out"
        >
          <LogOut size={16} />
          <span className="hidden sm:inline">Sign Out</span>
        </button>
      </div>
    );
  }

  // Unauthenticated state - show sign in and sign up buttons
  return (
    <>
      <div className="flex items-center gap-2">
        {/* Sign In button */}
        <button
          onClick={() => setShowSignin(true)}
          className="px-4 py-1.5 rounded-lg bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors text-sm font-medium"
        >
          Sign In
        </button>

        {/* Sign Up button */}
        <button
          onClick={() => setShowSignup(true)}
          className="px-4 py-1.5 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors text-sm font-medium"
        >
          Sign Up
        </button>
      </div>

      {/* Modals */}
      {showSignup && <SignupModal onClose={() => setShowSignup(false)} />}
      {showSignin && <SigninModal onClose={() => setShowSignin(false)} />}
    </>
  );
}
