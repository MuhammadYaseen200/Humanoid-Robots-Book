# Backend Scripts

Utility scripts for development environment setup and automation.

## `setup_dev.py` - Development Environment Setup

**Purpose**: Automate the complete setup of the development environment for Feature 003-better-auth.

### What It Does

1. **Environment Variables Setup**
   - Creates `backend/.env` from `backend/.env.example` if it doesn't exist
   - Generates a secure 32-byte `AUTH_SECRET` using Python's `secrets` module
   - Prompts for `DATABASE_URL` (Neon Postgres connection string) if missing
   - Validates all required environment variables are configured

2. **Backend Dependencies Installation**
   - Installs Python packages from `backend/requirements.txt` using pip
   - Includes authentication packages: `passlib[bcrypt]`, `python-jose[cryptography]`, `slowapi`, `email-validator`

3. **Frontend Dependencies Installation**
   - Installs Node.js packages from `package.json` using npm (if available)
   - Includes React Query and Axios for state management and HTTP requests

4. **Database Migration**
   - Runs `backend/db/migrations/003_user_profile_hardware.sql` using `psql`
   - Adds hardware profile columns: `gpu_type`, `ram_capacity`, `coding_languages`, `robotics_experience`
   - Verifies migration by checking for new columns in `user_profiles` table

### Prerequisites

**Required**:
- Python 3.8+ (with pip)
- PostgreSQL client tools (`psql`)
- Neon Postgres database connection string

**Optional**:
- Node.js and npm (for frontend dependencies)

### Installation Instructions

#### Ubuntu/Debian
```bash
# Install Python and pip
sudo apt-get update
sudo apt-get install python3 python3-pip

# Install PostgreSQL client
sudo apt-get install postgresql-client

# Install Node.js (optional)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### macOS
```bash
# Install Python (usually pre-installed)
brew install python3

# Install PostgreSQL client
brew install postgresql

# Install Node.js (optional)
brew install node
```

#### Windows
- Install Python: https://www.python.org/downloads/windows/
- Install PostgreSQL: https://www.postgresql.org/download/windows/
- Install Node.js: https://nodejs.org/en/download/

### Usage

**From project root**:
```bash
python backend/scripts/setup_dev.py
```

**Or with Python 3 explicitly**:
```bash
python3 backend/scripts/setup_dev.py
```

### Interactive Prompts

The script will prompt you for:

1. **DATABASE_URL** (if not already configured):
   ```
   Please enter your Neon Postgres connection string:
   Format: postgresql://user:password@host/database
   (You can find this in your Neon dashboard)
   DATABASE_URL:
   ```

   Example:
   ```
   postgresql://myuser:mypassword@ep-cool-cloud-123456.us-east-2.aws.neon.tech/mydb
   ```

2. **Migration Confirmation**:
   ```
   Proceed with database migration? (y/N):
   ```

   Type `y` or `yes` to proceed, or `N` to skip migration.

### Output Example

```
======================================================================
🚀 Development Environment Setup - Feature 003-better-auth
======================================================================

ℹ This script will:
ℹ   1. Setup environment variables (.env file with AUTH_SECRET)
ℹ   2. Install backend dependencies (pip)
ℹ   3. Install frontend dependencies (npm)
ℹ   4. Run database migration (psql)

Project Root: /path/to/Humanoid-Robots-Book
Backend Dir:  /path/to/Humanoid-Robots-Book/backend

======================================================================
Step 1: Environment Setup
======================================================================

ℹ Creating backend/.env from backend/.env.example
✓ Created backend/.env
ℹ Generating secure AUTH_SECRET...
✓ Generated AUTH_SECRET: rJ8kL9mN... (43 characters)
⚠ DATABASE_URL not configured
ℹ Please enter your Neon Postgres connection string:
DATABASE_URL: postgresql://user:pass@host/db
✓ DATABASE_URL configured
✓ Updated backend/.env
✓ Environment setup complete

======================================================================
Step 2a: Backend Dependencies
======================================================================

ℹ Using pip3 to install dependencies...
✓ Backend dependencies installed successfully
ℹ Installed packages:
  passlib-1.7.4 python-jose-3.3.0 slowapi-0.1.9 email-validator-2.1.0 ...

======================================================================
Step 2b: Frontend Dependencies
======================================================================

ℹ Running npm install...
✓ Frontend dependencies installed successfully

======================================================================
Step 3: Database Migration
======================================================================

ℹ Running migration: 003_user_profile_hardware.sql
ℹ This will add hardware profile columns to user_profiles table

Proceed with database migration? (y/N): y
✓ Database migration completed successfully
✓ Verified: All hardware profile columns created
ℹ   Columns: coding_languages, gpu_type, ram_capacity, robotics_experience

======================================================================
✅ Setup Complete!
======================================================================

✓ Development environment is ready

Next steps:
ℹ   1. Start the backend server:
ℹ      cd backend && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
ℹ   2. Start the frontend development server:
ℹ      npm start
ℹ   3. Visit http://localhost:3000 to test signup/signin

API Documentation:
ℹ   http://localhost:8000/docs
```

### Manual Migration (If Needed)

If the script fails or you skip the migration, you can run it manually:

```bash
# Load DATABASE_URL from .env
export $(cat backend/.env | grep DATABASE_URL | xargs)

# Run migration
psql $DATABASE_URL -f backend/db/migrations/003_user_profile_hardware.sql

# Verify columns were created
psql $DATABASE_URL -c "SELECT column_name FROM information_schema.columns WHERE table_name='user_profiles' ORDER BY column_name;"
```

### Troubleshooting

**Error: `psql not found in PATH`**
- Install PostgreSQL client tools (see Prerequisites above)

**Error: `pip or pip3 not found in PATH`**
- Install Python 3 and pip (see Prerequisites above)

**Error: `DATABASE_URL not configured in .env`**
- Run the script again and enter your Neon connection string when prompted
- Or manually edit `backend/.env` and add:
  ```
  DATABASE_URL=postgresql://user:password@host/database
  ```

**Error: `Migration file not found`**
- Ensure you're running the script from the project root directory
- Verify the migration file exists at `backend/db/migrations/003_user_profile_hardware.sql`

**Error: Database connection failed**
- Verify your DATABASE_URL is correct
- Check that your Neon database is running and accessible
- Ensure your IP is whitelisted in Neon (if using IP restrictions)

### What Gets Created

After successful execution:

```
backend/
├── .env                          # Generated with AUTH_SECRET and DATABASE_URL
├── requirements.txt              # Dependencies installed
└── db/
    └── migrations/
        └── 003_user_profile_hardware.sql  # Executed migration

Database (user_profiles table):
├── gpu_type                     # VARCHAR(100) with CHECK constraint
├── ram_capacity                 # VARCHAR(20) with CHECK constraint
├── coding_languages             # JSONB array
├── robotics_experience          # VARCHAR(50) with CHECK constraint
└── Indexes on gpu_type, ram_capacity
```

### Security Notes

- `AUTH_SECRET` is generated using Python's `secrets.token_urlsafe(32)` for cryptographic security
- The generated secret is 43 characters long (32 bytes base64-encoded)
- Never commit `.env` file to version control (already in `.gitignore`)
- Database credentials are read from `.env` and never logged

### Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the migration SQL file: `backend/db/migrations/003_user_profile_hardware.sql`
3. Consult the feature spec: `specs/003-better-auth/spec.md`
4. Check ADR-005 for authentication architecture decisions
