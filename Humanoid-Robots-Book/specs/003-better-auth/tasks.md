# Tasks: Better-Auth & User Profiling

**Input**: Design documents from `/specs/003-better-auth/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/auth-api.yaml, research.md, ADR-005

**Tests**: Tests are NOT requested in the specification. Focus on implementation with manual verification steps.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Target**: 50 Bonus Points for Authentication & User Profiling (Hackathon Requirement)

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Each task includes exact file paths and verification steps

## Path Conventions

- **Backend**: `backend/src/` (FastAPI application)
- **Frontend**: `frontend/src/` (React/Docusaurus)
- **Database Migrations**: `backend/db/migrations/`
- **Shared Types**: `backend/src/models/` (Pydantic schemas)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [ ] T001 Install backend dependencies (passlib, python-jose, slowapi) in backend/requirements.txt
  - **Verification**: Run `pip install -r backend/requirements.txt` without errors
  - **Details**: Add passlib[bcrypt]>=1.7.4, python-jose[cryptography]>=3.3.0, slowapi>=0.1.9

- [ ] T002 [P] Install frontend dependencies (@tanstack/react-query, axios) in frontend/package.json
  - **Verification**: Run `npm install` in frontend/ without errors
  - **Details**: Add react-query for state management, axios for HTTP requests

- [ ] T003 [P] Create environment variable template backend/.env.example
  - **Verification**: File exists with AUTH_SECRET, DATABASE_URL, CORS_ORIGINS placeholders
  - **Details**: Document required variables for authentication (AUTH_SECRET minimum 32 chars)

- [ ] T004 [P] Create environment variable template frontend/.env.example
  - **Verification**: File exists with VITE_API_URL, VITE_ENV placeholders
  - **Details**: VITE_ENV=development for localStorage, VITE_ENV=production for httpOnly cookies

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core authentication infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Layer

- [ ] T005 Create database migration 003_user_profile_hardware.sql in backend/db/migrations/
  - **Verification**: Migration SQL matches data-model.md schema (gpu_type, ram_capacity, coding_languages, robotics_experience columns with CHECK constraints)
  - **Details**: Extend user_profiles table with 4 new columns, add CHECK constraints for enum validation, create indexes on gpu_type and ram_capacity, add reset_counter to users table
  - **Reference**: See specs/003-better-auth/data-model.md lines 13-74

- [ ] T006 Run migration 003 on Neon Postgres database
  - **Verification**: Query `SELECT column_name FROM information_schema.columns WHERE table_name='user_profiles'` returns gpu_type, ram_capacity, coding_languages, robotics_experience
  - **Details**: Execute migration script, verify constraints created with `\d+ user_profiles` in psql

### Pydantic Models & Validation

- [ ] T007 [P] Create SignupRequest Pydantic model in backend/src/models/auth.py
  - **Verification**: Model validates email format, password strength (min 8 chars, uppercase, number, symbol), required profile fields (gpu_type, ram_capacity, coding_languages, robotics_experience)
  - **Details**: Use Literal types for enums matching database CHECK constraints
  - **Reference**: See specs/003-better-auth/contracts/auth-api.yaml lines 365-431

- [ ] T008 [P] Create SigninRequest Pydantic model in backend/src/models/auth.py
  - **Verification**: Model accepts email and password fields only
  - **Reference**: See specs/003-better-auth/contracts/auth-api.yaml lines 433-443

- [ ] T009 [P] Create ProfileUpdateRequest Pydantic model in backend/src/models/profile.py
  - **Verification**: Model allows updating gpu_type, ram_capacity, coding_languages, robotics_experience (but NOT email)
  - **Reference**: See specs/003-better-auth/contracts/auth-api.yaml lines 501-531

- [ ] T010 [P] Create UserProfile response model in backend/src/models/profile.py
  - **Verification**: Model includes all profile fields plus id, email, name, created_at, last_login
  - **Reference**: See specs/003-better-auth/contracts/auth-api.yaml lines 455-499

### Authentication Utilities (CRITICAL: ADR-005 Compliance)

- [ ] T011 Create password hashing utilities in backend/src/utils/auth.py
  - **Verification**: `hash_password()` function wraps bcrypt in `run_in_executor`, `verify_password()` wraps bcrypt.verify in `run_in_executor`, both are async functions returning in ~200-300ms
  - **Details**: Use passlib CryptContext with bcrypt scheme, 12 salt rounds, asyncio.get_event_loop().run_in_executor() to prevent blocking
  - **Reference**: ADR-005 lines 232-256 (MUST use async wrapper to prevent event loop blocking)
  - **CRITICAL**: Test with concurrent requests to verify event loop not blocked

- [ ] T012 Create JWT token utilities in backend/src/utils/jwt.py
  - **Verification**: `create_access_token(user_id, email, profile)` returns signed JWT with embedded profile claims (gpu_type, ram_capacity, coding_languages, robotics_experience), `decode_token(token)` validates signature and expiration
  - **Details**: Use python-jose, HS256 algorithm, AUTH_SECRET from env, 24-hour expiration, embed ALL profile fields in claims
  - **Reference**: specs/003-better-auth/data-model.md lines 155-206 (JWT claims structure)

- [ ] T013 [P] Create email enumeration prevention helper in backend/src/utils/auth.py
  - **Verification**: `constant_time_verify(email, password)` performs fake bcrypt hash when email not found, returns generic "Invalid email or password" error
  - **Details**: Use fake bcrypt hash constant, always call verify_password even if user not found
  - **Reference**: ADR-005 lines 283-316 (email enumeration prevention)

### Rate Limiting Middleware

- [ ] T014 Setup slowapi rate limiter in backend/src/main.py
  - **Verification**: Rate limiter configured with 10 requests/minute/IP, exception handler registered, limiter attached to app.state
  - **Details**: Use slowapi.Limiter with get_remote_address key function, add RateLimitExceeded exception handler
  - **Reference**: ADR-005 lines 258-280

### JWT Authentication Dependency

- [ ] T015 Create JWT authentication dependency in backend/src/dependencies/auth.py
  - **Verification**: `get_current_user(token: str)` dependency extracts JWT from Authorization header or Cookie, validates token, returns decoded claims (including profile fields)
  - **Details**: Use FastAPI HTTPBearer or Cookie dependency, call decode_token(), raise 401 if invalid/expired
  - **Reference**: Enables protected endpoints to access user profile without DB query

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - New User Signup with Hardware Profiling (Priority: P1) 🎯 MVP

**Goal**: Enable new users to create accounts with complete hardware/software profiles to unlock personalized content

**Independent Test**: Visit site, click "Sign Up", complete form with email/password/hardware questions, verify account created in database with all profile fields populated

**Why P1**: This is the foundation for earning 50 bonus points. Without signup and profile collection, content personalization cannot function.

### Backend Implementation for US1

- [ ] T016 [US1] Implement POST /api/auth/signup endpoint in backend/src/routes/auth.py
  - **Verification**:
    - POST request with valid SignupRequest returns 201 status with JWT token
    - Email uniqueness check prevents duplicate accounts (409 status)
    - Password is hashed with bcrypt before storage
    - User and user_profile records created in database
    - JWT token contains embedded profile claims (gpu_type, ram_capacity, coding_languages, robotics_experience)
    - Rate limiting enforced (10 requests/minute/IP)
  - **Details**:
    1. Validate SignupRequest with Pydantic
    2. Check email uniqueness (return 409 if exists)
    3. Hash password with `await hash_password(request.password)`
    4. Insert user record (BEGIN TRANSACTION)
    5. Insert user_profile record with profile fields
    6. COMMIT transaction
    7. Generate JWT with `create_access_token(user.id, user.email, profile)`
    8. Log signup event to user_activity table
    9. Return 201 with {token, user: UserProfile}
  - **Reference**: specs/003-better-auth/spec.md FR-001 to FR-020

- [ ] T017 [US1] Add request validation error handling to /api/auth/signup
  - **Verification**: Invalid requests return 422 with clear error messages (weak password: "Password must be at least 8 characters...", invalid email: "Please enter a valid email address", missing profile fields: "Please complete all hardware profile questions")
  - **Details**: Catch Pydantic ValidationError, format user-friendly error messages
  - **Reference**: specs/003-better-auth/contracts/auth-api.yaml lines 76-112

- [ ] T018 [US1] Add database error handling to /api/auth/signup
  - **Verification**: Database failures return 500 with generic message "Unable to create account. Please try again later." (no stack traces exposed), error logged with request ID
  - **Details**: Catch asyncpg exceptions, log full error internally, return sanitized message to client
  - **Reference**: specs/003-better-auth/spec.md edge case line 98

### Frontend Implementation for US1

- [ ] T019 [P] [US1] Create AuthContext provider in frontend/src/contexts/AuthContext.tsx
  - **Verification**: Context provides `signup(email, password, profile)` function, `user` state, `token` state, `isAuthenticated` boolean
  - **Details**: Use React Context API, manage JWT token storage (localStorage for dev, prepare for httpOnly cookie in production), persist user profile state
  - **Reference**: ADR-004 lines 173-206 (hybrid token storage strategy)

- [ ] T020 [US1] Create SignupModal component in frontend/src/components/auth/SignupModal.tsx
  - **Verification**:
    - Modal contains fields: email (input), password (input with strength indicator), name (input), gpu_type (dropdown), ram_capacity (dropdown), coding_languages (multi-select), robotics_experience (radio buttons)
    - All fields are required (form validation)
    - Password strength indicator shows weak/medium/strong as user types
    - Submit button disabled during async signup request
    - Success: modal closes, user redirected to welcome page
    - Error: displays error message from backend (email exists, weak password, validation errors)
  - **Details**: Use dropdown options matching database CHECK constraints exactly, implement client-side validation matching backend Pydantic models
  - **Reference**: specs/003-better-auth/spec.md FR-014 to FR-019 (profile questions)

- [ ] T021 [US1] Integrate SignupModal with AuthContext in frontend/src/components/auth/SignupModal.tsx
  - **Verification**:
    - Form submission calls `AuthContext.signup(email, password, profile)`
    - Success: JWT token stored, user state updated, modal closes
    - Failure: error displayed in modal (no page reload)
  - **Details**: Handle async errors, show loading spinner during request, clear form on success
  - **Reference**: User should see immediate feedback (no page reload needed)

- [ ] T022 [US1] Add "Sign Up" button to Docusaurus navigation in frontend/src/theme/Navbar/index.tsx
  - **Verification**: "Sign Up" button visible in top navigation on all pages, clicking opens SignupModal
  - **Details**: Conditionally render "Sign Up" button only when `!isAuthenticated`
  - **Reference**: specs/003-better-auth/spec.md FR-001

**Checkpoint**: At this point, User Story 1 should be fully functional - users can sign up with complete profiles

---

## Phase 4: User Story 2 - Returning User Signin (Priority: P2)

**Goal**: Enable returning users to authenticate and access their personalized profiles

**Independent Test**: Create test account, sign out, sign in with correct credentials (success), attempt signin with wrong password (error: "Invalid email or password")

**Why P2**: Authentication flow is incomplete without signin. Required for full 50 bonus points.

### Backend Implementation for US2

- [ ] T023 [US2] Implement POST /api/auth/signin endpoint in backend/src/routes/auth.py
  - **Verification**:
    - Valid credentials return 200 with JWT token
    - Invalid password returns 401 with "Invalid email or password"
    - Non-existent email returns 401 with "Invalid email or password" (same error, prevents email enumeration)
    - Response time is constant ~300ms regardless of email existence (timing attack prevention)
    - last_login timestamp updated in users table
    - Signin event logged to user_activity table
  - **Details**:
    1. Validate SigninRequest with Pydantic
    2. Query user by email (lowercase)
    3. If user exists: `is_valid = await verify_password(request.password, user.password_hash)`
    4. If user not found: `is_valid = await constant_time_verify(fake_email, request.password)` (fake bcrypt to maintain constant time)
    5. If not is_valid: raise 401 "Invalid email or password"
    6. Fetch user_profile (JOIN query)
    7. Generate JWT with `create_access_token(user.id, user.email, profile)`
    8. Update last_login timestamp
    9. Log signin event
    10. Return 200 with {token, user: UserProfile}
  - **Reference**: ADR-005 lines 283-316 (email enumeration prevention CRITICAL)

- [ ] T024 [US2] Add rate limiting to /api/auth/signin
  - **Verification**: 11th request within 1 minute returns 429 "Too many signin attempts. Please try again in 1 minute."
  - **Details**: Apply `@limiter.limit("10/minute")` decorator
  - **Reference**: ADR-005 lines 276-280

### Frontend Implementation for US2

- [ ] T025 [US2] Create SigninModal component in frontend/src/components/auth/SigninModal.tsx
  - **Verification**:
    - Modal contains fields: email (input), password (input)
    - Submit button disabled during async signin request
    - Success: modal closes, user name appears in navigation
    - Error: displays "Invalid email or password" (generic error for both wrong email and wrong password)
    - "Forgot Password?" link visible (for future P4 story)
  - **Details**: Implement client-side validation (email format, password not empty)
  - **Reference**: specs/003-better-auth/spec.md FR-010 to FR-013

- [ ] T026 [US2] Integrate SigninModal with AuthContext in frontend/src/components/auth/SigninModal.tsx
  - **Verification**:
    - Form submission calls `AuthContext.signin(email, password)`
    - Success: JWT token stored, user state updated, modal closes
    - Failure: error displayed in modal
  - **Details**: Handle 401 errors, show loading spinner, clear password field on error

- [ ] T027 [US2] Add "Sign In" button to Docusaurus navigation in frontend/src/theme/Navbar/index.tsx
  - **Verification**: "Sign In" button visible when `!isAuthenticated`, clicking opens SigninModal
  - **Details**: Position next to "Sign Up" button

- [ ] T028 [US2] Add authenticated user navigation UI in frontend/src/theme/Navbar/index.tsx
  - **Verification**: When `isAuthenticated`, show user name with dropdown containing "My Profile" and "Sign Out" options
  - **Details**: Replace "Sign Up"/"Sign In" buttons with user menu when authenticated
  - **Reference**: specs/003-better-auth/spec.md FR-030

- [ ] T029 [US2] Implement signout functionality in AuthContext
  - **Verification**: Clicking "Sign Out" clears JWT token, resets user state, redirects to homepage, shows "Sign Up"/"Sign In" buttons again
  - **Details**: Clear localStorage (dev) or send request to clear httpOnly cookie (production)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - users can signup and signin

---

## Phase 5: User Story 3 - Profile Management (Priority: P3)

**Goal**: Enable logged-in users to view and update their hardware/software profiles

**Independent Test**: Sign in, navigate to /profile, change GPU type from "None" to "RTX 4070 Ti", save, sign out, sign in again, verify updated GPU reflected in profile

**Why P3**: Enhances UX but not strictly required for bonus points. Users can re-register if needed.

### Backend Implementation for US3

- [ ] T030 [US3] Implement GET /api/profile endpoint in backend/src/routes/profile.py
  - **Verification**:
    - Valid JWT returns 200 with UserProfile (id, email, name, gpu_type, ram_capacity, coding_languages, robotics_experience, learning_style, difficulty_level, created_at, last_login)
    - Invalid/expired JWT returns 401 "Invalid or expired token"
    - No database query needed (profile extracted from JWT claims)
  - **Details**: Use `Depends(get_current_user)` dependency, return decoded JWT claims as UserProfile model
  - **Reference**: Stateless - no DB lookup, profile already in JWT (ADR-006 decision)

- [ ] T031 [US3] Implement PUT /api/profile endpoint in backend/src/routes/profile.py
  - **Verification**:
    - Valid JWT + ProfileUpdateRequest returns 200 with updated UserProfile
    - Profile fields updated in database (user_profiles table)
    - New JWT token issued with refreshed profile claims
    - Email cannot be changed (validation error if attempted)
    - Invalid JWT returns 401
  - **Details**:
    1. Extract user_id from JWT (`Depends(get_current_user)`)
    2. Validate ProfileUpdateRequest
    3. Update user_profiles table WHERE user_id = current_user.id
    4. Fetch updated profile from database
    5. Generate new JWT with `create_access_token(user_id, email, updated_profile)`
    6. Return 200 with {user: UserProfile, token: new_jwt}
  - **Reference**: specs/003-better-auth/spec.md FR-021 to FR-026

### Frontend Implementation for US3

- [ ] T032 [US3] Create ProfilePage component in frontend/src/pages/ProfilePage.tsx
  - **Verification**:
    - Page displays current profile values in editable form
    - Email field is read-only (grayed out, cannot edit)
    - Dropdowns for gpu_type, ram_capacity, robotics_experience
    - Multi-select for coding_languages
    - "Save Changes" button
    - Unauthenticated access redirects to signin modal
  - **Details**: Fetch current profile from AuthContext.user state (already loaded from JWT)
  - **Reference**: specs/003-better-auth/spec.md User Story 3

- [ ] T033 [US3] Implement profile update logic in ProfilePage
  - **Verification**:
    - Form submission calls `PUT /api/profile` with updated fields
    - Success: displays "Profile updated successfully" message, updates local user state, refreshes JWT token
    - Failure: displays error message
  - **Details**: Call AuthContext.updateProfile() function, handle token refresh
  - **Reference**: specs/003-better-auth/spec.md FR-023, FR-025

- [ ] T034 [US3] Add "My Profile" link to user navigation dropdown in frontend/src/theme/Navbar/index.tsx
  - **Verification**: Clicking user name dropdown shows "My Profile" link, clicking navigates to /profile
  - **Details**: Use React Router Link component

**Checkpoint**: All core user stories (US1, US2, US3) are now independently functional

---

## Phase 6: User Story 4 - Password Reset Flow (Priority: P4) [OPTIONAL]

**Goal**: Enable users to reset forgotten passwords via email link

**Independent Test**: Click "Forgot Password", enter email, check email for reset link (or backend logs), click link, set new password, sign in with new credentials

**Why P4**: Nice-to-have for production readiness but NOT required for hackathon bonus points. Many users can re-register with new email.

**⚠️ DEFER**: Skip this phase for MVP. Can implement post-hackathon if time permits.

### Backend Implementation for US4 (OPTIONAL)

- [ ] T035 [P] [US4] Create password reset token utilities in backend/src/utils/jwt.py
  - **Verification**: `create_reset_token(email, reset_counter)` returns JWT with 1-hour expiration and reset_counter claim, `decode_reset_token(token)` validates and returns email + reset_counter
  - **Details**: Include reset_counter in claims to invalidate old tokens after successful reset
  - **Reference**: specs/003-better-auth/data-model.md lines 208-245

- [ ] T036 [US4] Implement POST /api/auth/forgot-password endpoint in backend/src/routes/auth.py
  - **Verification**:
    - Valid email: generates reset token, sends email with reset link, returns 200 "Password reset link sent to your email"
    - Invalid email: returns SAME message (prevents email enumeration)
    - Rate limited to 10 requests/minute/IP
  - **Details**: Query user by email, generate reset_token, send email via SendGrid/SMTP, log event
  - **Reference**: specs/003-better-auth/spec.md FR-034, FR-035

- [ ] T037 [US4] Implement POST /api/auth/reset-password endpoint in backend/src/routes/auth.py
  - **Verification**:
    - Valid token + new password: updates password_hash, increments reset_counter (invalidates old tokens), returns 200
    - Expired/invalid token: returns 400 "Password reset link has expired. Please request a new one."
    - Token with old reset_counter: returns 400 "This reset link has already been used"
  - **Details**: Decode reset_token, validate reset_counter matches database, hash new password, increment reset_counter
  - **Reference**: specs/003-better-auth/spec.md FR-036, FR-037

### Frontend Implementation for US4 (OPTIONAL)

- [ ] T038 [US4] Create ForgotPasswordModal component in frontend/src/components/auth/ForgotPasswordModal.tsx
  - **Verification**: Modal contains email field, submit button, displays success message after submission
  - **Details**: Call POST /api/auth/forgot-password

- [ ] T039 [US4] Create PasswordResetPage component in frontend/src/pages/PasswordResetPage.tsx
  - **Verification**: Page accepts reset token from URL query param, displays new password fields, submits reset request, redirects to signin on success
  - **Details**: Extract token from URL, validate matching passwords, call POST /api/auth/reset-password

- [ ] T040 [US4] Add "Forgot Password?" link to SigninModal
  - **Verification**: Link opens ForgotPasswordModal
  - **Details**: Simple link below signin form

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Production readiness improvements affecting multiple user stories

### Security Hardening

- [ ] T041 [P] Add CORS middleware configuration in backend/src/main.py
  - **Verification**: CORS allows requests from frontend domain (localhost:3000 for dev, production domain for prod), credentials enabled for httpOnly cookies
  - **Details**: Use FastAPI CORSMiddleware, allow_credentials=True, specific allow_origins (not wildcard *)
  - **Reference**: ADR-004 lines 210-222

- [ ] T042 [P] Implement httpOnly cookie support for production in backend/src/routes/auth.py
  - **Verification**: When ENV=production, signup/signin set JWT in httpOnly cookie instead of response body
  - **Details**: Use Response.set_cookie(key="auth_token", httponly=True, secure=True, samesite="strict", max_age=86400)
  - **Reference**: ADR-004 lines 132-153

- [ ] T043 [P] Add environment-based token storage in AuthContext
  - **Verification**: Development uses localStorage, production uses httpOnly cookies (credentials: 'include' in fetch)
  - **Details**: Check VITE_ENV variable, branch logic for token storage/retrieval
  - **Reference**: ADR-004 lines 173-206

### Logging & Monitoring

- [ ] T044 [P] Add authentication event logging to user_activity table
  - **Verification**: All signup, signin, signout, failed_signin events logged with timestamp, IP address, user_agent
  - **Details**: Create insert_activity_log() utility function, call from auth endpoints
  - **Reference**: specs/003-better-auth/spec.md FR-031

- [ ] T045 [P] Add structured logging for auth operations in backend/src/routes/auth.py
  - **Verification**: Logs include request_id, user_id (if authenticated), operation, outcome (success/failure), no passwords logged
  - **Details**: Use Python logging module, INFO for success, WARNING for failures
  - **Reference**: specs/003-better-auth/spec.md FR-033

### Documentation

- [ ] T046 [P] Create API documentation in specs/003-better-auth/api-docs.md
  - **Verification**: Document all endpoints with request/response examples, error codes, authentication requirements
  - **Details**: Use OpenAPI spec from contracts/auth-api.yaml as reference
  - **Reference**: specs/003-better-auth/contracts/auth-api.yaml

- [ ] T047 [P] Update project README with authentication setup instructions
  - **Verification**: README explains how to set AUTH_SECRET, run migrations, configure CORS
  - **Details**: Document environment variables, migration commands, testing steps

### Performance Optimization

- [ ] T048 Verify bcrypt async wrapper prevents event loop blocking
  - **Verification**: Load test with 10 concurrent signup requests completes without timeout, all requests return within 2 seconds
  - **Details**: Use Apache Bench or wrk to test concurrent requests
  - **Reference**: ADR-005 CRITICAL requirement (async wrapper mandatory)

- [ ] T049 Add database connection pooling optimization
  - **Verification**: Database connection pool configured with min=5, max=20 connections
  - **Details**: Configure asyncpg pool settings in database connection setup

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - **BLOCKS all user stories**
- **User Story 1 (Phase 3)**: Depends on Foundational phase - **MVP TARGET**
- **User Story 2 (Phase 4)**: Depends on Foundational phase - Can run parallel to US1 or after
- **User Story 3 (Phase 5)**: Depends on Foundational phase AND US2 (needs signin first) - Can run parallel if staffed
- **User Story 4 (Phase 6)**: OPTIONAL - Defer for post-MVP
- **Polish (Phase 7)**: Depends on desired user stories being complete (at minimum US1+US2)

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies on other stories - **Can start after Foundational**
- **User Story 2 (P2)**: No hard dependency on US1 (independent signin flow) - **Can start after Foundational**
- **User Story 3 (P3)**: Requires US2 (must be able to signin before managing profile) - **Start after US2**
- **User Story 4 (P4)**: No dependencies (password reset works independently) - **OPTIONAL, defer**

### Within Each User Story

**Foundational Phase (CRITICAL):**
1. T005 (migration) → T006 (run migration) - **BLOCKING**
2. T007-T010 (Pydantic models) - Can run in parallel
3. T011 (bcrypt utils) → T012 (JWT utils) - Sequential (JWT needs user data from auth)
4. T013 (email enumeration), T014 (rate limiting), T015 (JWT dependency) - Can run parallel to T011-T012

**User Story 1:**
1. Backend: T016 (signup endpoint) requires T007, T011, T012 complete
2. Frontend: T019 (AuthContext) → T020 (SignupModal) → T021 (integration)
3. T022 (navigation button) can run parallel to T020-T021

**User Story 2:**
1. Backend: T023 (signin endpoint) requires T008, T011, T012, T013 complete
2. Frontend: T025 (SigninModal) → T026 (integration) → T027-T029 (navigation)

**User Story 3:**
1. Backend: T030 (GET profile) → T031 (PUT profile) - Sequential
2. Frontend: T032 (ProfilePage) → T033 (update logic) → T034 (navigation link)

### Parallel Opportunities

**Foundational Phase (After Migration T005-T006):**
```bash
# All Pydantic models can run in parallel:
T007 (SignupRequest) || T008 (SigninRequest) || T009 (ProfileUpdateRequest) || T010 (UserProfile)

