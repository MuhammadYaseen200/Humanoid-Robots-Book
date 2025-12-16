# Feature Specification: Better-Auth & User Profiling

**Feature Branch**: `003-better-auth`
**Created**: 2025-12-16
**Status**: Draft
**Input**: User description: "Better-Auth & User Profiling feature for hackathon bonus points: Implement Signup/Signin using Better-Auth (Python/FastAPI), ask Hardware Background questions during signup (GPU type, RAM, Coding Language), and store profiles in Neon Postgres for content personalization."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - New User Signup with Hardware Profiling (Priority: P1)

A first-time visitor wants to create an account to access personalized content and unlock premium features (content personalization, Urdu translation). During signup, they provide their email, password, and answer hardware/software background questions so the system can later recommend appropriate learning paths and content difficulty levels.

**Why this priority**: This is the foundation for earning the 50 bonus points. Without signup and profile collection, content personalization (another 50 points) cannot function. This is the MVP for the authentication feature.

**Independent Test**: Can be fully tested by visiting the site, clicking "Sign Up", completing the registration form with hardware questions, and verifying the account is created in the database with all profile fields populated.

**Acceptance Scenarios**:

1. **Given** a new visitor on any chapter page, **When** they click "Sign Up" button in the navigation bar, **Then** a signup modal appears with email, password, and hardware background fields
2. **Given** the signup form is displayed, **When** the user enters valid email (student@example.com), strong password (min 8 chars with uppercase, number, symbol), selects GPU type ("None/Integrated", "NVIDIA RTX 3060", "NVIDIA RTX 4070 Ti", "Other"), RAM ("4-8GB", "8-16GB", "16-32GB", "32GB+"), and primary coding language ("None", "Python", "C++", "JavaScript", "Other"), **Then** the system creates user account and profile, returns JWT token, and redirects to welcome page
3. **Given** user enters email already in database, **When** they submit signup form, **Then** system displays error "Email already registered. Please sign in instead." with link to signin form
4. **Given** user enters weak password (less than 8 characters), **When** they submit form, **Then** system displays error "Password must be at least 8 characters with uppercase, number, and symbol"
5. **Given** user successfully signs up, **When** the backend stores their profile, **Then** database contains user record with hashed password (bcrypt) and user_profile record with gpu_type, ram_capacity, coding_experience fields populated

---

### User Story 2 - Returning User Signin (Priority: P2)

A returning user who previously created an account wants to sign in to access their personalized content settings, chat history, and profile preferences. They provide their registered email and password to authenticate.

**Why this priority**: Authentication flow is incomplete without signin. This enables returning users to access their profiles and is required for the full 50 bonus points.

**Independent Test**: Create a test account, sign out, then attempt to sign in with correct and incorrect credentials to verify authentication logic.

**Acceptance Scenarios**:

1. **Given** a returning user on any page, **When** they click "Sign In" button in navigation, **Then** signin modal appears with email and password fields
2. **Given** user enters correct email and password, **When** they submit signin form, **Then** system validates credentials, generates JWT token with user profile claims (user_id, email, gpu_type, ram_capacity, coding_experience), returns token to frontend, and closes modal showing user as logged in
3. **Given** user enters incorrect password, **When** they submit form, **Then** system displays error "Invalid email or password" without revealing which field is wrong (security best practice)
4. **Given** user enters email not in database, **When** they submit form, **Then** system displays same "Invalid email or password" error to prevent email enumeration attacks
5. **Given** user successfully signs in, **When** frontend receives JWT token, **Then** token is stored securely (httpOnly cookie preferred, or localStorage with XSS protections), and user's name/email appears in navigation bar with "Sign Out" option

---

### User Story 3 - Profile Management (Priority: P3)

A logged-in user wants to view and update their hardware/software background profile after signup because they upgraded their GPU, learned a new programming language, or want to adjust their learning difficulty level.

**Why this priority**: Profile editing enhances user experience but is not strictly required for bonus points. Users can re-register if needed, but editing improves retention.

**Independent Test**: Sign in as existing user, navigate to profile page, change GPU type from "None" to "RTX 4070 Ti", save changes, sign out, sign in again, and verify updated GPU type is reflected in profile.

**Acceptance Scenarios**:

