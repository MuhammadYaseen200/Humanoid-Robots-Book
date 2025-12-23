# Feature Specification: Better-Auth & User Profiling

**Feature Branch**: `003-better-auth`
**Created**: 2025-12-23
**Status**: Implemented
**Input**: User description: "Implement Signup/Signin using Better-Auth (Python/FastAPI). Ask 'Hardware Background' questions during signup (GPU type, RAM, Coding Language). Store this profile in Neon Postgres so we can Personalize content later. This feature earns the 50 Bonus Points defined in the Hackathon Requirements."

## User Scenarios & Testing

### User Story 1 - Hardware-Aware Signup with Profile Collection (Priority: P1)

A new user visiting the Physical AI textbook platform can create an account by providing their email, password, and name in Step 1, then complete a hardware profiling questionnaire in Step 2 (GPU type, RAM capacity, coding languages, robotics experience). Upon successful signup, the system creates their account, stores their hardware profile in the database, and generates a JWT token containing their profile data for instant personalization without additional database queries.

**Why this priority**: This is the core MVP that earns the 50 bonus hackathon points. It demonstrates hardware-aware personalization capabilities and enables the platform to tailor content recommendations based on user capabilities (e.g., show cloud-based paths for users without GPUs, suggest beginner content for users with no robotics experience).

**Independent Test**: Open the platform homepage, click "Sign Up", complete the 2-step wizard with hardware details, verify account creation, check that JWT token contains hardware claims (gpu_type, ram_capacity, coding_languages, robotics_experience), and confirm navbar shows user name and GPU type.

**Acceptance Scenarios**:

1. **Given** a visitor clicks "Sign Up" on the navbar, **When** they complete Step 1 (email: test@example.com, password: SecurePass123!, name: "John Doe"), **Then** the UI advances to Step 2 showing hardware profiling form
2. **Given** a user is on Step 2 of signup, **When** they select GPU: "NVIDIA RTX 4070 Ti", RAM: "16-32GB", Languages: ["Python", "C++"], Experience: "Intermediate (1-3 years)" and submit, **Then** the system creates user account, user_profile record, returns JWT token with embedded profile, and redirects to homepage with authenticated navbar
3. **Given** a user completes signup, **When** the JWT token is decoded, **Then** it contains claims: user_id, email, name, gpu_type, ram_capacity, coding_languages (array), robotics_experience
4. **Given** an authenticated user views the navbar, **When** the page loads, **Then** the navbar displays their name and GPU type (e.g., "John Doe" with "NVIDIA RTX 4070 Ti" subtitle)

---

### User Story 2 - Secure Authentication with JWT Stateless Sessions (Priority: P1)

Returning users can sign in using their email and password to receive a JWT token that persists their authentication state across page reloads and sessions. The token expires after 24 hours for security, and users can sign out at any time to invalidate their client-side session.

**Why this priority**: Core authentication functionality required for any personalized platform. JWT stateless approach eliminates database lookups on every request, improving performance and scalability.

**Independent Test**: Create an account, sign out, sign in again with correct credentials, verify JWT token is stored in localStorage, refresh page and confirm user remains authenticated, sign out and verify token is cleared.

**Acceptance Scenarios**:

1. **Given** a registered user (email: test@example.com, password: SecurePass123!), **When** they click "Sign In", enter credentials, and submit, **Then** the system validates credentials, returns JWT token, stores it in localStorage, and updates navbar to authenticated state
2. **Given** an authenticated user, **When** they refresh the page, **Then** the system reads JWT from localStorage, decodes user data, and maintains authenticated state without server request
3. **Given** an authenticated user, **When** they click "Sign Out" in the navbar, **Then** the system removes JWT from localStorage, resets auth context to null, and navbar shows "Sign In" / "Sign Up" buttons
4. **Given** a user with invalid credentials (wrong password), **When** they attempt to sign in, **Then** the system returns 401 error with message "Invalid credentials" and does not issue a token

---

### User Story 3 - Password Security & Validation (Priority: P1)

Users must create strong passwords that meet minimum security requirements (8+ characters, uppercase, lowercase, number, special character). Passwords are hashed using bcrypt with async execution to prevent blocking the event loop during signup/signin operations.

