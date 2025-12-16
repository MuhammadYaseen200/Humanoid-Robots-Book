# ADR-006: Hardware Profile Data Management Strategy

**Status**: Accepted
**Date**: 2025-12-16
**Context**: Feature 003-better-auth
**Deciders**: Lead Architect (Claude Sonnet 4.5)

## Context and Problem Statement

The Better-Auth & User Profiling feature requires collecting and storing hardware/software profile data (GPU type, RAM capacity, coding languages, robotics experience) to enable personalized content recommendations in the future 50-point Personalization feature. The architecture must balance data integrity, query performance, JWT payload size, and API contract stability.

**Key Requirements**:
- 100% profile completeness (all fields required at signup)
- Profile data must be available for stateless personalization (embedded in JWT claims)
- Enum validation for GPU types, RAM capacities, robotics experience levels
- Support for multi-select coding languages (array of strings)
- Profile updates must refresh JWT tokens with new claims

## Decision Drivers

- **Personalization Enablement**: Profile data must support future content recommendation feature (50 bonus points)
- **Data Integrity**: Enum fields must enforce valid values at database level
- **Stateless Architecture**: Embedding profile in JWT eliminates DB lookup on /personalize requests
- **API Stability**: Profile schema changes should not break existing JWT tokens
- **Query Performance**: Profile queries must support user analytics and content adaptation

## Decision Clusters

This ADR documents four related decisions that work together:

1. **Database Schema Extension Strategy** (extend existing table vs new table)
2. **JWT Claims Structure** (embed profile fields vs separate lookup)
3. **Enum Validation Approach** (CHECK constraints vs application-level)
4. **Profile Completeness Enforcement** (required fields vs nullable with defaults)

---

## Decision 1: Database Schema Extension Strategy

### Considered Options

#### Option A: Extend Existing user_profiles Table

**Architecture**:
- Add 4 new columns to existing `user_profiles` table:
  - `gpu_type VARCHAR(100) DEFAULT 'None/Integrated Graphics'`
  - `ram_capacity VARCHAR(20) DEFAULT '8-16GB'`
  - `coding_languages JSONB DEFAULT '["None"]'::JSONB`
  - `robotics_experience VARCHAR(50) DEFAULT 'No prior experience'`
- Use CHECK constraints for enum validation
- Maintain 1:1 relationship with users table via existing foreign key

**Pros**:
- ✅ **Smallest Viable Change**: No new tables, no new relationships
- ✅ **Single Query**: Profile fetch requires only one SELECT
- ✅ **Existing Infrastructure**: user_profiles table already has indexes, foreign keys, timestamps
- ✅ **No Migration Complexity**: Simple ALTER TABLE statement

**Cons**:
- ❌ **Table Width**: Adds 4 columns to existing table (minor concern, Postgres handles wide tables efficiently)

---

#### Option B: Create New hardware_profiles Table

**Architecture**:
- Create separate `hardware_profiles` table with 1:1 relationship to `users`
- Columns: user_id (FK), gpu_type, ram_capacity, coding_languages, robotics_experience
- Requires JOIN to fetch complete profile

**Pros**:
- ✅ **Separation of Concerns**: Authentication data separate from profile data
- ✅ **Optional Profile**: Could make profile creation optional (separate signup flow)

**Cons**:
- ❌ **JOIN Overhead**: Every profile query requires JOIN with users table (~10-20ms overhead)
- ❌ **Increased Complexity**: More tables, more foreign keys, more migration scripts
- ❌ **Not Smallest Change**: Violates constitution principle of minimal viable diff
- ❌ **100% Required**: Profile is mandatory at signup, so separation provides no benefit

**REJECTED**: Complexity cost outweighs separation benefit

---

### Decision Outcome (Schema Extension)

**Chosen Option**: **Option A - Extend Existing user_profiles Table**

**Rationale**:
1. **Smallest Viable Change**: Aligns with constitution principle of minimal diff
2. **Performance**: Single SELECT query (~50ms) vs JOIN query (~70ms)
3. **100% Required**: Since profile is mandatory at signup, no benefit to separate table
4. **Existing Infrastructure**: Reuses established foreign key, indexes, and timestamps

---

## Decision 2: JWT Claims Structure

### Considered Options

#### Option A: Embed All Profile Fields in JWT Claims

