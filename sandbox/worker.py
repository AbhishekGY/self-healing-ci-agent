import os
import subprocess
import sys

import anthropic

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
ENVIRONMENT_ID = os.environ["ENVIRONMENT_ID"]


def execute_bash(command: str, timeout: int = 120) -> dict:
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd="/workspace",
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Command timed out", "exit_code": 124}


def execute_file_read(path: str) -> dict:
    try:
        with open(path) as f:
            return {"content": f.read()}
    except FileNotFoundError:
        return {"error": f"File not found: {path}"}


def execute_file_write(path: str, content: str) -> dict:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    return {"status": "ok"}


def handle_tool_call(tool_name: str, tool_input: dict) -> str:
    if tool_name == "bash":
        result = execute_bash(tool_input.get("command", ""))
        return f"exit_code={result['exit_code']}\n{result['stdout']}{result['stderr']}"
    elif tool_name == "file_read":
        result = execute_file_read(tool_input.get("path", ""))
        return result.get("content", result.get("error", ""))
    elif tool_name == "file_write":
        result = execute_file_write(tool_input.get("path", ""), tool_input.get("content", ""))
        return result["status"]
    else:
        return f"Unknown tool: {tool_name}"


def run_worker():
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    print(f"Worker started for environment {ENVIRONMENT_ID}")
    print("Polling for sessions...")

    while True:
        try:
            session = client.beta.managed_agents.sessions.claim(
                environment_id=ENVIRONMENT_ID,
                beta="managed-agents-2026-04-01",
            )

            if session is None:
                continue

            print(f"Claimed session {session.id}")

            while session.status == "running":
                for event in session.events:
                    if event.type == "tool_call":
                        print(f"  Tool: {event.tool_name}({event.tool_input})")
                        result = handle_tool_call(event.tool_name, event.tool_input)
                        session = client.beta.managed_agents.sessions.submit_tool_result(
                            session_id=session.id,
                            tool_call_id=event.id,
                            result=result,
                            beta="managed-agents-2026-04-01",
                        )

            print(f"Session {session.id} completed with status: {session.status}")

        except KeyboardInterrupt:
            print("\nWorker shutting down")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)


if __name__ == "__main__":
    run_worker()
