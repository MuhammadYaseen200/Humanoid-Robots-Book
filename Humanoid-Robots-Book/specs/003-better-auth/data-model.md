# Data Model: Better-Auth & User Profiling

**Feature**: 003-better-auth
**Created**: 2025-12-16
**Purpose**: Define database schema, entities, and data relationships

## Database Schema Changes

### Migration 003: User Profile Extensions for Hardware Background

**File**: `backend/db/migrations/003_user_profile_hardware.sql`

```sql
-- Migration 003: Add hardware/software profile fields for personalization
-- Feature: 003-better-auth
-- Created: 2025-12-16

-- Add hardware profile columns to existing user_profiles table
ALTER TABLE user_profiles
  ADD COLUMN IF NOT EXISTS gpu_type VARCHAR(100) DEFAULT 'None/Integrated Graphics',
  ADD COLUMN IF NOT EXISTS ram_capacity VARCHAR(20) DEFAULT '8-16GB',
  ADD COLUMN IF NOT EXISTS coding_languages JSONB DEFAULT '["None"]'::JSONB,
  ADD COLUMN IF NOT EXISTS robotics_experience VARCHAR(50) DEFAULT 'No prior experience';

-- Add constraints for enum-like validation
ALTER TABLE user_profiles
  ADD CONSTRAINT valid_gpu_type CHECK (
    gpu_type IN (
      'None/Integrated Graphics',
      'NVIDIA RTX 3060',
      'NVIDIA RTX 4070 Ti',
      'NVIDIA RTX 4080/4090',
      'AMD Radeon RX 7000 Series',
      'Other'
    )
  ),
  ADD CONSTRAINT valid_ram_capacity CHECK (
    ram_capacity IN (
      '4-8GB',
      '8-16GB',
      '16-32GB',
      '32GB or more'
    )
  ),
  ADD CONSTRAINT valid_robotics_experience CHECK (
    robotics_experience IN (
      'No prior experience',
      'Hobbyist (built simple projects)',
      'Student (taking courses)',
      'Professional (industry experience)'
    )
  );

-- Add index for common queries (filtering users by hardware capabilities)
CREATE INDEX IF NOT EXISTS idx_user_profiles_gpu_type ON user_profiles(gpu_type);
CREATE INDEX IF NOT EXISTS idx_user_profiles_ram_capacity ON user_profiles(ram_capacity);

-- Add reset_counter column for password reset token invalidation
ALTER TABLE users
  ADD COLUMN IF NOT EXISTS reset_counter INTEGER DEFAULT 0;

-- Update updated_at trigger (already exists, but ensure it's applied)
DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON user_profiles;
CREATE TRIGGER update_user_profiles_updated_at
  BEFORE UPDATE ON user_profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON COLUMN user_profiles.gpu_type IS 'User GPU for hardware-specific content recommendations (Module 3 Isaac Sim requires RTX 4070 Ti)';
COMMENT ON COLUMN user_profiles.ram_capacity IS 'User system RAM for performance-sensitive tutorials';
COMMENT ON COLUMN user_profiles.coding_languages IS 'JSON array of programming languages user knows (e.g., ["Python", "C++"])';
COMMENT ON COLUMN user_profiles.robotics_experience IS 'User robotics background for difficulty-appropriate content';
COMMENT ON COLUMN users.reset_counter IS 'Incremented on each password reset to invalidate previous reset tokens';
```

---

## Entity Definitions

### 1. User (Authentication Entity)

**Table**: `users` (already exists, extended with reset_counter)

**Purpose**: Store authentication credentials and account metadata

**Attributes**:
| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique user identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL, CHECK (email format) | User email (username for auth) |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt hashed password (never plaintext) |
| name | VARCHAR(255) | NULL | User display name |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | Account creation date |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |
| last_login | TIMESTAMP WITH TIME ZONE | NULL | Most recent successful signin |
| is_active | BOOLEAN | DEFAULT TRUE | Account status (for soft deletes) |
| preferences | JSONB | DEFAULT '{}'::JSONB | Misc user preferences |
| reset_counter | INTEGER | DEFAULT 0 | Password reset token version |

**Relationships**:
- **HAS ONE** UserProfile (one-to-one)
- **HAS MANY** ChatSessions (one-to-many)
- **HAS MANY** UserActivityLogs (one-to-many via user_activity table)