1. **Given** logged-in user clicks their name in navigation, **When** dropdown menu appears, **Then** "My Profile" option is visible
2. **Given** user navigates to profile page, **When** page loads, **Then** form displays current values for email (read-only), GPU type (dropdown), RAM capacity (dropdown), coding languages (multi-select), and difficulty preference (beginner/intermediate/advanced radio buttons)
3. **Given** user changes GPU type from "None" to "RTX 4070 Ti" and clicks Save, **When** backend receives update request with valid JWT, **Then** user_profiles table is updated, JWT is refreshed with new gpu_type claim, and success message "Profile updated successfully" is displayed
4. **Given** user attempts to access profile page without authentication, **When** they navigate to /profile URL directly, **Then** system redirects to signin modal with message "Please sign in to view your profile"

---

### User Story 4 - Password Reset Flow (Priority: P4)

A user who forgot their password wants to reset it via email link so they can regain access to their account without contacting support.

**Why this priority**: Password reset improves user experience but is not required for hackathon bonus points. Many users can re-register with new email if needed. This is a nice-to-have for production readiness.

**Independent Test**: Click "Forgot Password", enter registered email, receive reset link via email (or see link in backend logs for testing), click link, set new password, and sign in with new credentials.

**Acceptance Scenarios**:

1. **Given** user clicks "Forgot Password" link on signin modal, **When** forgot password form appears, **Then** user can enter their registered email address
2. **Given** user enters valid registered email, **When** they submit form, **Then** system generates password reset token (JWT with 1-hour expiration), sends email with reset link to user's email address, and displays "Password reset link sent to your email" message
3. **Given** user clicks reset link in email, **When** they land on password reset page with valid token, **Then** form displays two fields: "New Password" and "Confirm Password"
4. **Given** user enters matching strong passwords and submits, **When** backend validates token and updates password hash, **Then** success message "Password updated successfully. Please sign in with your new password" is displayed and user is redirected to signin modal

---

### Edge Cases

- **What happens when user tries to sign up without providing hardware background answers?** System displays validation error: "Please complete all hardware profile questions. This helps us personalize your learning experience." All fields are required.

- **How does system handle weak passwords during signup?** Frontend validates password strength in real-time (as user types) with visual indicators (weak/medium/strong). Backend validates on submission and rejects passwords shorter than 8 characters or missing uppercase/number/symbol with clear error message.

- **What happens if user closes signup modal halfway through filling form?** Form data is not persisted. User must restart signup process. (Session-based form saving is out of scope for MVP.)

- **How does system handle concurrent signin attempts from different devices?** JWT tokens are stateless, so user can be logged in on multiple devices simultaneously. Each device gets its own JWT. This is acceptable for MVP. Token revocation (blacklist) is out of scope.

- **What happens when JWT token expires while user is actively using the site?** When token expires (24-hour default), next API request to protected endpoint (/personalize, /translate, /profile) returns 401 Unauthorized. Frontend detects this, clears expired token, and displays modal: "Your session has expired. Please sign in again." User can sign in without losing their place on the current page.

- **How does system handle special characters in passwords (emojis, international characters)?** System accepts any UTF-8 characters in passwords. Bcrypt hashing supports UTF-8. No restrictions on character sets to accommodate international users.

- **What happens if user enters invalid email format during signup?** Frontend validates email format in real-time using HTML5 email input type. Backend validates using regex pattern (RFC 5322 compliant). Invalid emails are rejected with error: "Please enter a valid email address."

- **How does system prevent email enumeration attacks during signin?** System returns generic "Invalid email or password" error for both wrong email and wrong password. Response time is constant (no timing attacks) by always performing bcrypt hash comparison even if email doesn't exist.

- **What happens when database connection fails during signup?** Backend catches database exception, logs error with request ID for debugging, and returns user-friendly error: "Unable to create account. Please try again later." (Error ID: XYZ for support reference). Frontend displays error with retry button.

- **How does system handle user clicking signup submit button multiple times rapidly?** Frontend disables submit button after first click and shows loading spinner. Backend uses database email unique constraint to prevent duplicate accounts. If duplicate detected, returns error handled by frontend.

## Requirements *(mandatory)*

### Functional Requirements

**Authentication Core**

