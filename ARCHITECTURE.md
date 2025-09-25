# my-yc Real-Time Architecture

## 🎯 **Production Architecture: Vercel + Supabase + Modal**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Supabase      │    │     Modal       │
│   (Vercel)      │───▶│  Edge Functions │───▶│   AI Agents     │
│                 │    │                 │    │                 │
│ - Next.js 14    │    │ - spawn_project │    │ - GitHub Agent  │
│ - Real-time UI  │    │ - webhook recv  │    │ - Future agents │
│ - Terminal view │    │ - Database      │    │ - Embedded MCP  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐              │
         │              │   Supabase      │              │
         └──────────────│   Realtime      │◀─────────────┘
           WebSocket    │   (Live Logs)   │    HTTP Webhooks
                       └─────────────────┘
```

## 🔄 **Real-Time Workflow**

### **1. User Submits Idea**
```javascript
// Frontend (Vercel)
const response = await supabase.functions.invoke('spawn_project', {
  body: { title: 'AI Recipe App', description: '...', category: 'food-tech' }
})
```

### **2. Supabase Edge Function Triggers Modal**
```javascript
// Edge Function: supabase/functions/spawn_project/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

serve(async (req) => {
  const { title, description } = await req.json()

  // Create project record
  const { data: project } = await supabase.from('projects').insert({
    title, description, status: 'spawning', progress: 0
  }).select().single()

  // Trigger Modal agent
  const modalResponse = await fetch('https://your-modal-app--spawn-project.modal.run', {
    method: 'POST',
    body: JSON.stringify({
      project_id: project.id,
      config: { title, description }
    })
  })

  return new Response(JSON.stringify({ project_id: project.id }))
})
```

### **3. Modal Agents Stream Progress**
```python
# Modal Agent with real-time logging
async def log_to_supabase(self, message: str, level: str = "info"):
    """Stream logs to Supabase for real-time frontend updates."""
    await httpx.post(
        f"{SUPABASE_URL}/rest/v1/project_logs",
        headers={"Authorization": f"Bearer {SUPABASE_KEY}"},
        json={
            "project_id": self.project_id,
            "agent_name": self.agent_name,
            "level": level,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {"progress": self.progress}
        }
    )
    # Supabase Realtime automatically broadcasts this to frontend!
```

### **4. Frontend Shows Live Terminal**
```javascript
// Frontend real-time subscription
useEffect(() => {
  const subscription = supabase
    .channel(`project-${projectId}`)
    .on('postgres_changes', {
      event: 'INSERT',
      schema: 'public',
      table: 'project_logs',
      filter: `project_id=eq.${projectId}`
    }, (payload) => {
      // Live terminal like Lovable!
      setLogs(prev => [...prev, payload.new])
    })
    .subscribe()

  return () => subscription.unsubscribe()
}, [projectId])
```

## 📊 **Database Schema**

```sql
-- Projects table
CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  description TEXT,
  category TEXT,
  status TEXT CHECK (status IN ('spawning', 'running', 'completed', 'failed')) DEFAULT 'spawning',
  progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
  github_url TEXT,
  deployment_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Real-time logs table
CREATE TABLE project_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  agent_name TEXT NOT NULL,
  level TEXT CHECK (level IN ('info', 'success', 'warning', 'error')) DEFAULT 'info',
  message TEXT NOT NULL,
  data JSONB,
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Enable realtime for live updates
ALTER PUBLICATION supabase_realtime ADD TABLE project_logs;
```

## 🚀 **Modal Web Endpoints**

```python
# Modal provides web endpoints for direct frontend integration
@app.web_endpoint(method="POST", path="/spawn")
def spawn_project_web(project_id: str, config: dict):
    """Web endpoint for Supabase Edge Functions to trigger."""
    return spawn_project.spawn(project_id, config)

@app.web_endpoint(method="GET", path="/status/{project_id}")
def get_project_status_web(project_id: str):
    """Check project status via HTTP."""
    return get_project_status.remote(project_id)
```

## 🔧 **Component Architecture**

### **Frontend Components**
```
frontend/
├── app/
│   ├── launch/page.tsx          # Project creation form
│   ├── projects/[id]/page.tsx   # Live monitoring dashboard
│   └── components/
│       ├── ProjectTerminal.tsx  # Real-time log display
│       ├── ProgressBar.tsx      # Visual progress
│       └── ProjectCard.tsx      # Portfolio view
```

### **Supabase Functions**
```
supabase/
├── functions/
│   ├── spawn_project/index.ts   # Trigger Modal agents
│   ├── webhook_handler/index.ts # Receive Modal updates
│   └── get_projects/index.ts    # Portfolio data
└── migrations/
    └── 001_initial_schema.sql   # Database setup
```

### **Modal Agents**
```
backend/agents/
├── modal_spawner.py             # Main Modal deployment
├── supabase_integration.py     # Real-time logging
├── github_agent.py              # Repository creation
└── mcp_tools/                   # Embedded MCP tools
```

## ✨ **Real-Time Features Like Lovable**

### **Live Terminal Output**
- ✅ Real-time log streaming via Supabase Realtime
- ✅ Color-coded log levels (info, success, warning, error)
- ✅ Agent-specific log filtering
- ✅ Progress bar with completion percentage

### **SSH-Like Experience**
- ✅ Live command output as agents work
- ✅ Repository creation progress
- ✅ File creation notifications
- ✅ Deployment status updates
- ✅ Error handling with detailed messages

### **Portfolio Dashboard**
- ✅ All projects with live status
- ✅ Click to view detailed logs
- ✅ GitHub repo links
- ✅ One-click deployment buttons

## 🎯 **Next Implementation Steps**

1. **Update Modal agents** with Supabase integration
2. **Create Supabase Edge Functions** for project spawning
3. **Build real-time frontend** with terminal component
4. **Set up database schema** and realtime subscriptions
5. **Deploy and test** full end-to-end workflow

This architecture gives you **true real-time monitoring** like Lovable, with zero infrastructure management overhead!