**Validation Rules**:
- Email must match RFC 5322 pattern: `^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$`
- Password_hash must be bcrypt format (starts with `$2b$`)
- Email is case-insensitive (convert to lowercase before storage)

**Indexes**:
- `idx_users_email` (for fast login lookups)
- `idx_users_created_at` (for analytics queries)

---

### 2. UserProfile (Extended Profile Entity)

**Table**: `user_profiles` (already exists, extended with hardware fields)

**Purpose**: Store user hardware/software background for personalization

**Attributes**:
| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Profile unique ID |
| user_id | UUID | FOREIGN KEY REFERENCES users(id) ON DELETE CASCADE, UNIQUE | Link to user account |
| learning_style | VARCHAR(50) | DEFAULT 'balanced' | Learning preference (visual/auditory/kinesthetic) |
| difficulty_level | VARCHAR(50) | DEFAULT 'intermediate' | Current skill level |
| chapters_completed | INTEGER[] | DEFAULT ARRAY[]::INTEGER[] | Completed chapter IDs |
| total_chat_messages | INTEGER | DEFAULT 0 | Chat engagement metric |
| preferred_language | VARCHAR(10) | DEFAULT 'en' | UI language (en/ur) |
| **gpu_type** | **VARCHAR(100)** | **CHECK (valid enum values)** | **User GPU hardware** |
| **ram_capacity** | **VARCHAR(20)** | **CHECK (valid enum values)** | **User system RAM** |
| **coding_languages** | **JSONB** | **DEFAULT '["None"]'::JSONB** | **Programming languages known** |
| **robotics_experience** | **VARCHAR(50)** | **CHECK (valid enum values)** | **Robotics background level** |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | Profile creation date |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | Last profile update |

**Relationships**:
- **BELONGS TO** User (many-to-one, but enforced as one-to-one via UNIQUE constraint)

**Validation Rules**:
- `gpu_type` must be one of: "None/Integrated Graphics", "NVIDIA RTX 3060", "NVIDIA RTX 4070 Ti", "NVIDIA RTX 4080/4090", "AMD Radeon RX 7000 Series", "Other"
- `ram_capacity` must be one of: "4-8GB", "8-16GB", "16-32GB", "32GB or more"
- `coding_languages` must be non-empty JSON array with at least one element
- `robotics_experience` must be one of: "No prior experience", "Hobbyist (built simple projects)", "Student (taking courses)", "Professional (industry experience)"

**Indexes**:
- `idx_user_profiles_user_id` (for fast profile lookups by user)
- `idx_user_profiles_gpu_type` (for hardware-based content filtering)
- `idx_user_profiles_ram_capacity` (for performance-based recommendations)

---

### 3. JWT Token (Logical Entity, Not Stored)

**Purpose**: Authentication credential issued by backend, validated on every protected request

**Claims Structure**:
```typescript
interface JWTPayload {
  // Standard Claims (RFC 7519)
  sub: string;              // Subject: user UUID
  iat: number;              // Issued At: Unix timestamp
  exp: number;              // Expiration: Unix timestamp (iat + 24 hours)

  // Custom Claims (User Identity)
  email: string;            // User email address
  name: string;             // User display name

  // Custom Claims (Hardware Profile for Personalization)
  gpu_type: string;         // GPU hardware type
  ram_capacity: string;     // System RAM capacity
  coding_languages: string[]; // Programming languages array
  robotics_experience: string; // Robotics background level
}
```

