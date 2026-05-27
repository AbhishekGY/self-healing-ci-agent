"""Register a self-hosted environment with the Managed Agents API.

Usage:
    ANTHROPIC_API_KEY=... python sandbox/setup_environment.py

Prints the environment ID and key needed to run the worker.
"""

import os
import sys

import anthropic


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Set ANTHROPIC_API_KEY environment variable")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    print("Registering self-hosted environment...")
    environment = client.beta.managed_agents.environments.create(
        name="self-healing-ci-sandbox",
        type="self_hosted",
        beta="managed-agents-2026-04-01",
    )

    print(f"\nEnvironment registered successfully!")
    print(f"  ID:  {environment.id}")
    print(f"  Key: {environment.key}")
    print(f"\nSave these values. Run the worker with:")
    print(f"  docker run -e ANTHROPIC_API_KEY=... -e ENVIRONMENT_ID={environment.id} -e GITHUB_TOKEN=... self-healing-sandbox")


if __name__ == "__main__":
    main()
