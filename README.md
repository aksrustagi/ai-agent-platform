# 🏡 AI Agent Platform for Real Estate Professionals

A production-ready, multi-agent AI system with 7 specialized agents, multi-LLM support (Claude, GPT-4, Groq), persistent memory (Mem0), WebSocket real-time communication, and extensive integrations.

## 🌟 Features

### 7 Specialized AI Agents

1. **Growth Agent** (Claude) - Goals, KPIs, budgets, task coordination
2. **Outreach Agent** (GPT-4) - Lead nurturing, drip campaigns, multi-channel outreach
3. **Vendor Agent** (Groq) - Vendor coordination, quotes, scheduling
4. **MLS Agent** (GPT-4) - Property search via RealEstateAPI.com, CMAs
5. **Transaction Agent** (Claude) - Contracts, forms, transaction management
6. **Content Agent** (Claude) - Content creation, social media posting
7. **Marketing Agent** (GPT-4) - Ads, lead purchasing, ROI optimization

### Tech Stack

- **Backend**: Python 3.11+ with FastAPI
- **LLMs**: Anthropic Claude, OpenAI GPT-4, Groq
- **Memory**: Mem0 for persistent agent memory
- **Integrations**: Composio (200+ apps), RealEstateAPI.com
- **Database**: PostgreSQL with SQLAlchemy
- **Cache**: Redis for caching & pub/sub
- **Real-time**: WebSocket support
- **Deployment**: Docker & Docker Compose

### Code Quality

✅ Type hints on every function and variable  
✅ Async/await patterns throughout  
✅ Comprehensive error handling with custom exceptions  
✅ Structured logging using structlog  
✅ Pydantic for configuration and validation  
✅ Security best practices (no hardcoded secrets)  
✅ Production-ready patterns (retry logic, circuit breakers)  

## 📁 Project Structure

```
ai-agent-platform/
├── backend/
│   ├── agents/              # 7 specialized AI agents
│   ├── coordinator/         # Agent routing logic
│   ├── memory/              # Mem0 integration
│   ├── integrations/        # External API clients
│   ├── models/              # Pydantic & SQLAlchemy models
│   ├── services/            # LLM & WebSocket services
│   ├── utils/               # Utilities & helpers
│   ├── tests/               # Unit tests
│   ├── main.py              # FastAPI application
│   └── config.py            # Configuration
├── docker-compose.yml       # Docker orchestration
├── Dockerfile               # Docker image
├── requirements.txt         # Dependencies
└── README.md                # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- API keys for:
  - Anthropic (Claude)
  - OpenAI (GPT-4)
  - Groq
  - Mem0
  - Composio
  - RealEstateAPI.com

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd ai-agent-platform
```

2. **Set up environment variables**

```bash
cp .env.example .env
# Edit .env and add your API keys
```

3. **Start with Docker Compose** (Recommended)

```bash
docker-compose up -d
```

This starts:
- FastAPI application (port 8000)
- PostgreSQL database (port 5432)
- Redis cache (port 6379)

4. **OR Install locally**

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m backend.main
```

### Access the API

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **WebSocket**: ws://localhost:8000/ws/{user_id}

## 📖 API Usage

### REST API

#### Chat with an Agent

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

#### List Available Agents

```bash
curl http://localhost:8000/agents
```

#### Add Memory

```bash
curl -X POST http://localhost:8000/memory/add \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "agent_id": "growth",
    "content": "User's monthly revenue goal is $500,000",
    "category": "goals"
  }'
```

#### Search Memories

```bash
curl -X POST http://localhost:8000/memory/search \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "query": "revenue goals",
    "limit": 10
  }'
