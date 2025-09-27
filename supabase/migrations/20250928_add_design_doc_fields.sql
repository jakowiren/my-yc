-- Add design document and project tracking fields to startups table
-- This migration adds support for structured design docs and project spawning
BEGIN;

-- Add new columns to startups table
DO $$
BEGIN
    -- Design document storage (JSON structure from Jason AI)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'startups' AND column_name = 'design_doc') THEN
        ALTER TABLE startups ADD COLUMN design_doc JSONB DEFAULT NULL;
    END IF;

    -- Project status tracking
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'startups' AND column_name = 'project_status') THEN
        ALTER TABLE startups ADD COLUMN project_status TEXT DEFAULT 'designing' CHECK (project_status IN ('designing', 'design_ready', 'spawning', 'running', 'completed', 'error'));
    END IF;

    -- GitHub repository URL (populated after project creation)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'startups' AND column_name = 'github_url') THEN
        ALTER TABLE startups ADD COLUMN github_url TEXT DEFAULT NULL;
    END IF;

    -- Modal project ID (for tracking in Modal system)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'startups' AND column_name = 'modal_project_id') THEN
        ALTER TABLE startups ADD COLUMN modal_project_id TEXT DEFAULT NULL;
    END IF;

    -- Project spawn timestamp
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'startups' AND column_name = 'spawned_at') THEN
        ALTER TABLE startups ADD COLUMN spawned_at TIMESTAMP WITH TIME ZONE DEFAULT NULL;
    END IF;

    -- Error details (if project spawning fails)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'startups' AND column_name = 'error_details') THEN
        ALTER TABLE startups ADD COLUMN error_details TEXT DEFAULT NULL;
    END IF;
END $$;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_startups_project_status ON startups(project_status);
CREATE INDEX IF NOT EXISTS idx_startups_spawned_at ON startups(spawned_at DESC);
CREATE INDEX IF NOT EXISTS idx_startups_modal_project_id ON startups(modal_project_id) WHERE modal_project_id IS NOT NULL;

-- Add helpful comments
COMMENT ON COLUMN startups.design_doc IS 'Structured JSON design document from Jason AI';
COMMENT ON COLUMN startups.project_status IS 'Current status of the startup project';
COMMENT ON COLUMN startups.github_url IS 'GitHub repository URL after project creation';
COMMENT ON COLUMN startups.modal_project_id IS 'Modal project ID for tracking';
COMMENT ON COLUMN startups.spawned_at IS 'Timestamp when project spawning was initiated';
COMMENT ON COLUMN startups.error_details IS 'Error message if project spawning failed';

-- Create a function to update project status with timestamp
CREATE OR REPLACE FUNCTION update_startup_project_status(startup_id UUID, new_status TEXT, error_msg TEXT DEFAULT NULL)
RETURNS void AS $$
BEGIN
    UPDATE startups
    SET
        project_status = new_status,
        error_details = error_msg,
        updated_at = NOW(),
        spawned_at = CASE
            WHEN new_status = 'spawning' AND spawned_at IS NULL THEN NOW()
            ELSE spawned_at
        END
    WHERE id = startup_id;
END;
$$ LANGUAGE plpgsql;

-- Create a view for easy project status querying
CREATE OR REPLACE VIEW startup_project_summary AS
SELECT
    id,
    user_id,
    title,
    project_status,
    github_url,
    modal_project_id,
    spawned_at,
    created_at,
    updated_at,
    CASE
        WHEN design_doc IS NOT NULL THEN true
        ELSE false
    END as has_design_doc,
    CASE
        WHEN project_status = 'designing' THEN 'In conversation with Jason'
        WHEN project_status = 'design_ready' THEN 'Design complete, ready to start'
        WHEN project_status = 'spawning' THEN 'Creating project...'
        WHEN project_status = 'running' THEN 'Project active'
        WHEN project_status = 'completed' THEN 'Project deployed successfully'
        WHEN project_status = 'error' THEN 'Error occurred'
        ELSE project_status
    END as status_description
FROM startups
WHERE status = 'active';

COMMIT;