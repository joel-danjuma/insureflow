-- Manual SQL Migration for Notifications Table
-- Run this if the automatic Alembic migration fails

-- Create notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    broker_id INTEGER NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'payment_reminder',
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    policy_id INTEGER,
    is_read BOOLEAN NOT NULL DEFAULT false,
    is_dismissed BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    read_at TIMESTAMP WITHOUT TIME ZONE,
    dismissed_at TIMESTAMP WITHOUT TIME ZONE,
    
    -- Foreign key constraints
    CONSTRAINT fk_notifications_broker_id FOREIGN KEY (broker_id) REFERENCES users (id),
    CONSTRAINT fk_notifications_policy_id FOREIGN KEY (policy_id) REFERENCES policies (id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS ix_notifications_id ON notifications (id);
CREATE INDEX IF NOT EXISTS ix_notifications_broker_id ON notifications (broker_id);
CREATE INDEX IF NOT EXISTS ix_notifications_policy_id ON notifications (policy_id);
CREATE INDEX IF NOT EXISTS ix_notifications_is_read ON notifications (is_read);

-- Update Alembic version table (replace with actual latest revision)
-- Only run this if you want to mark the migration as completed
-- INSERT INTO alembic_version (version_num) VALUES ('2a3b4c5d6e7f')
-- ON CONFLICT (version_num) DO NOTHING;

-- Verify the table was created
SELECT table_name, column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'notifications' 
ORDER BY ordinal_position; 