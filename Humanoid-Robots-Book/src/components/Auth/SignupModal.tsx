/**
 * Signup Modal Component
 * Feature: 003-better-auth
 *
 * 2-step signup wizard with hardware profiling (THE 50-POINT FEATURE)
 * Step 1: Basic credentials (name, email, password)
 * Step 2: Hardware profile (GPU, RAM, languages, experience)
 */

import React, { useState } from 'react';
import { useAuth } from '@site/src/context/AuthContext';
import { X, ArrowLeft, ArrowRight, Cpu, Check } from 'lucide-react';

interface SignupModalProps {
  onClose: () => void;
}

// Hardware profiling options (THE 50-POINT FEATURE)
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
  'JavaScript',
  'Java',
  'Rust',
  'Go',
];

const ROBOTICS_EXPERIENCE = [
  'No prior experience',
  'Beginner (0-1 years)',
  'Intermediate (1-3 years)',
  'Advanced (3+ years)',
];

export default function SignupModal({ onClose }: SignupModalProps): JSX.Element {
  const { signup } = useAuth();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  // Step 1: Basic credentials
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // Step 2: Hardware profile (THE 50-POINT FEATURE)
  const [gpuType, setGpuType] = useState('');
  const [ramCapacity, setRamCapacity] = useState('');
  const [codingLanguages, setCodingLanguages] = useState<string[]>([]);
  const [roboticsExperience, setRoboticsExperience] = useState('');

  const toggleLanguage = (lang: string) => {
    setCodingLanguages((prev) =>
      prev.includes(lang) ? prev.filter((l) => l !== lang) : [...prev, lang]
    );
  };

  const validateStep1 = (): boolean => {
    if (!name || !email || !password || !confirmPassword) {
      setError('All fields are required');
      return false;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match');
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
    if (!/[0-9]/.test(password)) {
      setError('Password must contain at least one number');
      return false;
    }
    return true;
  };

  const validateStep2 = (): boolean => {
    if (!gpuType || !ramCapacity || codingLanguages.length === 0 || !roboticsExperience) {
      setError('All hardware profile fields are required');
      return false;
    }
    return true;
  };

  const handleNext = () => {
    setError('');
    if (validateStep1()) {
      setStep(2);
    }
  };

  const handleBack = () => {
    setError('');
    setStep(1);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!validateStep2()) return;

    setLoading(true);
    try {
      await signup({
        name,
        email,
        password,
        gpu_type: gpuType,
        ram_capacity: ramCapacity,
        coding_languages: codingLanguages,
        robotics_experience: roboticsExperience,
      });

      setSuccess(true);
      setTimeout(() => {
        onClose();
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Signup failed');
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="relative w-full max-w-md rounded-2xl bg-white dark:bg-gray-900 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-gray-200 dark:border-gray-700 p-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              {success ? 'Account Created!' : 'Create Account'}
            </h2>
            {!success && (
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Step {step} of 2: {step === 1 ? 'Basic Information' : 'Hardware Profile'}
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            aria-label="Close"
          >
            <X size={20} className="text-gray-500 dark:text-gray-400" />
          </button>
        </div>

        {/* Success state */}
        {success && (
          <div className="p-8 text-center">
            <div className="mb-4 flex justify-center">
              <div className="rounded-full bg-green-100 dark:bg-green-900/20 p-4">
                <Check size={48} className="text-green-600 dark:text-green-400" />
              </div>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
              Welcome to Physical AI & Humanoid Robotics
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Your account has been created successfully!
            </p>
          </div>
        )}

        {/* Form */}
        {!success && (
          <form onSubmit={handleSubmit} className="p-6 space-y-6">
            {/* Step 1: Basic credentials */}
            {step === 1 && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Full Name
                  </label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="John Doe"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="john@example.com"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Password
                  </label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Min 8 chars, 1 uppercase, 1 number"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Confirm Password
                  </label>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Re-enter password"
                    required
                  />
                </div>
              </div>
            )}

            {/* Step 2: Hardware profile (THE 50-POINT FEATURE) */}
            {step === 2 && (
              <div className="space-y-6">
                <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400 mb-4">
                  <Cpu size={20} />
                  <span className="text-sm font-medium">
                    Help us personalize your learning experience
                  </span>
                </div>

                {/* GPU Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    GPU Type
                  </label>
                  <select
                    value={gpuType}
                    onChange={(e) => setGpuType(e.target.value)}
                    className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    RAM Capacity
                  </label>
                  <select
                    value={ramCapacity}
                    onChange={(e) => setRamCapacity(e.target.value)}
                    className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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

                {/* Coding Languages (Multi-select) */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Coding Languages (select all that apply)
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {CODING_LANGUAGES.map((lang) => (
                      <button
                        key={lang}
                        type="button"
                        onClick={() => toggleLanguage(lang)}
                        className={`px-4 py-2 rounded-lg border transition-all ${
                          codingLanguages.includes(lang)
                            ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-500 text-blue-700 dark:text-blue-300 font-medium'
                            : 'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                        }`}
                      >
                        {lang}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Robotics Experience */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Robotics Experience
                  </label>
                  <select
                    value={roboticsExperience}
                    onChange={(e) => setRoboticsExperience(e.target.value)}
                    className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  >
                    <option value="">Select your experience...</option>
                    {ROBOTICS_EXPERIENCE.map((exp) => (
                      <option key={exp} value={exp}>
                        {exp}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            )}

            {/* Error message */}
            {error && (
              <div className="p-4 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
                <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
              </div>
            )}

            {/* Navigation buttons */}
            <div className="flex items-center justify-between pt-4">
              {step === 2 && (
                <button
                  type="button"
                  onClick={handleBack}
                  className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
                >
                  <ArrowLeft size={16} />
                  Back
                </button>
              )}

              {step === 1 && (
                <button
                  type="button"
                  onClick={handleNext}
                  className="ml-auto flex items-center gap-2 px-6 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors font-medium"
                >
                  Next: Hardware Profile
                  <ArrowRight size={16} />
                </button>
              )}

              {step === 2 && (
                <button
                  type="submit"
                  disabled={loading}
                  className="ml-auto px-6 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
                >
                  {loading ? 'Creating Account...' : 'Create Account'}
                </button>
              )}
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