**Why this priority**: Critical for security and user trust. Weak passwords compromise all user data. Non-blocking async hashing ensures good UX (fast response times) even with slow hashing algorithms.

**Independent Test**: Attempt signup with weak passwords ("pass", "12345678", "Password"), verify each is rejected with specific error messages, then use strong password ("SecurePass123!") and verify acceptance with ~400ms response time.

**Acceptance Scenarios**:

1. **Given** a user attempts signup with password "pass", **When** they submit Step 1, **Then** the system rejects it with error "Password must be at least 8 characters"
2. **Given** a user attempts signup with password "password123", **When** they submit Step 1, **Then** the system rejects it with error "Password must contain at least one uppercase letter"
3. **Given** a user attempts signup with password "PASSWORD123", **When** they submit Step 1, **Then** the system rejects it with error "Password must contain at least one lowercase letter"
4. **Given** a user attempts signup with password "Password", **When** they submit Step 1, **Then** the system rejects it with error "Password must contain at least one number"
5. **Given** a user attempts signup with password "Password123", **When** they submit Step 1, **Then** the system rejects it with error "Password must contain at least one special character"
6. **Given** a user submits valid signup with password "SecurePass123!", **When** the backend hashes the password, **Then** hashing completes in 200-300ms using async bcrypt without blocking other requests

---

### User Story 4 - Navbar Authentication UI Integration (Priority: P2)

The Docusaurus navbar dynamically displays authentication state: unauthenticated users see "Sign In" and "Sign Up" buttons, while authenticated users see their name, GPU type, profile icon, and "Sign Out" button. Clicking authentication buttons opens modal dialogs without navigating away from the current page.

**Why this priority**: Provides seamless UX for authentication without disrupting reading flow. Users can authenticate from any page without losing their place in the textbook.

**Independent Test**: Load any textbook page, verify unauthenticated state shows Sign In/Sign Up, click Sign Up, complete registration in modal, verify navbar updates to show user profile without page navigation.

**Acceptance Scenarios**:

1. **Given** an unauthenticated user views any page, **When** they look at the navbar (top-right), **Then** they see two buttons: "Sign In" and "Sign Up"
2. **Given** an unauthenticated user clicks "Sign Up", **When** the modal opens, **Then** the current page content remains visible (modal overlay), and closing modal returns to reading without page reload
3. **Given** an authenticated user (John Doe, NVIDIA RTX 4070 Ti) views any page, **When** they look at the navbar, **Then** they see: name ("John Doe"), GPU subtitle ("NVIDIA RTX 4070 Ti"), user icon, and "Sign Out" button
4. **Given** an authenticated user clicks "Sign Out", **When** the action completes, **Then** the navbar immediately updates to show "Sign In" / "Sign Up" without page reload

---

### User Story 5 - Email Uniqueness & Validation (Priority: P2)

The system prevents duplicate accounts by enforcing unique email addresses at both the application and database levels. Email addresses must be valid format (RFC 5322), and attempting to register with an existing email returns a clear error message.

**Why this priority**: Prevents user confusion and data integrity issues. Users should not be able to create multiple accounts with the same email.

**Independent Test**: Register user with test@example.com, attempt to register again with same email, verify rejection with error "Email already exists", verify email format validation rejects invalid emails.

**Acceptance Scenarios**:

1. **Given** a user registers with email "test@example.com", **When** another user attempts signup with "test@example.com", **Then** the system returns 400 error with message "Email already exists"
2. **Given** a user attempts signup with email "invalid-email", **When** they submit Step 1, **Then** the system rejects it with error "Invalid email format"
3. **Given** a user attempts signup with email "test@", **When** they submit Step 1, **Then** the system rejects it with error "Invalid email format"
4. **Given** the database has UNIQUE constraint on users.email column, **When** a duplicate email bypasses application validation, **Then** the database rejects the insert and returns constraint violation error

---

### Edge Cases

- **What happens when a user closes the signup modal after completing Step 1 but before Step 2?** The modal state resets, and reopening requires starting from Step 1 again. No partial account is created in the database until both steps complete successfully.

