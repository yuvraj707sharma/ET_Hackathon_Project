#!/bin/bash

# ET AI Concierge - Automated Setup Script
# This script sets up the complete development environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    if command_exists python3; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        REQUIRED_VERSION="3.8"
        
        if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
            print_success "Python $PYTHON_VERSION found (>= $REQUIRED_VERSION required)"
            return 0
        else
            print_error "Python $PYTHON_VERSION found, but >= $REQUIRED_VERSION required"
            return 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.8 or higher"
        return 1
    fi
}

# Function to create virtual environment
create_virtual_env() {
    print_status "Creating virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_success "Virtual environment activated"
    
    # Upgrade pip
    pip install --upgrade pip
    print_success "Pip upgraded to latest version"
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    # Install core dependencies
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Core dependencies installed"
    else
        print_error "requirements.txt not found"
        return 1
    fi
    
    # Ask user if they want enhanced features
    echo ""
    read -p "Do you want to install enhanced features (Phase 2/3 dependencies)? [y/N]: " install_enhanced
    
    if [[ $install_enhanced =~ ^[Yy]$ ]]; then
        if [ -f "requirements_enhanced.txt" ]; then
            pip install -r requirements_enhanced.txt
            print_success "Enhanced dependencies installed"
        else
            print_warning "requirements_enhanced.txt not found, skipping enhanced features"
        fi
    fi
}

# Function to setup environment variables
setup_environment() {
    print_status "Setting up environment variables..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Environment file created from template"
            print_warning "Please edit .env file with your API keys"
        else
            # Create basic .env file
            cat > .env << EOF
# ET AI Concierge Environment Configuration

# Core LLM Configuration
GROQ_API_KEY=
GROQ_MODEL=llama-3.1-8b-instant
GROQ_BASE_URL=https://api.groq.com/openai/v1

# Alternative LLM
OPENAI_API_KEY=

# Phase 2 Features
CLOUDFLARE_AI_API_KEY=
ET_API_KEY=
NSE_API_KEY=
BSE_API_KEY=

# Phase 3 Features
AZURE_SPEECH_KEY=
AZURE_SPEECH_REGION=centralindia
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
WHATSAPP_BUSINESS_NUMBER=

# Security Configuration
ENCRYPTION_KEY=
JWT_SECRET_KEY=
SECURITY_LEVEL=development
COMPLIANCE_MODE=basic

# Database Configuration
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://localhost:5432/et_concierge
MONGODB_URL=mongodb://localhost:27017/et_concierge

# Feature Flags
DEBUG_MODE=false
USE_MOCK_DATA=false
DEPLOYMENT_PHASE=phase_1

# UI Configuration
UI_THEME=light
ENABLE_ANIMATIONS=true
AUTO_REFRESH_INTERVAL=30

# Business Rules
MAX_INVESTMENT_AMOUNT=1000000
MIN_USER_AGE=18
MAX_USER_AGE=80
REQUIRE_RISK_ASSESSMENT=true
REQUIRE_KYC=false
DATA_RETENTION_DAYS=365
EOF
            print_success "Basic environment file created"
        fi
    else
        print_warning "Environment file already exists"
    fi
}

# Function to generate security keys
generate_security_keys() {
    print_status "Generating security keys..."
    
    # Generate encryption key
    ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
    
    # Generate JWT secret
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
    # Update .env file
    if [ -f ".env" ]; then
        # Use sed to update the keys (works on both Linux and macOS)
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s/ENCRYPTION_KEY=.*/ENCRYPTION_KEY=$ENCRYPTION_KEY/" .env
            sed -i '' "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$JWT_SECRET/" .env
        else
            # Linux
            sed -i "s/ENCRYPTION_KEY=.*/ENCRYPTION_KEY=$ENCRYPTION_KEY/" .env
            sed -i "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$JWT_SECRET/" .env
        fi
        print_success "Security keys generated and added to .env"
    fi
}

