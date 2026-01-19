#!/bin/bash

# BotConChat v1.1 - Setup Script
# This script sets up the environment for the Framework Assistant application

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}  BotConChat v1.1 - Setup${NC}"
echo -e "${BLUE}==================================================${NC}"
echo ""

# Check if we're in the right directory
if [ ! -d "framework-assistant" ]; then
    echo -e "${RED}Error: framework-assistant directory not found!${NC}"
    echo -e "${RED}Please run this script from the BotConChatv1.1 root directory.${NC}"
    exit 1
fi

# Check Python version
echo -e "${GREEN}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "Found Python ${python_version}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${GREEN}Creating virtual environment...${NC}"
    python3 -m venv venv
else
    echo -e "${YELLOW}Virtual environment already exists.${NC}"
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${GREEN}Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
echo -e "${GREEN}Installing dependencies from requirements.txt...${NC}"
if [ -f "framework-assistant/requirements.txt" ]; then
    pip install -r framework-assistant/requirements.txt
else
    echo -e "${RED}Error: requirements.txt not found in framework-assistant directory!${NC}"
    exit 1
fi

# Create necessary directories
echo -e "${GREEN}Creating necessary directories...${NC}"
mkdir -p framework-assistant/logs
mkdir -p framework-assistant/cache

# Setup .env file
if [ ! -f "framework-assistant/.env" ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    if [ -f "framework-assistant/.env.example" ]; then
        cp framework-assistant/.env.example framework-assistant/.env
        echo -e "${GREEN}.env file created!${NC}"
        echo -e "${YELLOW}IMPORTANT: Please edit framework-assistant/.env and add your OpenAI API key!${NC}"
    else
        echo -e "${YELLOW}Warning: .env.example not found. Creating basic .env...${NC}"
        cat > framework-assistant/.env << 'EOF'
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-api-key-here

# Database Configuration
DATABASE_PATH=frameworks.db

# Logging Configuration
FEEDBACK_LOG_FILE=logs/feedback.json
EOF
        echo -e "${GREEN}.env file created!${NC}"
        echo -e "${YELLOW}IMPORTANT: Please edit framework-assistant/.env and add your OpenAI API key!${NC}"
    fi
else
    echo -e "${YELLOW}.env file already exists.${NC}"
fi

# Check if database exists
if [ -f "framework-assistant/frameworks.db" ]; then
    echo -e "${GREEN}Database file found: frameworks.db${NC}"
else
    echo -e "${YELLOW}Warning: frameworks.db not found!${NC}"
    echo -e "${YELLOW}You may need to create or import your framework database.${NC}"
fi

# Make run.sh executable
if [ -f "run.sh" ]; then
    chmod +x run.sh
    echo -e "${GREEN}Made run.sh executable${NC}"
fi

echo ""
echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}  Setup Complete!${NC}"
echo -e "${GREEN}==================================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Edit framework-assistant/.env and add your OpenAI API key"
echo -e "  2. Ensure framework-assistant/frameworks.db exists with your data"
echo -e "  3. Run the application with: ${GREEN}./run.sh${NC}"
echo ""
echo -e "Or manually with: ${GREEN}cd framework-assistant && streamlit run app.py${NC}"
echo ""