- **How does the system handle JWT token expiration?** Tokens expire after 24 hours (configurable via JWT_EXPIRATION_SECONDS). When an expired token is decoded, the AuthContext treats the user as unauthenticated and shows Sign In/Sign Up buttons. Users must sign in again to get a new token.

- **What happens if the backend API is unreachable during signup/signin?** The frontend displays error message: "Unable to connect to authentication service. Please check your internet connection and try again." The user remains on the modal to retry.

- **How does the system handle users who select "No GPU" but want to use the platform?** The hardware profile is stored in their JWT and database record. Future features can use this data to show cloud-based alternatives or CPU-compatible content paths. No functionality is blocked based on hardware.

- **What happens when localStorage is disabled or unavailable?** The AuthContext attempts to read JWT from localStorage on mount. If unavailable (disabled cookies, private browsing strict modes), the user appears unauthenticated and must sign in each page load. A warning could be shown: "Enable cookies for persistent login."

- **How does the system handle special characters in names or coding languages?** Names and coding languages are stored as UTF-8 strings in Postgres. Input validation allows letters, spaces, hyphens, apostrophes for names. Coding languages are selected from predefined options (Python, C++, JavaScript, Rust, Go, Other) to prevent injection attacks.

- **What happens if a user submits signup with very long inputs?** Backend validation enforces limits: email ≤ 255 chars, password ≤ 128 chars, name ≤ 255 chars. Coding languages array limited to 10 selections. Exceeding limits returns 400 error with message specifying the field and limit.

- **How does the system handle concurrent signup attempts with the same email?** The database UNIQUE constraint on users.email prevents race conditions. If two requests arrive simultaneously, the first transaction commits successfully, and the second receives a constraint violation error, which the backend translates to "Email already exists" response.

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide a POST `/api/auth/signup` endpoint accepting email, password, name, gpu_type, ram_capacity, coding_languages (array), and robotics_experience
- **FR-002**: System MUST validate email format using RFC 5322 standard (via pydantic EmailStr)
- **FR-003**: System MUST enforce password requirements: minimum 8 characters, maximum 128 characters, at least one uppercase letter, one lowercase letter, one number, one special character
- **FR-004**: System MUST hash passwords using bcrypt with salt rounds = 12, executed asynchronously to prevent blocking
- **FR-005**: System MUST store user records in `users` table with columns: id (UUID), email (unique), password_hash, name, created_at (timestamp)
- **FR-006**: System MUST store hardware profile records in `user_profiles` table with columns: id (UUID), user_id (foreign key to users), gpu_type, ram_capacity, coding_languages (JSONB array), robotics_experience
- **FR-007**: System MUST enforce UNIQUE constraint on users.email at database level
- **FR-008**: System MUST return JWT token on successful signup containing claims: user_id, email, name, gpu_type, ram_capacity, coding_languages, robotics_experience, expiration (exp)
- **FR-009**: System MUST provide a POST `/api/auth/signin` endpoint accepting email and password
- **FR-010**: System MUST verify passwords using async bcrypt comparison against stored password_hash
- **FR-011**: System MUST return 401 Unauthorized for invalid credentials during signin with message "Invalid credentials"
- **FR-012**: System MUST sign JWT tokens using HS256 algorithm with AUTH_SECRET key (minimum 32 characters)
- **FR-013**: System MUST set JWT expiration to 24 hours from issuance (configurable via JWT_EXPIRATION_SECONDS environment variable)
- **FR-014**: Frontend MUST display 2-step signup modal: Step 1 (email, password, name), Step 2 (GPU type, RAM capacity, coding languages multi-select, robotics experience)
- **FR-015**: Frontend MUST validate Step 1 fields before advancing to Step 2 (non-empty name, valid email format, password meets strength requirements)
- **FR-016**: Frontend MUST provide predefined options for GPU type: "No GPU", "NVIDIA RTX 3060", "NVIDIA RTX 4070 Ti", "NVIDIA RTX 4090", "Apple M1/M2/M3", "Other"
- **FR-017**: Frontend MUST provide predefined options for RAM capacity: "Less than 8GB", "8-16GB", "16-32GB", "More than 32GB"
- **FR-018**: Frontend MUST provide multi-select checkboxes for coding languages: Python, C++, JavaScript, Rust, Go, Other (allow selecting multiple)
- **FR-019**: Frontend MUST provide dropdown for robotics experience: "No prior experience", "Beginner (0-1 years)", "Intermediate (1-3 years)", "Advanced (3+ years)"
- **FR-020**: Frontend MUST store JWT token in browser localStorage under key "auth_token" on successful signup/signin
- **FR-021**: Frontend MUST decode JWT token on AuthContext initialization to restore user session across page reloads
- **FR-022**: Frontend MUST provide client-side JWT decoding function using base64 URL-safe decoding (no server request required)
- **FR-023**: Frontend MUST remove JWT token from localStorage on signout
- **FR-024**: Frontend MUST display authentication state in Docusaurus navbar via custom NavbarItem component
- **FR-025**: Navbar MUST show "Sign In" and "Sign Up" buttons when user is unauthenticated
- **FR-026**: Navbar MUST show user name, GPU type, user icon, and "Sign Out" button when user is authenticated
- **FR-027**: Frontend MUST open signup/signin modals without navigating away from current page (overlay approach)
- **FR-028**: Frontend MUST close modals on successful authentication and update navbar state immediately
- **FR-029**: System MUST return 400 Bad Request for signup attempts with duplicate email containing message "Email already exists"
- **FR-030**: System MUST validate GPU type against allowed enum values at database level (CHECK constraint)
- **FR-031**: System MUST validate RAM capacity against allowed enum values at database level (CHECK constraint)
- **FR-032**: System MUST validate robotics experience against allowed enum values at database level (CHECK constraint)
- **FR-033**: System MUST cascade delete user_profiles records when parent users record is deleted (ON DELETE CASCADE)