- **FR-001**: System MUST provide signup form accessible from any page via "Sign Up" button in navigation bar
- **FR-002**: System MUST collect email address (unique identifier), password (minimum 8 characters), and full name during signup
- **FR-003**: System MUST hash passwords using bcrypt with salt rounds ≥ 12 before storing in database
- **FR-004**: System MUST validate email format using RFC 5322 compliant regex pattern on both frontend and backend
- **FR-005**: System MUST enforce password requirements: minimum 8 characters, at least one uppercase letter, one number, and one symbol
- **FR-006**: System MUST check email uniqueness in database before creating account and display clear error if email already exists
- **FR-007**: System MUST generate JWT token after successful signup/signin containing user_id, email, and profile claims (gpu_type, ram_capacity, coding_experience)
- **FR-008**: System MUST sign JWT tokens with AUTH_SECRET environment variable using HS256 algorithm
- **FR-009**: System MUST set JWT expiration to 24 hours from issuance time
- **FR-010**: System MUST provide signin form with email and password fields accessible via "Sign In" button
- **FR-011**: System MUST validate signin credentials by comparing bcrypt hash of submitted password against stored password_hash
- **FR-012**: System MUST return generic error "Invalid email or password" for both incorrect email and incorrect password to prevent email enumeration
- **FR-013**: System MUST update last_login timestamp in users table upon successful signin

**Hardware/Software Profiling**

- **FR-014**: Signup form MUST include dropdown field "GPU Type" with options: "None/Integrated Graphics", "NVIDIA RTX 3060", "NVIDIA RTX 4070 Ti", "NVIDIA RTX 4080/4090", "AMD Radeon RX 7000 Series", "Other (please specify in profile)"
- **FR-015**: Signup form MUST include dropdown field "RAM Capacity" with options: "4-8GB", "8-16GB", "16-32GB", "32GB or more"
- **FR-016**: Signup form MUST include multi-select field "Programming Languages" with options: "None (new to programming)", "Python", "C++", "JavaScript/TypeScript", "Java", "C#", "Rust", "Other"
- **FR-017**: Signup form MUST include radio button field "Robotics Experience" with options: "No prior experience", "Hobbyist (built simple projects)", "Student (taking courses)", "Professional (industry experience)"
- **FR-018**: System MUST store hardware/software profile answers in user_profiles table with columns: gpu_type (VARCHAR), ram_capacity (VARCHAR), coding_languages (JSONB array), robotics_experience (VARCHAR)
- **FR-019**: System MUST require all profile questions to be answered during signup (no optional fields) to ensure data completeness for personalization
- **FR-020**: System MUST include profile fields (gpu_type, ram_capacity, coding_languages, robotics_experience) in JWT token claims for stateless access by personalization endpoints

**Profile Management**

- **FR-021**: System MUST provide "My Profile" page accessible to authenticated users via navigation dropdown under user's name
- **FR-022**: Profile page MUST display current values for all hardware/software profile fields in editable form
- **FR-023**: System MUST allow users to update their profile fields and save changes
- **FR-024**: System MUST validate JWT token on profile update requests and reject unauthorized requests with 401 status
- **FR-025**: System MUST refresh JWT token with updated profile claims after successful profile update
- **FR-026**: System MUST prevent users from changing their email address on profile page (email is permanent identifier; users must contact support to change email)

**Security & Session Management**

- **FR-027**: System MUST store JWT tokens in httpOnly cookies (preferred) or localStorage with XSS protections
- **FR-028**: System MUST validate JWT signature and expiration on every request to protected endpoints (/api/personalize, /api/translate, /api/profile)
- **FR-029**: System MUST return 401 Unauthorized status with error message "Invalid or expired token" when JWT validation fails
- **FR-030**: System MUST provide "Sign Out" functionality that clears JWT token from browser storage and redirects to homepage
- **FR-031**: System MUST log all authentication events (signup, signin, failed signin attempts) to user_activity table for security monitoring
- **FR-032**: System MUST rate-limit authentication endpoints to 10 requests per IP per minute to prevent brute-force attacks
- **FR-033**: System MUST never log passwords (plaintext or hashed) in application logs or error messages

**Password Reset (Optional for MVP)**

- **FR-034**: System SHOULD provide "Forgot Password" link on signin modal
- **FR-035**: System SHOULD send password reset email with time-limited token (1-hour expiration) when user requests password reset
- **FR-036**: System SHOULD validate reset token and allow user to set new password via reset link
- **FR-037**: System SHOULD invalidate all existing JWT tokens for user after password reset (force re-signin on all devices)

