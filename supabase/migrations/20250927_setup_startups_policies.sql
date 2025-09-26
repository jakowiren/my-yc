-- Setup startup conversation system policies and triggers
-- Tables already exist, this migration adds missing policies/triggers
BEGIN;

-- Ensure startups table has all required columns
DO $$
BEGIN
    -- Add columns if they don't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'startups' AND column_name = 'title') THEN
        ALTER TABLE startups ADD COLUMN title TEXT;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'startups' AND column_name = 'status') THEN
        ALTER TABLE startups ADD COLUMN status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted'));
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'startups' AND column_name = 'metadata') THEN
        ALTER TABLE startups ADD COLUMN metadata JSONB DEFAULT '{}';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'startups' AND column_name = 'conversation_context') THEN
        ALTER TABLE startups ADD COLUMN conversation_context JSONB DEFAULT '{}';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'startups' AND column_name = 'user_id') THEN
        ALTER TABLE startups ADD COLUMN user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'startups' AND column_name = 'created_at') THEN
        ALTER TABLE startups ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'startups' AND column_name = 'updated_at') THEN
        ALTER TABLE startups ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
    END IF;
END $$;

-- Ensure messages table has all required columns
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'messages' AND column_name = 'startup_id') THEN
        ALTER TABLE messages ADD COLUMN startup_id UUID REFERENCES startups(id) ON DELETE CASCADE;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'messages' AND column_name = 'role') THEN
        ALTER TABLE messages ADD COLUMN role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system'));
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'messages' AND column_name = 'content') THEN
        ALTER TABLE messages ADD COLUMN content TEXT NOT NULL;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'messages' AND column_name = 'metadata') THEN
        ALTER TABLE messages ADD COLUMN metadata JSONB DEFAULT '{}';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'messages' AND column_name = 'created_at') THEN
        ALTER TABLE messages ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
    END IF;
END $$;

-- Create indexes if they don't exist
CREATE INDEX IF NOT EXISTS idx_startups_user_id ON startups(user_id);
CREATE INDEX IF NOT EXISTS idx_startups_status ON startups(status);
CREATE INDEX IF NOT EXISTS idx_startups_created_at ON startups(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_startup_id ON messages(startup_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Setup updated_at trigger
DROP TRIGGER IF EXISTS update_startups_updated_at ON startups;
CREATE TRIGGER update_startups_updated_at
    BEFORE UPDATE ON startups
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS
ALTER TABLE startups ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- Setup RLS policies for startups
DROP POLICY IF EXISTS "Users can view their own startups" ON startups;
CREATE POLICY "Users can view their own startups" ON startups
    FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert their own startups" ON startups;
CREATE POLICY "Users can insert their own startups" ON startups
    FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update their own startups" ON startups;
CREATE POLICY "Users can update their own startups" ON startups
    FOR UPDATE USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete their own startups" ON startups;
CREATE POLICY "Users can delete their own startups" ON startups
    FOR DELETE USING (auth.uid() = user_id);

-- Setup RLS policies for messages
DROP POLICY IF EXISTS "Users can view messages for their own startups" ON messages;
CREATE POLICY "Users can view messages for their own startups" ON messages
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM startups
            WHERE startups.id = messages.startup_id
            AND startups.user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS "Users can insert messages for their own startups" ON messages;
CREATE POLICY "Users can insert messages for their own startups" ON messages
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM startups
            WHERE startups.id = messages.startup_id
            AND startups.user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS "Users can update messages for their own startups" ON messages;
CREATE POLICY "Users can update messages for their own startups" ON messages
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM startups
            WHERE startups.id = messages.startup_id
            AND startups.user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS "Users can delete messages for their own startups" ON messages;
CREATE POLICY "Users can delete messages for their own startups" ON messages
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM startups
            WHERE startups.id = messages.startup_id
            AND startups.user_id = auth.uid()
        )
    );

-- Setup 5 startup limit function and trigger
CREATE OR REPLACE FUNCTION check_startup_limit()
RETURNS TRIGGER AS $$
BEGIN
    IF (
        SELECT COUNT(*)
        FROM startups
        WHERE user_id = NEW.user_id
        AND status != 'deleted'
    ) >= 5 THEN
        RAISE EXCEPTION 'Maximum of 5 active startups per user allowed';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS enforce_startup_limit ON startups;
CREATE TRIGGER enforce_startup_limit
    BEFORE INSERT ON startups
    FOR EACH ROW
    EXECUTE FUNCTION check_startup_limit();

COMMIT;