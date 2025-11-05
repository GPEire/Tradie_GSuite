# Contributing Guide

Thank you for your interest in contributing to the AI Email Extension for Builders/Carpenters!

## Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Tradie_GSuite
   ```

2. **Set up Python virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   # or
   venv\Scripts\activate      # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   npm install
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

## Branching Strategy

We follow the **Git Flow** branching strategy:

- **`main`** - Production-ready code
- **`develop`** - Integration branch for features
- **`feature/*`** - Feature branches (e.g., `feature/email-grouping`)
- **`bugfix/*`** - Bug fix branches
- **`hotfix/*`** - Hotfix branches for production issues
- **`release/*`** - Release preparation branches

### Creating a Feature Branch

```bash
# Start from develop
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: add your feature description"

# Push and create PR
git push origin feature/your-feature-name
```

## Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- **`feat:`** - New feature
- **`fix:`** - Bug fix
- **`docs:`** - Documentation changes
- **`style:`** - Code style changes (formatting, etc.)
- **`refactor:`** - Code refactoring
- **`test:`** - Adding or updating tests
- **`chore:`** - Maintenance tasks

Examples:
```
feat: add email grouping by project
fix: resolve Gmail API rate limiting issue
docs: update README with setup instructions
```

## Code Style

### Python
- Follow PEP 8
- Use `black` for formatting
- Use `flake8` for linting
- Use `mypy` for type checking

```bash
# Format code
black .

# Check linting
flake8 .

# Type check
mypy .
```

### JavaScript/TypeScript
- Follow ESLint rules
- Use Prettier for formatting
- Use TypeScript for type safety

## Testing

- Write tests for all new features
- Maintain test coverage above 80%
- Run tests before committing

```bash
# Backend tests
pytest

# Frontend tests
npm test
```

## Pull Request Process

1. **Update your branch**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout feature/your-feature-name
   git rebase develop
   ```

2. **Run tests and linting**
   ```bash
   pytest
   black --check .
   flake8 .
   ```

3. **Create Pull Request**
   - Target branch: `develop` (for features) or `main` (for hotfixes)
   - Provide clear description
   - Link related issues
   - Request review from at least one maintainer

4. **Address review feedback**
   - Make requested changes
   - Respond to comments
   - Update PR description if needed

5. **Merge**
   - Squash and merge (preferred)
   - Delete feature branch after merge

## Environment Variables

Never commit `.env` files. Use `.env.example` as a template.

## Questions?

Open an issue or contact the maintainers.

