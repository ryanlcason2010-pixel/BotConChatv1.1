#!/bin/bash

# BotConChat v1.1 - Run Script
# This script launches the Framework Assistant application

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}  BotConChat v1.1 - Framework Assistant${NC}"
echo -e "${GREEN}==================================================${NC}"
echo ""

# Check if we're in the right directory
if [ ! -d "framework-assistant" ]; then
    echo -e "${RED}Error: framework-assistant directory not found!${NC}"
    echo -e "${RED}Please run this script from the BotConChatv1.1 root directory.${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f "framework-assistant/.env" ]; then
    echo -e "${YELLOW}Warning: .env file not found!${NC}"
    echo -e "${YELLOW}Please copy .env.example to .env and add your OpenAI API key:${NC}"
    echo -e "${YELLOW}  cd framework-assistant${NC}"
    echo -e "${YELLOW}  cp .env.example .env${NC}"
    echo -e "${YELLOW}  # Edit .env and add your OPENAI_API_KEY${NC}"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Try to activate virtual environment
VENV_ACTIVATED=false

if [ -d "framework-assistant/venv/bin" ]; then
    echo -e "${GREEN}Activating virtual environment (framework-assistant/venv)...${NC}"
    source framework-assistant/venv/bin/activate
    VENV_ACTIVATED=true
elif [ -d "venv/bin" ]; then
    echo -e "${GREEN}Activating virtual environment (venv)...${NC}"
    source venv/bin/activate
    VENV_ACTIVATED=true
else
    echo -e "${YELLOW}Warning: No virtual environment found!${NC}"
    echo -e "${YELLOW}Using system Python. Run setup.sh to create a virtual environment.${NC}"
    echo ""
fi

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo -e "${RED}Error: Streamlit is not installed!${NC}"
    echo -e "${RED}Please run setup.sh first to install dependencies.${NC}"
    exit 1
fi

# Check if database exists
if [ ! -f "framework-assistant/frameworks.db" ]; then
    echo -e "${YELLOW}Warning: frameworks.db not found!${NC}"
    echo -e "${YELLOW}The application may not work correctly without the database.${NC}"
    echo ""
fi

echo -e "${GREEN}Starting Framework Assistant...${NC}"
echo -e "${GREEN}The application will open in your browser shortly.${NC}"
echo -e "${GREEN}Press Ctrl+C to stop the server.${NC}"
echo ""

# Change to framework-assistant directory and run the app
cd framework-assistant
streamlit run app.py