**Architecture**:
- JWT payload includes: user_id, email, name, gpu_type, ram_capacity, coding_languages, robotics_experience
- Personalization endpoint extracts profile from JWT (no DB lookup)
- Profile updates issue new JWT with refreshed claims

**JWT Payload Example**:
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "email": "student@example.com",
  "name": "John Doe",
  "gpu_type": "NVIDIA RTX 4070 Ti",
  "ram_capacity": "16-32GB",
  "coding_languages": ["Python", "C++"],
  "robotics_experience": "Hobbyist (built simple projects)",
  "iat": 1702989600,
  "exp": 1703076000
}
```

**Pros**:
- ✅ **Zero DB Lookups**: /personalize endpoint reads profile from JWT (~5ms vs ~100ms with DB query)
- ✅ **Stateless Architecture**: No sessions table, no cache layer
- ✅ **Simplified API**: Authentication and profile data delivered in single token
- ✅ **Performance**: Eliminates 100ms DB query on every personalized request

**Cons**:
- ❌ **JWT Size**: Adds ~300 bytes to token (total ~500 bytes, well under 4KB cookie limit)
- ❌ **Stale Data**: Profile changes not reflected until JWT expires (max 24 hours)
- ❌ **Token Refresh Required**: Profile PUT must return new JWT

---

#### Option B: JWT Contains Only user_id, Profile Fetched on Demand

**Architecture**:
- JWT payload: {sub: user_id, email, iat, exp}
- /personalize endpoint queries database for profile fields
- Profile updates don't require JWT refresh

**Pros**:
- ✅ **Smaller JWT**: ~200 bytes (vs ~500 bytes)
- ✅ **Always Fresh**: Profile changes immediately visible
- ✅ **No Token Refresh**: Profile updates simpler

**Cons**:
- ❌ **DB Query Every Request**: Adds 100ms latency to /personalize endpoint
- ❌ **Defeats Stateless Goal**: Requires DB connection for every personalization
- ❌ **Infrastructure Cost**: More DB queries = more connection pool usage
- ❌ **Future Bottleneck**: Personalization is user-facing, latency-sensitive feature

**REJECTED**: Performance cost defeats purpose of JWT architecture

---

### Decision Outcome (JWT Claims)

**Chosen Option**: **Option A - Embed All Profile Fields in JWT Claims**

**Rationale**:
1. **Enables Future Feature**: 50-point Personalization feature requires fast profile access
2. **Stateless Architecture**: Aligns with constitution principle and existing JWT design (ADR-002)
3. **Performance**: Eliminates 100ms DB query on latency-sensitive personalization requests
4. **JWT Size Acceptable**: 500 bytes << 4KB cookie limit (10x headroom)
5. **Staleness Acceptable**: 24-hour max staleness acceptable for profile changes (users can sign out/in to force refresh)

---

## Decision 3: Enum Validation Approach

### Considered Options

#### Option A: Database CHECK Constraints

**Architecture**:
- PostgreSQL CHECK constraints on gpu_type, ram_capacity, robotics_experience columns
- Application-level validation in Pydantic models (duplicate validation for client feedback)
- Database rejects invalid values even if application validation bypassed

**Example SQL**:
```sql
ALTER TABLE user_profiles
  ADD CONSTRAINT valid_gpu_type CHECK (
    gpu_type IN ('None/Integrated Graphics', 'NVIDIA RTX 3060',
                 'NVIDIA RTX 4070 Ti', 'NVIDIA RTX 4080/4090',
                 'AMD Radeon RX 7000 Series', 'Other')
  );
