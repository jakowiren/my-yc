# Database Migrations

## Rate Limiting Schema
```sql
-- Supabase table for tracking daily limits
CREATE TABLE user_daily_limits (
  user_id UUID REFERENCES auth.users PRIMARY KEY,
  message_count INTEGER DEFAULT 0,
  last_reset TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```