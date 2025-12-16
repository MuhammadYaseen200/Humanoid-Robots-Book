# Research: Better-Auth & User Profiling Implementation

**Feature**: 003-better-auth
**Created**: 2025-12-16
**Purpose**: Research technical decisions and best practices for authentication implementation

## Research Questions & Findings

### 1. JWT Token Storage Mechanism

**Question**: Should JWT tokens be stored in httpOnly cookies or localStorage?

**Decision**: **httpOnly Cookies (Production) + localStorage (Development Fallback)**

**Rationale**:
- **Security**: httpOnly cookies prevent XSS attacks (JavaScript cannot access token)
- **CSRF Protection**: Combine with SameSite=Strict cookie attribute
- **Cross-origin**: Requires CORS configuration with `credentials: 'include'`
- **Development**: localStorage acceptable for local development (easier debugging)

**Alternatives Considered**:
1. **localStorage only**: Vulnerable to XSS attacks, simpler implementation
2. **Session storage**: Tokens lost on tab close, poor UX
3. **Memory only**: Tokens lost on page refresh, poor UX

**Implementation Notes**:
- Backend sets cookie in `/auth/signup` and `/auth/signin` responses
- Frontend includes `credentials: 'include'` in fetch requests
- Cookie attributes: `HttpOnly`, `Secure` (HTTPS only), `SameSite=Strict`, `Max-Age=86400` (24 hours)

---

### 2. Password Hashing Algorithm

**Question**: Which password hashing algorithm provides best security/performance balance?

**Decision**: **bcrypt with 12 salt rounds**

**Rationale**:
- **Industry Standard**: Widely adopted, battle-tested
- **Adaptive**: Salt rounds can be increased as hardware improves
- **Timing**: ~200-300ms per hash (acceptable for signup/signin, prevents brute-force)
- **Python Library**: `passlib` provides bcrypt implementation with good API

**Alternatives Considered**:
1. **Argon2**: Newer, more secure, but less mature Python ecosystem
2. **PBKDF2**: Older standard, faster but less secure than bcrypt
3. **scrypt**: Good security but higher memory usage

**Implementation Notes**:
```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash(plain_password)  # Signup
is_valid = pwd_context.verify(plain_password, hashed)  # Signin
```

---

### 3. Rate Limiting Implementation

**Question**: How to implement rate limiting for auth endpoints without Redis?

**Decision**: **slowapi library (in-memory cache) for MVP, Redis for production**

**Rationale**:
- **MVP**: slowapi uses in-memory cache, zero infrastructure dependencies
- **Production**: Redis provides distributed rate limiting across multiple backend instances
- **Limits**: 10 requests per minute per IP for auth endpoints
- **Granularity**: Per-endpoint limits (signup, signin separate counters)

**Alternatives Considered**:
1. **Redis only**: Requires infrastructure setup, overkill for hackathon
2. **Custom middleware**: Reinventing wheel, error-prone
3. **No rate limiting**: Security risk, bonus points require security best practices

**Implementation Notes**:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)
@app.post("/auth/signup")
@limiter.limit("10/minute")
async def signup(request: Request, ...):
```

---

### 4. Email Validation Pattern

**Question**: Which email regex pattern balances strictness and usability?

**Decision**: **Simplified RFC 5322 pattern + DNS MX record check (optional)**

**Rationale**:
- **Pattern**: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
- **Trade-off**: Rejects edge cases (quoted strings, IP addresses) but catches 99.9% of real emails
- **UX**: Clear error messages for invalid formats
- **Future**: Can add DNS MX record validation in production

**Alternatives Considered**:
1. **Full RFC 5322**: Overly complex, allows edge cases users won't use
2. **Simple pattern** (`.*@.*`): Too permissive, allows invalid emails
3. **Email service validation**: Requires API calls, adds latency

**Implementation Notes**:
- Frontend: HTML5 `<input type="email">` for basic validation
- Backend: Pydantic `EmailStr` type + custom validator
- Error message: "Please enter a valid email address (e.g., student@example.com)"

---

### 5. JWT Claims Structure

**Question**: What profile data should be embedded in JWT to enable stateless personalization?

**Decision**: **Embed all hardware/software profile fields in JWT claims**

**Rationale**:
- **Stateless**: Personalization endpoint can extract user profile from JWT without database query
- **Performance**: Eliminates 1 database query per personalization request
- **Freshness**: JWT refreshed on profile update (max 24-hour staleness acceptable)
- **Size**: Profile claims ~500 bytes (well under 4KB cookie limit)

**JWT Payload Structure**:
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "email": "student@example.com",
  "name": "John Doe",
  "gpu_type": "NVIDIA RTX 4070 Ti",
  "ram_capacity": "16-32GB",
  "coding_languages": ["Python", "C++"],
  "robotics_experience": "Hobbyist",
  "iat": 1702989600,
  "exp": 1703076000
}
```

