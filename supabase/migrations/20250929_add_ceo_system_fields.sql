-- Add CEO system fields to support persistent Modal containers
-- Migration: 20250927_add_ceo_system_fields.sql

-- Add CEO-specific fields to startups table
ALTER TABLE startups
ADD COLUMN container_endpoint TEXT DEFAULT NULL,
ADD COLUMN ceo_status TEXT DEFAULT 'not_spawned' CHECK (ceo_status IN ('not_spawned', 'spawning', 'running', 'error', 'sleeping')),
ADD COLUMN team_plan JSONB DEFAULT NULL,
ADD COLUMN last_activity TIMESTAMP DEFAULT NOW(),
ADD COLUMN ceo_initialized_at TIMESTAMP DEFAULT NULL,
ADD COLUMN container_logs JSONB DEFAULT '[]';

-- Create CEO conversations table (separate from Jason conversations)
CREATE TABLE ceo_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    startup_id UUID REFERENCES startups(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'ceo')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index for efficient conversation queries
CREATE INDEX ceo_conversations_startup_id_idx ON ceo_conversations(startup_id);
CREATE INDEX ceo_conversations_created_at_idx ON ceo_conversations(created_at);

-- Create startup agents table for future agent team tracking
CREATE TABLE startup_agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    startup_id UUID REFERENCES startups(id) ON DELETE CASCADE,
    agent_type TEXT NOT NULL,
    agent_status TEXT DEFAULT 'planned' CHECK (agent_status IN ('planned', 'spawning', 'running', 'completed', 'error')),
    priority INTEGER DEFAULT 1,
    responsibilities JSONB DEFAULT '[]',
    rationale TEXT DEFAULT NULL,
    capabilities JSONB DEFAULT '{}',
    container_endpoint TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for startup agents
CREATE INDEX startup_agents_startup_id_idx ON startup_agents(startup_id);
CREATE INDEX startup_agents_status_idx ON startup_agents(agent_status);

-- Update existing startups to have proper ceo_status
UPDATE startups
SET ceo_status = CASE
    WHEN project_status = 'completed' AND github_url IS NOT NULL THEN 'running'
    WHEN project_status = 'spawning' THEN 'spawning'
    WHEN project_status = 'error' THEN 'error'
    ELSE 'not_spawned'
END;

-- Add comments for documentation
COMMENT ON COLUMN startups.container_endpoint IS 'Modal container endpoint URL for CEO agent communication';
COMMENT ON COLUMN startups.ceo_status IS 'Current status of the CEO agent container';
COMMENT ON COLUMN startups.team_plan IS 'AI-generated plan for agent team structure';
COMMENT ON COLUMN startups.last_activity IS 'Last activity timestamp from CEO or agents';
COMMENT ON COLUMN startups.ceo_initialized_at IS 'When the CEO agent was first initialized';
COMMENT ON COLUMN startups.container_logs IS 'Array of log entries from CEO container';

COMMENT ON TABLE ceo_conversations IS 'Chat conversations between founders and their CEO agents';
COMMENT ON TABLE startup_agents IS 'Planned and active AI agents for each startup';