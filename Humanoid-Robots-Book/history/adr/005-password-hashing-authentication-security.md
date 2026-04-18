# ADR-005: Password Hashing and Authentication Security Strategy

**Status**: Accepted
**Date**: 2025-12-16
**Context**: Feature 003-better-auth
**Deciders**: Lead Architect (Claude Sonnet 4.5)

## Context and Problem Statement

The Better-Auth & User Profiling feature requires secure password storage and authentication mechanisms to prevent common attacks (brute-force, rainbow tables, timing attacks, email enumeration). The implementation must balance security requirements with performance constraints and user experience.

**Key Security Requirements**:
- Passwords must never be stored in plaintext
- Protection against rainbow table attacks (pre-computed hash databases)
- Protection against brute-force attacks (automated credential guessing)
- Protection against timing attacks (inferring valid emails by response time)
- Protection against email enumeration (discovering registered emails)
- Authentication must complete within acceptable latency (< 2 seconds for signup/signin)

## Decision Drivers

- **Security**: Prevent password compromise, brute-force, and enumeration attacks
- **Performance**: bcrypt hashing is CPU-intensive (~200-300ms per operation)
- **Async Compatibility**: FastAPI is async; bcrypt is synchronous (must not block event loop)
- **Future-Proofing**: Hashing algorithm should remain secure as hardware improves
- **Compliance**: Meet OWASP authentication security standards for hackathon bonus points

## Decision Clusters

This ADR documents three related security decisions that work together:

1. **Password Hashing Algorithm** (bcrypt with 12 salt rounds)
2. **Rate Limiting Strategy** (slowapi for MVP, Redis for production)
3. **Email Enumeration Prevention** (constant-time responses, generic error messages)

---

## Decision 1: Password Hashing Algorithm

### Considered Options

#### Option A: bcrypt with 12 Salt Rounds

**Architecture**:
- Use `passlib` library with bcrypt scheme
- 12 salt rounds (2^12 = 4096 iterations)
- Wrap in `run_in_executor` to prevent blocking async event loop

**Pros**:
- ✅ **Industry Standard**: Widely adopted, battle-tested algorithm
- ✅ **Adaptive**: Salt rounds can be increased as hardware improves
- ✅ **Timing**: ~200-300ms per hash (slow enough to prevent brute-force, fast enough for good UX)
- ✅ **Python Ecosystem**: Mature `passlib` library with good documentation

**Cons**:
- ❌ **Synchronous**: bcrypt is CPU-bound, blocks async event loop if not wrapped
- ❌ **Performance Cost**: 200-300ms adds latency to signup/signin requests

---

#### Option B: Argon2 with Default Parameters

**Architecture**:
- Use `argon2-cffi` library
- Argon2id variant (hybrid mode)
- Default memory cost, time cost, parallelism

**Pros**:
- ✅ **Modern Standard**: Winner of Password Hashing Competition 2015
- ✅ **Memory-Hard**: Resistant to GPU/ASIC attacks
- ✅ **Configurable**: Can tune memory, time, parallelism independently

**Cons**:
- ❌ **Less Mature Python Ecosystem**: Fewer tutorials, less community knowledge
- ❌ **Higher Memory Usage**: ~64MB per hash (vs ~1MB for bcrypt)
- ❌ **Overkill for Hackathon**: Additional complexity without clear benefit for MVP

**REJECTED**: bcrypt provides sufficient security for MVP; Argon2 can be adopted later if needed

---

#### Option C: PBKDF2 with SHA-256

**Architecture**:
- Use Python's `hashlib.pbkdf2_hmac`
- SHA-256 hash function
- 100,000 iterations

**Pros**:
- ✅ **Built-in**: Part of Python standard library (no external dependency)
- ✅ **Fast**: ~50-100ms per hash

**Cons**:
- ❌ **Weaker Security**: Faster hashing means easier brute-force
- ❌ **Not Recommended by OWASP**: OWASP prefers bcrypt or Argon2

**REJECTED**: Security trade-off not worth performance gain

---

### Decision Outcome (Password Hashing)

**Chosen Option**: **Option A - bcrypt with 12 Salt Rounds**

**Rationale**:
1. **Industry Standard**: bcrypt is recommended by OWASP, FastAPI security docs, and has 20+ years of battle-testing
2. **Adaptive Security**: 12 salt rounds provide good security in 2025; can increase to 13-14 as hardware improves
3. **Performance Balance**: 200-300ms is acceptable for signup/signin (users expect some latency for security operations)
4. **Python Maturity**: `passlib` library is well-documented with excellent FastAPI integration examples

---

## Decision 2: Rate Limiting Strategy

### Considered Options

#### Option A: slowapi Library (In-Memory Cache)

**Architecture**:
- Use `slowapi` library (Flask-Limiter port for FastAPI)
- In-memory cache stores request counts per IP address
- Limits: 10 requests per minute per IP for auth endpoints
- Resets counter every minute

**Pros**:
- ✅ **Zero Infrastructure**: No Redis/Memcached required
- ✅ **Simple Setup**: 5 lines of code to configure
- ✅ **Good Enough for MVP**: Sufficient for hackathon demo and small-scale deployment