**Example Payload**:
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "iat": 1702989600,
  "exp": 1703076000,
  "email": "student@example.com",
  "name": "John Doe",
  "gpu_type": "NVIDIA RTX 4070 Ti",
  "ram_capacity": "16-32GB",
  "coding_languages": ["Python", "C++"],
  "robotics_experience": "Hobbyist (built simple projects)"
}
```

**Lifecycle**:
1. **Issued**: On successful signup or signin
2. **Stored**: In httpOnly cookie (production) or localStorage (development)
3. **Transmitted**: In `Authorization: Bearer <token>` header or Cookie header
4. **Validated**: On every request to protected endpoints (/personalize, /translate, /profile)
5. **Refreshed**: On profile update (new token issued with updated claims)
6. **Expired**: After 24 hours (86400 seconds)

**Validation Rules**:
- Signature must be valid (HMAC-SHA256 with AUTH_SECRET)
- Expiration must be in future (exp > current_time)
- Subject must be valid UUID format
- Custom claims must match expected types

---

### 4. PasswordResetToken (Logical Entity, Not Stored)

**Purpose**: Time-limited token for password reset flow

**Claims Structure**:
```typescript
interface PasswordResetPayload {
  sub: string;              // Subject: user UUID
  type: "password_reset";   // Token type discriminator
  reset_counter: number;    // User's current reset_counter from database
  iat: number;              // Issued At: Unix timestamp
  exp: number;              // Expiration: iat + 1 hour
}
```

**Example Payload**:
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "type": "password_reset",
  "reset_counter": 3,
  "iat": 1702989600,
  "exp": 1702993200
}
```

**Lifecycle**:
1. **Issued**: When user requests password reset (POST /auth/forgot-password)
2. **Transmitted**: Via email link (query parameter)
3. **Validated**: On password reset page load and submission
4. **Invalidated**: After successful password reset (reset_counter incremented)

**Validation Rules**:
- Signature must be valid (HMAC-SHA256 with AUTH_SECRET_RESET)
- Type must be "password_reset"
- Expiration must be within 1 hour of issuance
- reset_counter must match current value in database (prevents token reuse)

---

### 5. AuthenticationEvent (Audit Log Entity)

**Table**: `user_activity` (already exists, reused for auth events)

**Purpose**: Security monitoring and compliance audit trail

**Attributes**:
| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Event unique ID |
| user_id | UUID | FOREIGN KEY REFERENCES users(id) ON DELETE CASCADE, NULL for failed signin | User who triggered event |
| activity_type | VARCHAR(50) | NOT NULL | Event type (signup, signin, signout, failed_signin, profile_update, password_reset) |
| chapter_id | VARCHAR(100) | NULL (unused for auth events) | Chapter context (for other events) |
| metadata | JSONB | DEFAULT '{}'::JSONB | Event-specific data |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | Event timestamp |

**Auth-Specific Metadata Examples**:
- **Signup**: `{"ip": "192.168.1.1", "user_agent": "Mozilla/5.0...", "gpu_type": "RTX 4070 Ti"}`
- **Signin**: `{"ip": "192.168.1.1", "user_agent": "Mozilla/5.0...", "success": true}`
- **Failed Signin**: `{"ip": "192.168.1.1", "email": "attacker@example.com", "reason": "invalid_password"}`
- **Password Reset**: `{"ip": "192.168.1.1", "reset_method": "email"}`

**Indexes**:
- `idx_user_activity_user_id` (for user-specific queries)
- `idx_user_activity_created_at` (for time-range queries)

---

## Data Relationships Diagram

```
┌─────────────────────┐
│      users          │
├─────────────────────┤
│ id (PK)             │
│ email (UNIQUE)      │
│ password_hash       │
│ name                │
│ reset_counter       │
│ created_at          │
│ last_login          │
└─────────┬───────────┘
          │ 1
          │
          │ has_one
          │
          ▼ 1
┌─────────────────────┐
│   user_profiles     │
├─────────────────────┤
│ id (PK)             │
│ user_id (FK, UNIQUE)│
│ gpu_type *NEW*      │
│ ram_capacity *NEW*  │
│ coding_languages *  │
│ robotics_exp *NEW*  │
│ difficulty_level    │
│ learning_style      │
└─────────────────────┘

          │
          │ has_many
          │
          ▼ N
┌─────────────────────┐
│   user_activity     │
├─────────────────────┤
│ id (PK)             │
│ user_id (FK)        │
│ activity_type       │
│ metadata            │
│ created_at          │
└─────────────────────┘
```

---

## State Transitions

### User Account Lifecycle

```
[No Account]
    │
    │ POST /auth/signup
    │ (email, password, profile fields)
    ▼
[Active Account]
    │
    ├─→ POST /auth/signin → [Authenticated Session]
    │
    ├─→ PUT /profile → [Updated Profile] → JWT Refresh
    │
    ├─→ POST /auth/forgot-password → [Password Reset Requested]
    │       │
    │       │ POST /auth/reset-password
    │       │ (valid reset token)
    │       ▼
    │   [Password Reset Complete] → reset_counter++
    │
    └─→ SOFT DELETE → [Inactive Account] (is_active=false)
```

