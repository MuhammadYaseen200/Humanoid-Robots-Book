# ADR-004: JWT Token Storage and Security Mechanism

**Status**: Accepted
**Date**: 2025-12-16
**Context**: Feature 003-better-auth
**Deciders**: Lead Architect (Claude Sonnet 4.5)

## Context and Problem Statement

The Better-Auth & User Profiling feature requires secure client-side storage of JWT tokens to maintain user sessions across page navigations. The choice of storage mechanism impacts security posture (XSS, CSRF attacks), user experience (token persistence), and implementation complexity.

**Key Requirements**:
- Tokens must persist across page refreshes
- Protection against XSS attacks (malicious JavaScript accessing tokens)
- Protection against CSRF attacks (cross-site request forgery)
- Support for both development (localhost) and production (HTTPS) environments
- CORS compatibility for cross-origin requests

## Decision Drivers

- **Security**: Prevent token theft via XSS or CSRF attacks
- **User Experience**: Tokens should persist (not lost on page refresh)
- **Development Workflow**: Easy debugging during local development
- **Production Best Practices**: Industry-standard security for deployed application
- **CORS Complexity**: httpOnly cookies require specific CORS configuration

## Considered Options

### Option A: httpOnly Cookies Only (Production)

**Architecture**:
- Backend sets JWT token in httpOnly cookie via `Set-Cookie` header
- Cookie attributes: `HttpOnly`, `Secure` (HTTPS only), `SameSite=Strict`, `Max-Age=86400`
- Frontend does NOT access token directly (browser includes cookie automatically)
- CORS configured with `allow_credentials=True` and specific `allow_origins`

**Pros**:
- ✅ **XSS Protection**: JavaScript cannot access httpOnly cookies
- ✅ **Automatic inclusion**: Browser sends cookie with every request (no manual header management)
- ✅ **CSRF Protection**: `SameSite=Strict` prevents cross-site cookie sending
- ✅ **Industry Best Practice**: Recommended by OWASP for production authentication

**Cons**:
- ❌ **HTTPS Required**: `Secure` flag mandates HTTPS (localhost needs workaround)
- ❌ **CORS Complexity**: Requires `credentials: 'include'` in fetch requests and specific origin configuration
- ❌ **Debugging Difficulty**: Cannot inspect token payload in browser DevTools Application tab
- ❌ **Mobile App Limitations**: httpOnly cookies don't work with native mobile apps (requires different strategy)

---

### Option B: localStorage Only (Development)

**Architecture**:
- Backend returns JWT token in JSON response body
- Frontend stores token in `localStorage.setItem('auth_token', token)`
- Frontend adds `Authorization: Bearer <token>` header to every protected request
- Token accessible via JavaScript

**Pros**:
- ✅ **Debugging Friendly**: Token visible in DevTools Application tab
- ✅ **Simple Implementation**: No CORS credentials configuration needed
- ✅ **Mobile Compatibility**: Works with React Native and native mobile apps
- ✅ **No HTTPS Requirement**: Works on localhost without certificate

**Cons**:
- ❌ **XSS Vulnerability**: Malicious JavaScript can access `localStorage` and steal token
- ❌ **Manual Header Management**: Frontend must add `Authorization` header to every request
- ❌ **Security Risk in Production**: Not recommended by OWASP for sensitive data

---

### Option C: Hybrid Approach (httpOnly Cookies for Production + localStorage for Development)

**Architecture**:
- **Production** (HTTPS): Backend sets httpOnly cookie, frontend uses cookie-based auth
- **Development** (localhost): Backend returns token in JSON, frontend uses localStorage + Bearer header
- Environment detection via `VITE_ENV` variable (production vs development)

**Pros**:
- ✅ **Best of Both Worlds**: Security in production, convenience in development
- ✅ **XSS Protection in Production**: httpOnly cookies prevent token theft
- ✅ **Easy Debugging in Development**: Token visible in DevTools
- ✅ **Gradual Migration**: Can switch strategies based on environment

**Cons**:
- ❌ **Dual Implementation**: Must implement both authentication strategies
- ❌ **Complexity**: Frontend code branches based on environment
- ❌ **Testing Gap**: Development tests don't use production authentication strategy

---

### Option D: Session Storage (Tokens Lost on Tab Close)

**Architecture**:
- Frontend stores token in `sessionStorage`
- Token cleared when browser tab closes

**Pros**:
- ✅ **Automatic Cleanup**: Token removed when tab closes (reduces exposure window)

**Cons**:
- ❌ **Poor UX**: User must re-signin every time they close tab
- ❌ **XSS Vulnerable**: Same JavaScript access issue as localStorage
- ❌ **Mobile Incompatible**: Mobile browsers may clear sessionStorage aggressively

**REJECTED**: Poor user experience outweighs security benefit

---

## Decision Outcome

**Chosen Option**: **Option C - Hybrid Approach (httpOnly Cookies for Production + localStorage for Development)**

**Rationale**:

1. **Security First for Production**: httpOnly cookies eliminate XSS risk in deployed application where users' actual data is at risk. This aligns with hackathon bonus points requirement for "security best practices."

2. **Developer Experience**: localStorage in development allows easy token inspection for debugging authentication flows, JWT payload structure, and expiration handling. Speeds up development iteration.

3. **Hackathon Pragmatism**: Hybrid approach allows team to develop and test quickly on localhost without HTTPS certificates, then deploy securely to production with minimal code changes.