### Key Entities

- **User**: Represents an account holder with authentication credentials (email, password_hash, name) and metadata (id, created_at). Each user has exactly one associated hardware profile.

- **User Profile**: Represents hardware and experience data collected during signup to enable personalization. Contains gpu_type (enum: No GPU, NVIDIA RTX 3060, RTX 4070 Ti, RTX 4090, Apple M1/M2/M3, Other), ram_capacity (enum: <8GB, 8-16GB, 16-32GB, >32GB), coding_languages (array: Python, C++, JavaScript, Rust, Go, Other), robotics_experience (enum: No prior experience, Beginner 0-1y, Intermediate 1-3y, Advanced 3+y). Linked to User via user_id foreign key.

- **JWT Token**: Short-lived authentication credential (24-hour expiration) issued on successful signup/signin. Contains embedded user profile claims to enable stateless personalization without database queries. Stored client-side in localStorage and included in Authorization header for authenticated API requests.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can complete the full signup flow (Steps 1 and 2) in under 90 seconds
- **SC-002**: Signup API endpoint responds in under 500ms (including password hashing and database write)
- **SC-003**: Signin API endpoint responds in under 400ms (including password verification and JWT generation)
- **SC-004**: JWT token size remains under 1KB to fit in standard HTTP headers and cookies (current: ~500 bytes)
- **SC-005**: 100% of signup attempts with valid data successfully create user accounts with profiles stored in database
- **SC-006**: 100% of signin attempts with valid credentials return JWT tokens with correct embedded profile claims
- **SC-007**: Zero password storage vulnerabilities (passwords never stored in plaintext, always bcrypt-hashed with salt)
- **SC-008**: 100% of duplicate email signup attempts are rejected with clear error message before database write
- **SC-009**: JWT tokens decode successfully on client-side without requiring server requests (pure JavaScript base64 decoding)
- **SC-010**: Authenticated users see their personalized navbar (name + GPU type) within 100ms of page load (localStorage read + JWT decode)
- **SC-011**: Platform earns 50 bonus hackathon points by implementing functional hardware-aware authentication with profile persistence
- **SC-012**: Authentication modals open and close without page reload or navigation (smooth UX, no content loss)

## Assumptions

1. **Database Connection**: Assumes Neon Postgres database is provisioned and DATABASE_URL environment variable is configured with valid connection string (no sslmode parameter for asyncpg compatibility)

2. **Environment Variables**: Assumes AUTH_SECRET is configured with at least 32 characters for JWT signing security

3. **Frontend Environment**: Assumes Docusaurus React environment with localStorage available (modern browsers, not server-side rendering context)

