-- InsureFlow Database Initialization Script
-- This script is executed when the PostgreSQL container starts

-- Create database (if not exists - handled by Docker environment variable)
-- The database 'insureflow' is already created by POSTGRES_DB environment variable

-- Create extensions that might be useful for the application
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Grant necessary permissions to the application user
GRANT ALL PRIVILEGES ON DATABASE insureflow TO insureflow;

-- Set timezone
SET timezone = 'UTC'; 