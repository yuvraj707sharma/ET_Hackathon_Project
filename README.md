# ET AI Concierge - Autonomous Multi-Agent Customer Journey Orchestration

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Track 7 Submission** — ET AI Hackathon 2026  
> *Transforming Financial Literacy Through Intelligent Agent Orchestration*

## 🚀 Overview

ET AI Concierge is a revolutionary autonomous multi-agent system that orchestrates personalized customer journeys across Economic Times' entire ecosystem. Using a hybrid approach of deterministic logic and LLM enhancement, it delivers transparent, reliable, and contextually intelligent financial guidance.

### 🎯 Key Features

- **4-Agent Pipeline**: Profile → Need → Product → Onboarding orchestration
- **Real ET Integration**: Live URLs to ET Masterclass, ET Money, ET Prime content
- **Complete Transparency**: Full audit trails for every decision
- **Scenario Coverage**: Cold-start, Re-engagement, Cross-sell journeys
- **Market Intelligence**: Real-time data integration (Phase 2)
- **Multi-language Support**: Hindi, regional languages (Phase 3)

## 🏗️ Architecture

```
User Input → Profile Agent → Need Agent → Product Agent → Onboarding Agent → Personalized Journey
     ↓              ↓            ↓             ↓               ↓
  User Data    Segmentation   Intent      Recommendations   Action Plan
                              Detection
```

### Core Components

- **Deterministic Core**: Rule-based reliability for consistent performance
- **LLM Enhancement**: Groq API for natural language processing and tone
- **ET Content Catalog**: Real product database with working URLs
- **Analytics Engine**: Journey tracking and performance metrics

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment (recommended)

### Quick Start

**Option 1: Automated Setup (Recommended)**

```bash
# Linux/macOS
chmod +x setup.sh
./setup.sh

# Windows
setup.bat
```

The setup script will:
- Check Python version and dependencies
- Create virtual environment
- Install all required packages
- Setup environment variables
- Generate security keys
- Optionally setup databases with Docker
- Run tests to verify installation
- Create run scripts for easy access

**Option 2: Manual Setup**

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd et-concierge
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your API keys
   # Required for LLM enhancement (optional for basic demo)
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=llama-3.1-8b-instant
   GROQ_BASE_URL=https://api.groq.com/openai/v1
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Access the demo**
   - Open your browser to `http://localhost:8501`
   - Try the three demo scenarios: Cold-start, Re-engagement, Cross-sell

### Advanced Setup (Development)

For development with enhanced features:

```bash
# Install development dependencies
pip install -r requirements_enhanced.txt

# Run enhanced version with analytics
streamlit run app_enhanced.py

# Run analytics dashboard (separate terminal)
streamlit run analytics_dashboard.py --server.port 8502

# Run comprehensive tests
python features/testing_framework.py

# Or use pytest
pytest features/testing_framework.py -v
```

### Security Setup (Production)

For production deployment with security features:

```bash
# Generate encryption keys
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Set additional environment variables
ENCRYPTION_KEY=your_generated_encryption_key
JWT_SECRET_KEY=your_jwt_secret_key
SECURITY_LEVEL=production

# Enable security features in config.py
SECURITY_ENABLED=true
COMPLIANCE_MODE=sebi_compliant
```

## 📁 Project Structure

