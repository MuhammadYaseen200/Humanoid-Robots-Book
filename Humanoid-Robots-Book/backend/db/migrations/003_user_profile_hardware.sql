-- Migration 003: Add hardware/software profile fields for personalization
-- Feature: 003-better-auth
-- Created: 2025-12-16
-- Purpose: Extend user_profiles table with hardware background questions for personalization

-- Add hardware profile columns to existing user_profiles table
ALTER TABLE user_profiles
  ADD COLUMN IF NOT EXISTS gpu_type VARCHAR(100) DEFAULT 'None/Integrated Graphics',
  ADD COLUMN IF NOT EXISTS ram_capacity VARCHAR(20) DEFAULT '8-16GB',
  ADD COLUMN IF NOT EXISTS coding_languages JSONB DEFAULT '["None"]'::JSONB,
  ADD COLUMN IF NOT EXISTS robotics_experience VARCHAR(50) DEFAULT 'No prior experience';

-- Add CHECK constraints for enum-like validation
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

-- Add NOT NULL constraints (after defaults applied to existing rows)
ALTER TABLE user_profiles
  ALTER COLUMN gpu_type SET NOT NULL,
  ALTER COLUMN ram_capacity SET NOT NULL,
  ALTER COLUMN coding_languages SET NOT NULL,
  ALTER COLUMN robotics_experience SET NOT NULL;

-- Add indexes for common queries (filtering users by hardware capabilities)
CREATE INDEX IF NOT EXISTS idx_user_profiles_gpu_type ON user_profiles(gpu_type);
CREATE INDEX IF NOT EXISTS idx_user_profiles_ram_capacity ON user_profiles(ram_capacity);
CREATE INDEX IF NOT EXISTS idx_user_profiles_robotics_experience ON user_profiles(robotics_experience);

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

-- Verification queries (commented out, run manually to verify migration)
-- SELECT column_name, data_type, is_nullable, column_default
-- FROM information_schema.columns
-- WHERE table_name='user_profiles'
-- AND column_name IN ('gpu_type', 'ram_capacity', 'coding_languages', 'robotics_experience')
-- ORDER BY ordinal_position;
--
-- SELECT conname, pg_get_constraintdef(oid)
-- FROM pg_constraint
-- WHERE conrelid = 'user_profiles'::regclass
-- AND conname LIKE 'valid_%';