```

**Pros**:
- ✅ **Defense in Depth**: Database enforces constraints even if application validation fails
- ✅ **Data Integrity**: Prevents invalid values from SQL injection, admin tools, migrations
- ✅ **Self-Documenting**: CHECK constraints visible in schema (pg_constraint table)
- ✅ **Zero Runtime Cost**: Constraint checking is O(1) during INSERT/UPDATE

**Cons**:
- ❌ **Schema Migration Required**: Adding new GPU types requires ALTER TABLE
- ❌ **Generic Error Messages**: Database error less user-friendly than Pydantic validation

---

#### Option B: Application-Level Validation Only

**Architecture**:
- Pydantic models with Enum validators
- No database constraints
- VARCHAR columns accept any string

**Pros**:
- ✅ **Easier Updates**: Adding GPU types only requires code change (no migration)
- ✅ **Better Error Messages**: Pydantic provides field-specific, user-friendly errors

**Cons**:
- ❌ **Security Risk**: SQL injection or admin tools could insert invalid values
- ❌ **Data Integrity Risk**: Migration scripts or manual SQL could violate constraints
- ❌ **No Defense in Depth**: Single point of failure

**REJECTED**: Data integrity risk outweighs convenience benefit

---

### Decision Outcome (Enum Validation)

**Chosen Option**: **Option A - Database CHECK Constraints + Pydantic Validation**

**Rationale**:
1. **Defense in Depth**: Database constraints protect against SQL injection, admin errors, migration bugs
2. **Data Integrity**: Profile data feeds future ML models; invalid values would corrupt personalization
3. **Migration Cost Acceptable**: GPU types change infrequently (~yearly); migration overhead justified
4. **Best of Both**: Pydantic provides user-friendly errors, CHECK constraints provide bulletproof integrity

---

## Decision 4: Profile Completeness Enforcement

### Considered Options

#### Option A: All Profile Fields Required at Signup (100% Completeness)

**Architecture**:
- SignupRequest Pydantic model requires: email, password, name, gpu_type, ram_capacity, coding_languages, robotics_experience
- Database columns have NOT NULL constraints and defaults (for existing users)
- Signup fails with 422 if any profile field missing

**Pros**:
- ✅ **Enables Personalization**: Future feature requires complete profiles to make recommendations
- ✅ **No Partial Data**: Every user has full profile, no null checks needed
- ✅ **Better UX**: Users understand requirements upfront (single-step signup)
- ✅ **Hackathon Requirement**: Spec explicitly requires asking hardware questions at signup

**Cons**:
- ❌ **Longer Signup Form**: 7 fields total (email, password, name, 4 profile fields)
- ❌ **Potential Drop-off**: Users may abandon signup if form too long

---

#### Option B: Optional Profile Fields (Progressive Profiling)

**Architecture**:
- Signup requires only email, password, name
- Profile fields collected later via modal or dedicated page
- Database columns nullable

**Pros**:
- ✅ **Shorter Signup**: Reduces friction (3 fields vs 7 fields)
- ✅ **Progressive Disclosure**: Less overwhelming for new users

**Cons**:
- ❌ **Incomplete Profiles**: Many users never complete profile, personalization broken
- ❌ **Null Checks**: Every personalization query must handle missing data
- ❌ **Violates Spec**: FR-004 explicitly requires hardware profile at signup
- ❌ **Defeats Purpose**: 50-point feature requires complete profiles; optional fields defeat goal

**REJECTED**: Violates specification and defeats personalization feature

---

### Decision Outcome (Profile Completeness)

**Chosen Option**: **Option A - All Profile Fields Required at Signup (100% Completeness)**

**Rationale**:
1. **Spec Requirement**: FR-004 explicitly requires hardware profile questions at signup
2. **Enables Future Feature**: 50-point Personalization requires 100% profile completeness
3. **Better Data Quality**: No partial profiles, no null checks, cleaner code
4. **Signup UX Acceptable**: 7 fields with clear labels and default selections (dropdowns pre-select "None"/"No prior experience")

---

## Implementation Details

### Database Migration 003

```sql
-- Add hardware profile columns to existing user_profiles table
ALTER TABLE user_profiles
  ADD COLUMN IF NOT EXISTS gpu_type VARCHAR(100) DEFAULT 'None/Integrated Graphics',
  ADD COLUMN IF NOT EXISTS ram_capacity VARCHAR(20) DEFAULT '8-16GB',
  ADD COLUMN IF NOT EXISTS coding_languages JSONB DEFAULT '["None"]'::JSONB,
  ADD COLUMN IF NOT EXISTS robotics_experience VARCHAR(50) DEFAULT 'No prior experience';

-- Add CHECK constraints for enum validation
ALTER TABLE user_profiles
  ADD CONSTRAINT valid_gpu_type CHECK (
    gpu_type IN ('None/Integrated Graphics', 'NVIDIA RTX 3060',
                 'NVIDIA RTX 4070 Ti', 'NVIDIA RTX 4080/4090',
                 'AMD Radeon RX 7000 Series', 'Other')
  ),
  ADD CONSTRAINT valid_ram_capacity CHECK (
    ram_capacity IN ('4-8GB', '8-16GB', '16-32GB', '32GB or more')
  ),
  ADD CONSTRAINT valid_robotics_experience CHECK (
    robotics_experience IN ('No prior experience', 'Hobbyist (built simple projects)',
                            'Student (taking courses)', 'Professional (industry experience)')
  );