```

### WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/user_123');

ws.onopen = () => {
  // Send chat message
  ws.send(JSON.stringify({
    type: 'chat',
    message: 'Find leads that need follow-up',
    agent_type: 'outreach'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

## 🤖 Agent Details

### Growth Agent

**Purpose**: Strategic planning, goal tracking, budget management  
**LLM**: Claude (best for strategic thinking)  
**Capabilities**:
- Goal setting and tracking
- Budget management and ROI analysis
- Performance analytics
- Task coordination
- KPI monitoring

**Example queries**:
- "How am I doing this month?"
- "I want to increase my income by 50% this year"
- "What's my budget status?"

### Outreach Agent

**Purpose**: Lead nurturing and multi-channel outreach  
**LLM**: GPT-4 (best for tool orchestration)  
**Capabilities**:
- Lead segmentation and scoring
- Multi-channel campaigns (email, SMS, calls)
- Engagement tracking
- Follow-up automation

**Example queries**:
- "Find leads that need follow-up"
- "Create a nurture campaign for first-time buyers"
- "Send an email to lead_123"

### Vendor Agent

**Purpose**: Vendor coordination and scheduling  
**LLM**: Groq (optimized for speed)  
**Capabilities**:
- Vendor discovery and vetting
- Quote comparison
- Service scheduling
- Performance tracking

**Example queries**:
- "I need a home inspector for 123 Main St"
- "Find a photographer available tomorrow"
- "Get quotes for kitchen remodel under $15K"

### MLS Agent

**Purpose**: Property search and market analysis  
**LLM**: GPT-4  
**Capabilities**:
- Property search via RealEstateAPI.com
- CMA (Comparative Market Analysis)
- Market statistics
- Property details

**Example queries**:
- "Find 3-bedroom homes in Beverly Hills under $600K"
- "What's the market like in downtown?"
- "Get property details for MLS #12345"

### Transaction Agent

**Purpose**: Transaction and contract management  
**LLM**: Claude  
**Capabilities**:
- Contract management
- Transaction tracking
- Closing coordination
- Document management

**Example queries**:
- "What's the status of 123 Oak St transaction?"
- "Create a purchase agreement"
- "When is my next closing?"

### Content Agent

**Purpose**: Content creation and social media  
**LLM**: Claude (creative writing)  
**Capabilities**:
- Social media posts
- Blog articles
- Email templates
- Property listing descriptions

**Example queries**:
- "Create an Instagram post about spring home buying"
- "Write a property description for this listing"
- "Generate a blog post about first-time buyers"

### Marketing Agent

**Purpose**: Advertising and lead generation  
**LLM**: GPT-4  
**Capabilities**:
- Ad campaign management
- Lead purchasing strategies
- ROI optimization
- Marketing analytics

**Example queries**:
- "How are my Facebook ads performing?"
- "Should I increase my Zillow budget?"
- "What's my cost per lead this month?"

## 🔧 Configuration

### Environment Variables

See `.env.example` for all available configuration options.

Key settings:

```bash
# LLM API Keys
ANTHROPIC_API_KEY=your-key
OPENAI_API_KEY=your-key
GROQ_API_KEY=your-key

# Memory & Integrations
MEM0_API_KEY=your-key
COMPOSIO_API_KEY=your-key
REALESTATE_API_KEY=your-key

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/ai_agent_platform

# Redis
REDIS_URL=redis://localhost:6379/0
```

## 🧪 Testing

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test
pytest backend/tests/test_agents.py -v
```

## 🐳 Docker

### Build Image

```bash
docker build -t ai-agent-platform .
```

### Run with Docker Compose

```bash
docker-compose up -d
```

### View Logs

```bash
docker-compose logs -f api
```

### Stop Services

```bash
docker-compose down
```

## 🔒 Security

- API keys are never hardcoded
- All passwords are hashed with bcrypt
- Input validation with Pydantic
- CORS configuration
- Rate limiting support
- SQL injection protection with SQLAlchemy

## 📊 Monitoring

- Health check endpoint: `/health`
- Structured logging with structlog
- Metrics collection support
- Sentry integration (optional)

## 🛠️ Development

### Code Quality

```bash
# Format code
black backend/

# Sort imports
isort backend/

# Type checking
mypy backend/

# Linting
flake8 backend/
```

### Adding a New Agent

1. Create agent file in `backend/agents/`
2. Inherit from `BaseAgent`
3. Implement required properties and methods
4. Register in `AgentCoordinator`
5. Add routing keywords
6. Write tests

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## 📝 License

[Your License Here]

## 🙏 Acknowledgments

- Anthropic Claude API
- OpenAI GPT-4 API
- Groq API
- Mem0 for persistent memory
- Composio for integrations
- FastAPI framework

## 📧 Support

For issues and questions:
- GitHub Issues: [link]
- Documentation: [link]
- Email: [email]

---

Built with ❤️ for real estate professionals
