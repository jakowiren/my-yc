# Testing Checklist: New Workspace Architecture

## Overview

This document provides a comprehensive testing checklist for the new startup workspace architecture that replaces expensive CEO containers ($90/month) with cost-effective multi-agent workspaces (~$1/month).

## Architecture Changes

### Before (Expensive)
- ✗ One container per CEO agent
- ✗ `min_containers=1` always running
- ✗ $90/month per startup
- ✗ Single agent per container

### After (Cost-Effective)
- ✅ One container per startup workspace
- ✅ Cold start enabled (no min_containers)
- ✅ ~$1/month per startup
- ✅ Multiple agents per container with persistent memory

## Deployment Instructions

### 1. Deploy Backend to Modal

```bash
cd backend/agents

# Deploy the new workspace service
modal deploy startup_workspace.py

# Verify deployment
modal app list | grep startup-workspaces
```

Expected output:
```
my-yc-startup-workspaces   https://jakowiren--my-yc-startup-workspaces-*.modal.run
```

### 2. Update Frontend Environment Variables

Add to your environment (`.env.local` or Vercel):

```bash
# New workspace endpoints
NEXT_PUBLIC_WORKSPACE_INIT_ENDPOINT=https://jakowiren--my-yc-startup-workspaces-initialize.modal.run
NEXT_PUBLIC_WORKSPACE_AGENT_ENDPOINT=https://jakowiren--my-yc-startup-workspaces-agent-invoke.modal.run
NEXT_PUBLIC_WORKSPACE_AGENT_STREAM_ENDPOINT=https://jakowiren--my-yc-startup-workspaces-agent-stream.modal.run
NEXT_PUBLIC_WORKSPACE_STATUS_ENDPOINT=https://jakowiren--my-yc-startup-workspaces-workspace-status.modal.run
NEXT_PUBLIC_WORKSPACE_TEAM_BOARD_ENDPOINT=https://jakowiren--my-yc-startup-workspaces-team-board.modal.run
NEXT_PUBLIC_WORKSPACE_HEALTH_ENDPOINT=https://jakowiren--my-yc-startup-workspaces-health.modal.run
```

### 3. Deploy Frontend

```bash
cd frontend
npm run build
vercel deploy
```

## Manual Testing Checklist

### ✅ Test 1: Basic Persistence

**Objective**: Verify agents remember information across sessions

**Steps**:
1. Create a new startup
2. Initialize workspace (check that it works)
3. Ask CEO: "Please remember that the secret code is BANANA123"
4. Note the timestamp and container status (should show "active")
5. Log out of the application completely
6. Wait 5+ minutes (ensure container goes cold)
7. Log back in to the same startup
8. Ask CEO: "What was the secret code?"

**Expected Result**:
- ✅ CEO responds with "BANANA123"
- ✅ Response time on first question after wait is 3-5 seconds (cold start)
- ✅ Follow-up questions are faster (container warm)

**Troubleshooting**:
- If CEO doesn't remember: Check Modal logs for agent memory loading
- If cold start > 10 seconds: Check container resource allocation
- If error: Verify all endpoints are correctly configured

### ✅ Test 2: Team Message Board

**Objective**: Test team communication and tool usage

**Steps**:
1. In the same startup as Test 1
2. Ask CEO: "Please write a message to the team board saying 'Project kickoff meeting scheduled for 3pm tomorrow'"
3. Verify CEO confirms the message was written
4. Click "View Team Board" button in UI
5. Verify message appears in team board with correct timestamp and author
6. Log out and log back in
7. Ask CEO: "What messages are currently on the team board?"

**Expected Result**:
- ✅ CEO successfully writes message using `team_write_message` tool
- ✅ Message appears in team board UI
- ✅ CEO can read back the message after logout/login
- ✅ Message persists across sessions

**Troubleshooting**:
- If tool call fails: Check MCP tools registration in agent_orchestrator
- If message not in UI: Check team board API endpoint
- If CEO can't read back: Verify team_read_messages tool works