4. **API Base URL**: Assumes backend runs on http://localhost:8000 during development (hardcoded in AuthContext.tsx after process.env.REACT_APP_API_URL failed in browser)

5. **CORS Configuration**: Assumes backend allows CORS requests from frontend origin (http://localhost:3000 in development)

6. **User Hardware Honesty**: Assumes users provide accurate hardware information during signup (no verification mechanism for GPU/RAM claims)

7. **Single Device Login**: Assumes users primarily access platform from one device/browser (JWT in localStorage not synced across devices)

8. **No Password Recovery**: Initial implementation does not include "Forgot Password" flow (users with lost passwords cannot recover accounts)

9. **No Email Verification**: Initial implementation does not send verification emails (users can sign up with any email address without proving ownership)

10. **Session Duration**: Assumes 24-hour JWT expiration is acceptable balance between convenience and security (configurable via environment variable)

## Dependencies

- **External Services**: Neon Postgres (serverless PostgreSQL database for user and profile storage)
- **Backend Framework**: FastAPI (Python async web framework)
- **Database Driver**: asyncpg (async PostgreSQL driver for SQLAlchemy, requires connection strings without sslmode parameter)
- **Password Hashing**: bcrypt (via Python bcrypt library with async wrapper using asyncio.run_in_executor)
- **JWT Library**: PyJWT (Python implementation for HS256 token signing and verification)
- **Email Validation**: email-validator (required by pydantic EmailStr type)
- **Frontend Framework**: Docusaurus v3 with React 18 (static site generator with React components)
- **Styling**: Tailwind CSS (utility-first CSS framework for modal and navbar styling)
- **Icons**: lucide-react (icon library for User, LogOut, Lock, Mail icons)
- **Frontend HTTP**: Native fetch API (no axios or additional HTTP libraries)

## Out of Scope

1. **OAuth2 / Social Login**: Third-party authentication (Google, GitHub, etc.) is not included in this phase
2. **Email Verification**: No email confirmation flow or verification links sent after signup
3. **Password Recovery**: No "Forgot Password" / password reset functionality
4. **Multi-Factor Authentication (MFA)**: No 2FA or OTP verification
5. **Account Deletion**: No self-service account deletion UI (would require manual database operation)
6. **Profile Editing**: Users cannot update their hardware profile after signup (profile is immutable in v1)
7. **Admin Dashboard**: No administrative interface for managing users or viewing profiles
8. **Rate Limiting**: No API rate limiting or brute-force protection on signin attempts
9. **Audit Logging**: No logging of authentication events (signup, signin, signout) for security monitoring
10. **JWT Refresh Tokens**: No refresh token mechanism (users must sign in again after 24-hour expiration)
11. **RBAC / Permissions**: No role-based access control or permission system (all authenticated users have equal access)
12. **Hardware Verification**: No mechanism to verify user-reported GPU/RAM (relies on user honesty)
13. **Content Personalization Logic**: This spec only covers profile collection and storage; actual content filtering/recommendation based on hardware is a future phase
14. **Internationalization**: Authentication UI is English-only (no Urdu translation in this phase)
15. **Accessibility (WCAG)**: No formal accessibility audit or ARIA labels for screen readers (basic HTML semantics only)

## Notes

- This feature was implemented and deployed successfully as documented in the conversation transcript
- Backend running on port 8000, frontend on port 3000
- Database migration script: `backend/db/migrations/003_user_profile_hardware.sql` creates users and user_profiles tables
- Main implementation files:
  - Backend: `backend/src/routers/auth.py`, `backend/src/models/auth.py`, `backend/src/utils/jwt.py`, `backend/src/utils/password.py`
  - Frontend: `src/context/AuthContext.tsx`, `src/components/Auth/SignupModal.tsx`, `src/components/Auth/SigninModal.tsx`, `src/theme/NavbarItem/AuthButton.tsx`
- Known issue resolved: process.env undefined in browser context (replaced with hardcoded API URL)
- Known issue resolved: Docusaurus navbar validation error (changed type from 'default' to 'html')
- Launch scripts available: `scripts/start_all.sh` (with health checks) and `scripts/start_simple.sh` (recommended for quick startup)