**Cons**:
- ❌ **Single-Instance Only**: Doesn't work with multiple backend instances (each has separate counter)
- ❌ **Lost on Restart**: Counters reset when backend restarts
- ❌ **No Persistence**: Can't analyze rate limit violations after the fact

---

#### Option B: Redis-Based Rate Limiting

**Architecture**:
- Use Redis with `redis-py` library
- Store request counts in Redis with TTL (time-to-live)
- Distributed rate limiting across multiple backend instances

**Pros**:
- ✅ **Scalable**: Works with horizontal scaling (multiple backend instances)
- ✅ **Persistent**: Counters survive backend restarts
- ✅ **Analytics**: Can query Redis to analyze attack patterns

**Cons**:
- ❌ **Infrastructure Dependency**: Requires Redis instance (cost, maintenance)
- ❌ **Overkill for MVP**: Adds complexity for single-instance deployment
- ❌ **Free Tier Limits**: Upstash Redis free tier has connection limits

**DEFERRED**: Implement for production scaling, not MVP

---

### Decision Outcome (Rate Limiting)

**Chosen Option**: **Option A - slowapi for MVP, migrate to Redis for production**

**Rationale**:
1. **Hackathon Pragmatism**: slowapi provides immediate rate limiting without infrastructure setup
2. **Good Enough**: Single backend instance sufficient for demo and initial launch
3. **Migration Path**: Can swap slowapi for Redis later without changing endpoint logic
4. **Security Requirement Met**: Demonstrates rate limiting for bonus points (implementation details less critical)

---

## Decision 3: Email Enumeration Prevention

### Attack Vector

**Email Enumeration Attack**: Attacker can determine if email is registered by observing different error messages or response times:
- "Invalid password" → email exists
- "Email not found" → email doesn't exist
- Fast response (50ms) → email not in database (no bcrypt verification)
- Slow response (300ms) → email in database (bcrypt verification performed)

### Considered Options

#### Option A: Generic Error Message + Constant-Time Response

**Architecture**:
- Always return "Invalid email or password" error (never reveal which is wrong)
- Always perform bcrypt verification even if email not found (fake hash to maintain constant time)
- Log failed signin attempts for security monitoring

**Pros**:
- ✅ **Prevents Enumeration**: Attacker cannot determine if email exists
- ✅ **OWASP Recommended**: Best practice for authentication error messages
- ✅ **Constant Time**: Response time doesn't leak information about email existence

**Cons**:
- ❌ **Slightly Worse UX**: User doesn't know if they mistyped email or password (but security outweighs)

---

#### Option B: Different Errors for Email vs Password

**Architecture**:
- "Email not found" if email doesn't exist
- "Incorrect password" if email exists but password wrong

**Pros**:
- ✅ **Better UX**: User knows exactly what to fix

**Cons**:
- ❌ **Security Vulnerability**: Enables email enumeration attacks
- ❌ **OWASP Violation**: Explicitly discouraged by OWASP guidelines

**REJECTED**: Security risk outweighs UX benefit

---

### Decision Outcome (Email Enumeration)

**Chosen Option**: **Option A - Generic Error Message + Constant-Time Response**

**Rationale**:
1. **Security First**: Preventing email enumeration is OWASP authentication best practice
2. **Constant-Time Protection**: Performing bcrypt verification even on invalid emails prevents timing attacks
3. **Hackathon Bonus Points**: Demonstrates understanding of authentication security beyond basic password hashing
4. **Acceptable UX Trade-off**: Generic error message is industry standard (Gmail, GitHub, Twitter all use this pattern)

---

## Implementation Details

### Password Hashing with Async Wrapper

```python
from passlib.context import CryptContext
import asyncio

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def hash_password(plain_password: str) -> str:
    """Hash password using bcrypt (12 salt rounds).
    Runs in executor to avoid blocking event loop (~200-300ms)."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, pwd_context.hash, plain_password)

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash.
    Runs in executor to avoid blocking event loop (~200-300ms)."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, pwd_context.verify, plain_password, hashed_password)
```

**Why `run_in_executor`?**
- bcrypt is CPU-bound and synchronous (blocks for 200-300ms)
- FastAPI is async; blocking calls freeze entire event loop
- `run_in_executor` runs bcrypt in thread pool, freeing event loop for other requests

---

### Rate Limiting with slowapi

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from fastapi import Request

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/auth/signup")
@limiter.limit("10/minute")
async def signup(request: Request, data: SignupRequest):
    # ... signup logic ...
    pass
