"""Smoke test: create a session targeting the self-hosted environment.

Usage:
    ANTHROPIC_API_KEY=... AGENT_ID=... ENVIRONMENT_ID=... python sandbox/test_worker.py

The worker must be running in a separate process/container.
"""

import os
import sys
import time

import anthropic


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    agent_id = os.environ.get("AGENT_ID")
    env_id = os.environ.get("ENVIRONMENT_ID")

    if not api_key or not agent_id or not env_id:
        print("ERROR: Set ANTHROPIC_API_KEY, AGENT_ID, and ENVIRONMENT_ID")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    print("Creating test session...")
    session = client.beta.sessions.create(
        agent=agent_id,
        environment_id=env_id,
    )

    print(f"Session created: {session.id}")
    print("Waiting for completion...")

    for _ in range(60):
        session = client.beta.sessions.retrieve(session.id)
        if session.status in ("completed", "failed", "ended"):
            break
        time.sleep(2)

    print(f"\nStatus: {session.status}")
    if session.status in ("completed", "ended"):
        print("Worker test passed!")
    else:
        print("Worker test failed — check worker logs")
        sys.exit(1)


if __name__ == "__main__":
    main()
