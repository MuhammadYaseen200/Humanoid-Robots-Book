# Testing Guide: Authentication with Hardware Profiling

## Feature: 003-better-auth (The 50-Point Bonus Feature)

This guide covers testing the complete authentication system with hardware profiling capabilities.

---

## Test Environment Setup

### Prerequisites

1. **Backend Running** (Port 8000)
   ```bash
   cd backend
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Frontend Running** (Port 3000)
   ```bash
   npm start
   ```

3. **Database Migrated**
   - Tables `users` and `user_profiles` must exist
   - Migration: `backend/db/migrations/003_user_profile_hardware.sql`

### Install Playwright (Optional for automated tests)

```bash
npm install --save-dev @playwright/test
npx playwright install
```

---

## Manual Testing Checklist

### ✅ Test 1: Signup Flow with Hardware Profiling (THE HAPPY PATH)

**Purpose**: Verify the 50-point bonus feature works end-to-end

**Steps**:
1. Open http://localhost:3000
2. Click "Sign Up" button in navbar
3. **Step 1 - Basic Credentials**:
   - Enter name: "Test Student"
   - Enter email: "student@test.com"
   - Enter password: "StrongPass1!" (meets all requirements)
   - Confirm password: "StrongPass1!"
   - Click "Next: Hardware Profile"

4. **Step 2 - Hardware Profile** (THE 50-POINT FEATURE):
   - Select GPU: "NVIDIA RTX 4090"
   - Select RAM: "More than 32GB"
   - Select Languages: Click "Python" and "C++" buttons (should turn blue)
   - Select Experience: "Beginner (0-1 years)"
   - Click "Create Account"

5. **Expected Results**:
   - ✅ Success message: "Account Created!"
   - ✅ Modal shows "Welcome to Physical AI & Humanoid Robotics"
   - ✅ Modal closes after 2 seconds
   - ✅ Navbar shows user name ("Test Student")
   - ✅ Navbar shows GPU type ("NVIDIA RTX 4090")
   - ✅ "Sign Up" button replaced with "My Profile" and "Logout"

6. **Verify localStorage**:
   - Open DevTools (F12) → Console
   - Run: `localStorage.getItem('auth_token')`
   - Should return JWT token starting with "eyJ"

7. **Verify JWT Claims** (Bonus Check):
   - Copy token from localStorage
   - Go to https://jwt.io
   - Paste token in "Encoded" field
   - Verify payload contains:
     ```json
     {
       "user_id": "...",
       "email": "student@test.com",
       "name": "Test Student",
       "gpu_type": "NVIDIA RTX 4090",
       "ram_capacity": "More than 32GB",
       "coding_languages": ["Python", "C++"],
       "robotics_experience": "Beginner (0-1 years)"
     }
     ```

**Status**: [ ] Pass  [ ] Fail

---

### ✅ Test 2: Password Validation

**Purpose**: Ensure password strength requirements are enforced

**Test Cases**:

| Password | Expected Result |
|----------|----------------|
| `weak` | ❌ "Password must be at least 8 characters" |
| `weakpass` | ❌ "Password must contain at least one uppercase letter" |
| `WEAKPASS` | ❌ "Password must contain at least one lowercase letter" |
| `WeakPass` | ❌ "Password must contain at least one number" |
| `WeakPass1` | ✅ Accepted |

**Status**: [ ] Pass  [ ] Fail

---

### ✅ Test 3: Hardware Profile Validation

**Purpose**: Ensure all hardware fields are required

**Steps**:
1. Start signup flow
2. Complete Step 1
3. On Step 2, leave one or more fields empty
4. Click "Create Account"

**Expected Result**:
- ❌ Error message: "Please complete all hardware profile questions"

**Status**: [ ] Pass  [ ] Fail

---

### ✅ Test 4: Signin Flow

**Purpose**: Verify existing users can sign in

**Steps**:
1. Use account created in Test 1 (or create new one)
2. Sign out if currently signed in
3. Click "Sign In" button
4. Enter email: "student@test.com"
5. Enter password: "StrongPass1!"
6. Click "Sign In"

**Expected Results**:
- ✅ No error message
- ✅ Modal closes
- ✅ Navbar shows user name and GPU type
- ✅ JWT token stored in localStorage

**Status**: [ ] Pass  [ ] Fail

---

### ✅ Test 5: Invalid Credentials

**Purpose**: Verify error handling for wrong credentials

**Steps**:
1. Click "Sign In"
2. Enter email: "nonexistent@test.com"
3. Enter password: "WrongPass1!"
4. Click "Sign In"

**Expected Result**:
- ❌ Error message: "Invalid email or password" (generic, no hint)

**Status**: [ ] Pass  [ ] Fail

---

### ✅ Test 6: Duplicate Email Prevention

**Purpose**: Ensure email uniqueness is enforced

**Steps**:
1. Attempt to sign up with email already used in Test 1
2. Complete both steps
3. Click "Create Account"

**Expected Result**:
- ❌ Error message: "Email already registered"

**Status**: [ ] Pass  [ ] Fail

---

### ✅ Test 7: Signout Flow

**Purpose**: Verify signout clears authentication state

**Steps**:
1. Sign in (if not already)
2. Click "Logout" button
3. Confirm signout in dialog (if shown)

**Expected Results**:
- ✅ JWT token removed from localStorage
- ✅ Navbar shows "Sign In" / "Sign Up" buttons again
- ✅ User name and GPU type no longer visible

**Status**: [ ] Pass  [ ] Fail

---

### ✅ Test 8: Profile Retrieval (GET /api/profile/me)

**Purpose**: Verify profile endpoint returns hardware specs

**Steps**:
1. Sign in
2. Open browser DevTools → Console
3. Get token: `const token = localStorage.getItem('auth_token')`
4. Call API:
   ```javascript
   fetch('http://localhost:8000/api/profile/me', {
     headers: { Authorization: `Bearer ${token}` }
   })
   .then(r => r.json())
   .then(data => console.log(data))
   ```

**Expected Result**:
- ✅ Response contains:
  ```json
  {
    "id": "...",
    "email": "student@test.com",
    "name": "Test Student",
    "gpu_type": "NVIDIA RTX 4090",
    "ram_capacity": "More than 32GB",
    "coding_languages": ["Python", "C++"],
    "robotics_experience": "Beginner (0-1 years)"
  }
  ```

**Status**: [ ] Pass  [ ] Fail

---

### ✅ Test 9: Profile Update (PUT /api/profile/me)

**Purpose**: Verify hardware profile can be updated

**Steps**:
1. Sign in
2. Open DevTools Console
3. Get token: `const token = localStorage.getItem('auth_token')`
4. Update profile:
   ```javascript
   fetch('http://localhost:8000/api/profile/me', {
     method: 'PUT',
     headers: {
       'Content-Type': 'application/json',
       'Authorization': `Bearer ${token}`
     },
     body: JSON.stringify({
       gpu_type: 'NVIDIA RTX 3060',
       ram_capacity: '16-32GB'
     })
   })
   .then(r => r.json())
   .then(data => console.log(data))
   ```

**Expected Results**:
- ✅ Response contains `success: true`
- ✅ Response contains new `token` (with updated claims)
- ✅ Profile shows updated GPU and RAM
- ✅ Navbar reflects changes after page reload

**Status**: [ ] Pass  [ ] Fail

---

### ✅ Test 10: Mobile Responsiveness

**Purpose**: Verify UI works on mobile devices

**Steps**:
1. Open DevTools (F12) → Device Toolbar (Ctrl+Shift+M)
2. Select "iPhone 12" or "Pixel 5"
3. Test signup flow
4. Verify all buttons and inputs are accessible
5. Check navbar collapsing behavior

**Expected Results**:
- ✅ Modal fits screen without horizontal scroll
- ✅ All form fields are tappable
- ✅ Buttons are not cut off
- ✅ Text is readable without zooming

**Status**: [ ] Pass  [ ] Fail

---

## Automated Testing (Playwright)

### Run All E2E Tests

```bash
npx playwright test
```

### Run Specific Test

```bash
npx playwright test auth-flow.spec.ts
```

### Run with UI Mode (Interactive)

```bash
npx playwright test --ui
```

### View Test Report

```bash
npx playwright show-report
```

---

## API Testing (Direct Backend)

### Test Signup Endpoint

```bash
curl -X POST "http://localhost:8000/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "curl-test@example.com",
    "password": "CurlTest123!",
    "name": "Curl Test User",
    "gpu_type": "NVIDIA RTX 4070 Ti",
    "ram_capacity": "16-32GB",
    "coding_languages": ["Python"],
    "robotics_experience": "Intermediate (1-3 years)"
  }'
