#!/bin/bash

# Quick script to connect to GitHub repository
# Usage: ./connect-github.sh YOUR_USERNAME [https|ssh]

set -e

if [ -z "$1" ]; then
    echo "Usage: ./connect-github.sh YOUR_GITHUB_USERNAME [https|ssh]"
    echo "Example: ./connect-github.sh johndoe https"
    exit 1
fi

GITHUB_USERNAME=$1
CONNECTION_TYPE=${2:-https}

if [ "$CONNECTION_TYPE" == "ssh" ]; then
    REMOTE_URL="git@github.com:${GITHUB_USERNAME}/Tradie_GSuite.git"
else
    REMOTE_URL="https://github.com/${GITHUB_USERNAME}/Tradie_GSuite.git"
fi

# Check if remote already exists
if git remote get-url origin &> /dev/null; then
    echo "⚠️  Remote 'origin' already exists:"
    git remote -v
    echo ""
    read -p "Do you want to update it? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git remote remove origin
    else
        echo "Keeping existing remote. Exiting."
        exit 0
    fi
fi

echo "Adding remote: $REMOTE_URL"
git remote add origin "$REMOTE_URL"

echo ""
echo "✅ Remote added!"
echo ""
echo "To push your code:"
echo "  git push -u origin main"
echo "  git push -u origin develop"

