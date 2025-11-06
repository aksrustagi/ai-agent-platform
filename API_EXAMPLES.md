# 📘 API Examples

Complete examples for using the AI Agent Platform API.

## Base URL

```
http://localhost:8000
```

---

## REST API Examples

### 1. Health Check

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "database": true,
    "redis": true,
    "llm": true
  }
}
```

---

### 2. List All Agents

```bash
curl http://localhost:8000/agents
```

**Response:**
```json
{
  "agents": [
    {
      "agent_type": "growth",
      "name": "Growth Agent",
      "description": "Strategic planning, goal tracking, budget management, and performance analytics",
      "llm_provider": "claude",
      "capabilities": [
        "Goal setting and tracking",
        "Budget management and ROI analysis",
        "Performance analytics and reporting"
      ],
      "available_tools": [
        "get_goals",
        "update_goal",
        "get_budget_status",
        "calculate_metrics"
      ]
    }
    // ... 6 more agents
  ],
  "total": 7
}
```

---

### 3. Chat with Growth Agent

**Request:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "message": "How am I doing this month?",
    "agent_type": "growth",
    "include_memory": true
  }'
```

**Response:**
```json
{
  "conversation_id": "conv_abc123",
  "agent_type": "growth",
  "agent_name": "Growth Agent",
  "message": {
    "role": "assistant",
    "content": "Let's look at your progress! 📊\n\n**MONTHLY PERFORMANCE (January)**\n\n**Revenue:**\n• Goal: $500,000 | Actual: $320,000 (64% to target)\n• 10 days left in month - need $180K to hit goal\n\n**Closings:**\n• Goal: 8 deals | Actual: 4 deals (50% to target)\n• Average: $80K per closing (↑15% vs last month! 🎉)...",
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "processing_time_ms": 1250.5,
  "tokens_used": {
    "prompt": 150,
    "completion": 450,
    "total": 600
  }
}
```

---

### 4. Chat with Outreach Agent

**Request:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "message": "Find leads that need follow-up",
    "agent_type": "outreach"
  }'
```

**Response:**
```json
{
  "conversation_id": "conv_def456",
  "agent_type": "outreach",
  "agent_name": "Outreach Agent",
  "message": {
    "role": "assistant",
    "content": "I found 23 leads that need your attention! Let me break this down strategically:\n\n🔥 **HOT LEADS (Top Priority - 8 leads)**\n\n**1. John Smith** - Last contact: 35 days ago\n   • Opened your last 3 emails (high engagement!)\n   • Viewed 4 properties in Riverside neighborhood\n   • Budget: $400-450K\n   • **Recommended ACTION:** Send personalized email TODAY..."
  }
}
```

---

### 5. Auto-Route Message (Let Coordinator Decide)

**Request:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "message": "I need a home inspector for 123 Main St",
    "agent_type": "auto"
  }'
```

The coordinator will automatically route this to the **Vendor Agent**.

---

### 6. Add Memory

**Request:**
```bash
curl -X POST http://localhost:8000/memory/add \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "agent_id": "growth",
    "content": "User's monthly revenue goal is $500,000",
    "category": "goals",
    "metadata": {
      "goal_type": "revenue",
      "period": "monthly"
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Memory added successfully",
  "data": {
    "memory_id": "mem_xyz789"
  }
}
```

---

### 7. Search Memories

**Request:**
```bash
curl -X POST http://localhost:8000/memory/search \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "query": "revenue goals",
    "agent_id": "growth",
    "limit": 10
  }'
```

**Response:**
```json
{
  "memories": [
    {
      "id": "mem_xyz789",
      "user_id": "user_123",
      "agent_id": "growth",
      "content": "User's monthly revenue goal is $500,000",
      "category": "goals",
      "metadata": {
        "goal_type": "revenue",
        "period": "monthly"
      },
      "created_at": "2024-01-10T10:00:00Z",
      "relevance_score": 0.95
    }
  ],
  "total": 1
}
```

---

## WebSocket Examples

### JavaScript/Browser Example

```javascript
// Connect to WebSocket
const userId = 'user_123';
const ws = new WebSocket(`ws://localhost:8000/ws/${userId}`);

// Connection opened
ws.onopen = () => {
  console.log('Connected to AI Agent Platform');
  
  // Send chat message
  ws.send(JSON.stringify({
    type: 'chat',
    message: 'Find properties in Beverly Hills under $600K',
    agent_type: 'mls'
  }));
};

// Receive messages
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
  
  switch(data.type) {
    case 'connection_established':
      console.log('Connection ID:', data.connection_id);
      break;
    
    case 'typing':
      console.log('Agent is typing...');
      break;
    
    case 'chat_response':
      console.log('Agent:', data.agent_name);
      console.log('Response:', data.content);
      break;
    
    case 'error':
      console.error('Error:', data.error);
      break;
    
    case 'pong':
      console.log('Pong received');
      break;
  }
};

// Handle errors
ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

// Connection closed
ws.onclose = () => {
  console.log('Disconnected');
};

// Send ping to keep connection alive
setInterval(() => {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: 'ping' }));
  }
}, 30000); // Every 30 seconds
```

---

### Python WebSocket Client

```python
import asyncio
import websockets
import json