# Auth utilities can run in parallel:
T011 (bcrypt) || T013 (email enumeration) || T014 (rate limiting)
# Then T012 (JWT) after T011 completes
```

**User Story 1 (After Foundational):**
```bash
# Frontend components can start while backend is being built:
T016 (signup endpoint) || T019 (AuthContext) || T022 (navigation button)
# Then T020, T021 after T019
```

**User Story 2 (After Foundational):**
```bash
# Backend and frontend can proceed in parallel:
T023 (signin endpoint) || T025 (SigninModal)
# Then T026-T029 for integration
```

**Polish Phase (After US1+US2):**
```bash
# All polish tasks can run in parallel:
T041 (CORS) || T042 (httpOnly cookies) || T043 (env-based storage) || T044 (logging) || T046 (docs) || T047 (README)
```

---

## Parallel Example: Foundational Phase

```bash
# After migration completes (T005-T006), launch all models together:
Task T007: "Create SignupRequest Pydantic model in backend/src/models/auth.py"
Task T008: "Create SigninRequest Pydantic model in backend/src/models/auth.py"
Task T009: "Create ProfileUpdateRequest Pydantic model in backend/src/models/profile.py"
Task T010: "Create UserProfile response model in backend/src/models/profile.py"

# And launch auth utilities in parallel:
Task T011: "Create password hashing utilities in backend/src/utils/auth.py"
Task T013: "Create email enumeration prevention helper in backend/src/utils/auth.py"
Task T014: "Setup slowapi rate limiter in backend/src/main.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2 ONLY)