### Key Entities

- **User**: Represents an authenticated user account
  - Attributes: unique email, hashed password, full name, account creation timestamp, last login timestamp, active status
  - Relationships: Has one UserProfile, has many ChatSessions, has many UserActivityLogs

- **UserProfile**: Extended profile information for personalization
  - Attributes: GPU type, RAM capacity, programming languages (array), robotics experience level, learning difficulty preference, completed chapters (array)
  - Relationships: Belongs to one User

- **JWTToken** (logical entity, not stored in database): Authentication credential
  - Claims: user_id (subject), email, gpu_type, ram_capacity, coding_languages, robotics_experience, expiration timestamp
  - Lifecycle: Issued on signup/signin, validated on each protected request, expires after 24 hours

- **AuthenticationEvent** (stored in user_activity table): Audit log entry
  - Attributes: event type (signup, signin, signout, failed_signin, password_reset), timestamp, IP address, user agent, user_id (if authenticated)
  - Purpose: Security monitoring, suspicious activity detection, compliance auditing

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: New users can complete signup process including hardware profiling in under 2 minutes
- **SC-002**: Returning users can sign in within 10 seconds
- **SC-003**: System correctly authenticates valid credentials 100% of the time
- **SC-004**: System correctly rejects invalid credentials (wrong password, non-existent email) 100% of the time
- **SC-005**: Password reset emails are delivered within 60 seconds of request
- **SC-006**: Profile updates are persisted immediately (reflected in next API request)
- **SC-007**: JWT tokens enable stateless authentication (no database lookup required to validate token)
- **SC-008**: Authentication endpoints handle 100 concurrent requests without errors
- **SC-009**: Zero plaintext passwords stored in database or logged in application logs
- **SC-010**: 90% of users successfully complete signup on first attempt without validation errors
- **SC-011**: System prevents brute-force attacks by rate-limiting failed signin attempts to 10 per minute per IP
- **SC-012**: Profile data completeness is 100% (all hardware/software questions answered by all users)

### Assumptions