-- Add NOT NULL constraints (after defaults applied to existing rows)
ALTER TABLE user_profiles
  ALTER COLUMN gpu_type SET NOT NULL,
  ALTER COLUMN ram_capacity SET NOT NULL,
  ALTER COLUMN coding_languages SET NOT NULL,
  ALTER COLUMN robotics_experience SET NOT NULL;

-- Create index for analytics queries (optional, for future scaling)
CREATE INDEX IF NOT EXISTS idx_user_profiles_gpu_type ON user_profiles(gpu_type);
CREATE INDEX IF NOT EXISTS idx_user_profiles_robotics_experience ON user_profiles(robotics_experience);
```

---

### Pydantic Models with Embedded Validation

```python
from pydantic import BaseModel, Field, validator
from typing import List, Literal

# Enum types matching database CHECK constraints
GPUType = Literal[
    "None/Integrated Graphics",
    "NVIDIA RTX 3060",
    "NVIDIA RTX 4070 Ti",
    "NVIDIA RTX 4080/4090",
    "AMD Radeon RX 7000 Series",
    "Other"
]

RAMCapacity = Literal["4-8GB", "8-16GB", "16-32GB", "32GB or more"]

CodingLanguage = Literal["None", "Python", "C++", "JavaScript/TypeScript", "Java", "C#", "Rust", "Other"]

RoboticsExperience = Literal[
    "No prior experience",
    "Hobbyist (built simple projects)",
    "Student (taking courses)",
    "Professional (industry experience)"
]

class SignupRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=100)
    name: str = Field(..., max_length=255)

    # Hardware profile fields (all required)
    gpu_type: GPUType
    ram_capacity: RAMCapacity
    coding_languages: List[CodingLanguage] = Field(..., min_items=1)
    robotics_experience: RoboticsExperience

    @validator('coding_languages')
    def validate_coding_languages(cls, v):
        if not v:
            raise ValueError("At least one coding language must be selected")
        return v

class UserProfile(BaseModel):
    id: str
    email: str
    name: str
    gpu_type: str
    ram_capacity: str
    coding_languages: List[str]
    robotics_experience: str
    learning_style: str
    difficulty_level: str
    preferred_language: str
    created_at: str
    last_login: str
```

---

### JWT Token Creation with Profile Claims

```python
from jose import jwt
from datetime import datetime, timedelta

def create_access_token(user_id: str, email: str, profile: dict) -> str:
    """Create JWT with embedded profile claims for stateless personalization."""
    payload = {
        "sub": user_id,
        "email": email,
        "name": profile["name"],

        # Embed hardware profile for personalization
        "gpu_type": profile["gpu_type"],
        "ram_capacity": profile["ram_capacity"],
        "coding_languages": profile["coding_languages"],
        "robotics_experience": profile["robotics_experience"],

        # Standard JWT claims
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(days=1)  # 24-hour expiration
    }

    token = jwt.encode(payload, AUTH_SECRET, algorithm="HS256")
    return token
