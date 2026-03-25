@echo off
REM ET AI Concierge - Demo Setup Script (Windows)
REM Run this before your presentation to ensure everything works

echo 🚀 ET AI Concierge Demo Setup
echo ================================

REM Check if we're in the right directory
if not exist "app.py" (
    echo ❌ Error: Please run this script from the et-concierge directory
    pause
    exit /b 1
)

echo 📁 Checking project structure...

REM Check required files
set "files=app.py .env requirements.txt concierge\agents.py data\product_catalog.json"
for %%f in (%files%) do (
    if exist "%%f" (
        echo ✅ %%f found
    ) else (
        echo ❌ %%f missing
        pause
        exit /b 1
    )
)

echo.
echo 🔧 Checking Python environment...

REM Check Python version
python --version
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo.
echo 📦 Installing/updating dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo 🔑 Checking environment variables...

REM Check .env file
if exist ".env" (
    findstr "GROQ_API_KEY" .env >nul
    if errorlevel 1 (
        echo ❌ GROQ_API_KEY not found in .env
        echo Please add your Groq API key to .env file
        pause
        exit /b 1
    ) else (
        echo ✅ GROQ_API_KEY found in .env
    )
) else (
    echo ❌ .env file not found
    pause
    exit /b 1
)

echo.
echo 🧪 Testing core components...

REM Test imports
python -c "import streamlit as st; from concierge.agents import ProfileAgent, NeedAgent, ProductAgent, OnboardingAgent; from concierge.llm import LLMWrapper; import json; print('✅ All imports successful')"
if errorlevel 1 (
    echo ❌ Import test failed
    pause
    exit /b 1
)

REM Test LLM connection
python -c "from concierge.llm import LLMWrapper; llm = LLMWrapper(); response = llm.generate('Test connection', max_tokens=10); print('✅ LLM connection successful')"
if errorlevel 1 (
    echo ❌ LLM connection failed
    pause
    exit /b 1
)

REM Test product catalog
python -c "import json; catalog = json.load(open('data/product_catalog.json', 'r')); print(f'✅ Product catalog loaded: {len(catalog)} products')"
if errorlevel 1 (
    echo ❌ Product catalog test failed
    pause
    exit /b 1
)

echo.
echo 📊 Demo data preparation...

REM Create demo scenarios file
(
echo {
echo   "cold_start": {
echo     "name": "Priya Sharma",
echo     "age": 28,
echo     "experience": "Beginner",
echo     "interest": "Stock Market",
echo     "goals": "Long-term investing",
echo     "risk_tolerance": "Conservative"
echo   },
echo   "re_engagement": {
echo     "name": "Rajesh Kumar",
echo     "age": 35,
echo     "experience": "Intermediate",
echo     "last_active": "6 months ago",
echo     "previous_interest": "Mutual Funds",
echo     "current_status": "Inactive"
echo   },
echo   "cross_sell": {
echo     "name": "Anita Patel",
echo     "age": 42,
echo     "experience": "Advanced",
echo     "current_products": ["Stock Trading"],
echo     "activity_level": "High",
echo     "portfolio_size": "Large"
echo   }
echo }
) > demo_scenarios.json

echo ✅ Demo scenarios created

echo.
echo 🎬 Pre-demo checklist:
echo ================================
echo ✅ All dependencies installed
echo ✅ Environment variables configured
echo ✅ Core components tested
echo ✅ Demo scenarios prepared
echo.
echo 🚀 Ready for demo! Run: streamlit run app.py
echo.
echo 📝 Demo Tips:
echo • Test all three scenarios before recording
echo • Check that ET URLs are working
echo • Verify analytics page loads correctly
echo • Practice smooth transitions between features
echo • Have backup scenarios ready
echo.
echo 🎥 For video recording:
echo • Close unnecessary applications
echo • Set screen resolution to 1920x1080
echo • Test audio levels
echo • Prepare intro/outro slides
echo.
echo Good luck with your presentation! 🍀
echo.
pause