### JWT Token Lifecycle

```
[No Token]
    │
    │ Signup/Signin
    ▼
[Valid Token] (exp > now)
    │
    ├─→ Every Protected Request → Validate Signature & Expiration
    │
    ├─→ Profile Update → [Refreshed Token] (new claims)
    │
    ├─→ Time Passes (24 hours) → [Expired Token]
    │       │
    │       │ Next Protected Request
    │       ▼
    │   [401 Unauthorized] → User must re-signin
    │
    └─→ Signout → [Token Cleared] (client-side)
```

---

## Data Validation Rules Summary

### Signup Validation
1. **Email**: Must be unique, valid format, max 255 chars
2. **Password**: Min 8 chars, must contain uppercase, number, symbol
3. **Name**: Required, max 255 chars
4. **GPU Type**: Must be one of 6 enum values
5. **RAM Capacity**: Must be one of 4 enum values
6. **Coding Languages**: Must be non-empty array, at least one language
7. **Robotics Experience**: Must be one of 4 enum values

### Profile Update Validation
1. **Email**: Cannot be changed (read-only)
2. **GPU Type**: Must be valid enum value
3. **RAM Capacity**: Must be valid enum value
4. **Coding Languages**: Must be non-empty array
5. **Robotics Experience**: Must be valid enum value
6. **JWT**: Must be valid and not expired

### Password Reset Validation
1. **Email**: Must exist in database
2. **Reset Token**: Must be valid JWT with type="password_reset"
3. **Reset Counter**: Token reset_counter must match database value
4. **New Password**: Same rules as signup password validation

---

## Performance Considerations

### Query Optimization
1. **Signin Query** (most frequent):
   ```sql
   SELECT u.id, u.password_hash, u.name, p.gpu_type, p.ram_capacity,
          p.coding_languages, p.robotics_experience
   FROM users u
   LEFT JOIN user_profiles p ON u.id = p.user_id
   WHERE u.email = $1 AND u.is_active = true;
   ```
   - Uses `idx_users_email` index (O(log n) lookup)
   - Left join ensures query succeeds even if profile missing
   - Returns all data needed for JWT in single query

2. **Profile Update Query**:
   ```sql
   UPDATE user_profiles
   SET gpu_type = $1, ram_capacity = $2, coding_languages = $3,
       robotics_experience = $4, updated_at = CURRENT_TIMESTAMP
   WHERE user_id = $5;
   ```
   - Uses `idx_user_profiles_user_id` index
   - Trigger automatically updates `updated_at`

### Estimated Storage Requirements
- **User Record**: ~1KB (email, hash, timestamps)
- **User Profile**: ~500 bytes (profile fields, JSONB)
- **Auth Event Log**: ~300 bytes per event
- **100 Users with 10 auth events each**: ~150KB total
- **With 0.5GB Neon limit**: Can support ~300,000 users before hitting limit

---

## Security Considerations

### Password Storage
- **Never store plaintext passwords**
- **bcrypt with 12 salt rounds** (200-300ms hash time prevents brute-force)
- **password_hash column** is VARCHAR(255) to accommodate bcrypt format

### Email Privacy
- **Email is case-insensitive** (convert to lowercase before storage)
- **No email validation sent** (for hackathon MVP; add in production)
- **Email enumeration prevented** via constant-time responses

### Profile Data
- **Profile fields not considered sensitive** (GPU, RAM, languages are not PII)
- **Embedded in JWT** for stateless personalization
- **No encryption needed** (signed JWT ensures authenticity)

### Reset Token Security
- **reset_counter invalidates old tokens** (increment on each reset)
- **Separate secret key** (AUTH_SECRET_RESET) for reset tokens
- **1-hour expiration** prevents indefinite validity

---

## References

- **Migration 001**: `backend/db/migrations/001_initial_schema.sql` (base schema)
- **ADR-002**: Better-Auth Integration (JWT strategy)
- **Research Doc**: `specs/003-better-auth/research.md` (technical decisions)
- **Spec**: `specs/003-better-auth/spec.md` (functional requirements FR-001 to FR-037)