4. **Industry Standard**: httpOnly cookies for production JWT storage is recommended by OWASP, FastAPI security docs, and React security best practices.

5. **Future-Proof**: Hybrid pattern is extensible - can add refresh tokens, token rotation, or switch to full cookie-based auth later without frontend rewrite.

---

## Implementation Details

### Backend (FastAPI)

**Production Mode** (httpOnly cookie):
```python
from fastapi import Response
from datetime import timedelta

@router.post("/auth/signin")
async def signin(response: Response, credentials: SigninRequest):
    # ... validate credentials, generate JWT ...
    token = create_access_token(user_id, email, profile)

    # Set httpOnly cookie
    response.set_cookie(
        key="auth_token",
        value=token,
        httponly=True,
        secure=True,  # HTTPS only
        samesite="strict",  # CSRF protection
        max_age=86400  # 24 hours
    )

    return {"message": "Signed in successfully", "user": user_profile}
```

**Development Mode** (JSON response):
```python
@router.post("/auth/signin")
async def signin(credentials: SigninRequest, env: str = os.getenv("ENV", "development")):
    token = create_access_token(user_id, email, profile)

    if env == "production":
        # Set httpOnly cookie (code above)
        return {"message": "Signed in successfully", "user": user_profile}
    else:
        # Return token in JSON for localStorage
        return {"token": token, "user": user_profile}
```

---

### Frontend (React)

**Auth Context with Environment Detection**:
```typescript
const API_URL = import.meta.env.VITE_API_URL;
const IS_PRODUCTION = import.meta.env.VITE_ENV === 'production';

export function AuthProvider({ children }) {
  const [token, setToken] = useState<string | null>(
    IS_PRODUCTION ? null : localStorage.getItem('auth_token')
  );

  const signin = async (email: string, password: string) => {
    const response = await fetch(`${API_URL}/auth/signin`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: IS_PRODUCTION ? 'include' : 'same-origin',  // Send cookies in production
      body: JSON.stringify({ email, password })
    });

    const data = await response.json();

    if (IS_PRODUCTION) {
      // Token in httpOnly cookie, no localStorage needed
      setUser(data.user);
    } else {
      // Development: store token in localStorage
      localStorage.setItem('auth_token', data.token);
      setToken(data.token);
      setUser(data.user);
    }
  };

  // ... similar for signup, signout, protected requests ...
}
```

---

### CORS Configuration (Production Only)

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com", "https://www.example.com"],  # Specific origins only
    allow_credentials=True,  # Required for cookies
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"]
)
```

---

## Consequences

### Positive

- **XSS Protection in Production**: httpOnly cookies cannot be accessed by malicious JavaScript, preventing token theft
- **CSRF Protection**: `SameSite=Strict` prevents cookies from being sent in cross-site requests
- **Developer Velocity**: localStorage in development speeds up debugging and testing
- **Standards Compliance**: Follows OWASP recommendations for production JWT storage
- **Hackathon Scoring**: Demonstrates security best practices (likely bonus points from judges)

### Negative

- **Dual Implementation**: Must maintain two authentication code paths (environment branching)
- **HTTPS Required for Production**: Deployment must have valid SSL certificate (Vercel/GitHub Pages provide free)
- **CORS Complexity**: Frontend must include `credentials: 'include'` in fetch requests
- **Testing Gap**: Development tests don't exercise production authentication path (need separate production smoke tests)

### Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| **Environment variable misconfiguration** (using localStorage in production) | Validate `VITE_ENV` at build time, fail build if undefined; add runtime check in AuthContext |
| **CORS misconfiguration** (cookies not sent cross-origin) | Test from production frontend domain during deployment; verify `allow_credentials=True` and specific origins |
| **XSS vulnerability in development** (malicious script in localhost) | Acceptable risk for development; never deploy development build to production |
| **httpOnly cookie not set** (backend forgets `Set-Cookie` header) | Add integration test to verify `Set-Cookie` header in signin/signup responses |

---

## Alternatives Not Chosen

### Why Not Option A (httpOnly Cookies Only)?
- Rejected because development on localhost without HTTPS is cumbersome
- Requires mocking httpOnly cookies in tests
- Slows down development iteration speed

### Why Not Option B (localStorage Only)?
- Rejected for production due to XSS vulnerability
- OWASP explicitly discourages localStorage for authentication tokens
- Would likely lose hackathon bonus points for security

### Why Not Option D (sessionStorage)?
- Rejected due to poor UX (user must re-signin every tab close)
- Still vulnerable to XSS like localStorage

---

## References

- **Planning Artifacts**:
  - [research.md](../../specs/003-better-auth/research.md) - Section 1: JWT Token Storage Mechanism
  - [plan.md](../../specs/003-better-auth/plan.md) - Phase 2.1: Authentication Context Implementation

- **Security Standards**:
  - OWASP Authentication Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
  - FastAPI Security Best Practices: https://fastapi.tiangolo.com/tutorial/security/
  - MDN Web Docs - HTTP Cookies: https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies

- **Related ADRs**:
  - [ADR-002: Better Auth Integration](./002-better-auth-integration.md) - JWT vs Better Auth backend decision
  - [ADR-005: Password Hashing & Authentication Security](./005-password-hashing-security.md) - Complementary security measures

---

## Decision Review Date

**Review By**: 2025-03-16 (3 months after implementation)
**Criteria for Review**:
- Any XSS incidents in production
- Developer complaints about debugging difficulty
- Mobile app requirements emerge
- Token refresh/rotation needed (may require reevaluation)
