#!/bin/bash

# Script to help set up GitHub remote repository
# This script will guide you through adding the remote and pushing your code

set -e

echo "🚀 GitHub Repository Setup"
echo "=========================="
echo ""

# Check if remote already exists
if git remote get-url origin &> /dev/null; then
    echo "⚠️  Remote 'origin' already exists:"
    git remote -v
    echo ""
    read -p "Do you want to update it? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing remote..."
        git remote remove origin
    else
        echo "Keeping existing remote. Exiting."
        exit 0
    fi
fi

echo "📋 To complete the setup, you need to:"
echo ""
echo "1. Create a repository on GitHub:"
echo "   - Go to https://github.com/new"
echo "   - Name: Tradie_GSuite (or your preferred name)"
echo "   - DO NOT initialize with README, .gitignore, or license"
echo "   - Create the repository"
echo ""
echo "2. After creating, provide your GitHub username:"
read -p "   Enter your GitHub username: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo "❌ GitHub username is required. Exiting."
    exit 1
fi

echo ""
echo "3. Choose connection method:"
echo "   [1] HTTPS (easier, requires GitHub password/token)"
echo "   [2] SSH (requires SSH keys set up)"
read -p "   Enter choice (1 or 2): " CONNECTION_CHOICE

if [ "$CONNECTION_CHOICE" == "1" ]; then
    REMOTE_URL="https://github.com/${GITHUB_USERNAME}/Tradie_GSuite.git"
    echo ""
    echo "Using HTTPS connection"
elif [ "$CONNECTION_CHOICE" == "2" ]; then
    REMOTE_URL="git@github.com:${GITHUB_USERNAME}/Tradie_GSuite.git"
    echo ""
    echo "Using SSH connection"
else
    echo "❌ Invalid choice. Using HTTPS by default."
    REMOTE_URL="https://github.com/${GITHUB_USERNAME}/Tradie_GSuite.git"
fi

echo ""
echo "4. Adding remote 'origin'..."
git remote add origin "$REMOTE_URL"

echo "✅ Remote added successfully!"
echo ""
echo "5. Ready to push? Make sure you've created the repository on GitHub first."
read -p "   Push to GitHub now? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Pushing main branch..."
    git push -u origin main
    
    echo "Pushing develop branch..."
    git push -u origin develop
    
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "Your repository is now available at:"
    echo "https://github.com/${GITHUB_USERNAME}/Tradie_GSuite"
else
    echo ""
    echo "To push manually later, run:"
    echo "  git push -u origin main"
    echo "  git push -u origin develop"
fi

