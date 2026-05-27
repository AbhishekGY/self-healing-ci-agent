"""Smoke test: create a session and verify the worker can execute it.

Usage:
    ANTHROPIC_API_KEY=... ENVIRONMENT_ID=... python sandbox/test_worker.py

The worker must be running in a separate process/container.
"""

import os
import sys
import time

import anthropic


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    env_id = os.environ.get("ENVIRONMENT_ID")

    if not api_key or not env_id:
        print("ERROR: Set ANTHROPIC_API_KEY and ENVIRONMENT_ID")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    print("Creating test session...")
    session = client.beta.managed_agents.sessions.create(
        environment_id=env_id,
        model="claude-sonnet-4-20250514",
        system="You are a test agent. Run the command given and report the output.",
        messages=[{"role": "user", "content": "Run: echo 'Hello from sandbox'"}],
        beta="managed-agents-2026-04-01",
    )

    print(f"Session created: {session.id}")
    print("Waiting for completion...")

    for _ in range(60):
        session = client.beta.managed_agents.sessions.retrieve(
            session_id=session.id,
            beta="managed-agents-2026-04-01",
        )
        if session.status in ("completed", "failed"):
            break
        time.sleep(2)

    print(f"\nStatus: {session.status}")
    if session.status == "completed":
        print("Worker test passed!")
    else:
        print("Worker test failed — check worker logs")
        sys.exit(1)


if __name__ == "__main__":
    main()
