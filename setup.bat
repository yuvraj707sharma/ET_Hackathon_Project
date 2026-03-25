@echo off
REM ET AI Concierge - Windows Setup Script
REM This script sets up the complete development environment on Windows

setlocal enabledelayedexpansion

REM Colors for output (Windows 10+)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

echo ==========================================
echo   ET AI Concierge - Windows Setup
echo ==========================================
echo.

REM Check Python installation
echo %BLUE%[INFO]%NC% Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Python not found. Please install Python 3.8 or higher
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo %GREEN%[SUCCESS]%NC% Python %PYTHON_VERSION% found

REM Check if virtual environment exists
if not exist "venv" (
    echo %BLUE%[INFO]%NC% Creating virtual environment...
    python -m venv venv
    echo %GREEN%[SUCCESS]%NC% Virtual environment created
) else (
    echo %YELLOW%[WARNING]%NC% Virtual environment already exists
)

REM Activate virtual environment
echo %BLUE%[INFO]%NC% Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo %BLUE%[INFO]%NC% Upgrading pip...
python -m pip install --upgrade pip
echo %GREEN%[SUCCESS]%NC% Pip upgraded

REM Install core dependencies
echo %BLUE%[INFO]%NC% Installing core dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo %GREEN%[SUCCESS]%NC% Core dependencies installed
) else (
    echo %RED%[ERROR]%NC% requirements.txt not found
    pause
    exit /b 1
)

REM Ask for enhanced features
echo.
set /p "install_enhanced=Do you want to install enhanced features (Phase 2/3 dependencies)? [y/N]: "
if /i "%install_enhanced%"=="y" (
    if exist "requirements_enhanced.txt" (
        echo %BLUE%[INFO]%NC% Installing enhanced dependencies...
        pip install -r requirements_enhanced.txt
        echo %GREEN%[SUCCESS]%NC% Enhanced dependencies installed
    ) else (
        echo %YELLOW%[WARNING]%NC% requirements_enhanced.txt not found, skipping enhanced features
    )
)

REM Setup environment variables
echo %BLUE%[INFO]%NC% Setting up environment variables...
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo %GREEN%[SUCCESS]%NC% Environment file created from template
        echo %YELLOW%[WARNING]%NC% Please edit .env file with your API keys
    ) else (
        REM Create basic .env file
        (
            echo # ET AI Concierge Environment Configuration
            echo.
            echo # Core LLM Configuration
            echo GROQ_API_KEY=
            echo GROQ_MODEL=llama-3.1-8b-instant
            echo GROQ_BASE_URL=https://api.groq.com/openai/v1
            echo.
            echo # Alternative LLM
            echo OPENAI_API_KEY=
            echo.
            echo # Phase 2 Features
            echo CLOUDFLARE_AI_API_KEY=
            echo ET_API_KEY=
            echo NSE_API_KEY=
            echo BSE_API_KEY=
            echo.
            echo # Phase 3 Features
            echo AZURE_SPEECH_KEY=
            echo AZURE_SPEECH_REGION=centralindia
            echo TWILIO_ACCOUNT_SID=
            echo TWILIO_AUTH_TOKEN=
            echo WHATSAPP_BUSINESS_NUMBER=
            echo.
            echo # Security Configuration
            echo ENCRYPTION_KEY=
            echo JWT_SECRET_KEY=
            echo SECURITY_LEVEL=development
            echo COMPLIANCE_MODE=basic
            echo.
            echo # Database Configuration
            echo REDIS_URL=redis://localhost:6379
            echo DATABASE_URL=postgresql://localhost:5432/et_concierge
            echo MONGODB_URL=mongodb://localhost:27017/et_concierge
            echo.
            echo # Feature Flags
            echo DEBUG_MODE=false
            echo USE_MOCK_DATA=false
            echo DEPLOYMENT_PHASE=phase_1
            echo.
            echo # UI Configuration
            echo UI_THEME=light
            echo ENABLE_ANIMATIONS=true
            echo AUTO_REFRESH_INTERVAL=30
            echo.
            echo # Business Rules
            echo MAX_INVESTMENT_AMOUNT=1000000
            echo MIN_USER_AGE=18
            echo MAX_USER_AGE=80
            echo REQUIRE_RISK_ASSESSMENT=true
            echo REQUIRE_KYC=false
            echo DATA_RETENTION_DAYS=365
        ) > .env
        echo %GREEN%[SUCCESS]%NC% Basic environment file created
    )
) else (
    echo %YELLOW%[WARNING]%NC% Environment file already exists
)

REM Generate security keys
echo %BLUE%[INFO]%NC% Generating security keys...
for /f %%i in ('python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"') do set ENCRYPTION_KEY=%%i
for /f %%i in ('python -c "import secrets; print(secrets.token_urlsafe(32))"') do set JWT_SECRET=%%i

