"""Self-hosted environment worker.

Polls the Anthropic work queue and executes tool calls locally
using the SDK's built-in EnvironmentWorker.

Required env vars:
    ANTHROPIC_ENVIRONMENT_KEY  - generated in the Console
    ANTHROPIC_ENVIRONMENT_ID   - from environment creation
"""

import asyncio
import os
import sys

from anthropic import AsyncAnthropic
from anthropic.lib.environments import EnvironmentWorker


async def main():
    environment_key = os.environ.get("ANTHROPIC_ENVIRONMENT_KEY")
    environment_id = os.environ.get("ANTHROPIC_ENVIRONMENT_ID")

    if not environment_key or not environment_id:
        print("ERROR: Set ANTHROPIC_ENVIRONMENT_KEY and ANTHROPIC_ENVIRONMENT_ID")
        sys.exit(1)

    print(f"Worker starting for environment {environment_id}")
    print("Polling for sessions...")

    async with AsyncAnthropic(auth_token=environment_key) as client:
        await EnvironmentWorker(
            client,
            environment_id=environment_id,
            environment_key=environment_key,
            workdir="/workspace",
        ).run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nWorker shutting down")
        sys.exit(0)