**Alternatives Considered**:
1. **Minimal JWT** (user_id only): Requires database lookup on every request (defeats stateless goal)
2. **Separate profile token**: Adds complexity, two tokens to manage
3. **Encrypted JWT**: Overkill, signed JWT sufficient (data not secret, just authenticated)

**Implementation Notes**:
- Use `python-jose` library for JWT encoding/decoding
- Sign with HS256 algorithm (symmetric key from AUTH_SECRET env var)
- Validate expiration on every request
- Refresh token on profile update by re-issuing JWT with new claims

---

### 6. Database Schema Extension

**Question**: Should profile fields be in `users` table or separate `user_profiles` table?

**Decision**: **Extend existing `user_profiles` table** (already exists from migration 001)

**Rationale**:
- **Separation of Concerns**: Authentication data (email, password) separate from profile data
- **Existing Schema**: `user_profiles` table already has `user_id` foreign key to `users`
- **Performance**: JSONB column for `coding_languages` array is PostgreSQL-native
- **Migration**: Add 4 columns to existing table (non-breaking change)

**Schema Changes Required**:
```sql
ALTER TABLE user_profiles
  ADD COLUMN gpu_type VARCHAR(100),
  ADD COLUMN ram_capacity VARCHAR(20),
  ADD COLUMN coding_languages JSONB DEFAULT '[]'::JSONB,
  ADD COLUMN robotics_experience VARCHAR(50);
```

**Alternatives Considered**:
1. **Add to `users` table**: Mixes auth and profile data, violates separation of concerns
2. **New `hardware_profiles` table**: Over-engineering, unnecessary join complexity
3. **Store in `preferences` JSONB column**: Untyped, harder to query

---

### 7. Frontend Form Validation

**Question**: Should validation be client-side only, server-side only, or both?

**Decision**: **Both (client-side for UX, server-side for security)**

**Rationale**:
- **Client-side**: Real-time feedback, prevents unnecessary API calls, better UX
- **Server-side**: Security boundary, cannot be bypassed, catches edge cases
- **Libraries**: Frontend uses HTML5 validation + custom JavaScript, backend uses Pydantic

**Validation Rules**:
- **Email**: HTML5 email type + backend Pydantic `EmailStr`
- **Password**: Frontend regex `/^(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*]).{8,}$/` + backend validator
- **Dropdown fields**: Frontend `<select required>` + backend `Enum` validation
- **Multi-select**: Frontend minimum 1 selection + backend non-empty list check

**Implementation Notes**:
- Frontend shows validation errors on blur (after user leaves field)
- Backend returns 422 Unprocessable Entity with detailed error messages
- Error message format: `{"detail": [{"loc": ["body", "password"], "msg": "Password must contain uppercase, number, and symbol"}]}`

---

### 8. Password Reset Token Security

**Question**: How to securely implement password reset without session storage?

**Decision**: **Short-lived JWT with reset-specific claim**

**Rationale**:
- **Stateless**: No database storage of reset tokens
- **Time-Limited**: 1-hour expiration prevents token reuse
- **Single-Use**: Include `reset_counter` in JWT (increment in database on each reset)
- **Secure**: Different secret key for reset tokens (separate from auth tokens)

**Reset Token Structure**:
```json
{
  "sub": "user_id",
  "type": "password_reset",
  "reset_counter": 5,
  "exp": 1702993200
}
```

**Alternatives Considered**:
1. **Random tokens in database**: Requires new table, cleanup job for expired tokens
2. **Magic links with UUID**: Requires token storage, difficult to expire
3. **Email verification code**: Poor UX (user must copy code), phishing risk

**Implementation Notes**:
- Generate reset token with separate SECRET_KEY_RESET environment variable
- Send reset link: `https://example.com/reset-password?token=<jwt>`
- Validate token, check `reset_counter` matches database value
- On successful reset: increment `reset_counter` in database (invalidates old tokens)

