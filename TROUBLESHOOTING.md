# Quick Troubleshooting Guide

## Most Common Issues & Solutions

### 1. ModuleNotFoundError (plotly, pandas, etc.)
```bash
# Activate virtual environment first
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# Install missing packages
pip install -r requirements.txt
```

### 2. Streamlit command not found
```bash
# Use python -m instead
python -m streamlit run app.py
```

### 3. Port already in use
```bash
# Use different port
streamlit run app.py --server.port 8502
```

### 4. Virtual environment not activated
```bash
# Check for (venv) in terminal prompt
# If missing, activate:
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS
```

### 5. API key issues
```bash
# Check .env file exists and has GROQ_API_KEY
# Get free API key from: https://console.groq.com/
```

## Quick Fix Commands
```bash
# Reinstall everything
pip install -r requirements.txt

# Test imports
python -c "import streamlit, plotly, pandas; print('OK')"

# Run with different port
python -m streamlit run app.py --server.port 8502
```

For detailed troubleshooting, see README.md section "🚨 Troubleshooting"