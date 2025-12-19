-- Migration: 003_user_profile_hardware
-- Feature: Better-Auth & User Profiling (Feature 003-better-auth)
-- Purpose: Add hardware background profiling to earn 50 Hackathon Bonus Points
-- Date: 2025-12-19

-- ============================================================================
-- Create users table
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on email for fast lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- ============================================================================
-- Create user_profiles table with hardware background fields
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Hardware Profile Fields (THE 50-POINT HACKATHON FEATURE)
    gpu_type VARCHAR(100) CHECK (gpu_type IN (
        'No GPU',
        'NVIDIA RTX 3060',
        'NVIDIA RTX 4070 Ti',
        'NVIDIA RTX 4090',
        'Apple M1/M2/M3',
        'Other'
    )),

    ram_capacity VARCHAR(20) CHECK (ram_capacity IN (
        'Less than 8GB',
        '8-16GB',
        '16-32GB',
        'More than 32GB'
    )),

    coding_languages JSONB DEFAULT '[]'::jsonb,

    robotics_experience VARCHAR(50) CHECK (robotics_experience IN (
        'No prior experience',
        'Beginner (0-1 years)',
        'Intermediate (1-3 years)',
        'Advanced (3+ years)'
    )),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Ensure one profile per user
    UNIQUE(user_id)
);

-- Create indexes for personalization queries
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_gpu_type ON user_profiles(gpu_type);
CREATE INDEX IF NOT EXISTS idx_user_profiles_ram_capacity ON user_profiles(ram_capacity);

-- ============================================================================
-- Create trigger to update updated_at timestamp
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Verification Query
-- ============================================================================
-- Run this to verify the migration:
-- SELECT column_name, data_type, character_maximum_length
-- FROM information_schema.columns
-- WHERE table_name IN ('users', 'user_profiles')
-- ORDER BY table_name, ordinal_position;
