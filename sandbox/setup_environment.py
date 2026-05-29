"""Register a self-hosted environment with the Anthropic API.

Usage:
    ANTHROPIC_API_KEY=... python sandbox/setup_environment.py

Prints the environment ID needed to generate an environment key
in the Console and run the worker.
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
    environment = client.beta.environments.create(
        name="self-healing-ci-sandbox",
        config={"type": "self_hosted"},
    )

    print("\nEnvironment registered successfully!")
    print(f"  ID: {environment.id}")
    print("\nNext steps:")
    print("  1. Go to https://platform.claude.com/workspaces/default/environments")
    print("  2. Open the environment and click 'Generate environment key'")
    print("  3. Export the key and ID on the worker host:")
    print(f'     export ANTHROPIC_ENVIRONMENT_ID="{environment.id}"')
    print('     export ANTHROPIC_ENVIRONMENT_KEY="sk-ant-oat01-..."')
    print("  4. Run the worker with:")
    print(
        f"     docker run -e ANTHROPIC_ENVIRONMENT_KEY=..."
        f" -e ANTHROPIC_ENVIRONMENT_ID={environment.id}"
        " -e GITHUB_TOKEN=... self-healing-sandbox"
    )


if __name__ == "__main__":
    main()
