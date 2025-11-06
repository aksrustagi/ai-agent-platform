# 📚 AI Agent Platform - Complete Index

Your complete guide to navigating this project.

## 🚀 Quick Start

**New to the project?** Start here:

1. **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** - Step-by-step setup instructions
2. **[quick-start.sh](quick-start.sh)** - Automated setup script
3. **[README.md](README.md)** - Project overview and features

## 📖 Documentation Files

### Getting Started
- **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** - Complete installation guide (Docker & Local)
- **[quick-start.sh](quick-start.sh)** - Automated setup script
- **[verify-setup.sh](verify-setup.sh)** - Verify your installation

### Understanding the Project
- **[README.md](README.md)** - Project overview, features, and basic usage
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Comprehensive technical overview
- **[INDEX.md](INDEX.md)** - This file - navigate the project

### Using the API
- **[API_EXAMPLES.md](API_EXAMPLES.md)** - Complete API examples (REST & WebSocket)
- Visit `/docs` when running for interactive API documentation

### Configuration
- **[.env.example](.env.example)** - Environment variables template
- **[docker-compose.yml](docker-compose.yml)** - Docker orchestration
- **[Dockerfile](Dockerfile)** - Docker image definition
- **[pytest.ini](pytest.ini)** - Test configuration

### Dependencies
- **[requirements.txt](requirements.txt)** - Production dependencies
- **[requirements-dev.txt](requirements-dev.txt)** - Development dependencies

## 🏗️ Code Structure

### Core Application
```
backend/
├── main.py                  # FastAPI application (START HERE)
├── config.py                # Configuration with Pydantic
└── dependencies.py          # Dependency injection
```

### The 7 AI Agents
```
backend/agents/
├── base_agent.py            # Abstract base class
├── growth_agent.py          # Goals, KPIs, budgets
├── outreach_agent.py        # Lead nurturing, campaigns
├── vendor_agent.py          # Vendor coordination
├── mls_agent.py             # Property search
├── transaction_agent.py     # Transaction management
├── content_agent.py         # Content creation
└── marketing_agent.py       # Marketing & ads
```

### Agent Coordination
```
backend/coordinator/
└── agent_coordinator.py     # Intelligent message routing
```

### Memory System
```
backend/memory/
├── mem0_client.py           # Mem0 API integration
└── memory_manager.py        # Memory abstraction
```

### External Integrations
```
backend/integrations/
├── composio_client.py       # 200+ app integrations
├── realestateapi_client.py  # Property data API
└── mcp_client.py            # MCP wrapper
```

### Data Models
```
backend/models/
├── requests.py              # API request models
├── responses.py             # API response models
└── database.py              # SQLAlchemy models
```

### Services
```
backend/services/
├── llm_service.py           # Multi-LLM service (Claude, GPT-4, Groq)
└── websocket_service.py     # WebSocket connection manager
```

### Utilities
```
backend/utils/
├── errors.py                # Custom exceptions
├── logger.py                # Structured logging
├── security.py              # Auth & security
└── helpers.py               # Utility functions
```

### Tests
```
backend/tests/
├── conftest.py              # Pytest fixtures
├── test_agents.py           # Agent tests
└── test_coordinator.py      # Coordinator tests
```

## 🎯 Common Tasks

### I want to...

**Run the application**
→ See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)
→ Run `./quick-start.sh`

**Understand the architecture**
→ Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
→ Read [README.md](README.md)

**Use the API**
→ Visit http://localhost:8000/docs
→ Read [API_EXAMPLES.md](API_EXAMPLES.md)

**Add a new agent**
→ Check `backend/agents/base_agent.py`
→ Copy pattern from `backend/agents/growth_agent.py`
→ Register in `backend/coordinator/agent_coordinator.py`

**Modify an existing agent**
→ Find agent in `backend/agents/`
→ Update system prompt or tools
→ Test with `pytest backend/tests/test_agents.py`

**Add a new integration**
→ Create client in `backend/integrations/`
→ Follow pattern from `composio_client.py`
→ Add to agent tools

**Run tests**
→ `pytest`
→ `pytest --cov=backend`
→ `pytest backend/tests/test_agents.py -v`

**Deploy to production**
→ Follow checklist in [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)
→ Use Docker Compose
→ Set proper environment variables

