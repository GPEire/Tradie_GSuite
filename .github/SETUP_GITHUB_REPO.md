# Setting Up GitHub Repository

This guide will help you create the repository on GitHub and push your local code.

## Option 1: Create Repository via GitHub Web Interface (Recommended)

1. **Go to GitHub.com** and sign in
2. **Click the "+" icon** in the top right corner
3. **Select "New repository"**
4. **Repository Settings:**
   - **Repository name:** `Tradie_GSuite` (or your preferred name)
   - **Description:** `AI-powered email grouping extension for Gmail - Automated project email organization for builders and carpenters`
   - **Visibility:** Choose Private or Public
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
5. **Click "Create repository"**

6. **After creating, GitHub will show you commands. Use these:**

```bash
cd /Users/james/Documents/Project_Repo/Tradie_GSuite

# Add the remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/Tradie_GSuite.git

# Or if you prefer SSH (requires SSH keys set up):
# git remote add origin git@github.com:YOUR_USERNAME/Tradie_GSuite.git

# Push all branches to GitHub
git push -u origin main
git push -u origin develop
```

## Option 2: Using GitHub CLI (if installed)

If you have GitHub CLI (`gh`) installed:

```bash
# Login to GitHub
gh auth login

# Create repository and push
cd /Users/james/Documents/Project_Repo/Tradie_GSuite
gh repo create Tradie_GSuite --private --source=. --remote=origin --push
```

## After Pushing

Once pushed, your repository will be available at:
- `https://github.com/YOUR_USERNAME/Tradie_GSuite`

## Next Steps

1. Set up branch protection rules (see `.github/BRANCHING_STRATEGY.md`)
2. Configure GitHub Actions secrets for CI/CD
3. Add collaborators if needed

