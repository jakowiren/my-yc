-- Add user_id column to projects table and enable RLS
BEGIN;

-- Add user_id column to projects table
ALTER TABLE projects
ADD COLUMN user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;

-- Add created_at column if it doesn't exist
ALTER TABLE projects
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Enable Row Level Security on projects table
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

-- Create policy: Users can only see their own projects
CREATE POLICY "Users can view their own projects" ON projects
    FOR SELECT USING (auth.uid() = user_id);

-- Create policy: Users can only insert their own projects
CREATE POLICY "Users can insert their own projects" ON projects
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Create policy: Users can only update their own projects
CREATE POLICY "Users can update their own projects" ON projects
    FOR UPDATE USING (auth.uid() = user_id);

-- Create policy: Users can only delete their own projects
CREATE POLICY "Users can delete their own projects" ON projects
    FOR DELETE USING (auth.uid() = user_id);

-- Enable RLS on project_logs table as well
ALTER TABLE project_logs ENABLE ROW LEVEL SECURITY;

-- Create policy for project_logs: Users can only see logs for their own projects
CREATE POLICY "Users can view logs for their own projects" ON project_logs
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = project_logs.project_id
            AND projects.user_id = auth.uid()
        )
    );

-- Create policy for project_logs: Users can only insert logs for their own projects
CREATE POLICY "Users can insert logs for their own projects" ON project_logs
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = project_logs.project_id
            AND projects.user_id = auth.uid()
        )
    );

COMMIT;