```

**Rate Limit Configuration**:
- **10 requests per minute per IP** for signup, signin, forgot-password endpoints
- **No limit** for profile GET/PUT (authenticated users only, less abuse risk)
- **Response**: 429 Too Many Requests with `Retry-After` header

---

### Email Enumeration Prevention

```python
@app.post("/api/auth/signin")
async def signin(credentials: SigninRequest):
    # Query user by email
    user = await db.fetchrow(
        "SELECT id, password_hash FROM users WHERE email = $1",
        credentials.email.lower()
    )

    if user:
        # Email exists: verify password
        is_valid = await verify_password(credentials.password, user['password_hash'])
    else:
        # Email doesn't exist: perform fake bcrypt to maintain constant time
        fake_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU8bvbW5JQCW"
        is_valid = await verify_password(credentials.password, fake_hash)

    if not is_valid:
        # Generic error (same for wrong email and wrong password)
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # ... generate JWT, return token ...
```

**Key Security Features**:
1. **Generic Error**: "Invalid email or password" for both cases
2. **Constant Time**: Always call `verify_password` (even with fake hash) so response time doesn't leak information
3. **Lowercase Email**: Convert to lowercase for case-insensitive comparison
4. **Logging**: Log failed attempts to `user_activity` table for security monitoring

---

## Consequences

### Positive

- **Strong Password Security**: bcrypt with 12 salt rounds resists rainbow tables and brute-force
- **Async Performance**: `run_in_executor` prevents bcrypt from blocking event loop
- **Brute-Force Protection**: Rate limiting (10 req/min) makes automated attacks impractical
- **Email Privacy**: Constant-time responses prevent enumeration of registered users
- **OWASP Compliance**: Meets authentication security best practices for hackathon scoring
- **Future-Proof**: Can increase bcrypt rounds or migrate to Argon2 without API changes

### Negative

- **Latency Cost**: bcrypt adds 200-300ms to signup/signin (acceptable for security)
- **Single-Instance Limitation**: slowapi rate limiting doesn't work with horizontal scaling (acceptable for MVP)
- **Slightly Worse UX**: Generic error messages don't tell user if email or password is wrong (security trade-off)

### Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **bcrypt blocks event loop** (if `run_in_executor` not used) | High - Entire backend freezes for 200-300ms per auth request | Mandatory code review checks for async wrapper; integration test verifies concurrent requests work |
| **Rate limit bypass** (attacker uses multiple IPs) | Medium - Can still attempt brute-force with VPN/proxies | Add account lockout after 5 failed attempts (future enhancement) |
| **Fake bcrypt hash is invalid** (timing attack still possible) | Medium - Response time differs if fake hash verification fails instantly | Use real bcrypt hash from deleted/test user as fake hash |
| **slowapi counters reset on deployment** | Low - Attacker gets fresh 10 requests after deployment | Acceptable for MVP; migrate to Redis for production |

---

## Performance Benchmarks

### Expected Latencies (p95)

| Operation | bcrypt Time | DB Time | Network | Total |
|-----------|-------------|---------|---------|-------|
| **Signup** | 300ms (hash password) | 200ms (insert user + profile) | 500ms | **1.0s** |
| **Signin (valid)** | 300ms (verify password) | 100ms (query user) | 500ms | **0.9s** |
| **Signin (invalid)** | 300ms (fake verify) | 50ms (query user) | 500ms | **0.85s** |

**Observations**:
- Signup and signin have similar total latency (prevents timing attacks)
- bcrypt is dominant cost (~30-35% of total time)
- Both operations complete under 2-second target (meets spec SC-001, SC-002)

---

## Alternatives Not Chosen

### Why Not Argon2?
- Rejected because bcrypt provides sufficient security for MVP
- Argon2 migration possible later without breaking changes
- Less mature Python ecosystem would slow development

### Why Not PBKDF2?
- Rejected because OWASP recommends bcrypt or Argon2 over PBKDF2
- Performance gain (~100-150ms saved) not worth security trade-off

### Why Not Redis Rate Limiting?
- Deferred (not rejected) because slowapi sufficient for MVP
- Production scaling will require Redis migration

### Why Not Separate Error Messages?
- Rejected because enabling email enumeration is security vulnerability
- OWASP explicitly discourages revealing whether email exists

---

## References

- **Planning Artifacts**:
  - [research.md](../../specs/003-better-auth/research.md) - Sections 2 (Password Hashing), 3 (Rate Limiting), 8 (Email Enumeration)
  - [plan.md](../../specs/003-better-auth/plan.md) - Phase 1.3 (Password Hashing), Phase 1.5 (Authentication Routes)

- **Security Standards**:
  - OWASP Authentication Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
  - OWASP Password Storage Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
  - FastAPI Security Tutorial: https://fastapi.tiangolo.com/tutorial/security/

- **Libraries**:
  - passlib Documentation: https://passlib.readthedocs.io/
  - slowapi GitHub: https://github.com/laurentS/slowapi

- **Related ADRs**:
  - [ADR-002: Better Auth Integration](./002-better-auth-integration.md) - JWT strategy decision
  - [ADR-004: JWT Token Storage](./004-jwt-token-storage-security.md) - Complementary security measures

---

## Decision Review Date

**Review By**: 2025-06-16 (6 months after implementation)
**Criteria for Review**:
- Successful brute-force attack attempts
- Performance complaints about auth latency
- Horizontal scaling requirements (triggers Redis migration)
- New OWASP recommendations for password hashing