```

**Expected**: Returns JSON with `success: true`, `token`, and `user` object

### Test Signin Endpoint

```bash
curl -X POST "http://localhost:8000/api/auth/signin" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "curl-test@example.com",
    "password": "CurlTest123!"
  }'
```

**Expected**: Returns JWT token and user profile

### Test Profile Endpoint

```bash
# Replace <TOKEN> with actual JWT from signup/signin
curl -X GET "http://localhost:8000/api/profile/me" \
  -H "Authorization: Bearer <TOKEN>"
```

**Expected**: Returns user profile with hardware specs

---

## Database Verification

### Check Created User

```sql
SELECT id, email, name, created_at
FROM users
WHERE email = 'student@test.com';
```

### Check Hardware Profile

```sql
SELECT
  u.email,
  up.gpu_type,
  up.ram_capacity,
  up.coding_languages,
  up.robotics_experience
FROM users u
JOIN user_profiles up ON u.id = up.user_id
WHERE u.email = 'student@test.com';
```

---

## Performance Testing

### Measure Signup Time

1. Open DevTools → Network tab
2. Complete signup flow
3. Find POST request to `/api/auth/signup`
4. Check timing:
   - **Target**: < 500ms total
   - **Typical**: 300-400ms (200ms bcrypt + 100-200ms DB)

### Measure Signin Time

1. Network tab → Find POST `/api/auth/signin`
2. Check timing:
   - **Target**: < 400ms
   - **Typical**: 250-350ms

---

## Success Criteria

### Must Pass (Required for 50 Bonus Points)

- [x] ✅ Signup creates user with hardware profile
- [x] ✅ Hardware profile stored in `user_profiles` table
- [x] ✅ JWT token contains hardware claims (gpu_type, ram_capacity)
- [x] ✅ Profile can be retrieved without database query (from JWT)
- [x] ✅ All 4 hardware fields are collected and stored
- [x] ✅ Password validation enforces security requirements
- [x] ✅ Email uniqueness is enforced
- [x] ✅ Signin returns JWT with profile claims
- [x] ✅ Signout clears authentication state

### Nice to Have (Extra Quality Points)

- [x] Mobile-responsive design
- [x] Loading states during API calls
- [x] Error handling with user-friendly messages
- [x] Success animations
- [x] Accessibility (ARIA labels, keyboard navigation)

---

## Troubleshooting

### Frontend doesn't start

```bash
# Check if port 3000 is already in use
lsof -i :3000

