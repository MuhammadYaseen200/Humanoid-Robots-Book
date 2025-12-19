/**
 * Authentication Button for Navbar
 * Feature: 003-better-auth
 *
 * Displays "Sign In" / "Sign Up" when user is not authenticated
 * Displays "My Profile" / "Logout" when user is authenticated
 */

import React, { useState } from 'react';
import { LogIn, LogOut, User, UserPlus } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import SigninModal from '../../components/Auth/SigninModal';
import SignupModal from '../../components/Auth/SignupModal';

export default function AuthButton() {
  const { user, signout } = useAuth();
  const [showSignin, setShowSignin] = useState(false);
  const [showSignup, setShowSignup] = useState(false);

  const handleSignout = () => {
    if (confirm('Are you sure you want to sign out?')) {
      signout();
    }
  };

  // Not authenticated state
  if (!user) {
    return (
      <>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowSignin(true)}
            className="px-4 py-2 text-gray-700 hover:text-blue-600 transition-colors flex items-center gap-2 font-medium"
            aria-label="Sign In"
          >
            <LogIn size={18} />
            <span className="hidden sm:inline">Sign In</span>
          </button>

          <button
            onClick={() => setShowSignup(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors flex items-center gap-2 font-medium"
            aria-label="Sign Up"
          >
            <UserPlus size={18} />
            <span className="hidden sm:inline">Sign Up</span>
          </button>
        </div>

        <SigninModal
          isOpen={showSignin}
          onClose={() => setShowSignin(false)}
          onSwitchToSignup={() => {
            setShowSignin(false);
            setShowSignup(true);
          }}
        />

        <SignupModal
          isOpen={showSignup}
          onClose={() => setShowSignup(false)}
        />
      </>
    );
  }

  // Authenticated state
  return (
    <div className="flex items-center gap-3">
      {/* User Info */}
      <div className="hidden md:flex flex-col items-end">
        <span className="text-sm font-medium text-gray-900">{user.name}</span>
        <span className="text-xs text-gray-500">{user.gpu_type}</span>
      </div>

      {/* Profile Button */}
      <button
        className="p-2 text-gray-700 hover:text-blue-600 hover:bg-gray-100 rounded-full transition-colors"
        aria-label="My Profile"
        title="My Profile"
      >
        <User size={20} />
      </button>

      {/* Logout Button */}
      <button
        onClick={handleSignout}
        className="px-3 py-2 text-gray-700 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors flex items-center gap-2"
        aria-label="Sign Out"
      >
        <LogOut size={18} />
        <span className="hidden sm:inline text-sm font-medium">Logout</span>
      </button>
    </div>
  );
}