**Target**: 50 Bonus Points for Authentication & User Profiling

1. ✅ **Phase 1: Setup** (T001-T004) - ~30 minutes
   - Install dependencies
   - Setup environment variables

2. ✅ **Phase 2: Foundational** (T005-T015) - ~4 hours
   - **CRITICAL**: Database migration with profile columns
   - **CRITICAL**: Async bcrypt wrapper (ADR-005 compliance)
   - Pydantic models, JWT utilities, rate limiting

3. ✅ **Phase 3: User Story 1** (T016-T022) - ~3 hours
   - Backend: Signup endpoint with profile collection
   - Frontend: Signup modal with hardware questions (THE 50-POINT FEATURE)

4. ✅ **Phase 4: User Story 2** (T023-T029) - ~2 hours
   - Backend: Signin endpoint with email enumeration prevention
   - Frontend: Signin modal and navigation integration

5. **STOP and VALIDATE**: Test signup → signout → signin flow
   - Verify JWT contains profile claims (gpu_type, ram_capacity, coding_languages, robotics_experience)
   - Verify 100% profile completeness (all fields required)
   - **Deploy/Demo MVP** → Earn 50 Bonus Points! 🎯

### Incremental Delivery

1. **MVP (US1 + US2)**: ~9-10 hours total - **HACKATHON TARGET**
   - Signup with hardware profiling → Signin with JWT
   - **DEMO READY**: Users can create accounts with complete profiles

