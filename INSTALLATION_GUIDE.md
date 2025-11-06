# 🚀 Installation Guide - AI Agent Platform

This guide will help you set up and run the AI Agent Platform in minutes.

## Prerequisites

Before you begin, ensure you have:

### Required
- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Docker & Docker Compose** - [Download](https://www.docker.com/get-started)
- **Git** - [Download](https://git-scm.com/downloads)

### API Keys Required
You'll need API keys from:
- **Anthropic** (Claude) - [Get key](https://console.anthropic.com/)
- **OpenAI** (GPT-4) - [Get key](https://platform.openai.com/)
- **Groq** - [Get key](https://console.groq.com/)
- **Mem0** - [Get key](https://mem0.ai/)
- **Composio** - [Get key](https://composio.dev/)
- **RealEstateAPI.com** - [Get key](https://realestateapi.com/)

## Installation Methods

Choose one of two installation methods:

### Method 1: Docker Compose (Recommended) 🐳

This is the easiest and recommended method for most users.

#### Step 1: Clone the Repository

```bash
git clone <your-repository-url>
cd ai-agent-platform
```

#### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your favorite editor
```

Required environment variables:
```bash
# LLM API Keys
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...

# Memory & Integrations
MEM0_API_KEY=mem0-...
COMPOSIO_API_KEY=composio-...
REALESTATE_API_KEY=re-...

# Security (change this!)
SECRET_KEY=your-secret-key-change-this-in-production

# Database (defaults are fine for Docker)
POSTGRES_PASSWORD=postgres
```

#### Step 3: Start the Platform

```bash
# Option A: Use quick-start script
./quick-start.sh

# Option B: Manual Docker Compose
docker-compose up -d
```

#### Step 4: Verify Installation

```bash
# Check service health
curl http://localhost:8000/health

# View logs
docker-compose logs -f api

# Check API documentation
open http://localhost:8000/docs
```

**That's it!** The platform is now running at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws/{user_id}

---

### Method 2: Local Python Installation 🐍

For development or if you prefer running Python locally.

#### Step 1: Clone and Setup

```bash
git clone <your-repository-url>
cd ai-agent-platform
```

#### Step 2: Create Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate venv
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows
```

#### Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install production dependencies
pip install -r requirements.txt

# Optional: Install dev dependencies
pip install -r requirements-dev.txt
```

#### Step 4: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

#### Step 5: Start PostgreSQL and Redis

You still need PostgreSQL and Redis. Start them with Docker:

```bash
docker-compose up -d postgres redis
```

#### Step 6: Run the Application

```bash
# Run with Python
python -m backend.main

# OR run with uvicorn directly
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Step 7: Verify Installation

```bash
# In another terminal
curl http://localhost:8000/health
```

---

## Testing Your Installation

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "database": true,
    "redis": true,
    "llm": true
  }
}
```

### 2. List Agents

```bash
curl http://localhost:8000/agents
```

Should return all 7 agents.

### 3. Send a Test Message

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "How am I doing this month?",
    "agent_type": "growth"
  }'
```

### 4. Test WebSocket

Use a WebSocket client or browser console:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/test_user');

ws.onopen = () => {
  console.log('Connected!');
  ws.send(JSON.stringify({
    type: 'chat',
    message: 'Hello, Growth Agent!',
    agent_type: 'growth'
  }));
};

ws.onmessage = (event) => {
  console.log('Response:', JSON.parse(event.data));
};
```

---

## Common Issues & Solutions

### Issue: "Module not found" errors

**Solution:**
```bash
# Ensure you're in the venv
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Docker port conflicts

**Solution:**
```bash
# Check what's using the ports
lsof -i :8000
lsof -i :5432
lsof -i :6379

# Change ports in docker-compose.yml if needed
```

### Issue: API key authentication fails

**Solution:**
- Verify API keys are correct in `.env`
- Ensure no spaces or quotes around keys
- Check if keys have proper permissions/credits

### Issue: Database connection fails

**Solution:**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Issue: Redis connection fails

**Solution:**
```bash
# Check if Redis is running
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli ping
# Should return: PONG
```

---

## Running Tests

```bash
# Activate venv if using local installation
source venv/bin/activate

# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest backend/tests/test_agents.py -v

# Run specific test
pytest backend/tests/test_agents.py::TestGrowthAgent::test_agent_properties
```

---

## Stopping the Platform

### Docker Compose Method

```bash
# Stop services (keeps data)
docker-compose stop

# Stop and remove containers (keeps volumes)
docker-compose down

# Stop and remove everything including volumes
docker-compose down -v
```

### Local Python Method

```bash
# Press Ctrl+C in the terminal running the app

# Stop Docker databases
docker-compose down postgres redis
```

---

## Updating the Platform

```bash
# Pull latest changes
git pull origin main

# Rebuild Docker images
docker-compose build

# Restart services
docker-compose up -d

# OR for local Python:
pip install -r requirements.txt
```

---

## Production Deployment Checklist

Before deploying to production:

- [ ] Change `SECRET_KEY` in `.env`
- [ ] Use strong database passwords
- [ ] Set `APP_ENV=production`
- [ ] Set `DEBUG=False`
- [ ] Configure proper `ALLOWED_ORIGINS`
- [ ] Enable HTTPS/TLS
- [ ] Set up proper logging
- [ ] Configure backup strategy
- [ ] Set up monitoring (Sentry, etc.)
- [ ] Review rate limits
- [ ] Configure firewall rules
- [ ] Set up CI/CD pipeline

---

## Getting Help

If you encounter issues:

1. **Check Logs**
   ```bash
   docker-compose logs -f api
   docker-compose logs -f postgres
   docker-compose logs -f redis
   ```

2. **Verify Setup**
   ```bash
   ./verify-setup.sh
   ```

3. **Check Documentation**
   - README.md
   - PROJECT_SUMMARY.md
   - API Docs: http://localhost:8000/docs

4. **Common Commands**
   ```bash
   # View running containers
   docker-compose ps
   
   # Restart a service
   docker-compose restart api
   
   # View service logs
   docker-compose logs -f api
   
   # Access database
   docker-compose exec postgres psql -U postgres -d ai_agent_platform
   
   # Access Redis CLI
   docker-compose exec redis redis-cli
   ```

---

## Next Steps

Once installed:

1. **Read the README** - Understand the architecture
2. **Explore API Docs** - Visit http://localhost:8000/docs
3. **Try Different Agents** - Test all 7 specialized agents
4. **Review PROJECT_SUMMARY.md** - Learn about the implementation
5. **Customize** - Extend agents or add new features

---

## Development Mode

For active development:

```bash
# Run with auto-reload
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Run tests in watch mode
pytest-watch

# Format code
black backend/
isort backend/

# Type checking
mypy backend/
```

---

**Congratulations! Your AI Agent Platform is ready to use! 🎉**

For more information, see README.md and PROJECT_SUMMARY.md.
