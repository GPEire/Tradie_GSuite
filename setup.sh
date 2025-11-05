#!/bin/bash

# Setup script for AI Email Extension Development Environment
# This script sets up both Python and Node.js virtual environments

set -e  # Exit on error

echo "🚀 Setting up AI Email Extension Development Environment"
echo "========================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.9+ first.${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 18+ first.${NC}"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm is not installed. Please install npm first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"
echo ""

# Python Virtual Environment Setup
echo -e "${YELLOW}📦 Setting up Python virtual environment...${NC}"

if [ -d "venv" ]; then
    echo "   Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    echo -e "${GREEN}✅ Python virtual environment created${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "   Upgrading pip..."
pip install --upgrade pip --quiet

# Install Python dependencies
if [ -f "requirements.txt" ]; then
    echo "   Installing Python dependencies..."
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Python dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  requirements.txt not found. Creating template...${NC}"
    cat > requirements.txt << EOF
# Core dependencies
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0

# Google APIs
google-api-python-client>=2.100.0
google-auth-httplib2>=0.1.1
google-auth-oauthlib>=1.1.0

# AI/ML
openai>=1.3.0
anthropic>=0.7.0

# Database
sqlalchemy>=2.0.0
alembic>=1.12.0

# Utilities
python-dotenv>=1.0.0
requests>=2.31.0
python-multipart>=0.0.6

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-asyncio>=0.21.0

# Development
black>=23.11.0
flake8>=6.1.0
mypy>=1.7.0
EOF
    echo -e "${YELLOW}⚠️  Please review and update requirements.txt before installing${NC}"
fi

echo ""

# Node.js Setup
echo -e "${YELLOW}📦 Setting up Node.js environment...${NC}"

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo "   Initializing Node.js project..."
    
    # Check if frontend directory exists
    if [ -d "frontend" ]; then
        cd frontend
    fi
    
    # Create package.json if it doesn't exist
    if [ ! -f "package.json" ]; then
        npm init -y
        echo -e "${YELLOW}⚠️  Created package.json. Please update with project dependencies.${NC}"
    fi
fi

# Install Node.js dependencies
if [ -f "package.json" ]; then
    echo "   Installing Node.js dependencies..."
    npm install
    echo -e "${GREEN}✅ Node.js dependencies installed${NC}"
fi

echo ""

# Environment Variables Setup
echo -e "${YELLOW}⚙️  Setting up environment variables...${NC}"

if [ ! -f ".env" ]; then
    echo "   Creating .env file from template..."
    cat > .env << EOF
# Backend Configuration
BACKEND_PORT=8000
BACKEND_HOST=localhost
DEBUG=True

# Google OAuth
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback

# Gmail API
GMAIL_SCOPES=gmail.readonly,gmail.modify,gmail.labels

# AI Services
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Database
DATABASE_URL=sqlite:///./app.db

# Security
SECRET_KEY=your_secret_key_here_change_in_production
ENCRYPTION_KEY=your_encryption_key_here_change_in_production

# Frontend
FRONTEND_URL=http://localhost:3000
CHROME_EXTENSION_ID=your_extension_id_here
EOF
    echo -e "${YELLOW}⚠️  Created .env file. Please update with your actual credentials.${NC}"
else
    echo "   .env file already exists. Skipping creation."
fi

echo ""

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "   Creating .gitignore..."
    # .gitignore is created separately
fi

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Activate Python virtual environment: ${GREEN}source venv/bin/activate${NC}"
echo "2. Update .env file with your API credentials"
echo "3. Review and install dependencies from requirements.txt"
echo "4. Run backend: ${GREEN}python -m uvicorn app.main:app --reload${NC}"
echo "5. Run frontend: ${GREEN}npm run dev${NC}"
echo ""
echo "To deactivate Python virtual environment: ${GREEN}deactivate${NC}"