# Function to setup database (optional)
setup_database() {
    echo ""
    read -p "Do you want to setup local databases (Redis, PostgreSQL)? [y/N]: " setup_db
    
    if [[ $setup_db =~ ^[Yy]$ ]]; then
        print_status "Setting up databases..."
        
        # Check for Docker
        if command_exists docker && command_exists docker-compose; then
            print_status "Using Docker to setup databases..."
            
            # Create docker-compose.yml for databases
            cat > docker-compose.dev.yml << EOF
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: et_concierge
      POSTGRES_USER: et_user
      POSTGRES_PASSWORD: et_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  mongodb:
    image: mongo:6
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    environment:
      MONGO_INITDB_DATABASE: et_concierge

volumes:
  redis_data:
  postgres_data:
  mongodb_data:
EOF
            
            docker-compose -f docker-compose.dev.yml up -d
            print_success "Databases started with Docker"
            
        else
            print_warning "Docker not found. Please install databases manually or use Docker"
            print_status "Installation guides:"
            print_status "- Redis: https://redis.io/download"
            print_status "- PostgreSQL: https://www.postgresql.org/download/"
            print_status "- MongoDB: https://docs.mongodb.com/manual/installation/"
        fi
    fi
}

# Function to run tests
run_tests() {
    echo ""
    read -p "Do you want to run the test suite to verify installation? [y/N]: " run_test
    
    if [[ $run_test =~ ^[Yy]$ ]]; then
        print_status "Running test suite..."
        
        # Run basic tests
        if python3 features/testing_framework.py; then
            print_success "All tests passed! Installation verified."
        else
            print_warning "Some tests failed. Check the output above for details."
        fi
    fi
}

# Function to create desktop shortcut (optional)
create_shortcuts() {
    echo ""
    read -p "Do you want to create desktop shortcuts for easy access? [y/N]: " create_shortcut
    
    if [[ $create_shortcut =~ ^[Yy]$ ]]; then
        print_status "Creating shortcuts..."
        
        # Create run script
        cat > run_concierge.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
streamlit run app.py
EOF
        chmod +x run_concierge.sh
        
        # Create enhanced run script
        cat > run_concierge_enhanced.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
streamlit run app_enhanced.py
EOF
        chmod +x run_concierge_enhanced.sh
        
        print_success "Run scripts created (run_concierge.sh, run_concierge_enhanced.sh)"
    fi
}

# Function to display final instructions
display_final_instructions() {
    echo ""
    echo "=========================================="
    print_success "ET AI Concierge Setup Complete!"
    echo "=========================================="
    echo ""
    print_status "Next steps:"
    echo "1. Edit .env file with your API keys (especially GROQ_API_KEY for LLM features)"
    echo "2. Start the application:"
    echo "   ${GREEN}source venv/bin/activate${NC}"
    echo "   ${GREEN}streamlit run app.py${NC}"
    echo ""
    print_status "Alternative commands:"
    echo "• Basic version:    ${BLUE}streamlit run app.py${NC}"
    echo "• Enhanced version: ${BLUE}streamlit run app_enhanced.py${NC}"
    echo "• Run tests:        ${BLUE}python features/testing_framework.py${NC}"
    echo ""
    print_status "Access URLs:"
    echo "• Main app:         ${BLUE}http://localhost:8501${NC}"
    echo "• Analytics:        ${BLUE}http://localhost:8502${NC} (enhanced version)"
    echo ""
    print_status "Documentation:"
    echo "• README.md         - Complete setup guide"
    echo "• ARCHITECTURE.md   - System architecture"
    echo "• features/         - Future feature modules"
    echo ""
    print_warning "Remember to:"
    echo "• Keep your API keys secure"
    echo "• Review security settings for production"
    echo "• Check compliance settings if using for real advisory"
    echo ""
}

# Main setup function
main() {
    echo "=========================================="
    echo "  ET AI Concierge - Automated Setup"
    echo "=========================================="
    echo ""
    
    # Check prerequisites
    print_status "Checking prerequisites..."
    
    if ! check_python_version; then
        exit 1
    fi
    
    if ! command_exists git; then
        print_error "Git not found. Please install Git first."
        exit 1
    fi
    
    # Setup steps
    create_virtual_env
    install_dependencies
    setup_environment
    generate_security_keys
    setup_database
    run_tests
    create_shortcuts
    display_final_instructions
    
    print_success "Setup completed successfully! 🎉"
}

# Run main function
main "$@"