#!/bin/bash
set -e

if [ -z "$ANTHROPIC_ENVIRONMENT_KEY" ]; then
    echo "ERROR: ANTHROPIC_ENVIRONMENT_KEY not set"
    exit 1
fi

if [ -z "$ANTHROPIC_ENVIRONMENT_ID" ]; then
    echo "ERROR: ANTHROPIC_ENVIRONMENT_ID not set"
    exit 1
fi

if [ -n "$GITHUB_TOKEN" ]; then
    echo "$GITHUB_TOKEN" | gh auth login --with-token
    echo "GitHub CLI authenticated"
fi

echo "Starting environment worker..."
python /app/worker.py
