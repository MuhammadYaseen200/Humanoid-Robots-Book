/**
 * E2E Test: Authentication Flow with Hardware Profiling
 * Feature: 003-better-auth
 * Test Type: End-to-End (E2E)
 *
 * Purpose: Verify the 50-point bonus feature (Hardware Profiling during Signup)
 *
 * Prerequisites:
 * - Backend running on http://localhost:8000
 * - Frontend running on http://localhost:3000
 * - Clean database state (or unique test emails)
 */

import { test, expect } from '@playwright/test';

// Test configuration
const FRONTEND_URL = 'http://localhost:3000';
const BACKEND_URL = 'http://localhost:8000';

// Test data
const TEST_USER = {
  email: `student-${Date.now()}@test.com`, // Unique email to avoid conflicts
  password: 'StrongPass1!',
  name: 'Test Student',

  // Hardware profile (THE 50-POINT BONUS FEATURE)
  gpu_type: 'NVIDIA RTX 4090',
  ram_capacity: 'More than 32GB',
  coding_languages: ['Python', 'C++'],
  robotics_experience: 'Beginner (0-1 years)',
};

test.describe('Authentication Flow - Signup with Hardware Profiling', () => {

  test.beforeEach(async ({ page }) => {
    // Navigate to homepage
    await page.goto(FRONTEND_URL);

    // Wait for page to be fully loaded
    await page.waitForLoadState('networkidle');
  });

  test('Scenario 1: Complete signup flow with hardware profiling (THE HAPPY PATH)', async ({ page }) => {
    // ========================================================================
    // STEP 1: Click "Sign Up" Button
    // ========================================================================
    console.log('Step 1: Opening signup modal...');

    const signupButton = page.getByRole('button', { name: /sign up/i });
    await expect(signupButton).toBeVisible();
    await signupButton.click();

    // Verify modal opened
    await expect(page.getByText('Create Account')).toBeVisible();
    await expect(page.getByText('Step 1 of 2: Basic Information')).toBeVisible();

    // ========================================================================
    // STEP 2: Fill Step 1 - Basic Credentials
    // ========================================================================
    console.log('Step 2: Filling basic credentials...');

    await page.getByLabel('Full Name').fill(TEST_USER.name);
    await page.getByLabel('Email Address').fill(TEST_USER.email);
    await page.getByLabel('Password', { exact: true }).fill(TEST_USER.password);
    await page.getByLabel('Confirm Password').fill(TEST_USER.password);

    // Click "Next: Hardware Profile" button
    const nextButton = page.getByRole('button', { name: /next.*hardware profile/i });
    await nextButton.click();

    // Verify we moved to Step 2
    await expect(page.getByText('Step 2 of 2: Hardware Profile')).toBeVisible();

    // ========================================================================
    // STEP 3: Fill Step 2 - Hardware Profile (THE BONUS FEATURE)
    // ========================================================================
    console.log('Step 3: Filling hardware profile (THE 50-POINT FEATURE)...');

    // Select GPU Type
    await page.getByLabel('GPU Type').selectOption(TEST_USER.gpu_type);

    // Select RAM Capacity
    await page.getByLabel('RAM Capacity').selectOption(TEST_USER.ram_capacity);

    // Select Coding Languages (multi-select buttons)
    for (const lang of TEST_USER.coding_languages) {
      const langButton = page.getByRole('button', { name: lang, exact: true });
      await langButton.click();

      // Verify button is in selected state (has blue background)
      await expect(langButton).toHaveClass(/bg-blue-50/);
    }

    // Select Robotics Experience
    await page.getByLabel('Robotics Experience').selectOption(TEST_USER.robotics_experience);

    // ========================================================================
    // STEP 4: Submit Signup
    // ========================================================================
    console.log('Step 4: Submitting signup...');

    const createAccountButton = page.getByRole('button', { name: /create account/i });
    await createAccountButton.click();

    // Wait for success state
    await expect(page.getByText('Account Created!')).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('Welcome to Physical AI & Humanoid Robotics')).toBeVisible();

    // ========================================================================
    // STEP 5: Verify Authentication State
    // ========================================================================
    console.log('Step 5: Verifying authentication state...');

    // Wait for modal to close (2 second delay in SignupModal.tsx)
    await page.waitForTimeout(2500);

    // ASSERTION 1: Verify "Sign Up" button is replaced with user info
    const signupButtonAfter = page.getByRole('button', { name: /sign up/i });
    await expect(signupButtonAfter).not.toBeVisible();

    // Should show user name or "My Profile"
    const userNameDisplay = page.getByText(TEST_USER.name);
    const profileButton = page.getByRole('button', { name: /my profile/i });
    const logoutButton = page.getByRole('button', { name: /logout/i });

    // At least one of these should be visible
    const isAuthenticated =
      await userNameDisplay.isVisible() ||
      await profileButton.isVisible() ||
      await logoutButton.isVisible();

    expect(isAuthenticated).toBeTruthy();

    // ASSERTION 2: Verify localStorage contains JWT token
    const tokenInStorage = await page.evaluate(() => {
      return localStorage.getItem('auth_token');
    });

    expect(tokenInStorage).toBeTruthy();
    expect(tokenInStorage).toMatch(/^eyJ/); // JWT tokens start with "eyJ"

    // BONUS ASSERTION: Decode JWT and verify hardware profile claims
    const decodedToken = await page.evaluate((token) => {
      const parts = token!.split('.');
      const payload = parts[1];
      const base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      return JSON.parse(jsonPayload);
    }, tokenInStorage);

    // Verify hardware profile claims in JWT
    expect(decodedToken.gpu_type).toBe(TEST_USER.gpu_type);
    expect(decodedToken.ram_capacity).toBe(TEST_USER.ram_capacity);
    expect(decodedToken.coding_languages).toEqual(TEST_USER.coding_languages);
    expect(decodedToken.robotics_experience).toBe(TEST_USER.robotics_experience);

    console.log('✅ All assertions passed! Hardware profiling feature working correctly.');
  });

  test('Scenario 2: Password validation prevents weak passwords', async ({ page }) => {
    console.log('Testing password validation...');

    await page.getByRole('button', { name: /sign up/i }).click();

    // Try weak password (no uppercase)
    await page.getByLabel('Full Name').fill('Test User');
    await page.getByLabel('Email Address').fill('test@example.com');
    await page.getByLabel('Password', { exact: true }).fill('weakpass1'); // No uppercase
    await page.getByLabel('Confirm Password').fill('weakpass1');

    await page.getByRole('button', { name: /next/i }).click();

    // Should show error message
    await expect(page.getByText(/password must contain.*uppercase/i)).toBeVisible();
  });

  test('Scenario 3: All hardware fields are required', async ({ page }) => {
    console.log('Testing hardware profile validation...');

    await page.getByRole('button', { name: /sign up/i }).click();

    // Fill Step 1
    await page.getByLabel('Full Name').fill(TEST_USER.name);
    await page.getByLabel('Email Address').fill(`incomplete-${Date.now()}@test.com`);
    await page.getByLabel('Password', { exact: true }).fill(TEST_USER.password);
    await page.getByLabel('Confirm Password').fill(TEST_USER.password);
    await page.getByRole('button', { name: /next/i }).click();

    // Try to submit without filling hardware profile
    await page.getByRole('button', { name: /create account/i }).click();

    // Should show error message
    await expect(page.getByText(/complete all hardware profile/i)).toBeVisible();
  });

  test('Scenario 4: Signin flow with existing user', async ({ page, request }) => {
    console.log('Testing signin flow...');

    // First, create a user via API
    const signupResponse = await request.post(`${BACKEND_URL}/api/auth/signup`, {
      data: {
        email: `signin-test-${Date.now()}@test.com`,
        password: TEST_USER.password,
        name: 'Signin Test User',
        gpu_type: 'NVIDIA RTX 3060',
        ram_capacity: '16-32GB',
        coding_languages: ['Python'],
        robotics_experience: 'No prior experience',
      },
    });

    expect(signupResponse.ok()).toBeTruthy();
    const signupData = await signupResponse.json();

    // Now test signin
    await page.getByRole('button', { name: /sign in/i }).click();

    await page.getByLabel('Email Address').fill(signupData.user.email);
    await page.getByLabel('Password').fill(TEST_USER.password);
    await page.getByRole('button', { name: /sign in/i, exact: true }).click();

    // Wait for signin to complete
    await page.waitForTimeout(2000);

    // Verify authentication
    const tokenAfterSignin = await page.evaluate(() => localStorage.getItem('auth_token'));
    expect(tokenAfterSignin).toBeTruthy();
  });

  test('Scenario 5: Signout clears authentication state', async ({ page }) => {
    console.log('Testing signout flow...');

    // Manually set auth token to simulate logged-in state
    await page.evaluate((token) => {
      localStorage.setItem('auth_token', token);
    }, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXItaWQiLCJ1c2VyX2lkIjoidGVzdC11c2VyLWlkIiwiZW1haWwiOiJ0ZXN0QGV4YW1wbGUuY29tIiwibmFtZSI6IlRlc3QgVXNlciIsImdwdV90eXBlIjoiTlZJRElBIFJUWCAzMDYwIiwicmFtX2NhcGFjaXR5IjoiMTYtMzJHQiIsImNvZGluZ19sYW5ndWFnZXMiOlsiUHl0aG9uIl0sInJvYm90aWNzX2V4cGVyaWVuY2UiOiJCZWdpbm5lciJ9.fake-signature');

    // Reload to trigger auth context initialization
    await page.reload();
    await page.waitForLoadState('networkidle');

    // Click logout
    const logoutButton = page.getByRole('button', { name: /logout/i });
    await logoutButton.click();

    // Confirm dialog (if exists)
    page.on('dialog', dialog => dialog.accept());

    // Verify token is removed
    const tokenAfterLogout = await page.evaluate(() => localStorage.getItem('auth_token'));
    expect(tokenAfterLogout).toBeNull();

    // Verify "Sign In" button is visible again
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
  });
});

