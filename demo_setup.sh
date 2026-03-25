#!/bin/bash
# ET AI Concierge - Demo Setup Script
# Run this before your presentation to ensure everything works

echo "🚀 ET AI Concierge Demo Setup"
echo "================================"

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the et-concierge directory"
    exit 1
fi

echo "📁 Checking project structure..."

# Check required files
required_files=("app.py" ".env" "requirements.txt" "concierge/agents.py" "data/product_catalog.json")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file found"
    else
        echo "❌ $file missing"
        exit 1
    fi
done

echo ""
echo "🔧 Checking Python environment..."

# Check Python version
python_version=$(python --version 2>&1)
echo "Python version: $python_version"

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment active: $VIRTUAL_ENV"
else
    echo "⚠️  No virtual environment detected. Consider using one."
fi

echo ""
echo "📦 Installing/updating dependencies..."
pip install -r requirements.txt

echo ""
echo "🔑 Checking environment variables..."

# Check .env file
if [ -f ".env" ]; then
    if grep -q "GROQ_API_KEY" .env; then
        echo "✅ GROQ_API_KEY found in .env"
    else
        echo "❌ GROQ_API_KEY not found in .env"
        echo "Please add your Groq API key to .env file"
        exit 1
    fi
else
    echo "❌ .env file not found"
    exit 1
fi

echo ""
echo "🧪 Testing core components..."

# Test imports
python -c "
import streamlit as st
from concierge.agents import ProfileAgent, NeedAgent, ProductAgent, OnboardingAgent
from concierge.llm import LLMWrapper
import json
print('✅ All imports successful')
"

# Test LLM connection
python -c "
from concierge.llm import LLMWrapper
try:
    llm = LLMWrapper()
    response = llm.generate('Test connection', max_tokens=10)
    print('✅ LLM connection successful')
except Exception as e:
    print(f'❌ LLM connection failed: {e}')
    exit(1)
"

# Test product catalog
python -c "
import json
with open('data/product_catalog.json', 'r') as f:
    catalog = json.load(f)
print(f'✅ Product catalog loaded: {len(catalog)} products')
"

echo ""
echo "🌐 Testing Streamlit app..."

# Start Streamlit in background for testing
streamlit run app.py --server.headless true --server.port 8502 &
STREAMLIT_PID=$!

# Wait for app to start
sleep 5

# Test if app is running
if curl -s http://localhost:8502 > /dev/null; then
    echo "✅ Streamlit app running successfully"
    kill $STREAMLIT_PID
else
    echo "❌ Streamlit app failed to start"
    kill $STREAMLIT_PID 2>/dev/null
    exit 1
fi

echo ""
echo "📊 Demo data preparation..."

# Create demo scenarios file
cat > demo_scenarios.json << EOF
{
  "cold_start": {
    "name": "Priya Sharma",
    "age": 28,
    "experience": "Beginner",
    "interest": "Stock Market",
    "goals": "Long-term investing",
    "risk_tolerance": "Conservative"
  },
  "re_engagement": {
    "name": "Rajesh Kumar",
    "age": 35,
    "experience": "Intermediate",
    "last_active": "6 months ago",
    "previous_interest": "Mutual Funds",
    "current_status": "Inactive"
  },
  "cross_sell": {
    "name": "Anita Patel",
    "age": 42,
    "experience": "Advanced",
    "current_products": ["Stock Trading"],
    "activity_level": "High",
    "portfolio_size": "Large"
  }
}
EOF

echo "✅ Demo scenarios created"

echo ""
echo "🎬 Pre-demo checklist:"
echo "================================"
echo "✅ All dependencies installed"
echo "✅ Environment variables configured"
echo "✅ Core components tested"
echo "✅ Streamlit app verified"
echo "✅ Demo scenarios prepared"
echo ""
echo "🚀 Ready for demo! Run: streamlit run app.py"
echo ""
echo "📝 Demo Tips:"
echo "• Test all three scenarios before recording"
echo "• Check that ET URLs are working"
echo "• Verify analytics page loads correctly"
echo "• Practice smooth transitions between features"
echo "• Have backup scenarios ready"
echo ""
echo "🎥 For video recording:"
echo "• Close unnecessary applications"
echo "• Set screen resolution to 1920x1080"
echo "• Test audio levels"
echo "• Prepare intro/outro slides"
echo ""
echo "Good luck with your presentation! 🍀"