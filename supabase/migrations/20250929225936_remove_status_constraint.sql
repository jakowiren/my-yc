-- Remove project_status check constraint for faster iteration
-- This allows us to use any status values while developing
BEGIN;

-- Drop the check constraint
ALTER TABLE startups DROP CONSTRAINT IF EXISTS startups_project_status_check;

-- Update existing problematic statuses to workspace_ready
UPDATE startups
SET project_status = 'workspace_ready'
WHERE project_status IN ('spawning', 'running');

COMMIT;