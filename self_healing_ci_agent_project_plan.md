# Self-healing CI/CD agent — project plan

A Claude Managed Agent that automatically diagnoses CI pipeline failures, fixes the code, runs tests in a self-hosted sandbox, and opens a pull request — all without human intervention.

**Primary goal:** Demonstrate Claude Managed Agents capabilities (self-hosted sandboxes, MCP tunnels, long-running autonomous sessions, session streaming, session steering).

---

## Phase 1: Build the demo codebase

**Goal:** A clean, working REST API with full test coverage that you can deliberately break for demos.

### 1.1 Scaffold the todo API

- Python 3.11 + FastAPI + SQLAlchemy + SQLite + pytest
- 10-15 files, ~500-700 lines total
- Structure:
  - `app/main.py` — FastAPI app, route registration
  - `app/models.py` — SQLAlchemy models (Task, User)
  - `app/schemas.py` — Pydantic v2 request/response schemas
  - `app/routes/tasks.py` — CRUD endpoints for tasks
  - `app/routes/users.py` — User registration, basic auth
  - `app/database.py` — DB connection, session management
  - `app/utils.py` — Date parsing, pagination, helpers
  - `tests/test_tasks.py` — Task CRUD endpoint tests
  - `tests/test_users.py` — User endpoint tests
  - `tests/test_utils.py` — Unit tests for utility functions
  - `requirements.txt` — Pinned dependencies
  - `README.md` — Setup instructions

### 1.2 Ensure full test coverage

- All endpoints have at least 2 tests (happy path + error case)
- Utility functions have unit tests
- All tests pass: `pytest -v` should show 15-20 passing tests
- Add a linter config (ruff or flake8) so the agent can lint too

### 1.3 Pre-plant breakable scenarios

Create git branches, each with a specific pre-planted failure the agent will fix during demos:

| Branch | Failure type | What's broken | Complexity |
|--------|-------------|---------------|------------|
| `break/simple-test` | Broken test assertion | Response schema changed, test expects old field name | Easy |
| `break/import-error` | Dependency breakage | Pydantic v1 syntax used with v2 installed (`from pydantic import validator` → `field_validator`) | Medium |
| `break/env-var` | Missing config | `DATABASE_URL` env var referenced but not set, app crashes at startup | Easy |
| `break/type-error` | Logic bug | `utils.py` date parser returns string instead of datetime, downstream comparison fails | Medium |
| `break/flaky-test` | Test ordering issue | Test depends on DB insertion order, fails when run in parallel | Medium |
| `break/multi-file` | Cascading breakage | Model field renamed, not updated in schemas, routes, or tests | Hard |

### 1.4 Set up the GitHub repository

- Push the clean codebase to a GitHub repo
- Set up GitHub Actions CI workflow (`.github/workflows/ci.yml`):
  - Trigger on push
  - Steps: install deps → lint → run tests
- Verify CI passes on `main`, fails on each `break/*` branch

**Deliverable:** A GitHub repo with green CI on `main` and 6 branches that each fail CI in a different way.

---

## Phase 2: Build the self-hosted sandbox

**Goal:** A container where the agent can clone repos, edit code, run tests, and push changes.

### 2.1 Create the Docker image

- Base image: `python:3.11-slim`
- Install: git, gh (GitHub CLI), ruff, pytest, plus all `requirements.txt` deps
- Include: SSH keys or GitHub token for repo access (mounted at runtime, not baked in)
- Working directory: `/workspace` (Managed Agents default)

### 2.2 Set up the environment worker

- Use the `ant` CLI or Python SDK to run an always-on worker
- The worker polls Anthropic's work queue, claims sessions, executes tool calls inside the container
- Tool calls the agent will use:
  - `bash` — run git commands, pytest, ruff, gh CLI
  - `file` — read/write/edit source files
  - `grep`/`glob` — search across the codebase

### 2.3 Create the Managed Agents environment

- Register a `self_hosted` environment via the API
- Configure the environment key for your worker
- Test: start a session, confirm the worker claims it and can execute a simple bash command

### 2.4 Test locally first

- Run the Docker container locally
- Simulate the workflow manually:
  - Clone the `break/simple-test` branch
  - Run `pytest` → observe failure
  - Fix the test
  - Run `pytest` → confirm pass
- Then run the same flow through the environment worker to confirm end-to-end

**Deliverable:** A running environment worker in a Docker container that can execute bash and file tool calls from Managed Agents sessions.

---

## Phase 3: Build the MCP server for internal context

**Goal:** Give the agent access to project-specific context (coding standards, known issues, architecture notes) via MCP tunnel.

### 3.1 Create the knowledge base

