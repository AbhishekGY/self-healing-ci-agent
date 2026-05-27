#!/bin/bash
set -e

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "ERROR: ANTHROPIC_API_KEY not set"
    exit 1
fi

if [ -z "$ENVIRONMENT_ID" ]; then
    echo "ERROR: ENVIRONMENT_ID not set"
    exit 1
fi

if [ -n "$GITHUB_TOKEN" ]; then
    echo "$GITHUB_TOKEN" | gh auth login --with-token
    echo "GitHub CLI authenticated"
fi

echo "Starting environment worker..."
python /app/worker.py
