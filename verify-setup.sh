#!/bin/bash

echo "🔍 AI Agent Platform - Setup Verification"
echo "=========================================="
echo ""

# Count Python files
PY_FILES=$(find backend -name "*.py" | wc -l)
echo "✅ Python files: $PY_FILES"

# Check key files
echo ""
echo "📁 Key Files:"
[ -f "backend/main.py" ] && echo "  ✅ main.py (FastAPI app)"
[ -f "backend/config.py" ] && echo "  ✅ config.py (Configuration)"
[ -f "backend/dependencies.py" ] && echo "  ✅ dependencies.py (DI)"
[ -f "Dockerfile" ] && echo "  ✅ Dockerfile"
[ -f "docker-compose.yml" ] && echo "  ✅ docker-compose.yml"
[ -f "requirements.txt" ] && echo "  ✅ requirements.txt"
[ -f ".env.example" ] && echo "  ✅ .env.example"

echo ""
echo "🤖 Agents:"
for agent in growth outreach vendor mls transaction content marketing; do
    [ -f "backend/agents/${agent}_agent.py" ] && echo "  ✅ ${agent}_agent.py"
done

echo ""
echo "📦 Modules:"
[ -d "backend/agents" ] && echo "  ✅ agents/"
[ -d "backend/coordinator" ] && echo "  ✅ coordinator/"
[ -d "backend/memory" ] && echo "  ✅ memory/"
[ -d "backend/integrations" ] && echo "  ✅ integrations/"
[ -d "backend/models" ] && echo "  ✅ models/"
[ -d "backend/services" ] && echo "  ✅ services/"
[ -d "backend/utils" ] && echo "  ✅ utils/"
[ -d "backend/tests" ] && echo "  ✅ tests/"

echo ""
echo "📚 Documentation:"
[ -f "README.md" ] && echo "  ✅ README.md"
[ -f "PROJECT_SUMMARY.md" ] && echo "  ✅ PROJECT_SUMMARY.md"
[ -f "quick-start.sh" ] && echo "  ✅ quick-start.sh"

echo ""
echo "🎉 Setup verification complete!"
echo ""
echo "Next steps:"
echo "  1. cp .env.example .env"
echo "  2. Add your API keys to .env"
echo "  3. ./quick-start.sh"