### ✅ Test 3: Cold Start Performance

**Objective**: Measure and verify cold start performance

**Steps**:
1. Use a startup that hasn't been active for 10+ minutes
2. Note exact timestamp before sending first message
3. Ask CEO: "Hello, what's the current status of the project?"
4. Note exact timestamp when response begins
5. Immediately ask: "Can you give me more details?"
6. Note timestamp for second response

**Expected Result**:
- ✅ First response starts within 5 seconds
- ✅ Second response starts within 1 second
- ✅ Workspace Status component shows container transition from "cold" to "active"

**Performance Benchmarks**:
- Cold start: < 5 seconds
- Warm response: < 1 second
- Memory loading: < 2 seconds

### ✅ Test 4: Multi-Agent Communication

**Objective**: Test different agents and cross-agent awareness

**Steps**:
1. Create a fresh startup
2. Chat with CEO: "Tell the Frontend Agent that we should use blue (#007bff) as our primary color"
3. Verify CEO writes this to team board or shared notes
4. Switch to Frontend Agent using agent selector
5. Ask Frontend Agent: "What color should I use for the primary theme?"
6. Switch back to CEO
7. Ask CEO: "What instructions have been given to the Frontend Agent?"

**Expected Result**:
- ✅ CEO uses team communication tools to share the instruction
- ✅ Frontend Agent can access the color information
- ✅ CEO remembers the instruction it gave
- ✅ Both agents maintain separate conversation histories

**Troubleshooting**:
- If agents can't communicate: Check team tools registration
- If agent switching fails: Verify agent_type parameter handling
- If memory isolation breaks: Check agent memory directory structure

### ✅ Test 5: Workspace Isolation

**Objective**: Verify different startups have isolated workspaces

**Steps**:
1. Create Startup A
2. Ask CEO in Startup A: "Remember that our project name is 'Project Alpha'"
3. Create Startup B
4. Ask CEO in Startup B: "Remember that our project name is 'Project Beta'"
5. Switch back to Startup A
6. Ask CEO: "What's our project name?"
7. Switch to Startup B
8. Ask CEO: "What's our project name?"

**Expected Result**:
- ✅ Startup A CEO only knows "Project Alpha"
- ✅ Startup B CEO only knows "Project Beta"
- ✅ No cross-contamination of information
- ✅ Each startup shows separate workspace status

### ✅ Test 6: Error Handling and Recovery

**Objective**: Test system behavior under error conditions

**Steps**:
1. Try to access workspace for non-existent startup
2. Send malformed requests to agent endpoint
3. Test with very long messages (>10k characters)
4. Test rapid-fire requests (10 requests in 10 seconds)
5. Test agent invocation without proper authentication

**Expected Result**:
- ✅ Graceful error messages for invalid startups
- ✅ Proper validation of request format
- ✅ Long messages handled appropriately
- ✅ Rate limiting or queuing for rapid requests
- ✅ Proper authentication enforcement

## UI Testing Checklist

### ✅ UI Test 1: Workspace Status Component

**Steps**:
1. Navigate to startup chat page
2. Verify workspace status component appears
3. Check that it shows container status (cold/active)
4. Verify last activity timestamp
5. Click refresh button
6. Expand debug info section

**Expected Result**:
- ✅ Status loads correctly
- ✅ Container status updates in real-time
- ✅ Debug info shows comprehensive workspace data
- ✅ Refresh works without errors

### ✅ UI Test 2: Team Board Viewer

**Steps**:
1. Click "View Team Board" button
2. Verify dialog opens with empty state message
3. Ask CEO to write a test message
4. Refresh team board
5. Verify message appears with proper formatting
6. Test message filtering if implemented

**Expected Result**:
- ✅ Dialog opens and displays correctly
- ✅ Empty state shows helpful instructions
- ✅ Messages display with author, timestamp, priority
- ✅ Real-time updates work

### ✅ UI Test 3: Agent Selector

