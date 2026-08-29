# Computer Agents Python SDK

[![PyPI version](https://img.shields.io/pypi/v/computer-agents.svg)](https://pypi.org/project/computer-agents/)
[![Python versions](https://img.shields.io/pypi/pyversions/computer-agents.svg)](https://pypi.org/project/computer-agents/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Official Python SDK for [Computer Agents](https://computer-agents.com), the Agentic Compute Platform.

Computer Agents gives AI agents the things a real teammate needs to finish work: persistent cloud computers, files, project plans, tasks, memory, skills, scheduled work, and deployable resources. Use this SDK from Python scripts, services, notebooks, backend jobs, and internal tools to start agents, stream their work, manage projects and computers, deploy resources, store data, and monitor usage.

## What You Can Build

- **Agentic product workspaces** with projects, releases, tickets, reviewers, comments, and task-linked threads.
- **Persistent cloud computers** where agents can browse, code, run CLIs, install packages, edit files, and keep state across sessions.
- **Hosted products and internal tools** with Web Apps, Functions, Databases, Auth, Agent Runtimes, and Secrets.
- **Automated research and operations** with threads, schedules, triggers, skills, and reusable custom agents.
- **Python control planes** for your own apps, CI jobs, data workflows, research systems, and backend automation.

## Install

```bash
pip install computer-agents
```

Python 3.9 or newer is required.

## Authenticate

Create an API key in Computer Agents, then set:

```bash
export COMPUTER_AGENTS_API_KEY="ca_..."
```

```python
from computer_agents import ComputerAgentsClient

client = ComputerAgentsClient()
```

You can also pass the key directly:

```python
client = ComputerAgentsClient(api_key="ca_...")
```

## Cloud and Appliance Base URLs

Set `base_url` per client to target a local appliance or another Computer
Agents deployment:

```python
client = ComputerAgentsClient(
    api_key="ca_...",
    base_url="https://stockifi.computer-agents.com",
)
```

You can alternatively configure a process-wide default:

```bash
export COMPUTER_AGENTS_BASE_URL="https://stockifi.computer-agents.com"
```

An origin and an already-versioned URL are both accepted, so
`https://stockifi.computer-agents.com` and
`https://stockifi.computer-agents.com/v1` resolve to the same API. The setting
applies to regular requests, event streams, downloads, and multipart uploads.
The older `COMPUTER_AGENTS_API_URL` environment variable remains supported.

For direct HTTP calls, append the canonical `/v1` API prefix:

```bash
curl https://stockifi.computer-agents.com/v1/agents \
  -H "Authorization: Bearer $COMPUTER_AGENTS_API_KEY"
```

## Quick Start

Run a task and stream the agent's work:

```python
from computer_agents import ComputerAgentsClient

client = ComputerAgentsClient()

result = client.run(
    "Create a small FastAPI service and explain how to run it.",
    on_event=lambda event: print(event["type"]),
)

print(result.content)
print(result.thread_id)
```

## Core Concepts

| Concept | What it means |
| --- | --- |
| **Threads** | Multi-turn agent sessions with messages, logs, reasoning, diffs, permission requests, feedback, and resumable state. |
| **Computers** | Persistent cloud workspaces with files, runtimes, packages, GUI access, Git, snapshots, and deployment context. |
| **Projects** | Shared workspaces for complex work: strategy, releases, tasks, comments, resources, review state, and task-linked threads. |
| **Agents** | Reusable agent profiles with model, instructions, skills, reasoning effort, and analytics. |
| **Tests** | Versioned engineering verification plans with durable runs, case evidence, artifacts, commit identity, and pass/fail gates. |
| **Resources** | Deployable product surfaces: Web Apps, Functions, Databases, Auth, Agent Runtimes, and Secrets. |
| **Skills** | Reusable capabilities agents can invoke, such as research, image generation, app deployment, or task management. |

All 43 tenant-facing platform service groups—including prompts, knowledge,
guardrails, evaluations, Tests, assurance, fine-tuning, optimization campaigns
and candidates, Metronomes, Batches, Security Agents, evidence review,
organization administration, and billing/inference endpoints—are available as
first-class SDK managers. See the
[API and SDK capability map](../../docs/API_SDK_CAPABILITY_PARITY.md).

## Persistent Computers and Threads

Create a computer, start a thread inside it, and continue later with the same files and state:

```python
computer = client.computers.create(
    name="product-build-computer",
    internet_access=True,
)

thread = client.threads.create(environment_id=computer["id"])

client.threads.send_message(
    thread["id"],
    content="Create a Python API with a health route.",
    on_event=lambda event: print(event["type"]),
)

client.threads.send_message(
    thread["id"],
    content="Now add authentication and tests.",
)

logs = client.threads.get_logs(thread["id"])
diffs = client.threads.get_diffs(thread["id"])
```

Thread methods include `create`, `list`, `get`, `send_message`, `cancel`, `resume`, `copy`, `search`, `get_messages`, `get_logs`, `get_status`, `get_diffs`, `list_steps`, `download_step_file`, `fork_from_step`, `revert_to_step`, `set_feedback`, `report_issue`, and permission request approval/denial.

## Projects and Tasks

Use projects when agents need the same context a human team would need: the goal, current release, backlog, comments, dependencies, resources, and review policy.

```python
project = client.projects.create(
    "Customer Portal",
    description="Build and deploy an authenticated customer portal.",
)

release = client.tasks.create_release(
    project["id"],
    "v0.1 MVP",
    description="Ship the first production-ready customer workflow.",
    success_criteria=[
        "Customers can sign in and update account settings.",
        "The release passes its linked test and assurance gates.",
    ],
)

task = client.tasks.create(
    "Deploy login and account settings",
    project_id=project["id"],
    release_id=release["id"],
    status="todo",
    priority="high",
)

client.tasks.create_comment(
    task["id"],
    body="Include password reset and session validation.",
)

client.tasks.run_thread(
    task["id"],
    environment_id=computer["id"],
)
```

For an autonomous project, submit one strict delivery contract and let the
control plane create the standard graph and bindings atomically:

```python
planned = client.projects.put_delivery_plan(
    project["id"],
    contract,
    idempotency_key=f"mission-control-{project['id']}-delivery-v1",
)
delivery_plan = client.projects.provision_delivery_plan(project["id"])

print(delivery_plan["graph"]["nodes"])
print(delivery_plan["bindings"])
```

The provisioned optimization job starts in `planned`; queue it only after the
bound build, Test, and baseline Evaluation dependencies pass:

```python
optimization_job_id = delivery_plan["bindings"].get("optimizationJobId")
if optimization_job_id:
    client.fine_tuning.queue_job(
        optimization_job_id,
        source="project_delivery_graph",
    )
```

## Tests, Evaluations, and Optimization

Use `client.tests` for engineering verification. Test Plans are immutable by
version, execute in a selected Computer Agents environment, and return
case-level results plus a server-fingerprinted terminal evidence envelope.

```python
test_plan = client.tests.create(
    name="Customer Portal release gate",
    project_id=project["id"],
    target_type="project",
    definition={
        "cases": [
            {
                "id": "unit",
                "name": "Unit tests",
                "kind": "command",
                "command": "pytest",
            },
            {
                "id": "health",
                "name": "Deployed health contract",
                "kind": "contract",
                "request": {"method": "GET", "path": "/api/health"},
                "assertions": [{"kind": "status", "equals": 200}],
            },
        ]
    },
)

test_run = client.tests.run(
    test_plan["id"],
    environment_id=computer["id"],
    project_id=project["id"],
    task_id=task["id"],
    release_id=release["id"],
    commit_sha="0123456789abcdef",
    trigger_type="mission_control",
)

evidence = client.tests.get_run(test_run["id"])
print(evidence["status"], evidence["evidence"])

assurance_policy = client.assurance.create_policy(
    name="Customer Portal release assurance",
    project_id=project["id"],
    definition={
        "testGates": [
            {
                "id": "engineering",
                "testPlanId": test_plan["id"],
                "versionId": test_plan["publishedVersionId"],
                "requireCommitSha": True,
            }
        ],
        "approval": {"mode": "manual"},
    },
)

assurance_run = client.assurance.run(
    assurance_policy["id"],
    project_id=project["id"],
    release_id=release["id"],
    commit_sha="0123456789abcdef",
    evidence_references={"testRunIds": [test_run["id"]]},
)

if assurance_run["status"] == "blocked":
    client.assurance.approve(
        assurance_run["id"],
        assurance_run["evidence"]["fingerprint"],
    )
```

Tests answer whether software and workflows work. `client.evaluations` measures
behavioral quality on versioned datasets, while `client.fine_tuning` performs a
bounded optimization job from Evaluation evidence. `client.assurance` verifies
the actual terminal evidence, pins it to versioned release gates, and emits one
fingerprinted decision.

## Deployable Server Resources

Computer Agents resources let humans and agents ship software from the same workspace where the work is planned and built.

| Manager | Resource kind | Typical use |
| --- | --- | --- |
| `client.web_apps` | `web_app` | Dashboards, internal tools, portals, prototypes, AI apps. |
| `client.functions` | `function` | APIs, webhooks, jobs, data transforms, backend actions. |
| `client.databases` | Database | Collections and JSON documents for apps, functions, and agents. |
| `client.auth` | `auth` | Sign-up, sign-in, sessions, protected app workflows. |
| `client.runtimes` | `agent_runtime` | Always-on agent APIs and embedded agent services. |
| `client.secrets` | `secrets` | Secret vaults for API keys, tokens, credentials, and private config. |
| `client.resources` | Generic resources | Cross-kind automation when one workflow handles multiple resource types. |

### Create and Deploy a Function

Upload source code from a computer, create the Function, deploy it, then invoke it.

```python
client.files.upload_file(
    computer["id"],
    path="functions/hello-world",
    filename="index.mjs",
    content="""
export default async function handler(request) {
  return Response.json({ message: 'Hello from Computer Agents Functions' });
}
""",
    content_type="text/javascript",
)

fn = client.functions.create(
    name="hello-world",
    source_type="computer",
    source_environment_id=computer["id"],
    source_path="functions/hello-world",
    runtime="nodejs22",
    auth_mode="public",
)

client.functions.deploy(fn["id"])

response = client.functions.invoke(
    fn["id"],
    method="GET",
    path="/",
)

print(response)
```

Resource managers support `create`, `list`, `get`, `update`, `delete`, `deploy`, `list_deployments`, `rollback_deployment`, `invoke`, `get_analytics`, `get_logs`, `list_bindings`, `upsert_binding`, `delete_binding`, file operations, and secret operations. Auth resources also support `list_users`, `create_user`, `sign_up`, and `sign_in`.

## Databases and Secrets

Use databases for app state and structured output. Use Secrets for credentials that functions, web apps, and agents can read at runtime.

```python
import os

db = client.databases.create(name="crm-data")

leads = client.databases.create_collection(
    db["id"],
    name="leads",
)

client.databases.create_document(
    db["id"],
    leads["id"],
    data={
        "company": "Acme",
        "stage": "qualified",
        "owner": "agent",
    },
)

vault = client.secrets.create(name="production-secrets")

client.secrets.create_secret(
    vault["id"],
    name="SENDGRID_API_KEY",
    value=os.environ["SENDGRID_API_KEY"],
)

client.functions.upsert_binding(
    fn["id"],
    "database",
    target_id=db["id"],
    alias="appDatabase",
)

client.functions.upsert_binding(
    fn["id"],
    "secrets",
    target_id=vault["id"],
    alias="productionSecrets",
)
```

Server-side runtime helpers for deployed Node Functions and server-rendered Web Apps are available from the JavaScript SDK:

```ts
import { getSecretValue } from 'computer-agents/runtime/server';
```

Use this Python SDK to create, bind, deploy, invoke, monitor, and operate those resources from Python services and automation.

## Schedules, Triggers, and Orchestrations

```python
automation_agent = client.agents.list()[0]

client.schedules.create(
    "Daily competitor brief",
    automation_agent["id"],
    automation_agent["name"],
    "Research competitors and write a concise Markdown brief.",
    "recurring",
    environment_id=computer["id"],
    cron_expression="0 9 * * *",
)

client.triggers.create(
    "New lead enrichment",
    computer["id"],
    "webhook",
    "lead.created",
    {
        "type": "send_message",
        "message": "Enrich the new lead and update the CRM database.",
    },
    agent_id=automation_agent["id"],
)

client.orchestrations.create(
    "Research and build landing page",
    computer["id"],
    "sequential",
    [
        {
            "agentId": automation_agent["id"],
            "name": "Research market",
            "instructions": "Research the market and summarize the findings.",
        },
        {
            "agentId": automation_agent["id"],
            "name": "Build landing page",
            "instructions": "Use the research to write and deploy a landing page.",
        },
    ],
)
```

## Agents and Models

```python
models = client.agents.list_models()
model = next(entry["id"] for entry in models["models"] if not entry.get("locked"))

agent = client.agents.create(
    name="Senior Product Engineer",
    model=model,
    instructions="Build carefully, test changes, and explain tradeoffs.",
    reasoning_effort="high",
)
```

Computer Agents supports built-in models from Anthropic, OpenAI, Gemini, DeepSeek, Kimi, and connected external models on supported plans. Use `client.agents.list_models()` to read the current catalog instead of hard-coding model availability.

## Budget and Usage

```python
budget = client.budget.get_status()
can_run = client.budget.can_execute()
usage = client.billing.get_stats(days=30)

print({
    "budget": budget,
    "can_run": can_run,
    "usage": usage,
})
```

## Context Manager

```python
with ComputerAgentsClient(api_key="ca_...") as client:
    result = client.run("Hello world")
    print(result.content)
```

## SDK Surface

| Manager | Scope |
| --- | --- |
| `client.threads` | Messages, logs, diffs, research, feedback, permission requests, and thread lifecycle. |
| `client.computers` / `client.environments` | Persistent cloud computers, runtimes, packages, snapshots, GUI, analytics. |
| `client.files` | Workspace files and directories. |
| `client.git` | Git status, diffs, commits, branches, clone, push. |
| `client.projects` | Project lifecycle, project files, schedules, computers, sync. |
| `client.tasks` | Tasks, comments, releases, sprints, and task-linked threads. |
| `client.agents` | Agent profiles, models, analytics. |
| `client.web_apps`, `client.functions`, `client.auth`, `client.databases`, `client.runtimes`, `client.secrets` | Product resources. |
| `client.resources` | Generic server resource operations. |
| `client.skills` | Custom skills. |
| `client.schedules`, `client.triggers`, `client.orchestrations` | Recurring, event-driven, and multi-agent work. |
| `client.notifications` | In-app notifications and push tokens. |
| `client.budget` / `client.billing` | Budget checks, checkout, usage, and transactions. |

## Links

- [Website](https://computer-agents.com)
- [Documentation](https://computer-agents.com/developers)
- [API Reference](https://computer-agents.com/api-reference)
- [PyPI](https://pypi.org/project/computer-agents/)
- [GitHub](https://github.com/computer-agents/computer-agents-sdk-python)

## License

MIT
