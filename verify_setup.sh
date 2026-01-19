#!/bin/bash

# Verification script for BotConChat v1.1 deployment readiness

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "==================================================="
echo "  BotConChat v1.1 - Deployment Verification"
echo "==================================================="
echo ""

ERRORS=0
WARNINGS=0

# Check directory structure
echo -n "Checking directory structure... "
if [ -d "framework-assistant" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ framework-assistant directory not found${NC}"
    ((ERRORS++))
fi

# Check main app file
echo -n "Checking app.py... "
if [ -f "framework-assistant/app.py" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ app.py not found${NC}"
    ((ERRORS++))
fi

# Check requirements.txt
echo -n "Checking requirements.txt... "
if [ -f "framework-assistant/requirements.txt" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ requirements.txt not found${NC}"
    ((ERRORS++))
fi

# Check .env file
echo -n "Checking .env file... "
if [ -f "framework-assistant/.env" ]; then
    echo -e "${GREEN}✓${NC}"

    # Check if API key is set
    if grep -q "your-api-key-here" framework-assistant/.env 2>/dev/null; then
        echo -e "  ${YELLOW}⚠ Warning: OpenAI API key not configured (still showing placeholder)${NC}"
        ((WARNINGS++))
    fi
else
    echo -e "${YELLOW}⚠ .env file not found (will use .env.example)${NC}"
    ((WARNINGS++))
fi

# Check .env.example
echo -n "Checking .env.example... "
if [ -f "framework-assistant/.env.example" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠ .env.example not found${NC}"
    ((WARNINGS++))
fi

# Check database
echo -n "Checking frameworks.db... "
if [ -f "framework-assistant/frameworks.db" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠ frameworks.db not found${NC}"
    ((WARNINGS++))
fi

# Check run scripts
echo -n "Checking run.sh... "
if [ -f "run.sh" ] && [ -x "run.sh" ]; then
    echo -e "${GREEN}✓${NC}"
elif [ -f "run.sh" ]; then
    echo -e "${YELLOW}⚠ run.sh found but not executable${NC}"
    echo "  Run: chmod +x run.sh"
    ((WARNINGS++))
else
    echo -e "${RED}✗ run.sh not found${NC}"
    ((ERRORS++))
fi

echo -n "Checking setup.sh... "
if [ -f "setup.sh" ] && [ -x "setup.sh" ]; then
    echo -e "${GREEN}✓${NC}"
elif [ -f "setup.sh" ]; then
    echo -e "${YELLOW}⚠ setup.sh found but not executable${NC}"
    echo "  Run: chmod +x setup.sh"
    ((WARNINGS++))
else
    echo -e "${RED}✗ setup.sh not found${NC}"
    ((ERRORS++))
fi

# Check Python
echo -n "Checking Python... "
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✓ ($PYTHON_VERSION)${NC}"
else
    echo -e "${RED}✗ Python 3 not found${NC}"
    ((ERRORS++))
fi

# Check if dependencies are installed
echo -n "Checking Streamlit installation... "
if command -v streamlit &> /dev/null || [ -f "framework-assistant/venv/bin/streamlit" ] || [ -f "venv/bin/streamlit" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠ Streamlit not found (run setup.sh to install)${NC}"
    ((WARNINGS++))
fi

# Check documentation
echo -n "Checking documentation... "
DOC_COUNT=0
[ -f "DEPLOYMENT.md" ] && ((DOC_COUNT++))
[ -f "QUICKSTART.md" ] && ((DOC_COUNT++))
if [ $DOC_COUNT -gt 0 ]; then
    echo -e "${GREEN}✓ ($DOC_COUNT files)${NC}"
else
    echo -e "${YELLOW}⚠ No deployment documentation found${NC}"
    ((WARNINGS++))
fi

# Summary
echo ""
echo "==================================================="
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! Ready to deploy.${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Configure your API key in framework-assistant/.env"
    echo "  2. Run: ./run.sh"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ Ready with $WARNINGS warning(s)${NC}"
    echo ""
    echo "You can proceed, but please address the warnings above."
else
    echo -e "${RED}✗ Found $ERRORS error(s) and $WARNINGS warning(s)${NC}"
    echo ""
    echo "Please fix the errors before deploying."
    exit 1
fi
echo "==================================================="