---

## Technology Stack Summary

### Backend Dependencies
- **FastAPI**: 0.110+ (async web framework)
- **python-jose[cryptography]**: 3.3+ (JWT encoding/decoding)
- **passlib[bcrypt]**: 1.7+ (password hashing)
- **slowapi**: 0.1+ (rate limiting)
- **pydantic**: 2.5+ (data validation)
- **asyncpg**: 0.29+ (PostgreSQL async driver, already in project)

### Frontend Dependencies
- **Better-Auth React**: 0.x (optional, for UI components only)
- **React**: 18.2+ (already in Docusaurus)
- **Fetch API**: Native (no axios needed)

### Infrastructure
- **Neon Postgres**: Existing database (0.5GB free tier)
- **Environment Variables**: AUTH_SECRET (32+ chars), AUTH_SECRET_RESET (32+ chars)

---

## Risk Analysis

### High Priority Risks

1. **JWT Size Exceeds Cookie Limit (4KB)**
   - **Mitigation**: Current profile claims ~500 bytes, well under limit
   - **Monitoring**: Log JWT size in development, alert if approaching 3KB

2. **Bcrypt Blocking Event Loop**
   - **Mitigation**: Use `run_in_executor` for bcrypt operations in async context
   - **Code**: `await loop.run_in_executor(None, pwd_context.hash, password)`

3. **Email Enumeration via Timing Attacks**
   - **Mitigation**: Always perform bcrypt hash even if email doesn't exist (constant time)
   - **Code**: `fake_hash = pwd_context.hash("dummy_password")` when email not found

4. **CORS Misconfiguration with httpOnly Cookies**
   - **Mitigation**: Set `allow_credentials=True` and specific `allow_origins` (not wildcard)
   - **Code**: `CORSMiddleware(allow_credentials=True, allow_origins=["https://example.com"])`

### Medium Priority Risks

5. **JWT Expiration During Active Session**
   - **Mitigation**: Frontend detects 401 errors, prompts user to re-signin without losing page state
   - **UX**: "Your session expired. Please sign in again to continue."

6. **Password Reset Token Reuse**
   - **Mitigation**: `reset_counter` in database invalidates all previous tokens
   - **Trade-off**: Acceptable for MVP, full blacklist implementation deferred to production

---

## Performance Benchmarks

### Expected Latencies (p95)
- **Signup**: 1.5 seconds (500ms DB insert + 300ms bcrypt + 200ms JWT generation + 500ms network)
- **Signin**: 1.2 seconds (200ms DB query + 300ms bcrypt verify + 200ms JWT generation + 500ms network)
- **Profile Update**: 800ms (300ms DB update + 200ms JWT refresh + 300ms network)
- **JWT Validation**: 30ms (signature verification only, no DB query)

### Bottlenecks
1. **bcrypt hashing**: 200-300ms per operation (unavoidable for security)
2. **Database roundtrip**: 100-200ms (Neon Postgres network latency)
3. **Email sending**: 2-5 seconds for password reset (async, doesn't block response)

---

## Security Checklist

- [x] Passwords hashed with bcrypt (12 salt rounds)
- [x] JWT tokens signed with HS256 and secret ≥ 32 characters
- [x] Rate limiting enabled (10 requests/minute/IP for auth endpoints)
- [x] Email enumeration prevention (constant-time responses, generic errors)
- [x] httpOnly cookies for production (XSS protection)
- [x] SameSite=Strict cookies (CSRF protection)
- [x] HTTPS enforced for Secure cookies
- [x] Password validation (min 8 chars, uppercase, number, symbol)
- [x] Email validation (RFC 5322 compliant regex)
- [x] SQL injection prevention (Pydantic models, parameterized queries)
- [x] CORS configured with specific origins (not wildcard with credentials)
- [x] Authentication event logging for security monitoring
- [x] Password reset tokens time-limited (1 hour expiration)

---

## References

- **ADR-002**: Better-Auth Integration (JWT token strategy)
- **Migration 001**: Initial database schema (users and user_profiles tables)
- **Spec FR-001 to FR-037**: Functional requirements
- **FastAPI Security Docs**: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
- **OWASP Authentication Cheat Sheet**: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
