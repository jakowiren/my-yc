# Jason AI Integration - TODO List

## Environment Setup Required
- [ ] Add your OpenAI API key to `frontend/.env.local` (replace `your_openai_api_key_here`)
- [ ] Add your Supabase service role key to `frontend/.env.local` (replace `your_supabase_service_role_key_here`)

## Future Features to Implement
- [ ] Rate limiting: 10 messages per day for free users
  - Create Supabase migration for `user_daily_limits` table
  - Add message count tracking in API endpoint
  - Display remaining messages to user
  - Reset count daily at midnight UTC
- [ ] Premium tier with unlimited messages
- [ ] Save chat history to Supabase for persistence
- [ ] Copy button for design documents
- [ ] Markdown rendering for Jason's responses
- [ ] Message editing/deletion
- [ ] Export design documents as PDF

## Database Schema (for rate limiting)
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

## Testing Checklist
- [ ] Test authentication flow (login modal appears when not signed in)
- [ ] Test successful message sending and Jason response
- [ ] Test chat expansion behavior
- [ ] Test error handling (network errors, API failures)
- [ ] Test streaming response display
- [ ] Test mobile responsiveness