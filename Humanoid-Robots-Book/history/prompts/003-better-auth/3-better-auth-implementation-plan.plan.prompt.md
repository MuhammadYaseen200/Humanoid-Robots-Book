---
id: 3
title: Better-Auth Implementation Plan
stage: plan
date: 2025-12-16
surface: agent
model: claude-sonnet-4-5
feature: 003-better-auth
branch: 003-better-auth
user: lead-architect
command: /sp.plan
labels: ["authentication", "jwt", "fastapi", "react", "planning", "architecture"]
links:
  spec: specs/003-better-auth/spec.md
  ticket: null
  adr: history/adr/002-better-auth-integration.md
  pr: null
files:
  - specs/003-better-auth/plan.md
  - specs/003-better-auth/research.md
  - specs/003-better-auth/data-model.md
  - specs/003-better-auth/contracts/auth-api.yaml
tests:
  - none (planning phase, tests defined in plan)
---

## Prompt

@.claude/agents/Lead_Architect_Agent.md
@specs/003-better-auth/spec.md

Please activate the Lead Architect Persona.
We are moving to the **Planning Phase**.
Based on the approved specification in 'specs/003-better-auth/spec.md', generate a comprehensive Technical Implementation Plan.

**Context & Goals:**
1. We are targeting the 50 Bonus Points for Auth & Profiling.
2. The plan must strictly enforce the collection of "Hardware Background" data (GPU, RAM) to enable Personalization later.
3. Ensure the architecture aligns with our decision to use FastAPI + JWT for the backend.

**Output Requirement:**
Create a file `specs/003-better-auth/plan.md` containing:
- **Phase 1: Database & Backend** (Schema updates in Neon, FastAPI Auth Routes).
- **Phase 2: Frontend Integration** (Better-Auth Client setup, Registration Form UI).
- **Phase 3: Verification** (Playwright tests for the Signup Flow).

Use your strategic breakdown skill to ensure dependencies are ordered correctly (e.g., DB must exist before API).

## Response snapshot

**Lead Architect Persona Activated - Comprehensive Planning Complete**

Created detailed technical implementation plan for Better-Auth & User Profiling feature targeting 50 hackathon bonus points.

**Planning Artifacts Created**:

1. **research.md** (8 Research Questions):
   - JWT token storage mechanism (httpOnly cookies vs localStorage)
   - Password hashing algorithm (bcrypt with 12 salt rounds)
   - Rate limiting implementation (slowapi for MVP, Redis for production)
   - Email validation pattern (simplified RFC 5322)
   - JWT claims structure (embed all profile fields for stateless personalization)
   - Database schema extension (extend user_profiles table)
   - Frontend validation strategy (both client and server-side)
   - Password reset token security (short-lived JWT with reset_counter)

2. **data-model.md** (5 Entity Definitions):
   - User (authentication entity, extended with reset_counter)
   - UserProfile (extended with gpu_type, ram_capacity, coding_languages, robotics_experience)
   - JWT Token (logical entity with profile claims)
   - PasswordResetToken (logical entity with type discrimination)
   - AuthenticationEvent (audit log in user_activity table)
   - Database migration 003 SQL provided
   - Entity relationship diagram
   - State transition diagrams (user lifecycle, JWT lifecycle)

3. **contracts/auth-api.yaml** (OpenAPI 3.1 Specification):
   - 6 endpoints: POST /auth/signup, POST /auth/signin, POST /auth/signout, GET /profile, PUT /profile, POST /auth/forgot-password, POST /auth/reset-password
   - Complete request/response schemas with validation rules
   - Error responses with status codes (201, 400, 401, 409, 422, 429)
   - JWT authentication scheme documented
   - Example payloads for beginner and advanced users

4. **plan.md** (4-Phase Implementation Plan):
   - **Phase 1: Database & Backend Foundation** (6-8 hours)
     - 1.1: Database migration (add profile columns, constraints, indexes)
     - 1.2: Pydantic models (SignupRequest, SigninRequest, ProfileUpdateRequest with validators)
     - 1.3: Password hashing utility (bcrypt with run_in_executor)
     - 1.4: JWT token management (create_access_token, decode_token, password reset tokens)
     - 1.5: Authentication routes (signup, signin, signout with rate limiting)
     - 1.6: Profile management routes (GET/PUT /profile with JWT refresh)
     - 1.7: Password reset routes (optional for MVP)

   - **Phase 2: Frontend Integration** (4-6 hours)
     - 2.1: Authentication context (React Context with useAuth hook)
     - 2.2: Signup modal component (hardware profile form with validation)
     - 2.3: Signin modal component (email/password with generic errors)
     - 2.4: Navigation bar integration (conditional rendering based on auth state)
     - 2.5: Profile page (editable hardware profile fields)

   - **Phase 3: Verification & Testing** (2-3 hours)
     - 3.1: Integration tests (pytest for backend endpoints)
     - 3.2: End-to-end tests (Playwright for complete user flows)
     - 3.3: Security validation (checklist for bcrypt, rate limiting, email enumeration)
     - 3.4: Performance benchmarks (signup <2s, signin <1s, JWT validation <50ms)

   - **Phase 4: Deployment & Monitoring** (2 hours)
     - 4.1: Environment configuration (AUTH_SECRET, CORS, DATABASE_URL)
     - 4.2: Database migration on production Neon
     - 4.3: Deploy backend (Railway/Render) and frontend (GitHub Pages/Vercel)
     - 4.4: Monitoring & logging setup (authentication events, failure rates)