// ============================================================================
// API-Level Tests (Backend Verification)
// ============================================================================

test.describe('API Tests - Authentication Endpoints', () => {

  test('API: POST /api/auth/signup creates user with hardware profile', async ({ request }) => {
    const response = await request.post(`${BACKEND_URL}/api/auth/signup`, {
      data: {
        email: `api-test-${Date.now()}@test.com`,
        password: 'ApiTest123!',
        name: 'API Test User',
        gpu_type: 'NVIDIA RTX 4070 Ti',
        ram_capacity: '16-32GB',
        coding_languages: ['Python', 'Rust'],
        robotics_experience: 'Intermediate (1-3 years)',
      },
    });

    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.success).toBe(true);
    expect(data.token).toBeTruthy();
    expect(data.user.gpu_type).toBe('NVIDIA RTX 4070 Ti');
    expect(data.user.ram_capacity).toBe('16-32GB');
    expect(data.user.coding_languages).toEqual(['Python', 'Rust']);
  });

  test('API: POST /api/auth/signin returns JWT with profile claims', async ({ request }) => {
    // First create a user
    const signupResponse = await request.post(`${BACKEND_URL}/api/auth/signup`, {
      data: {
        email: `signin-api-${Date.now()}@test.com`,
        password: 'SigninTest123!',
        name: 'Signin API User',
        gpu_type: 'Apple M1/M2/M3',
        ram_capacity: '8-16GB',
        coding_languages: ['JavaScript/TypeScript'],
        robotics_experience: 'Advanced (3+ years)',
      },
    });

    const signupData = await signupResponse.json();

    // Now signin
    const signinResponse = await request.post(`${BACKEND_URL}/api/auth/signin`, {
      data: {
        email: signupData.user.email,
        password: 'SigninTest123!',
      },
    });

    expect(signinResponse.ok()).toBeTruthy();

    const signinData = await signinResponse.json();
    expect(signinData.success).toBe(true);
    expect(signinData.token).toBeTruthy();
    expect(signinData.user.gpu_type).toBe('Apple M1/M2/M3');
  });

  test('API: GET /api/profile/me returns user profile', async ({ request }) => {
    // Create user and get token
    const signupResponse = await request.post(`${BACKEND_URL}/api/auth/signup`, {
      data: {
        email: `profile-test-${Date.now()}@test.com`,
        password: 'ProfileTest123!',
        name: 'Profile Test User',
        gpu_type: 'No GPU',
        ram_capacity: 'Less than 8GB',
        coding_languages: ['Java'],
        robotics_experience: 'No prior experience',
      },
    });

    const signupData = await signupResponse.json();
    const token = signupData.token;

    // Get profile
    const profileResponse = await request.get(`${BACKEND_URL}/api/profile/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    expect(profileResponse.ok()).toBeTruthy();

    const profileData = await profileResponse.json();
    expect(profileData.gpu_type).toBe('No GPU');
    expect(profileData.ram_capacity).toBe('Less than 8GB');
  });
});
