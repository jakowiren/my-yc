-- Add workspace tracking fields for persistent CEO architecture
-- Migration: 20250930_add_workspace_tracking.sql

-- Add workspace-specific fields to startups table
ALTER TABLE startups
ADD COLUMN workspace_path TEXT DEFAULT NULL,
ADD COLUMN workspace_version TEXT DEFAULT '1.0',
ADD COLUMN workspace_created_at TIMESTAMP DEFAULT NULL,
ADD COLUMN workspace_last_updated TIMESTAMP DEFAULT NULL;

-- Update ceo_status enum to include 'ready' status
ALTER TABLE startups DROP CONSTRAINT IF EXISTS startups_ceo_status_check;
ALTER TABLE startups ADD CONSTRAINT startups_ceo_status_check
    CHECK (ceo_status IN ('not_spawned', 'spawning', 'running', 'ready', 'error', 'sleeping'));

-- Create workspace activity log table
CREATE TABLE workspace_activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    startup_id UUID REFERENCES startups(id) ON DELETE CASCADE,
    activity_type TEXT NOT NULL CHECK (activity_type IN ('workspace_created', 'ceo_state_saved', 'conversation', 'decision_logged', 'agent_spawned')),
    activity_data JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index for efficient workspace activity queries
CREATE INDEX workspace_activities_startup_id_idx ON workspace_activities(startup_id);
CREATE INDEX workspace_activities_type_idx ON workspace_activities(activity_type);
CREATE INDEX workspace_activities_created_at_idx ON workspace_activities(created_at);

-- Update existing startups that might have workspaces
UPDATE startups
SET
    workspace_path = '/workspace/' || id,
    workspace_created_at = ceo_initialized_at,
    workspace_last_updated = last_activity
WHERE ceo_status IN ('running', 'ready') AND workspace_path IS NULL;

-- Add comments for documentation
COMMENT ON COLUMN startups.workspace_path IS 'Path to persistent workspace in Modal Volume';
COMMENT ON COLUMN startups.workspace_version IS 'Version of workspace structure';
COMMENT ON COLUMN startups.workspace_created_at IS 'When the workspace was first created';
COMMENT ON COLUMN startups.workspace_last_updated IS 'Last activity in the workspace';

COMMENT ON TABLE workspace_activities IS 'Log of all activities in startup workspaces';
COMMENT ON COLUMN workspace_activities.activity_type IS 'Type of workspace activity';
COMMENT ON COLUMN workspace_activities.activity_data IS 'JSON data specific to the activity type';