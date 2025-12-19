/**
 * Signup Modal with Hardware Profiling Wizard
 * Feature: 003-better-auth
 *
 * Two-step signup process:
 * Step 1: Basic credentials (email, password, name)
 * Step 2: Hardware profiling (THE 50-POINT BONUS FEATURE)
 */

import React, { useState } from 'react';
import { X, ChevronRight, ChevronLeft, Check, Cpu, HardDrive, Code, Award } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface SignupModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

// Hardware options (matching backend validation)
const GPU_OPTIONS = [
  'No GPU',
  'NVIDIA RTX 3060',
  'NVIDIA RTX 4070 Ti',
  'NVIDIA RTX 4090',
  'Apple M1/M2/M3',
  'Other',
];

const RAM_OPTIONS = [
  'Less than 8GB',
  '8-16GB',
  '16-32GB',
  'More than 32GB',
];

const CODING_LANGUAGES = [
  'Python',
  'C++',
  'JavaScript/TypeScript',
  'Rust',
  'Java',
  'Other',
];

const ROBOTICS_EXPERIENCE = [
  'No prior experience',
  'Beginner (0-1 years)',
  'Intermediate (1-3 years)',
  'Advanced (3+ years)',
];

export default function SignupModal({ isOpen, onClose, onSuccess }: SignupModalProps) {
  const { signup } = useAuth();

  // Form state
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // Step 1: Basic credentials
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [name, setName] = useState('');

  // Step 2: Hardware profile
  const [gpuType, setGpuType] = useState('');
  const [ramCapacity, setRamCapacity] = useState('');
  const [codingLanguages, setCodingLanguages] = useState<string[]>([]);
  const [roboticsExperience, setRoboticsExperience] = useState('');

  // Reset form
  const resetForm = () => {
    setStep(1);
    setEmail('');
    setPassword('');
    setConfirmPassword('');
    setName('');
    setGpuType('');
    setRamCapacity('');
    setCodingLanguages([]);
    setRoboticsExperience('');
    setError(null);
    setSuccess(false);
  };

  // Handle close
  const handleClose = () => {
    resetForm();
    onClose();
  };

  // Validate Step 1
  const validateStep1 = (): boolean => {
    if (!email || !password || !name) {
      setError('All fields are required');
      return false;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return false;
    }

    if (!/[A-Z]/.test(password)) {
      setError('Password must contain at least one uppercase letter');
      return false;
    }

    if (!/[a-z]/.test(password)) {
      setError('Password must contain at least one lowercase letter');
      return false;
    }

    if (!/\d/.test(password)) {
      setError('Password must contain at least one number');
      return false;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return false;
    }

    setError(null);
    return true;
  };

  // Validate Step 2
  const validateStep2 = (): boolean => {
    if (!gpuType || !ramCapacity || codingLanguages.length === 0 || !roboticsExperience) {
      setError('Please complete all hardware profile questions');
      return false;
    }

    setError(null);
    return true;
  };

  // Go to Step 2
  const goToStep2 = () => {
    if (validateStep1()) {
      setStep(2);
    }
  };

  // Toggle coding language selection
  const toggleLanguage = (lang: string) => {
    if (codingLanguages.includes(lang)) {
      setCodingLanguages(codingLanguages.filter((l) => l !== lang));
    } else {
      setCodingLanguages([...codingLanguages, lang]);
    }
  };

  // Submit signup
  const handleSubmit = async () => {
    if (!validateStep2()) return;

    setLoading(true);
    setError(null);

    try {
      await signup({
        email,
        password,
        name,
        gpu_type: gpuType,
        ram_capacity: ramCapacity,
        coding_languages: codingLanguages,
        robotics_experience: roboticsExperience,
      });

      setSuccess(true);
      setTimeout(() => {
        if (onSuccess) onSuccess();
        handleClose();
      }, 2000);
    } catch (err: any) {
      setError(err.message || 'Signup failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Create Account</h2>
            <p className="text-sm text-gray-600 mt-1">
              {step === 1 ? 'Step 1 of 2: Basic Information' : 'Step 2 of 2: Hardware Profile'}
            </p>
          </div>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="Close"
          >
            <X size={24} />
          </button>
        </div>

        {/* Success State */}
        {success && (
          <div className="px-6 py-12 text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Check size={32} className="text-green-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Account Created!</h3>
            <p className="text-gray-600">Welcome to Physical AI & Humanoid Robotics</p>
          </div>
        )}

        {/* Form */}
        {!success && (
          <div className="px-6 py-6">
            {/* Error Message */}
            {error && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}

            {/* Step 1: Basic Credentials */}
            {step === 1 && (
              <div className="space-y-4">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                    Full Name
                  </label>
                  <input
                    type="text"
                    id="name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="John Doe"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                    Email Address
                  </label>
                  <input
                    type="email"
                    id="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="you@example.com"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                    Password
                  </label>
                  <input
                    type="password"
                    id="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Min 8 chars, uppercase, lowercase, number"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
                    Confirm Password
                  </label>
                  <input
                    type="password"
                    id="confirmPassword"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Re-enter your password"
                    required
                  />
                </div>

                <button
                  onClick={goToStep2}
                  className="w-full bg-blue-600 text-white py-3 px-4 rounded-md font-medium hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
                >
                  Next: Hardware Profile
                  <ChevronRight size={20} />
                </button>
              </div>
            )}

            {/* Step 2: Hardware Profile (THE 50-POINT BONUS FEATURE) */}
            {step === 2 && (
              <div className="space-y-6">
                {/* GPU Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                    <Cpu size={18} className="text-blue-600" />
                    GPU Type
                  </label>
                  <select
                    value={gpuType}
                    onChange={(e) => setGpuType(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  >
                    <option value="">Select your GPU...</option>
                    {GPU_OPTIONS.map((gpu) => (
                      <option key={gpu} value={gpu}>
                        {gpu}
                      </option>
                    ))}
                  </select>
                </div>

                {/* RAM Capacity */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                    <HardDrive size={18} className="text-green-600" />
                    RAM Capacity
                  </label>
                  <select
                    value={ramCapacity}
                    onChange={(e) => setRamCapacity(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  >
                    <option value="">Select your RAM...</option>
                    {RAM_OPTIONS.map((ram) => (
                      <option key={ram} value={ram}>
                        {ram}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Coding Languages */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                    <Code size={18} className="text-purple-600" />
                    Coding Languages (Select all that apply)
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {CODING_LANGUAGES.map((lang) => (
                      <button
                        key={lang}
                        type="button"
                        onClick={() => toggleLanguage(lang)}
                        className={`px-4 py-2 rounded-md border-2 transition-all ${
                          codingLanguages.includes(lang)
                            ? 'bg-blue-50 border-blue-500 text-blue-700'
                            : 'bg-white border-gray-300 text-gray-700 hover:border-blue-300'
                        }`}
                      >
                        {lang}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Robotics Experience */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                    <Award size={18} className="text-orange-600" />
                    Robotics Experience
                  </label>
                  <select
                    value={roboticsExperience}
                    onChange={(e) => setRoboticsExperience(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  >
                    <option value="">Select your experience level...</option>
                    {ROBOTICS_EXPERIENCE.map((exp) => (
                      <option key={exp} value={exp}>
                        {exp}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3">
                  <button
                    onClick={() => setStep(1)}
                    className="flex-1 bg-gray-100 text-gray-700 py-3 px-4 rounded-md font-medium hover:bg-gray-200 transition-colors flex items-center justify-center gap-2"
                  >
                    <ChevronLeft size={20} />
                    Back
                  </button>
                  <button
                    onClick={handleSubmit}
                    disabled={loading}
                    className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-md font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {loading ? 'Creating Account...' : 'Create Account'}
                    {!loading && <Check size={20} />}
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
