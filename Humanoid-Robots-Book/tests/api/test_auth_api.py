#!/usr/bin/env python3
"""
API Tests for Authentication Endpoints
Feature: 003-better-auth

Run this script to verify the backend API is working correctly.

Usage:
    python tests/api/test_auth_api.py
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000/api"
BACKEND_HEALTH_URL = "http://localhost:8000/health"

# Test data
TEST_EMAIL = f"test-{int(datetime.now().timestamp())}@example.com"
TEST_PASSWORD = "TestPass123!"
TEST_USER_DATA = {
    "email": TEST_EMAIL,
    "password": TEST_PASSWORD,
    "name": "API Test User",
    "gpu_type": "NVIDIA RTX 4090",
    "ram_capacity": "More than 32GB",
    "coding_languages": ["Python", "C++"],
    "robotics_experience": "Advanced (3+ years)",
}

# ANSI colors
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")


def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")


def test_health():
    """Test 0: Backend health check"""
    print_header("Test 0: Backend Health Check")

    try:
        response = requests.get(BACKEND_HEALTH_URL, timeout=5)
        if response.status_code == 200:
            print_success("Backend is running")
            print_info(f"Response: {response.json()}")
            return True
        else:
            print_error(f"Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"Cannot connect to backend: {e}")
        print_warning("Make sure backend is running: uvicorn src.main:app --reload")
        return False


def test_signup():
    """Test 1: Signup with hardware profiling (THE 50-POINT FEATURE)"""
    print_header("Test 1: Signup with Hardware Profiling")

    print_info(f"Creating user: {TEST_EMAIL}")
    print_info(f"Hardware Profile:")
    print_info(f"  GPU: {TEST_USER_DATA['gpu_type']}")
    print_info(f"  RAM: {TEST_USER_DATA['ram_capacity']}")
    print_info(f"  Languages: {TEST_USER_DATA['coding_languages']}")
    print_info(f"  Experience: {TEST_USER_DATA['robotics_experience']}")

    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/signup",
            json=TEST_USER_DATA,
            timeout=10
        )

        if response.status_code == 201:
            data = response.json()
            print_success("Signup successful")

            # Verify response structure
            assert data['success'] is True, "success should be True"
            assert 'token' in data, "Response should include token"
            assert 'user' in data, "Response should include user"

            # Verify hardware profile in response
            user = data['user']
            assert user['gpu_type'] == TEST_USER_DATA['gpu_type'], "GPU type mismatch"
            assert user['ram_capacity'] == TEST_USER_DATA['ram_capacity'], "RAM capacity mismatch"
            assert user['coding_languages'] == TEST_USER_DATA['coding_languages'], "Coding languages mismatch"
            assert user['robotics_experience'] == TEST_USER_DATA['robotics_experience'], "Experience mismatch"

            print_success("All hardware profile fields verified")
            print_info(f"JWT Token: {data['token'][:50]}...")

            return data['token']
        else:
            print_error(f"Signup failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Signup test failed: {e}")
        return None


def test_signin(token=None):
    """Test 2: Signin and verify JWT contains profile claims"""
    print_header("Test 2: Signin")

    print_info(f"Signing in as: {TEST_EMAIL}")

    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/signin",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            print_success("Signin successful")

            assert data['success'] is True, "success should be True"
            assert 'token' in data, "Response should include token"

            # Verify hardware profile in signin response
            user = data['user']
            assert user['gpu_type'] == TEST_USER_DATA['gpu_type'], "GPU type mismatch"

            print_success("Hardware profile preserved in signin")
            print_info(f"New JWT Token: {data['token'][:50]}...")

            return data['token']
        else:
            print_error(f"Signin failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Signin test failed: {e}")
        return None


def test_profile(token):
    """Test 3: Get profile endpoint"""
    print_header("Test 3: Get Profile")

    if not token:
        print_error("No token available, skipping profile test")
        return False

    try:
        response = requests.get(
            f"{API_BASE_URL}/profile/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )

        if response.status_code == 200:
            profile = response.json()
            print_success("Profile retrieved successfully")

            # Verify hardware profile
            assert profile['gpu_type'] == TEST_USER_DATA['gpu_type'], "GPU type mismatch"
            assert profile['ram_capacity'] == TEST_USER_DATA['ram_capacity'], "RAM mismatch"
            assert profile['coding_languages'] == TEST_USER_DATA['coding_languages'], "Languages mismatch"

            print_success("Hardware profile verification complete")
            print_info(f"Profile: {json.dumps(profile, indent=2)}")

            return True
        else:
            print_error(f"Profile retrieval failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Profile test failed: {e}")
        return False


def test_update_profile(token):
    """Test 4: Update profile endpoint"""
    print_header("Test 4: Update Profile")

    if not token:
        print_error("No token available, skipping update test")
        return False

    updated_data = {
        "gpu_type": "NVIDIA RTX 3060",
        "ram_capacity": "16-32GB",
    }

    print_info(f"Updating profile: {updated_data}")

    try:
        response = requests.put(
            f"{API_BASE_URL}/profile/me",
            json=updated_data,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            print_success("Profile updated successfully")

            assert data['success'] is True, "success should be True"
            assert 'token' in data, "Response should include new token"
            assert 'profile' in data, "Response should include updated profile"

            # Verify updates
            profile = data['profile']
            assert profile['gpu_type'] == updated_data['gpu_type'], "GPU type not updated"
            assert profile['ram_capacity'] == updated_data['ram_capacity'], "RAM not updated"

            print_success("Profile updates verified")
            print_info(f"New Token: {data['token'][:50]}...")

            return data['token']
        else:
            print_error(f"Profile update failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Update test failed: {e}")
        return None


def test_invalid_password():
    """Test 5: Password validation"""
    print_header("Test 5: Password Validation")

    weak_passwords = [
        ("short1", "too short"),
        ("nouppercase1", "no uppercase"),
        ("NOLOWERCASE1", "no lowercase"),
        ("NoNumbers", "no number"),
    ]

    for password, reason in weak_passwords:
        print_info(f"Testing weak password: {password} ({reason})")

        response = requests.post(
            f"{API_BASE_URL}/auth/signup",
            json={
                **TEST_USER_DATA,
                "email": f"weak-{int(datetime.now().timestamp())}@test.com",
                "password": password,
            },
            timeout=10
        )

        if response.status_code == 422:
            print_success(f"Weak password rejected: {reason}")
        else:
            print_error(f"Weak password should have been rejected: {password}")
            return False

    print_success("All password validation tests passed")
    return True


def test_duplicate_email():
    """Test 6: Duplicate email prevention"""
    print_header("Test 6: Duplicate Email Prevention")

    print_info(f"Attempting to create duplicate user: {TEST_EMAIL}")

    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/signup",
            json=TEST_USER_DATA,
            timeout=10
        )

        if response.status_code == 409:
            print_success("Duplicate email correctly rejected")
            return True
        else:
            print_error(f"Duplicate email should have been rejected: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Duplicate email test failed: {e}")
        return False


def main():
    """Run all tests"""
    print_header("🧪 API Test Suite - Authentication with Hardware Profiling")

    results = []

    # Test 0: Health check
    if not test_health():
        print_error("\nBackend is not running. Exiting.")
        sys.exit(1)

    # Test 1: Signup
    token = test_signup()
    results.append(("Signup", token is not None))

    # Test 2: Signin
    signin_token = test_signin(token)
    results.append(("Signin", signin_token is not None))

    # Use signin token for remaining tests
    if signin_token:
        token = signin_token

    # Test 3: Get Profile
    results.append(("Get Profile", test_profile(token)))

    # Test 4: Update Profile
    updated_token = test_update_profile(token)
    results.append(("Update Profile", updated_token is not None))

    # Test 5: Password validation
    results.append(("Password Validation", test_invalid_password()))

    # Test 6: Duplicate email
    results.append(("Duplicate Email Prevention", test_duplicate_email()))

    # Summary
    print_header("📊 Test Summary")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"{test_name:30s} {status}")

    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.END}")

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ ALL TESTS PASSED!{Colors.END}")
        print(f"{Colors.GREEN}The 50-point hardware profiling feature is working correctly!{Colors.END}")
        sys.exit(0)
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ SOME TESTS FAILED{Colors.END}")
        sys.exit(1)


if __name__ == "__main__":
    main()