- Users have valid email addresses they can access for signup confirmation and password resets
- Better-Auth library is used only for frontend UI components (signup/signin forms); backend authentication logic is custom FastAPI implementation using JWT
- Database schema already exists (users and user_profiles tables from migration 001_initial_schema.sql)
- Database schema will be extended with new columns: gpu_type, ram_capacity, coding_languages, robotics_experience in user_profiles table
- Frontend is React-based (Docusaurus) and can integrate Better-Auth React components or custom forms
- Backend API base URL is available as environment variable (VITE_API_URL for frontend, configurable via .env)
- AUTH_SECRET environment variable is securely generated (minimum 32 characters, cryptographically random)
- Neon Postgres database supports JSONB type for storing coding_languages array
- Email sending service is available for password reset emails (SendGrid, AWS SES, or SMTP server)
- Rate limiting can be implemented using FastAPI middleware or Redis (if available; fallback to in-memory cache)
- User timezone handling is out of scope (all timestamps stored in UTC, displayed in browser's local timezone)
- Multi-factor authentication (MFA) is out of scope for this MVP
- OAuth2 social signin (Google, GitHub) is out of scope for this MVP
- Anonymous users can still browse textbook content; authentication is required only for personalization, translation, and chat history features

### Out of Scope

- **OAuth2 Social Signin**: No Google, GitHub, or other social login providers (adds complexity, not required for bonus points)
- **Multi-Factor Authentication (MFA)**: No SMS or authenticator app 2FA (security enhancement for future iteration)
- **Email Verification**: No email confirmation link sent after signup (acceptable for hackathon; users can immediately access features after signup)
- **Session Management Database Table**: No sessions table in database; JWT tokens are stateless (aligns with ADR-002 decision)
- **Token Revocation/Blacklist**: Cannot revoke JWT tokens before expiration (acceptable; use short expiration times)
- **Account Deletion**: Users cannot delete their own accounts via UI (must contact support; prevents accidental data loss)
- **Admin Panel**: No admin interface for managing users, viewing analytics, or moderating content
- **Usage Analytics Dashboard**: No user-facing dashboard showing learning progress, time spent, or chapters completed
- **Real-Time Notifications**: No WebSocket or push notifications for account events
- **API Rate Limiting by User**: Rate limiting is per-IP only; no per-user API quotas
- **Internationalization (i18n) for Auth Forms**: Signup/signin forms are English-only (Urdu translation feature applies to textbook content, not auth UI)

### Dependencies

- **Better-Auth Library**: Frontend UI components for signup/signin forms (React library)
- **python-jose**: Python library for JWT encoding/decoding (backend dependency)
- **bcrypt or passlib**: Python library for password hashing (backend dependency)
- **FastAPI HTTPBearer Security**: FastAPI security utilities for extracting Bearer tokens from Authorization header
- **Neon Postgres Database**: Existing database with users and user_profiles tables (already provisioned)
- **Email Service** (optional for password reset): SendGrid, AWS SES, or SMTP server with credentials in .env
- **Redis** (optional for rate limiting): If available, use for distributed rate limiting; otherwise use in-memory cache

### Constraints

- **Cost**: Must operate within free tiers (Neon Postgres 0.5GB limit includes all tables: users, profiles, chat sessions)
- **Latency**: JWT validation must complete in under 50ms (stateless, no database lookup)
- **Security**: Password hashing (bcrypt) takes ~100-300ms per request (acceptable for signup/signin; unavoidable for security)
- **Database Size**: Each user account + profile consumes ~1KB (email, hash, profile fields). With 0.5GB limit and other tables, support up to ~100,000 users (more than sufficient for hackathon demo).
- **JWT Size**: Token payload must be under 4KB to fit in cookie header (current profile claims ~500 bytes; well within limit)
- **CORS**: Backend must allow requests from frontend domain (GitHub Pages or localhost during development)
- **HTTPS Required**: JWT tokens in cookies require Secure flag, which mandates HTTPS for production deployment

### Agent Assignments

- **@Backend-Engineer** (using `skills/fastapi-coder.md`):
  - Create `/api/auth/signup` POST endpoint for user registration
  - Create `/api/auth/signin` POST endpoint for authentication
  - Create `/api/auth/signout` POST endpoint (optional; primarily client-side token clearing)
  - Create `/api/profile` GET endpoint to fetch user profile
  - Create `/api/profile` PUT endpoint to update user profile
  - Implement JWT token generation, signing, and validation middleware
  - Implement bcrypt password hashing utility functions
  - Add validation for email format, password strength, profile fields
  - Implement rate limiting middleware for auth endpoints
  - Add authentication event logging to user_activity table
  - Write database migration to add new profile columns (gpu_type, ram_capacity, coding_languages, robotics_experience)

- **@Frontend-Architect** (using `skills/react-component.md`):
  - Create `<SignupModal />` React component with email, password, name, and hardware profile fields
  - Create `<SigninModal />` React component with email and password fields
  - Create `<ProfilePage />` React component for viewing/editing user profile
  - Integrate Better-Auth UI components or build custom forms with validation
  - Implement JWT token storage (httpOnly cookie via backend or localStorage with XSS protections)
  - Add "Sign Up" and "Sign In" buttons to Docusaurus navigation bar
  - Implement authenticated navigation state (show user name, "My Profile", "Sign Out" when logged in)
  - Add form validation with real-time feedback (password strength indicator, email format check)
  - Implement error handling for API failures (network errors, validation errors, authentication failures)
  - Add loading states for async operations (signup, signin, profile update)

### Non-Functional Requirements

**Performance**:
- Signup request must complete in under 2 seconds (p95)
- Signin request must complete in under 1 second (p95)
- JWT validation must complete in under 50ms
- Profile update must complete in under 1 second (p95)

**Security**:
- Passwords hashed with bcrypt salt rounds ≥ 12
- JWT tokens signed with HS256 and secret ≥ 32 characters
- Rate limiting: 10 auth requests per IP per minute
- No plaintext passwords in logs, database, or error messages
- Generic error messages to prevent email enumeration

**Reliability**:
- Auth endpoints must maintain 99.9% uptime
- Database failures must return user-friendly errors (no stack traces exposed)
- Token expiration must be handled gracefully with clear re-signin prompts

**Usability**:
- Signup form must complete in under 2 minutes
- Error messages must be clear and actionable
- Password requirements must be visible before submission
- Profile fields must have clear labels and help text explaining purpose