- A SQLite database or flat markdown files containing:
  - Project coding conventions (naming, import order, error handling patterns)
  - Known issues / common failure patterns and their fixes
  - Architecture notes (which files depend on which)
  - Dependency compatibility notes (e.g., "Pydantic v2 changed `validator` to `field_validator`")

### 3.2 Build the MCP server

- Use the MCP Python SDK
- Expose tools:
  - `search_conventions(query)` — search coding standards by keyword
  - `get_known_fixes(error_message)` — look up known fixes for common errors
  - `get_file_dependencies(filename)` — return which other files import/depend on this file
- Run locally on `localhost:8080`

### 3.3 Set up MCP tunnel

- Install the MCP tunnel gateway
- Configure outbound connection to Anthropic's relay
- Register the MCP server as a tool on the agent
- Test: start a session, confirm the agent can call `search_conventions` and get results

**Deliverable:** A running MCP server accessible through the tunnel, providing project-specific context to the agent.

---

## Phase 4: Configure the Managed Agent

**Goal:** An agent with the right system prompt, tools, and skills to autonomously diagnose and fix CI failures.

### 4.1 Write the agent system prompt

The system prompt should instruct Claude to follow this workflow:

```
1. Read the CI failure logs (provided as input or fetched via bash)
2. Identify the type of failure (test failure, import error, lint error, runtime crash)
3. Search project conventions via MCP for relevant context
4. Read the failing file(s) and their dependencies
5. Form a hypothesis about the root cause
6. Make the fix (edit files)
7. Run the tests locally (pytest -v)
8. If tests still fail, read the new error, adjust, and retry (max 3 retries)
9. Run the linter (ruff check .)
10. If everything passes, commit the fix and open a PR using gh CLI
11. Write a summary of what was wrong and what was fixed to /mnt/session/outputs/fix_report.md
```

