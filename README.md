# AI Email Extension for Builders/Carpenters
## Gmail/G Suite Integration - Automated Project Email Grouping

This project provides an AI-powered email grouping extension for Gmail that automatically organizes customer emails by project/job.

---

## Prerequisites

Before setting up the development environment, ensure you have:

- **Python 3.9+** (for backend services)
- **Node.js 18+** (for frontend Chrome extension)
- **npm** or **yarn** (package manager)
- **Git** (version control)
- **Google Cloud Account** (for Gmail API access)

---

## Development Environment Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Tradie_GSuite
```

### 2. Backend Setup (Python)

#### Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

#### Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

#### Verify Installation

```bash
python --version
pip list
```

### 3. Frontend Setup (Node.js)

#### Install Node.js Dependencies

```bash
# Navigate to frontend directory (if separate)
cd frontend  # or extension

# Install dependencies
npm install

# Or using yarn
yarn install
```

#### Verify Installation

```bash
node --version
npm --version
```

### 4. Environment Variables

Create environment configuration files:

```bash
# Copy example environment files
cp .env.example .env
cp .env.backend.example .env.backend
cp .env.frontend.example .env.frontend
```

Edit `.env` files with your configuration:
- Google OAuth credentials
- API keys for AI services
- Database connection strings
- Other sensitive configuration

**Note:** Never commit `.env` files to version control.

---

## Project Structure

```
Tradie_GSuite/
├── backend/                 # Python backend services
│   ├── app/
│   ├── tests/
│   ├── requirements.txt
│   └── ...
├── frontend/                # React Chrome Extension
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
├── docs/                    # Documentation
├── venv/                    # Python virtual environment (gitignored)
├── .env                     # Environment variables (gitignored)
├── .gitignore
└── README.md
```

---

## Running the Development Environment

### Backend (Python)

```bash
# Activate virtual environment first
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Run development server
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend (React Chrome Extension)

```bash
# Build and watch for changes
npm run dev

# Or for production build
npm run build
```

---

## Development Workflow

1. **Always activate virtual environment** before working on backend
2. **Create feature branches** from `main`
3. **Run tests** before committing
4. **Follow coding standards** and linting rules

---

## Testing

### Backend Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

### Frontend Tests

```bash
npm test
```

---

## Troubleshooting

### Virtual Environment Issues

**Problem:** `python3` command not found
- **Solution:** Install Python 3.9+ from python.org

**Problem:** Virtual environment not activating
- **Solution:** Ensure you're using the correct path (check `which python3`)

**Problem:** Packages not installing in virtual environment
- **Solution:** Verify virtual environment is activated (should see `(venv)` in prompt)

### Node.js Issues

**Problem:** `npm install` fails
- **Solution:** Clear cache: `npm cache clean --force` and try again

**Problem:** Version conflicts
- **Solution:** Use `nvm` (Node Version Manager) to manage Node.js versions

---

## Additional Resources

- [Python Virtual Environments Guide](https://docs.python.org/3/tutorial/venv.html)
- [Node.js Best Practices](https://github.com/goldbergyoni/nodebestpractices)
- [Chrome Extension Development](https://developer.chrome.com/docs/extensions/)
- [Gmail API Documentation](https://developers.google.com/gmail/api)

---

## Contributing

Please read our contributing guidelines before submitting pull requests.

---

## License

[To be determined]