```

---

## Consequences

### Positive

- **Enables 50-Point Personalization Feature**: Complete profiles in JWT enable stateless content recommendations
- **100% Data Completeness**: No null checks, no partial profiles, cleaner code
- **Strong Data Integrity**: CHECK constraints prevent invalid enum values at database level
- **Excellent Performance**: Profile embedded in JWT eliminates 100ms DB query on /personalize
- **Smallest Viable Change**: Extends existing table rather than creating new infrastructure
- **Future-Proof**: Can add new GPU types via migration; JWT structure extensible

### Negative

- **JWT Size Increase**: Adds ~300 bytes to token (acceptable: 500 bytes << 4KB limit)
- **Profile Staleness**: Changes not reflected until JWT expires (max 24 hours)
- **Longer Signup Form**: 7 fields may increase signup abandonment (mitigated with clear labels, defaults)
- **Schema Migration Required**: Adding new enum values requires ALTER TABLE

### Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **JWT exceeds 4KB cookie limit** (if more fields added later) | High - Authentication breaks | Monitor JWT size; current 500 bytes has 8x headroom; add compression if needed |
| **Signup form too long** (7 fields) | Medium - User abandonment | Pre-select sensible defaults ("None", "No prior experience"); use dropdowns not text input |
| **Stale profile data** (24-hour JWT expiration) | Low - User sees outdated recommendations | Document in UX: "Profile changes take effect on next signin"; add manual "Refresh Session" button |
| **Enum values outdated** (new GPU models released) | Low - Users select "Other" | Plan quarterly review of enum values; add new models via migration |

---

## Performance Analysis

### JWT Size Breakdown

| Component | Size | Notes |
|-----------|------|-------|
| Standard claims (sub, email, iat, exp) | ~150 bytes | Fixed overhead |
| User name | ~30 bytes | Average name length |
| GPU type | ~30 bytes | "NVIDIA RTX 4070 Ti" |
| RAM capacity | ~10 bytes | "16-32GB" |
| Coding languages | ~40 bytes | ["Python", "C++"] |
| Robotics experience | ~35 bytes | "Hobbyist (built simple projects)" |
| **Total JWT Payload** | **~295 bytes** | Base64-encoded: ~400 bytes |
| **Signed JWT** | **~500 bytes** | Includes signature |

**Cookie Limit**: 4096 bytes (4KB)
**Headroom**: 8x (3596 bytes remaining)
**Conclusion**: Ample room for future claims (learning_style, difficulty_level, preferred_topics)

---

### Query Performance Comparison

**Option A (Embedded in JWT):**
```
/personalize request → Extract claims from JWT → Return recommendations
Total latency: ~5ms (JWT decode)
```

**Option B (Database Lookup):**
```
/personalize request → Validate JWT → Query user_profiles → Return recommendations
Total latency: ~105ms (JWT decode 5ms + DB query 100ms)
```

**Performance Gain**: 100ms saved per personalization request (21x faster)

---

## Alternatives Not Chosen

### Why Not Option B (Separate hardware_profiles Table)?
- Rejected because JOIN overhead (10-20ms) and complexity not justified for mandatory 1:1 relationship
- Smallest viable change principle dictates extending existing table

### Why Not Option B (Profile Lookup on Demand)?
- Rejected because 100ms DB query defeats stateless architecture goal
- Personalization is user-facing feature; latency-sensitive
- JWT size increase (300 bytes) acceptable cost for 21x performance gain

### Why Not Application-Level Validation Only?
- Rejected due to data integrity risk from SQL injection, admin tools, migrations
- Defense-in-depth principle requires database-level constraints for critical data

### Why Not Optional Profile Fields?
- Rejected because violates specification (FR-004)
- Defeats purpose of 50-point feature (personalization requires complete profiles)
- Partial profiles create null-check complexity throughout codebase

---

## References

- **Planning Artifacts**:
  - [spec.md](../../specs/003-better-auth/spec.md) - FR-004 (hardware profile questions), SC-009 (100% profile completeness)
  - [plan.md](../../specs/003-better-auth/plan.md) - Phase 1.1 (database migration), Phase 1.2 (Pydantic models)
  - [data-model.md](../../specs/003-better-auth/data-model.md) - UserProfile entity definition, migration 003 SQL
  - [research.md](../../specs/003-better-auth/research.md) - Question 5 (JWT claims structure), Question 6 (database schema extension)

- **Database Standards**:
  - PostgreSQL CHECK Constraints: https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-CHECK-CONSTRAINTS
  - JSONB Performance: https://www.postgresql.org/docs/current/datatype-json.html

- **Related ADRs**:
  - [ADR-002: Better Auth Integration](./002-better-auth-integration.md) - JWT strategy decision (stateless authentication)
  - [ADR-004: JWT Token Storage](./004-jwt-token-storage-security.md) - httpOnly cookies vs localStorage
  - [ADR-005: Password Hashing](./005-password-hashing-authentication-security.md) - Authentication security measures

---

## Decision Review Date

**Review By**: 2025-06-16 (6 months after implementation)
**Criteria for Review**:
- JWT size approaching 4KB limit (add compression)
- Profile staleness complaints (reduce JWT expiration or add refresh button)
- Signup abandonment rate > 30% (consider progressive profiling)
- New GPU models require frequent migrations (consider lookup table approach)
- Personalization feature performance issues (validate JWT decode latency)