- Include instructions for common pitfalls (don't delete tests to make them pass, preserve existing functionality, make minimal changes)
- Set a retry ceiling so the agent doesn't loop forever

### 4.2 Create the agent via API

- Model: claude-sonnet-4-20250514 (good balance of speed and capability for code tasks)
- Register the system prompt
- Attach MCP server as a tool
- Built-in tools: bash, file, grep, glob (all enabled by default)

### 4.3 Create agent skills (optional but recommended)

- Package the coding conventions and fix patterns as downloadable skills
- Skills get placed in `/workspace/skills/<name>/` inside the sandbox
- This gives the agent local access to context even without MCP

### 4.4 Test with each failure branch

- Run a session for each `break/*` branch
- Input message: "CI failed on branch `break/simple-test`. Clone the repo, diagnose the failure, fix it, and open a PR."
- Verify the agent:
  - Correctly identifies the root cause
  - Makes a targeted fix (not a shotgun rewrite)
  - Tests pass after the fix
  - PR is opened with a clear description

| Branch | Expected agent behavior |
|--------|------------------------|
| `break/simple-test` | Reads test output, sees field name mismatch, updates test assertion |
| `break/import-error` | Sees ImportError, checks MCP for Pydantic v2 migration notes, updates import syntax |
| `break/env-var` | Sees crash at startup, finds missing env var reference, adds a default or .env fallback |
| `break/type-error` | Reads test failure, traces to utils.py, fixes return type |
| `break/flaky-test` | Recognizes ordering dependency, adds explicit sorting or fixture isolation |
| `break/multi-file` | Reads initial error, uses grep to find all references to renamed field, updates all files |

**Deliverable:** A fully configured agent that can fix all 6 failure scenarios autonomously.

---

## Phase 5: Wire up the CI webhook trigger

**Goal:** CI failure automatically triggers the agent — no manual session creation.

### 5.1 Set up a webhook receiver

- A lightweight FastAPI or Flask app that:
  - Receives GitHub Actions webhook on CI failure
  - Extracts: repo URL, branch name, commit SHA, failure logs URL
  - Creates a Managed Agents session via API with this context as the input message
  - Returns the session ID

### 5.2 Configure GitHub Actions to call the webhook

- Add a step to the CI workflow that runs on failure:
  ```yaml
  - name: Trigger self-healing agent
    if: failure()
    run: |
      curl -X POST https://your-webhook.example.com/ci-failed \
        -H "Content-Type: application/json" \
        -d '{"repo": "${{ github.repository }}", "branch": "${{ github.ref_name }}", "run_id": "${{ github.run_id }}"}'
  ```

### 5.3 Alternative: webhook-triggered worker pattern

- Instead of always-on polling, use the SDK's webhook-triggered worker
- Anthropic sends `session.status_run_started` to your endpoint
- Your handler spins up a container, starts polling, executes the session, shuts down
- More cost-efficient for infrequent CI failures

### 5.4 Test the full loop

- Push to a `break/*` branch
- CI runs → fails → webhook fires → agent session starts → agent fixes code → opens PR
- Verify the PR appears on GitHub with the fix

**Deliverable:** End-to-end automation: push broken code → agent fixes it → PR appears.

---

## Phase 6: Build the live demo UI

**Goal:** A web interface that shows the agent working in real-time during demos.

### 6.1 Stream session events

- Use the SSE event stream from the Managed Agents API
- Events include: tool calls (what bash command is being run), tool results (test output), text responses (agent's reasoning)
- Parse and display in a structured timeline

### 6.2 Build the frontend

- React app with three panels:
  - **Left: CI failure log** — the original failure that triggered the agent
  - **Center: Agent activity stream** — live feed of what the agent is doing (reading files, running tests, editing code), with syntax-highlighted code diffs
  - **Right: File tree** — shows which files the agent has touched, with before/after diffs
- Bottom bar: session steering input — you can type mid-session to redirect the agent

### 6.3 Add session steering demo

- While the agent is working on `break/multi-file`, interrupt with: "Also add a test for the renamed field to prevent this regression"
- Show the agent adapting its plan and adding the test
- This is one of the strongest Managed Agents differentiators — you can't do this with a static script

### 6.4 Polish for demo day

- Pre-record a fallback video in case of network issues
- Prepare talking points for each phase of the agent's execution
- Time the demo: aim for 3-5 minutes for a simple fix, 8-10 for multi-file

**Deliverable:** A live demo UI that streams the agent's work in real-time with session steering.

---

## Phase 7: Stretch goals

### 7.1 Managed Agents webhooks for notifications

- Subscribe to `session.completed` and `session.failed` webhooks
- Post to Slack: "Agent fixed CI on branch X — PR #42 opened" or "Agent couldn't fix the failure after 3 attempts — needs human review"

### 7.2 Multi-repo support

- Agent handles failures across multiple repos
- Uses multiagent sessions (research preview) to spawn sub-agents per repo

### 7.3 Learning from past fixes

- Store successful fix patterns in the MCP knowledge base
- Agent checks past fixes before attempting a new one
- Over time, common failures get fixed faster

### 7.4 Metrics dashboard

- Track: time to fix, number of retries, fix success rate per failure type
- Display on the demo UI as a secondary tab

---

## Architecture summary

```
GitHub Actions (CI fails)
        │
        ▼
  Webhook receiver ──────────► Anthropic Managed Agents API
                                        │
                        ┌───────────────┼───────────────┐
                        ▼                               ▼
              Self-hosted sandbox                 MCP tunnel
              (Docker container)                      │
              ┌──────────────┐                        ▼
              │ git clone    │                 MCP server (local)
              │ pytest       │                 ┌──────────────┐
              │ ruff         │                 │ conventions  │
              │ file edits   │                 │ known fixes  │
              │ gh pr create │                 │ dependencies │
              └──────────────┘                 └──────────────┘
                        │
                        ▼
                  Pull request opened
```

---

## Estimated costs

| Component | Free tier | Estimated monthly cost |
|-----------|-----------|------------------------|
| Anthropic API (agent sessions) | — | $10-20 (depends on session count) |
| Self-hosted sandbox | Your own Docker host or Modal free tier | $0-5 |
| MCP tunnel | Free (part of Managed Agents) | $0 |
| GitHub Actions | 2,000 free minutes/month | $0 |
| **Total** | | **$10-25/month** |

---

## Prerequisites

- Python 3.11+
- Docker
- GitHub account with Actions enabled
- Anthropic API key with Managed Agents access (beta header: `managed-agents-2026-04-01`)
- `ant` CLI or Anthropic Python SDK
- Basic familiarity with FastAPI, pytest, and git

---

## Demo script (suggested flow)

1. Show the clean codebase on `main` — CI is green
2. Push to `break/simple-test` — CI goes red
3. Show the webhook firing and session starting
4. Watch the agent in the live UI: it reads the error, finds the broken test, fixes the assertion, runs tests, they pass, opens a PR
5. Show the PR on GitHub — clean diff, clear description
6. Now push to `break/multi-file` — the hard one
7. Watch the agent trace dependencies across files, fix each one, retry when first attempt misses a reference
8. Mid-session, steer: "Also add a regression test"
9. Agent adapts, adds the test, final pytest passes, PR opened
10. Show the fix report in `/mnt/session/outputs/fix_report.md`

Total demo time: ~15 minutes for the full walkthrough, ~5 minutes for the quick version (simple fix only).

---

## Documentation sources

- [Claude Managed Agents overview](https://platform.claude.com/docs/en/managed-agents/overview)
- [Self-hosted sandboxes integration guide](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes)