```
et-concierge/
├── concierge/                 # Core agent system
│   ├── __init__.py
│   ├── agents.py             # 4-agent pipeline implementation
│   ├── catalog.py            # ET product catalog management
│   ├── llm.py               # LLM integration (Groq/OpenAI)
│   ├── models.py            # Data models and schemas
│   └── scenarios.py         # Scenario pack implementations
├── data/
│   └── product_catalog.json  # Real ET content with URLs
├── features/                 # Future feature modules
│   ├── analytics.py         # Advanced analytics engine
│   ├── cloudflare_ai.py     # Cloudflare AI integration (Phase 2)
│   ├── compliance.py        # SEBI compliance and regulatory (Phase 4)
│   ├── market_integration.py # Real-time market data (Phase 2)
│   ├── multilingual.py      # Multi-language support (Phase 3)
│   ├── personalization.py   # Advanced personalization engine
│   ├── security.py          # Authentication, authorization, encryption
│   ├── testing_framework.py # Comprehensive testing suite
│   ├── voice_interface.py   # Voice interaction (Phase 3)
│   └── whatsapp_bot.py      # WhatsApp integration (Phase 3)
├── tests/                   # Test suite
│   ├── test_agents.py
│   ├── test_scenarios.py
│   └── test_integration.py
├── docs/                    # Documentation
│   ├── API.md
│   ├── ARCHITECTURE.md
│   └── DEPLOYMENT.md
├── .env.example             # Environment variables template
├── .gitignore              # Git ignore rules
├── app.py                   # Main Streamlit application
├── app_enhanced.py          # Enhanced version with Phase 2 features
├── requirements.txt         # Core dependencies
├── requirements_enhanced.txt # Enhanced dependencies
├── setup.sh                # Automated setup script (Linux/macOS)
├── setup.bat               # Automated setup script (Windows)
├── Dockerfile              # Container deployment
├── docker-compose.yml      # Multi-service deployment
└── README.md               # This file
```

## 🎮 Demo Scenarios

### 1. Cold-Start Journey
**User**: Priya Sharma, 28, Software Engineer, Investment Beginner
- **Profile Agent**: Identifies "Tech-savvy Conservative Beginner"
- **Need Agent**: Detects "SIP investments" and "tax saving" needs
- **Product Agent**: Recommends ET Money SIP + ET Masterclass basics
- **Onboarding**: 4-week learning path with ET Prime articles

### 2. Re-engagement Journey
**User**: Rajesh Kumar, 35, Dormant ET Prime subscriber
- **Profile Agent**: "Dormant Intermediate Investor" classification
- **Need Agent**: Identifies "Market update anxiety" and "Portfolio review"
- **Product Agent**: Latest ET Prime outlook + portfolio analysis
- **Onboarding**: Gentle re-entry with market summary

### 3. Cross-sell Journey
**User**: Anita Patel, 42, Active ET Markets user
- **Profile Agent**: "Advanced Active Trader" with high engagement
- **Need Agent**: Discovers "Portfolio diversification" opportunities
- **Product Agent**: ET Prime derivatives + advanced tools
- **Onboarding**: Premium trial + expert consultation

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GROQ_API_KEY` | Groq API key for LLM enhancement | No | None |
| `GROQ_MODEL` | Groq model name | No | llama-3.1-8b-instant |
| `GROQ_BASE_URL` | Groq API base URL | No | https://api.groq.com/openai/v1 |
| `OPENAI_API_KEY` | OpenAI API key (alternative to Groq) | No | None |
| `ET_API_KEY` | ET content API key (future) | No | None |
| `CLOUDFLARE_AI_API_KEY` | Cloudflare AI API key (Phase 2) | No | None |
| `ENCRYPTION_KEY` | Data encryption key (production) | No | None |
| `JWT_SECRET_KEY` | JWT token secret key | No | None |
| `SECURITY_LEVEL` | Security level (development/production) | No | development |
| `COMPLIANCE_MODE` | Compliance mode (basic/sebi_compliant) | No | basic |

### Feature Flags

Enable/disable features in `config.py`:

```python
FEATURES = {
    'llm_enhancement': True,      # Enable LLM-powered responses
    'analytics_tracking': True,   # Enable user journey analytics
    'security_features': True,    # Enable authentication & encryption
    'compliance_checking': True,  # Enable SEBI compliance checks
    'market_integration': False,  # Real-time market data (Phase 2)
    'voice_interface': False,     # Voice interaction (Phase 3)
    'multilingual': False,        # Multi-language support (Phase 3)
}
```

## 🚨 Troubleshooting

### Common Setup Issues

#### 1. **ModuleNotFoundError: No module named 'plotly'** (or other modules)

**Problem**: Missing dependencies not installed in virtual environment

**Solution**:
```bash
# Activate virtual environment first
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Install missing package
pip install plotly

