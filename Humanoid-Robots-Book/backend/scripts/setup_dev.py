#!/usr/bin/env python3
"""
Development Environment Setup Script
Feature: 003-better-auth
Purpose: Automate environment setup, dependency installation, and database migration

Usage:
    python backend/scripts/setup_dev.py

This script will:
1. Setup environment variables (.env file with AUTH_SECRET)
2. Install backend dependencies (pip)
3. Install frontend dependencies (npm)
4. Run database migration (psql)
"""

import os
import sys
import secrets
import subprocess
import shutil
from pathlib import Path
from typing import Optional


# ============================================================================
# Color Output Utilities
# ============================================================================

class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(message: str):
    """Print section header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")


def print_success(message: str):
    """Print success message."""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_error(message: str):
    """Print error message."""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")


def print_warning(message: str):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")


def print_info(message: str):
    """Print info message."""
    print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")


# ============================================================================
# Path Configuration
# ============================================================================

# Assume script is run from project root or backend/scripts/
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent  # backend/scripts/ -> backend/ -> project_root/
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"

ENV_EXAMPLE_FILE = BACKEND_DIR / ".env.example"
ENV_FILE = BACKEND_DIR / ".env"
REQUIREMENTS_FILE = BACKEND_DIR / "requirements.txt"
MIGRATION_FILE = BACKEND_DIR / "db" / "migrations" / "003_user_profile_hardware.sql"
PACKAGE_JSON = PROJECT_ROOT / "package.json"


# ============================================================================
# Step 1: Environment Setup
# ============================================================================

def generate_auth_secret() -> str:
    """
    Generate a secure 32-byte AUTH_SECRET using secrets module.

    Returns:
        str: URL-safe base64-encoded secret (43 characters)
    """
    return secrets.token_urlsafe(32)


def setup_environment():
    """
    Setup environment variables in backend/.env file.

    - Copy .env.example to .env if it doesn't exist
    - Generate AUTH_SECRET if placeholder exists
    - Prompt for DATABASE_URL if missing
    """
    print_header("Step 1: Environment Setup")

    # Check if .env.example exists
    if not ENV_EXAMPLE_FILE.exists():
        print_error(f".env.example not found at {ENV_EXAMPLE_FILE}")
        print_info("Please ensure you're running this script from the project root.")
        sys.exit(1)

    # Create .env from .env.example if it doesn't exist
    if not ENV_FILE.exists():
        print_info(f"Creating {ENV_FILE} from {ENV_EXAMPLE_FILE}")
        shutil.copy(ENV_EXAMPLE_FILE, ENV_FILE)
        print_success(f"Created {ENV_FILE}")
    else:
        print_info(f"{ENV_FILE} already exists")

    # Read current .env content
    with open(ENV_FILE, 'r') as f:
        env_content = f.read()

    modified = False

    # Generate AUTH_SECRET if placeholder exists
    if "your-secret-key-here-minimum-32-characters" in env_content:
        print_info("Generating secure AUTH_SECRET...")
        auth_secret = generate_auth_secret()
        env_content = env_content.replace(
            "your-secret-key-here-minimum-32-characters",
            auth_secret
        )
        modified = True
        print_success(f"Generated AUTH_SECRET: {auth_secret[:10]}... (43 characters)")
    else:
        print_info("AUTH_SECRET already configured")

    # Check if DATABASE_URL is missing or placeholder
    if "DATABASE_URL=" not in env_content or "postgresql://user:password@host/database" in env_content:
        print_warning("DATABASE_URL not configured")
        print_info("Please enter your Neon Postgres connection string:")
        print_info("Format: postgresql://user:password@host/database")
        print_info("(You can find this in your Neon dashboard)")

        database_url = input(f"{Colors.BOLD}DATABASE_URL: {Colors.ENDC}").strip()

        if not database_url:
            print_error("DATABASE_URL cannot be empty")
            sys.exit(1)

        if "postgresql://user:password@host/database" in env_content:
            env_content = env_content.replace(
                "postgresql://user:password@host/database",
                database_url
            )
        else:
            # Append if missing
            env_content += f"\nDATABASE_URL={database_url}\n"

        modified = True
        print_success("DATABASE_URL configured")
    else:
        print_info("DATABASE_URL already configured")

    # Write updated .env file
    if modified:
        with open(ENV_FILE, 'w') as f:
            f.write(env_content)
        print_success(f"Updated {ENV_FILE}")

    print_success("Environment setup complete")


# ============================================================================
# Step 2: Dependency Installation
# ============================================================================

def check_command_exists(command: str) -> bool:
    """
    Check if a command exists in PATH.

    Args:
        command: Command name to check

    Returns:
        bool: True if command exists
    """
    return shutil.which(command) is not None


def install_backend_dependencies():
    """
    Install Python backend dependencies using pip.

    Requires: pip or pip3
    """
    print_header("Step 2a: Backend Dependencies")

    # Check if requirements.txt exists
    if not REQUIREMENTS_FILE.exists():
        print_error(f"requirements.txt not found at {REQUIREMENTS_FILE}")
        sys.exit(1)

    # Check for pip
    pip_command = None
    if check_command_exists("pip3"):
        pip_command = "pip3"
    elif check_command_exists("pip"):
        pip_command = "pip"
    else:
        print_error("pip or pip3 not found in PATH")
        print_info("Please install Python 3 and pip first")
        sys.exit(1)

    print_info(f"Using {pip_command} to install dependencies...")

    # Run pip install
    try:
        result = subprocess.run(
            [pip_command, "install", "-r", str(REQUIREMENTS_FILE)],
            cwd=str(BACKEND_DIR),
            check=True,
            capture_output=True,
            text=True
        )
        print_success("Backend dependencies installed successfully")

        # Print summary of installed packages
        if "Successfully installed" in result.stdout:
            print_info("Installed packages:")
            for line in result.stdout.split('\n'):
                if "Successfully installed" in line:
                    packages = line.replace("Successfully installed", "").strip()
                    print(f"  {packages}")

    except subprocess.CalledProcessError as e:
        print_error("Failed to install backend dependencies")
        print_error(f"Error: {e.stderr}")
        sys.exit(1)


def install_frontend_dependencies():
    """
    Install Node.js frontend dependencies using npm.

    Requires: npm
    """
    print_header("Step 2b: Frontend Dependencies")

    # Check if package.json exists
    if not PACKAGE_JSON.exists():
        print_warning(f"package.json not found at {PACKAGE_JSON}")
        print_info("Skipping frontend dependency installation")
        return

    # Check for npm
    if not check_command_exists("npm"):
        print_warning("npm not found in PATH")
        print_info("Skipping frontend dependency installation")
        print_info("Please install Node.js and npm manually")
        return

    print_info("Running npm install...")

    # Run npm install
    try:
        result = subprocess.run(
            ["npm", "install"],
            cwd=str(PROJECT_ROOT),
            check=True,
            capture_output=True,
            text=True
        )
        print_success("Frontend dependencies installed successfully")

    except subprocess.CalledProcessError as e:
        print_error("Failed to install frontend dependencies")
        print_error(f"Error: {e.stderr}")
        print_warning("Continuing with setup (frontend dependencies optional)")


# ============================================================================
# Step 3: Database Migration
# ============================================================================

def run_database_migration():
    """
    Run the database migration using psql.

    Requires: psql, DATABASE_URL in .env
    """
    print_header("Step 3: Database Migration")

    # Check if migration file exists
    if not MIGRATION_FILE.exists():
        print_error(f"Migration file not found at {MIGRATION_FILE}")
        sys.exit(1)

    # Check for psql
    if not check_command_exists("psql"):
        print_error("psql not found in PATH")
        print_info("Please install PostgreSQL client tools")
        print_info("Ubuntu/Debian: sudo apt-get install postgresql-client")
        print_info("macOS: brew install postgresql")
        print_info("Windows: Install PostgreSQL from https://www.postgresql.org/download/windows/")
        sys.exit(1)

    # Read DATABASE_URL from .env
    database_url = None
    with open(ENV_FILE, 'r') as f:
        for line in f:
            if line.startswith("DATABASE_URL="):
                database_url = line.split("=", 1)[1].strip()
                break

    if not database_url or "postgresql://user:password@host/database" in database_url:
        print_error("DATABASE_URL not configured in .env")
        print_info("Please run this script again and provide your Neon connection string")
        sys.exit(1)

    print_info(f"Running migration: {MIGRATION_FILE.name}")
    print_info("This will add hardware profile columns to user_profiles table")

    # Confirm before running migration
    response = input(f"\n{Colors.BOLD}Proceed with database migration? (y/N): {Colors.ENDC}").strip().lower()
    if response not in ['y', 'yes']:
        print_warning("Migration cancelled by user")
        print_info("You can run the migration manually later:")
        print_info(f"  psql $DATABASE_URL -f {MIGRATION_FILE}")
        return

    # Run migration
    try:
        with open(MIGRATION_FILE, 'r') as f:
            migration_sql = f.read()

        result = subprocess.run(
            ["psql", database_url, "-f", str(MIGRATION_FILE)],
            check=True,
            capture_output=True,
            text=True
        )

        print_success("Database migration completed successfully")

        # Verify migration by checking for new columns
        verify_sql = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name='user_profiles'
        AND column_name IN ('gpu_type', 'ram_capacity', 'coding_languages', 'robotics_experience')
        ORDER BY column_name;
        """

        verify_result = subprocess.run(
            ["psql", database_url, "-t", "-c", verify_sql],
            check=True,
            capture_output=True,
            text=True
        )

        columns = [col.strip() for col in verify_result.stdout.strip().split('\n') if col.strip()]

        if len(columns) == 4:
            print_success("Verified: All hardware profile columns created")
            print_info(f"  Columns: {', '.join(columns)}")
        else:
            print_warning(f"Verification incomplete: Found {len(columns)}/4 columns")

    except subprocess.CalledProcessError as e:
        print_error("Failed to run database migration")
        print_error(f"Error: {e.stderr}")
        print_info("You can run the migration manually:")
        print_info(f"  psql $DATABASE_URL -f {MIGRATION_FILE}")
        sys.exit(1)


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Main setup script execution."""
    print_header("🚀 Development Environment Setup - Feature 003-better-auth")

    print_info("This script will:")
    print_info("  1. Setup environment variables (.env file with AUTH_SECRET)")
    print_info("  2. Install backend dependencies (pip)")
    print_info("  3. Install frontend dependencies (npm)")
    print_info("  4. Run database migration (psql)")

    print(f"\n{Colors.BOLD}Project Root: {PROJECT_ROOT}{Colors.ENDC}")
    print(f"{Colors.BOLD}Backend Dir:  {BACKEND_DIR}{Colors.ENDC}\n")

    try:
        # Step 1: Environment Setup
        setup_environment()

        # Step 2: Dependency Installation
        install_backend_dependencies()
        install_frontend_dependencies()

        # Step 3: Database Migration
        run_database_migration()

        # Success Summary
        print_header("✅ Setup Complete!")
        print_success("Development environment is ready")
        print_info("\nNext steps:")
        print_info("  1. Start the backend server:")
        print_info("     cd backend && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000")
        print_info("  2. Start the frontend development server:")
        print_info("     npm start")
        print_info("  3. Visit http://localhost:3000 to test signup/signin")
        print_info("\nAPI Documentation:")
        print_info("  http://localhost:8000/docs")

    except KeyboardInterrupt:
        print_warning("\n\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
