# Git Branching Strategy

This project follows the **Git Flow** branching model for organized development and release management.

## Branch Types

### Main Branches

#### `main`
- **Purpose:** Production-ready code
- **Protection:** Protected branch, requires PR approval
- **Deployment:** Auto-deploys to production
- **Merges:** Only from `release/*` or `hotfix/*` branches

#### `develop`
- **Purpose:** Integration branch for features
- **Protection:** Protected branch, requires PR approval
- **Deployment:** Auto-deploys to staging
- **Merges:** Feature branches merge here

### Supporting Branches

#### `feature/*`
- **Purpose:** New features and enhancements
- **Naming:** `feature/email-grouping`, `feature/ai-integration`
- **Source:** Branched from `develop`
- **Merge:** Back to `develop`
- **Lifecycle:** Deleted after merge

#### `bugfix/*`
- **Purpose:** Bug fixes for development
- **Naming:** `bugfix/gmail-api-rate-limit`
- **Source:** Branched from `develop`
- **Merge:** Back to `develop`
- **Lifecycle:** Deleted after merge

#### `hotfix/*`
- **Purpose:** Critical production fixes
- **Naming:** `hotfix/security-patch-v1.0.1`
- **Source:** Branched from `main`
- **Merge:** Back to `main` AND `develop`
- **Lifecycle:** Deleted after merge

#### `release/*`
- **Purpose:** Release preparation
- **Naming:** `release/v1.0.0`
- **Source:** Branched from `develop`
- **Merge:** Back to `main` AND `develop`
- **Lifecycle:** Deleted after merge

## Workflow Examples

### Starting a New Feature

```bash
# Start from develop
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/email-grouping

# Work on feature, commit changes
git add .
git commit -m "feat: add email grouping functionality"

# Push and create PR
git push origin feature/email-grouping
# Create PR: feature/email-grouping → develop
```

### Creating a Hotfix

```bash
# Start from main
git checkout main
git pull origin main

# Create hotfix branch
git checkout -b hotfix/security-patch-v1.0.1

# Make fix, commit
git add .
git commit -m "fix: security patch for authentication"

# Push and create PRs
git push origin hotfix/security-patch-v1.0.1
# Create PR: hotfix/security-patch-v1.0.1 → main
# After merging to main, create PR to develop
```

### Preparing a Release

```bash
# Start from develop
git checkout develop
git pull origin develop

# Create release branch
git checkout -b release/v1.0.0

# Update version numbers, changelog, etc.
# Commit changes
git add .
git commit -m "chore: prepare release v1.0.0"

# Push and create PRs
git push origin release/v1.0.0
# Create PR: release/v1.0.0 → main
# After merging to main, create PR to develop
```

## Branch Protection Rules

### Main Branch
- Require pull request reviews (at least 1)
- Require status checks to pass
- Require branches to be up to date
- No force pushes
- No deletion

### Develop Branch
- Require pull request reviews (at least 1)
- Require status checks to pass
- No force pushes
- No deletion

## Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `style:` - Code style (formatting)
- `refactor:` - Code refactoring
- `test:` - Tests
- `chore:` - Maintenance tasks
- `perf:` - Performance improvements
- `ci:` - CI/CD changes

## Tagging Strategy

- **Format:** `v{major}.{minor}.{patch}` (e.g., `v1.0.0`)
- **Location:** Tags on `main` branch only
- **Purpose:** Mark production releases

## Best Practices

1. **Always pull latest before branching**
   ```bash
   git checkout develop
   git pull origin develop
   ```

2. **Keep branches up to date**
   ```bash
   git checkout feature/your-feature
   git rebase develop
   ```

3. **Delete merged branches**
   - Feature branches are auto-deleted after merge
   - Manually delete if needed: `git branch -d branch-name`

4. **Never commit directly to main or develop**
   - Always use pull requests

5. **Keep commits atomic and meaningful**
   - One logical change per commit
   - Write clear commit messages

6. **Sync develop with main regularly**
   - After each release, ensure develop includes main's changes