**Constitution Check - All Principles Aligned**:
- ✅ Stateless Architecture: JWT with profile claims, no sessions table
- ✅ Security Best Practices: bcrypt (12 rounds), rate limiting, email enumeration prevention
- ✅ Smallest Viable Change: Extends existing tables, no new infrastructure
- ✅ Clear API Contracts: OpenAPI 3.1 spec with complete documentation
- ⚠️ Test-First: Unit tests planned but full TDD deferred due to hackathon timeline

**Key Architectural Decisions**:
1. **JWT Claims Strategy**: Embed all profile fields (gpu_type, ram_capacity, coding_languages, robotics_experience) in JWT to enable stateless personalization (eliminates DB query on /personalize requests)
2. **Password Hashing**: bcrypt with 12 salt rounds, wrapped in run_in_executor to prevent blocking async event loop
3. **Rate Limiting**: slowapi (in-memory) for MVP, Redis for production scaling
4. **Token Storage**: httpOnly cookies for production (XSS protection), localStorage for development (easier debugging)
5. **Profile Schema**: Extend existing user_profiles table with CHECK constraints for enum validation
6. **Email Enumeration Prevention**: Constant-time responses, generic error messages, always perform bcrypt hash even if email not found

**Risk Mitigation**:
- bcrypt blocking event loop → run_in_executor
- JWT size exceeds 4KB cookie limit → current claims ~500 bytes, well under limit
- Email enumeration timing attacks → constant-time responses with fake bcrypt hash
- CORS with httpOnly cookies → allow_credentials=True with specific origins

**Performance Targets**:
- Signup: <2 seconds (p95)
- Signin: <1 second (p95)
- Profile update: <1 second (p95)
- JWT validation: <50ms

**Acceptance Criteria**:
- 100% profile data completeness (all hardware questions required)
- JWT tokens enable stateless authentication (no DB lookup per request)
- Security checklist: 12 items (bcrypt, rate limiting, email enumeration, XSS protection, CORS, SQL injection prevention)
- All authentication events logged to user_activity table

**Dependencies Ordered Correctly**:
1. Database migration → Pydantic models → JWT system → Authentication routes
2. Authentication context → Signup/signin modals → Navigation integration → Profile page
3. Backend tests → Frontend tests → E2E tests → Production deployment

## Outcome

- ✅ Impact: Comprehensive 4-phase implementation plan created targeting 50 bonus points; all design artifacts complete (research, data model, API contracts, implementation plan); ready for /sp.tasks
- 🧪 Tests: Test strategies defined for all 3 phases (integration tests, E2E tests, security validation, performance benchmarks); acceptance criteria specified for each subtask
- 📁 Files: 4 files created (plan.md with 4 phases, research.md with 8 decisions, data-model.md with 5 entities and migration SQL, contracts/auth-api.yaml with OpenAPI spec)
- 🔁 Next prompts: `/sp.adr` to document JWT storage mechanism, password hashing configuration, rate limiting strategy decisions; `/sp.tasks` to generate detailed implementation tasks
- 🧠 Reflection: Plan is production-ready with rigorous architecture. JWT claims strategy enables stateless personalization (unlocks next 50-point feature). Security best practices comprehensive (bcrypt, rate limiting, email enumeration prevention, XSS protection). Performance targets realistic. Risk mitigation strategies defined for all high-priority risks.

## Evaluation notes (flywheel)

- Failure modes observed: None; planning process completed successfully with all design artifacts
- Graders run and results (PASS/FAIL): Constitution check: 5/5 principles aligned (1 partial for Test-First due to hackathon timeline); dependency ordering: PASS (DB → backend → frontend → deployment sequence correct); security checklist: 12/12 items addressed
- Prompt variant (if applicable): Standard /sp.plan workflow with Lead Architect persona activation and explicit phase requirements from user
- Next experiment (smallest change to try): Consider adding acceptance test scenarios for concurrent profile updates (race conditions); consider specifying JWT refresh token mechanism if 24-hour expiration proves too short for UX
