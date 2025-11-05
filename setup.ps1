# Setup script for AI Email Extension Development Environment (Windows PowerShell)
# This script sets up both Python and Node.js virtual environments

Write-Host "🚀 Setting up AI Email Extension Development Environment" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python 3 is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python 3 is not installed. Please install Python 3.9+ first." -ForegroundColor Red
    exit 1
}

# Check if Node.js is installed
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js is not installed. Please install Node.js 18+ first." -ForegroundColor Red
    exit 1
}

# Check if npm is installed
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "❌ npm is not installed. Please install npm first." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Prerequisites check passed" -ForegroundColor Green
Write-Host ""

# Python Virtual Environment Setup
Write-Host "📦 Setting up Python virtual environment..." -ForegroundColor Yellow

if (Test-Path "venv") {
    Write-Host "   Virtual environment already exists. Skipping creation."
} else {
    python -m venv venv
    Write-Host "✅ Python virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
& "venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "   Upgrading pip..."
python -m pip install --upgrade pip --quiet

# Install Python dependencies
if (Test-Path "requirements.txt") {
    Write-Host "   Installing Python dependencies..."
    pip install -r requirements.txt
    Write-Host "✅ Python dependencies installed" -ForegroundColor Green
} else {
    Write-Host "⚠️  requirements.txt not found. Creating template..." -ForegroundColor Yellow
    @"
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
"@ | Out-File -FilePath "requirements.txt" -Encoding UTF8
    Write-Host "⚠️  Please review and update requirements.txt before installing" -ForegroundColor Yellow
}

Write-Host ""

# Node.js Setup
Write-Host "📦 Setting up Node.js environment..." -ForegroundColor Yellow

# Check if package.json exists
if (-not (Test-Path "package.json")) {
    Write-Host "   Initializing Node.js project..."
    
    # Check if frontend directory exists
    if (Test-Path "frontend") {
        Set-Location frontend
    }
    
    # Create package.json if it doesn't exist
    if (-not (Test-Path "package.json")) {
        npm init -y
        Write-Host "⚠️  Created package.json. Please update with project dependencies." -ForegroundColor Yellow
    }
}

# Install Node.js dependencies
if (Test-Path "package.json") {
    Write-Host "   Installing Node.js dependencies..."
    npm install
    Write-Host "✅ Node.js dependencies installed" -ForegroundColor Green
}

Write-Host ""

# Environment Variables Setup
Write-Host "⚙️  Setting up environment variables..." -ForegroundColor Yellow

if (-not (Test-Path ".env")) {
    Write-Host "   Creating .env file from template..."
    @"
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
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "⚠️  Created .env file. Please update with your actual credentials." -ForegroundColor Yellow
} else {
    Write-Host "   .env file already exists. Skipping creation."
}

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Activate Python virtual environment: " -NoNewline; Write-Host "venv\Scripts\Activate.ps1" -ForegroundColor Green
Write-Host "2. Update .env file with your API credentials"
Write-Host "3. Review and install dependencies from requirements.txt"
Write-Host "4. Run backend: " -NoNewline; Write-Host "python -m uvicorn app.main:app --reload" -ForegroundColor Green
Write-Host "5. Run frontend: " -NoNewline; Write-Host "npm run dev" -ForegroundColor Green
Write-Host ""
Write-Host "To deactivate Python virtual environment: " -NoNewline; Write-Host "deactivate" -ForegroundColor Green