# Or reinstall all requirements
pip install -r requirements.txt

# For enhanced features
pip install -r requirements_enhanced.txt
```

**Prevention**: Always use the automated setup scripts which handle all dependencies.

#### 2. **Virtual Environment Issues**

**Problem**: Commands not working or packages not found

**Solution**:
```bash
# Check if virtual environment is activated
# You should see (venv) in your terminal prompt

# If not activated:
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Verify Python is using virtual environment
which python  # Linux/macOS
where python   # Windows
```

#### 3. **Streamlit Not Starting**

**Problem**: `streamlit: command not found` or similar errors

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install streamlit if missing
pip install streamlit

# Try running with python -m
python -m streamlit run app.py
```

#### 4. **Port Already in Use**

**Problem**: `Port 8501 is already in use`

**Solution**:
```bash
# Use a different port
streamlit run app.py --server.port 8502

# Or kill existing streamlit processes
# Windows
taskkill /f /im streamlit.exe
# Linux/macOS
pkill -f streamlit
```

#### 5. **API Key Issues**

**Problem**: LLM features not working or API errors

**Solution**:
```bash
# Check if .env file exists and has API keys
cat .env  # Linux/macOS
type .env # Windows

# Ensure GROQ_API_KEY is set (get from https://console.groq.com/)
GROQ_API_KEY=your_actual_api_key_here

# Test API connection
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key loaded:', bool(os.getenv('GROQ_API_KEY')))"
```

#### 6. **Import Errors from Custom Modules**

**Problem**: `ModuleNotFoundError: No module named 'concierge'`

**Solution**:
```bash
# Ensure you're in the project root directory
cd et-concierge

# Add current directory to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Linux/macOS
set PYTHONPATH=%PYTHONPATH%;%CD%          # Windows

# Or run from project root
python -m streamlit run app.py
```

#### 7. **Database Connection Issues**

**Problem**: Redis/PostgreSQL connection errors

**Solution**:
```bash
# Check if databases are running (if using Docker)
docker-compose -f docker-compose.dev.yml ps

# Start databases if stopped
docker-compose -f docker-compose.dev.yml up -d

# Or disable database features temporarily
# In .env file:
USE_MOCK_DATA=true
DEBUG_MODE=true
```

#### 8. **Permission Errors**

**Problem**: Permission denied errors on Linux/macOS

**Solution**:
```bash
# Make setup script executable
chmod +x setup.sh

# Fix file permissions
chmod -R 755 .

# Run with proper permissions
sudo ./setup.sh  # Only if necessary
```

#### 9. **Python Version Issues**

**Problem**: Compatibility errors or features not working

**Solution**:
```bash
# Check Python version
python --version

# Ensure Python 3.8+ is installed
# If using older version, install Python 3.8+
# Then recreate virtual environment
rm -rf venv  # Linux/macOS
rmdir /s venv  # Windows

python3.8 -m venv venv  # Use specific version
```

#### 10. **Memory/Performance Issues**

**Problem**: App running slowly or crashing

**Solution**:
```bash
# Increase memory limit
streamlit run app.py --server.maxUploadSize 200

# Disable heavy features temporarily
# In .env:
USE_MOCK_DATA=true
ENABLE_ANIMATIONS=false

# Monitor resource usage
top  # Linux/macOS
Task Manager  # Windows
```

### Quick Diagnostic Commands

```bash
# Check Python and pip versions
python --version && pip --version

# Verify virtual environment
which python && which pip

# List installed packages
pip list

# Test core imports
python -c "import streamlit, plotly, pandas, numpy; print('Core packages OK')"

# Test application imports
python -c "from concierge.agents import ConciergeOrchestrator; print('App imports OK')"

# Check environment variables
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Env loaded:', bool(os.getenv('GROQ_API_KEY')))"
```