async def chat_with_agent():
    uri = "ws://localhost:8000/ws/user_123"
    
    async with websockets.connect(uri) as websocket:
        # Wait for connection confirmation
        response = await websocket.recv()
        print(f"Connected: {response}")
        
        # Send chat message
        message = {
            "type": "chat",
            "message": "What's my budget status?",
            "agent_type": "growth"
        }
        await websocket.send(json.dumps(message))
        
        # Receive response
        response = await websocket.recv()
        data = json.loads(response)
        print(f"Agent: {data.get('agent_name')}")
        print(f"Response: {data.get('content')}")

# Run the client
asyncio.run(chat_with_agent())
```

---

## Agent-Specific Examples

### Growth Agent Queries

```bash
# Monthly performance
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "message": "How am I doing this month?", "agent_type": "growth"}'

# Set new goal
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "message": "I want to increase my income by 50% this year", "agent_type": "growth"}'

# Budget status
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "message": "What is my marketing budget status?", "agent_type": "growth"}'
```

---

### Outreach Agent Queries

```bash
# Find leads needing follow-up
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "message": "Find leads that need follow-up", "agent_type": "outreach"}'

# Create campaign
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "message": "Create a nurture campaign for first-time buyers", "agent_type": "outreach"}'

# Send email
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "message": "Send a follow-up email to John Smith about the Riverside properties", "agent_type": "outreach"}'
```

---

### Vendor Agent Queries

```bash
# Find inspector
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "message": "I need a home inspector for 123 Main St tomorrow", "agent_type": "vendor"}'

# Get quotes
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "message": "Find contractors for kitchen remodel under $15K", "agent_type": "vendor"}'

# Schedule photographer
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "message": "Book a photographer for 456 Oak Ave this Friday", "agent_type": "vendor"}'
```

---

### MLS Agent Queries

```bash
# Property search
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "message": "Find 3-bedroom homes in Beverly Hills under $600K", "agent_type": "mls"}'

# Market analysis
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "message": "What are the market trends in downtown?", "agent_type": "mls"}'

# Property details
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "message": "Get details for MLS listing #12345", "agent_type": "mls"}'
```

---

### Transaction Agent Queries

```bash
# Transaction status
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "message": "What is the status of the 123 Oak St transaction?", "agent_type": "transaction"}'

# Upcoming closings
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "message": "When are my next closings?", "agent_type": "transaction"}'
```

---

### Content Agent Queries

```bash
# Social media post
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "message": "Create an Instagram post about spring home buying tips", "agent_type": "content"}'

# Property description
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "message": "Write a compelling property description for 789 Elm Road", "agent_type": "content"}'

# Blog post
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "message": "Write a blog post about first-time homebuyer mistakes to avoid", "agent_type": "content"}'
```

---

### Marketing Agent Queries

```bash
# Ad performance
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "message": "How are my Facebook ads performing?", "agent_type": "marketing"}'

# Budget optimization
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "message": "Should I increase my Zillow lead budget?", "agent_type": "marketing"}'

# ROI analysis
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "message": "What is my cost per lead this month?", "agent_type": "marketing"}'
```

---

## Error Handling

### Error Response Format

```json
{
  "error": "VALIDATION_ERROR",
  "message": "Invalid input parameters",
  "details": {
    "field": "message",
    "issue": "Message cannot be empty"
  },
  "request_id": "req_abc123",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Common Error Codes

- `VALIDATION_ERROR` - Invalid input
- `AUTHENTICATION_ERROR` - Auth failed
- `AGENT_ERROR` - Agent processing error
- `LLM_PROVIDER_ERROR` - LLM API error
- `MEMORY_ERROR` - Memory operation failed
- `INTEGRATION_ERROR` - External API error
- `RATE_LIMIT_ERROR` - Rate limit exceeded

---

## Rate Limiting

Default limits (configurable in `.env`):
- **100 requests per 60 seconds** per user

When rate limited, you'll receive:
```json
{
  "error": "RATE_LIMIT_ERROR",
  "message": "Rate limit exceeded",
  "details": {
    "retry_after": 30
  }
}
```

---

## Testing with cURL

### Save response to file
```bash
curl http://localhost:8000/agents > agents.json
```

### Pretty print JSON
```bash
curl http://localhost:8000/health | jq '.'
```

### Include headers in output
```bash
curl -i http://localhost:8000/health
```

### Verbose output
```bash
curl -v http://localhost:8000/health
```

---

## Testing with Postman

Import this collection URL:
```
http://localhost:8000/openapi.json
```

Or manually create requests using the examples above.

---

## SDKs and Client Libraries

### Python Client Example

```python
import httpx
import asyncio

class AIAgentClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def chat(self, user_id, message, agent_type="auto"):
        response = await self.client.post(
            f"{self.base_url}/chat",
            json={
                "user_id": user_id,
                "message": message,
                "agent_type": agent_type
            }
        )
        return response.json()
    
    async def list_agents(self):
        response = await self.client.get(f"{self.base_url}/agents")
        return response.json()

# Usage
async def main():
    client = AIAgentClient()
    
    # Chat with growth agent
    response = await client.chat(
        user_id="user_123",
        message="How am I doing this month?",
        agent_type="growth"
    )
    print(response["message"]["content"])

asyncio.run(main())
```

---

For more examples and documentation, visit:
- **API Docs**: http://localhost:8000/docs
- **README.md**
- **PROJECT_SUMMARY.md**