**Steps**:
1. Verify agent selector shows all 6 agents
2. Switch between different agents
3. Verify agent details expand/collapse
4. Test capabilities display for each agent
5. Send messages to different agents

**Expected Result**:
- ✅ All agents available in dropdown
- ✅ Agent details show correctly
- ✅ Messages route to correct agent
- ✅ Each agent has distinct personality/responses

## Automated Testing

### Backend Tests

```bash
cd backend/agents

# Test workspace initialization
python -m pytest tests/test_workspace_manager.py -v

# Test agent orchestrator
python -m pytest tests/test_agent_orchestrator.py -v

# Test team tools
python -m pytest tests/test_team_tools.py -v
```

### Frontend Tests

```bash
cd frontend

# Test API routes
npm run test -- --testNamePattern="workspace"

# Test UI components
npm run test -- --testNamePattern="WorkspaceStatus|TeamBoard|AgentSelector"
```

## Cost Monitoring

### Before/After Comparison

**Monitor Modal Usage**:
1. Check Modal dashboard for compute costs
2. Verify containers are not kept warm unnecessarily
3. Compare costs to previous CEO container approach

**Expected Savings**:
- Per startup: $90/month → $1/month (99% reduction)
- Total platform: Linear savings based on number of startups
- Storage costs: Minimal ($0.50/month for 30GB workspace)

### Cost Alerts

Set up monitoring for:
- Unexpected container warm time (>1 hour continuously)
- High memory usage (>4GB per workspace)
- Excessive API calls (>1000/day per startup)

## Production Deployment

### 1. Migration Strategy

```bash
# Phase 1: Deploy new architecture alongside existing
modal deploy startup_workspace.py

# Phase 2: Update frontend to use new endpoints (feature flag)
# Phase 3: Migrate existing startups (data migration script)
# Phase 4: Deprecate old CEO containers
```

### 2. Rollback Plan

If issues occur:
```bash
# Quickly revert frontend to use old endpoints
# Old CEO containers should still be running
# Update environment variables back to CEO endpoints
```

### 3. Monitoring

Set up alerts for:
- High error rates (>5% in 5 minutes)
- Cold start times >10 seconds
- Memory usage >90% in containers
- Failed agent initializations

## Success Criteria

✅ **Performance**:
- Cold start < 5 seconds
- Warm response < 1 second
- 99.9% uptime

✅ **Functionality**:
- All 5 test scenarios pass
- Team communication works
- Multi-agent coordination works
- Memory persistence across sessions

✅ **Cost**:
- <$2/month per startup
- >95% cost reduction from previous architecture
- No idle compute costs

✅ **User Experience**:
- Seamless agent switching
- Clear workspace status
- Intuitive team board interface
- Helpful testing instructions

## Troubleshooting Guide

### Common Issues

1. **Agent doesn't remember previous conversation**
   - Check: Agent memory file exists
   - Check: Conversation history loading in orchestrator
   - Solution: Verify workspace initialization

2. **Cold start takes >10 seconds**
   - Check: Container resource allocation
   - Check: Image size and dependencies
   - Solution: Optimize imports, reduce memory

3. **Team board messages not appearing**
   - Check: MCP tools registration
   - Check: File permissions in workspace
   - Solution: Verify team tools initialization

4. **Cross-agent communication fails**
   - Check: Shared notes directory exists
   - Check: Tool execution logs
   - Solution: Debug team tools MCP implementation

5. **High costs despite new architecture**
   - Check: min_containers settings (should be 0)
   - Check: Container keep-alive times
   - Solution: Verify cold start configuration

---

## Final Checklist

Before declaring the migration successful:

- [ ] All 6 test scenarios pass
- [ ] UI components work correctly
- [ ] Cost monitoring shows expected savings
- [ ] Error handling works appropriately
- [ ] Performance meets benchmarks
- [ ] Documentation is updated
- [ ] Team is trained on new architecture
- [ ] Rollback plan is tested

**Expected Outcome**: Cost-effective, scalable multi-agent workspace architecture with persistent memory and seamless user experience.