-- PostgreSQL Database Initialization Script
-- This script sets up the face attendance database with pgvector extension

-- Create database if it doesn't exist
-- Note: This needs to be run as a superuser
-- CREATE DATABASE face_attendance;

-- Connect to the face_attendance database
-- \c face_attendance;

-- Create pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create user if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'face_user') THEN
        CREATE ROLE face_user WITH LOGIN PASSWORD 'face_password';
    END IF;
END
$$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE face_attendance TO face_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO face_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO face_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO face_user;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO face_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO face_user;

-- Create indexes for better performance
-- These will be created after Django migrations

-- Face embeddings table for vector similarity search
CREATE TABLE IF NOT EXISTS face_embeddings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    embedding vector(512), -- Adjust size based on your model
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for vector similarity search
CREATE INDEX IF NOT EXISTS face_embeddings_embedding_idx 
ON face_embeddings USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create index on user_id for faster lookups
CREATE INDEX IF NOT EXISTS face_embeddings_user_id_idx ON face_embeddings(user_id);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for face_embeddings table
CREATE TRIGGER update_face_embeddings_updated_at 
    BEFORE UPDATE ON face_embeddings 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create attendance logs table with proper indexing
CREATE TABLE IF NOT EXISTS attendance_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    attendance_type VARCHAR(20) NOT NULL DEFAULT 'check_in',
    camera_id VARCHAR(50),
    location VARCHAR(200),
    confidence FLOAT DEFAULT 0.0,
    verification_time FLOAT,
    face_position JSONB,
    photo_path VARCHAR(500),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for attendance logs
CREATE INDEX IF NOT EXISTS attendance_logs_user_id_idx ON attendance_logs(user_id);
CREATE INDEX IF NOT EXISTS attendance_logs_timestamp_idx ON attendance_logs(timestamp);
CREATE INDEX IF NOT EXISTS attendance_logs_attendance_type_idx ON attendance_logs(attendance_type);
CREATE INDEX IF NOT EXISTS attendance_logs_camera_id_idx ON attendance_logs(camera_id);

-- Create attendance summaries table
CREATE TABLE IF NOT EXISTS attendance_summaries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL,
    check_in_time TIME,
    check_out_time TIME,
    total_hours FLOAT DEFAULT 0.0,
    break_duration FLOAT DEFAULT 0.0,
    is_present BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, date)
);

-- Create indexes for attendance summaries
CREATE INDEX IF NOT EXISTS attendance_summaries_user_id_idx ON attendance_summaries(user_id);
CREATE INDEX IF NOT EXISTS attendance_summaries_date_idx ON attendance_summaries(date);
CREATE INDEX IF NOT EXISTS attendance_summaries_is_present_idx ON attendance_summaries(is_present);

-- Create trigger for attendance_summaries table
CREATE TRIGGER update_attendance_summaries_updated_at 
    BEFORE UPDATE ON attendance_summaries 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create cameras table
CREATE TABLE IF NOT EXISTS cameras (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(200),
    camera_type VARCHAR(50) NOT NULL,
    ip_address INET,
    rtsp_url TEXT,
    status VARCHAR(20) DEFAULT 'offline',
    is_active BOOLEAN DEFAULT TRUE,
    last_seen TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for cameras
CREATE INDEX IF NOT EXISTS cameras_status_idx ON cameras(status);
CREATE INDEX IF NOT EXISTS cameras_is_active_idx ON cameras(is_active);
CREATE INDEX IF NOT EXISTS cameras_last_seen_idx ON cameras(last_seen);

-- Create trigger for cameras table
CREATE TRIGGER update_cameras_updated_at 
    BEFORE UPDATE ON cameras 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium',
    is_read BOOLEAN DEFAULT FALSE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    read_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for notifications
CREATE INDEX IF NOT EXISTS notifications_is_read_idx ON notifications(is_read);
CREATE INDEX IF NOT EXISTS notifications_created_at_idx ON notifications(created_at);
CREATE INDEX IF NOT EXISTS notifications_notification_type_idx ON notifications(notification_type);
CREATE INDEX IF NOT EXISTS notifications_priority_idx ON notifications(priority);

-- Create users table (extending Django's default user model)
CREATE TABLE IF NOT EXISTS users_user (
    id SERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    employee_id VARCHAR(50) UNIQUE,
    department VARCHAR(100),
    phone_number VARCHAR(20),
    role VARCHAR(20) DEFAULT 'student',
    face_enrolled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for users
CREATE INDEX IF NOT EXISTS users_user_employee_id_idx ON users_user(employee_id);
CREATE INDEX IF NOT EXISTS users_user_email_idx ON users_user(email);
CREATE INDEX IF NOT EXISTS users_user_is_active_idx ON users_user(is_active);
CREATE INDEX IF NOT EXISTS users_user_face_enrolled_idx ON users_user(face_enrolled);
CREATE INDEX IF NOT EXISTS users_user_role_idx ON users_user(role);

-- Create trigger for users table
CREATE TRIGGER update_users_user_updated_at 
    BEFORE UPDATE ON users_user 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user (password: admin123)
INSERT INTO users_user (
    password, username, first_name, last_name, email, 
    is_staff, is_superuser, is_active, employee_id, role
) VALUES (
    'pbkdf2_sha256$600000$dummy$dummy', -- This should be properly hashed
    'admin', 'Admin', 'User', 'admin@example.com',
    TRUE, TRUE, TRUE, 'ADMIN001', 'admin'
) ON CONFLICT (username) DO NOTHING;

-- Create function to calculate face similarity
CREATE OR REPLACE FUNCTION calculate_face_similarity(
    embedding1 vector(512),
    embedding2 vector(512)
) RETURNS FLOAT AS $$
BEGIN
    RETURN 1 - (embedding1 <=> embedding2);
END;
$$ LANGUAGE plpgsql;

-- Create function to find similar faces
CREATE OR REPLACE FUNCTION find_similar_faces(
    query_embedding vector(512),
    similarity_threshold FLOAT DEFAULT 0.6,
    max_results INTEGER DEFAULT 10
) RETURNS TABLE (
    user_id INTEGER,
    similarity FLOAT,
    embedding_id INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        fe.user_id,
        calculate_face_similarity(query_embedding, fe.embedding) as similarity,
        fe.id as embedding_id
    FROM face_embeddings fe
    WHERE calculate_face_similarity(query_embedding, fe.embedding) >= similarity_threshold
    ORDER BY similarity DESC
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Grant execute permissions on functions
GRANT EXECUTE ON FUNCTION calculate_face_similarity(vector(512), vector(512)) TO face_user;
GRANT EXECUTE ON FUNCTION find_similar_faces(vector(512), FLOAT, INTEGER) TO face_user;