### Getting Help

If you're still experiencing issues:

1. **Check the logs**: Look for error messages in the terminal
2. **Use automated setup**: Run `setup.sh` (Linux/macOS) or `setup.bat` (Windows)
3. **Clean installation**: Delete `venv` folder and start fresh
4. **Check system requirements**: Ensure Python 3.8+, sufficient RAM (4GB+)
5. **Report issues**: Create a GitHub issue with error details and system info

### System Requirements

- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **OS**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Network**: Internet connection for API calls and package installation

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests with custom framework
python features/testing_framework.py

# Run specific test categories with pytest
python -m pytest features/testing_framework.py::test_agent_functionality -v
python -m pytest features/testing_framework.py::test_security -v
python -m pytest features/testing_framework.py::test_performance -v

# Run with coverage
python -m pytest features/testing_framework.py --cov=concierge --cov-report=html

# Run security-specific tests
python -c "from features.testing_framework import SecurityTestSuite; SecurityTestSuite().test_authentication()"

# Run performance benchmarks
python -c "from features.testing_framework import PerformanceTestSuite; PerformanceTestSuite().test_response_time()"
```

### Test Categories

- **Agent Tests**: Individual agent functionality
- **Scenario Tests**: Complete user journey scenarios
- **Integration Tests**: End-to-end system integration
- **Performance Tests**: Response time and concurrent user handling
- **Security Tests**: Authentication, input validation, and data protection
- **Compliance Tests**: SEBI regulatory compliance validation

## 🚀 Deployment

### Docker Deployment

```bash
# Build the image
docker build -t et-ai-concierge .

# Run the container
docker run -p 8501:8501 --env-file .env et-ai-concierge

# Or use docker-compose for full stack
docker-compose up -d
```

### Cloud Deployment

#### Streamlit Cloud
1. Fork this repository
2. Connect to Streamlit Cloud
3. Add environment variables in Streamlit Cloud settings
4. Deploy automatically

#### AWS/GCP/Azure
See `docs/DEPLOYMENT.md` for detailed cloud deployment instructions.

## 📊 Analytics & Monitoring

### Built-in Analytics
- User journey completion rates
- Agent decision accuracy
- Content engagement metrics
- Conversion tracking

### Monitoring Dashboard
Access at `http://localhost:8502` when running enhanced version:
- Real-time user sessions
- Agent performance metrics
- Business impact visualization
- System health monitoring

## 🔮 Future Roadmap

### Phase 2: Intelligence Enhancement (Q2 2026)
- **Cloudflare AI Integration**: Real-time market data scraping
- **Advanced Personalization**: ML-powered user modeling
- **Market Intelligence**: Live sentiment analysis

### Phase 3: Multi-modal Experience (Q3 2026)
- **Voice Interface**: Hindi and regional language support
- **WhatsApp Integration**: Business API for mobile users
- **Mobile App**: Progressive web app with offline support

### Phase 4: Autonomous Advisory (Q4 2026)
- **SEBI Compliance**: Regulatory-approved recommendations with full compliance engine
- **Portfolio Management**: Automated rebalancing with risk management
- **Enterprise Security**: Advanced authentication, encryption, and audit trails
- **Enterprise Integration**: CRM and marketing automation with SSO

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `python -m pytest`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

- **GitHub**: [Repository](https://github.com/your-repo)

## 🙏 Acknowledgments

- **Economic Times** for the comprehensive content ecosystem
- **Groq** for lightning-fast LLM inference
- **Streamlit** for the amazing web framework
- **Cloudflare** for next-generation AI capabilities

---

**Built with ❤️ for India's Financial Literacy Revolution**

*Transforming how 1.4 billion Indians learn about and invest in financial markets*