**Troubleshoot issues**
→ Check [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) "Common Issues"
→ Run `./verify-setup.sh`
→ Check logs with `docker-compose logs -f api`

## 📊 Project Statistics

- **Total Files**: 51
- **Python Files**: 38
- **Code Files**: ~5,000+ lines
- **Agents**: 7 specialized agents
- **LLM Providers**: 3 (Claude, GPT-4, Groq)
- **Integration Channels**: 200+ (via Composio)

## 🔗 Key Endpoints

When running locally:

- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **List Agents**: http://localhost:8000/agents
- **Chat**: http://localhost:8000/chat
- **WebSocket**: ws://localhost:8000/ws/{user_id}

## 🤖 The 7 Agents

| Agent | LLM | Purpose | Key Capabilities |
|-------|-----|---------|-----------------|
| **Growth** | Claude | Goals & KPIs | Goal tracking, budgets, analytics |
| **Outreach** | GPT-4 | Lead nurturing | Email/SMS campaigns, follow-ups |
| **Vendor** | Groq | Vendor coordination | Fast vendor search, scheduling |
| **MLS** | GPT-4 | Property search | MLS search, CMAs, market data |
| **Transaction** | Claude | Deal management | Contracts, closings, documents |
| **Content** | Claude | Content creation | Social posts, blogs, listings |
| **Marketing** | GPT-4 | Advertising | Ad campaigns, ROI, lead gen |

## 📋 Checklists

### Setup Checklist
- [ ] Clone repository
- [ ] Copy `.env.example` to `.env`
- [ ] Add API keys to `.env`
- [ ] Install Docker & Docker Compose
- [ ] Run `./quick-start.sh`
- [ ] Verify with `./verify-setup.sh`
- [ ] Test with API call

### Development Checklist
- [ ] Activate virtual environment
- [ ] Install dev dependencies
- [ ] Run tests with `pytest`
- [ ] Format code with `black`
- [ ] Check types with `mypy`
- [ ] Update documentation

### Deployment Checklist
- [ ] Set production environment variables
- [ ] Change `SECRET_KEY`
- [ ] Set strong passwords
- [ ] Configure HTTPS
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Review security settings

## 🎓 Learning Path

**Day 1: Setup & Basics**
1. Install using [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)
2. Read [README.md](README.md)
3. Try examples from [API_EXAMPLES.md](API_EXAMPLES.md)

**Day 2: Understanding Architecture**
1. Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
2. Explore `backend/main.py`
3. Review one agent (start with `growth_agent.py`)

**Day 3: Customization**
1. Modify an agent system prompt
2. Add a new tool to an agent
3. Test your changes

**Week 2: Advanced**
1. Add a new agent
2. Integrate a new external service
3. Implement new features

## 🆘 Getting Help

**Issue**: Installation problems
→ See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) "Common Issues"

**Issue**: API not working
→ Check `docker-compose logs -f api`
→ Verify health with `/health` endpoint

**Issue**: Agent not responding correctly
→ Check agent system prompt in `backend/agents/`
→ Review memory context
→ Check LLM API keys in `.env`

**Issue**: Tests failing
→ Check pytest configuration in `pytest.ini`
→ Review test fixtures in `backend/tests/conftest.py`
→ Run specific test with verbose output

## 🔄 Update Process

```bash
# Pull latest changes
git pull origin main

# Rebuild if using Docker
docker-compose build
docker-compose up -d

# Or update Python packages
pip install -r requirements.txt

# Run tests
pytest

# Verify setup
./verify-setup.sh
```

## 📞 Support Resources

- **Documentation**: README.md, PROJECT_SUMMARY.md
- **API Docs**: http://localhost:8000/docs
- **Examples**: API_EXAMPLES.md
- **Installation**: INSTALLATION_GUIDE.md
- **Logs**: `docker-compose logs -f`

## 🎯 Next Steps

After reviewing this index:

1. **If new to the project**: Start with [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)
2. **To understand architecture**: Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
3. **To use the API**: Check [API_EXAMPLES.md](API_EXAMPLES.md)
4. **To contribute**: Review code in `backend/` directory

---

**Welcome to the AI Agent Platform! 🎉**

This index is your roadmap. Pick a destination and start exploring!