2. **Post-MVP (US3)**: +2-3 hours if time permits
   - Profile management (edit GPU, RAM, languages, experience)
   - **ENHANCED UX**: Users can update profiles without re-registering

3. **Post-Hackathon (US4)**: +3-4 hours
   - Password reset flow (email-based recovery)
   - **PRODUCTION READY**: Complete authentication system

### Parallel Team Strategy

With 2 developers:

1. **Together**: Complete Setup + Foundational (Phase 1-2) - ~4.5 hours
2. **Split**:
   - Developer A: User Story 1 Backend (T016-T018)
   - Developer B: User Story 1 Frontend (T019-T022)
3. **Integrate**: Test US1 together
4. **Split Again**:
   - Developer A: User Story 2 Backend (T023-T024)
   - Developer B: User Story 2 Frontend (T025-T029)
5. **Integrate**: Test US2 together
6. **Deploy MVP** → Demo for 50 points! 🎯

---

## Critical Success Criteria (Per Spec)

**From spec.md Success Criteria:**

- ✅ **SC-001**: Signup completes in under 2 minutes
  - **Verify**: Time complete flow from "Sign Up" click to account created

- ✅ **SC-002**: Signin completes within 10 seconds
  - **Verify**: Time from credentials submit to authenticated state

- ✅ **SC-007**: JWT enables stateless authentication
  - **Verify**: Profile data in JWT claims, no DB query needed for /personalize