REM Update .env file with keys (simple replacement)
powershell -Command "(Get-Content .env) -replace 'ENCRYPTION_KEY=.*', 'ENCRYPTION_KEY=%ENCRYPTION_KEY%' | Set-Content .env"
powershell -Command "(Get-Content .env) -replace 'JWT_SECRET_KEY=.*', 'JWT_SECRET_KEY=%JWT_SECRET%' | Set-Content .env"
echo %GREEN%[SUCCESS]%NC% Security keys generated and added to .env

REM Ask about database setup
echo.
set /p "setup_db=Do you want to setup local databases with Docker? [y/N]: "
if /i "%setup_db%"=="y" (
    REM Check for Docker
    docker --version >nul 2>&1
    if errorlevel 1 (
        echo %YELLOW%[WARNING]%NC% Docker not found. Please install Docker Desktop for Windows
        echo Download from: https://www.docker.com/products/docker-desktop
    ) else (
        echo %BLUE%[INFO]%NC% Creating Docker Compose file for databases...
        (
            echo version: '3.8'
            echo services:
            echo   redis:
            echo     image: redis:7-alpine
            echo     ports:
            echo       - "6379:6379"
            echo     volumes:
            echo       - redis_data:/data
            echo     command: redis-server --appendonly yes
            echo.
            echo   postgres:
            echo     image: postgres:15-alpine
            echo     environment:
            echo       POSTGRES_DB: et_concierge
            echo       POSTGRES_USER: et_user
            echo       POSTGRES_PASSWORD: et_password
            echo     ports:
            echo       - "5432:5432"
            echo     volumes:
            echo       - postgres_data:/var/lib/postgresql/data
            echo.
            echo   mongodb:
            echo     image: mongo:6
            echo     ports:
            echo       - "27017:27017"
            echo     volumes:
            echo       - mongodb_data:/data/db
            echo     environment:
            echo       MONGO_INITDB_DATABASE: et_concierge
            echo.
            echo volumes:
            echo   redis_data:
            echo   postgres_data:
            echo   mongodb_data:
        ) > docker-compose.dev.yml
        
        docker-compose -f docker-compose.dev.yml up -d
        echo %GREEN%[SUCCESS]%NC% Databases started with Docker
    )
)

REM Ask about running tests
echo.
set /p "run_tests=Do you want to run the test suite to verify installation? [y/N]: "
if /i "%run_tests%"=="y" (
    echo %BLUE%[INFO]%NC% Running test suite...
    python features\testing_framework.py
    if errorlevel 1 (
        echo %YELLOW%[WARNING]%NC% Some tests failed. Check the output above for details.
    ) else (
        echo %GREEN%[SUCCESS]%NC% All tests passed! Installation verified.
    )
)

REM Create run scripts
echo.
set /p "create_shortcuts=Do you want to create run scripts for easy access? [y/N]: "
if /i "%create_shortcuts%"=="y" (
    echo %BLUE%[INFO]%NC% Creating run scripts...
    
    REM Create basic run script
    (
        echo @echo off
        echo cd /d "%%~dp0"
        echo call venv\Scripts\activate.bat
        echo streamlit run app.py
        echo pause
    ) > run_concierge.bat
    
    REM Create enhanced run script
    (
        echo @echo off
        echo cd /d "%%~dp0"
        echo call venv\Scripts\activate.bat
        echo streamlit run app_enhanced.py
        echo pause
    ) > run_concierge_enhanced.bat
    
    echo %GREEN%[SUCCESS]%NC% Run scripts created (run_concierge.bat, run_concierge_enhanced.bat)
)

REM Display final instructions
echo.
echo ==========================================
echo %GREEN%[SUCCESS]%NC% ET AI Concierge Setup Complete!
echo ==========================================
echo.
echo %BLUE%[INFO]%NC% Next steps:
echo 1. Edit .env file with your API keys (especially GROQ_API_KEY for LLM features)
echo 2. Start the application:
echo    %GREEN%venv\Scripts\activate.bat%NC%
echo    %GREEN%streamlit run app.py%NC%
echo.
echo %BLUE%[INFO]%NC% Alternative commands:
echo • Basic version:    %BLUE%streamlit run app.py%NC%
echo • Enhanced version: %BLUE%streamlit run app_enhanced.py%NC%
echo • Run tests:        %BLUE%python features\testing_framework.py%NC%
echo.
echo %BLUE%[INFO]%NC% Access URLs:
echo • Main app:         %BLUE%http://localhost:8501%NC%
echo • Analytics:        %BLUE%http://localhost:8502%NC% (enhanced version)
echo.
echo %BLUE%[INFO]%NC% Documentation:
echo • README.md         - Complete setup guide
echo • ARCHITECTURE.md   - System architecture
echo • features\         - Future feature modules
echo.
echo %YELLOW%[WARNING]%NC% Remember to:
echo • Keep your API keys secure
echo • Review security settings for production
echo • Check compliance settings if using for real advisory
echo.
echo %GREEN%[SUCCESS]%NC% Setup completed successfully! 🎉
echo.
pause