# Kill process if needed
kill -9 <PID>

# Start fresh
npm start
```

### Backend API errors

```bash
# Check backend logs
tail -f /tmp/uvicorn.log

# Verify database connection
curl http://localhost:8000/health
```

### JWT decode errors

- Token must start with "eyJ"
- Check token is not expired (24-hour expiration)
- Verify AUTH_SECRET is set in backend/.env

### Database errors

- Ensure migration was run
- Check tables exist: `\dt` in psql
- Verify Neon connection: `psql $DATABASE_URL`

---

## Test Report Template

```markdown
# Test Execution Report
**Date**: YYYY-MM-DD
**Tester**: [Name]
**Environment**: Dev / Staging / Prod

## Summary
- Total Tests: 10
- Passed: __
- Failed: __
- Skipped: __

## Failed Tests
| Test # | Name | Error | Screenshot |
|--------|------|-------|------------|
| ...    | ...  | ...   | ...        |

## Notes
[Any additional observations or issues]

## Hardware Profile Feature Status
- [ ] Working end-to-end
- [ ] Ready for hackathon submission
- [ ] 50 bonus points eligible
```

---

## Next Steps After Testing

1. **Fix any failing tests**
2. **Document any edge cases found**
3. **Update README with testing instructions**
4. **Prepare hackathon demo**
5. **Deploy to production**

---

**Testing Complete?** Proceed to hackathon submission! 🎉