- ✅ **SC-009**: Zero plaintext passwords in database or logs
  - **Verify**: All password_hash values start with `$2b$` (bcrypt), logs contain no password fields

- ✅ **SC-012**: 100% profile data completeness
  - **Verify**: All users have gpu_type, ram_capacity, coding_languages, robotics_experience populated (NOT NULL)

**From ADR-005 Requirements:**

- ✅ **bcrypt async wrapper prevents event loop blocking**
  - **Verify**: Load test with 10 concurrent signup requests, all complete within 2 seconds
  - **CRITICAL**: This is MANDATORY per ADR-005 lines 232-256

- ✅ **Email enumeration prevention works**
  - **Verify**: Signin with non-existent email takes same time (~300ms) as signin with wrong password
  - **CRITICAL**: Response time must be constant per ADR-005 lines 283-316

- ✅ **Rate limiting blocks brute-force**
  - **Verify**: 11th signin attempt within 1 minute returns 429 status

---

## Notes

- **[P] tasks** = Can run in parallel (different files, no dependencies)
- **[Story] label** = Maps task to specific user story for traceability
- **Each user story** should be independently completable and testable
- **Stop at any checkpoint** to validate story independently
- **Commit after each task** or logical group for safety
- **ADR-005 compliance** is MANDATORY - async bcrypt wrapper non-negotiable
- **100% profile completeness** is REQUIRED for 50 bonus points - all fields mandatory
- **MVP = US1 + US2** (~9-10 hours) - sufficient for hackathon demo and 50 points
- **US3 optional** for enhanced UX - **US4 defer** to post-hackathon
