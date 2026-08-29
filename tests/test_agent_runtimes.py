from __future__ import annotations

from typing import Any

from computer_agents.resources.product_resources import AgentRuntimesResource


class RecordingClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, dict[str, Any] | None]] = []

    def get(self, path: str, *, query: dict[str, Any] | None = None) -> dict[str, Any]:
        self.calls.append(("GET", path, query))
        if path.endswith("/deployments"):
            return {"deployments": [{"id": "deployment-one"}]}
        if path.endswith("/events"):
            return {"events": [{"type": "completed"}]}
        if path.endswith("/runs"):
            return {"runs": [{"id": "run-one"}]}
        if path == "/agent-runtimes":
            return {"data": [{"id": "runtime-one"}]}
        return {
            "server": {"id": "runtime-one"},
            "agentRuntime": {"id": "runtime-one", "deployed": True},
        }

    def post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(("POST", path, body))
        if path == "/agent-runtimes":
            return {"server": {"id": "runtime-one"}}
        return {"id": "run-one", "status": "running"}

    def patch(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(("PATCH", path, body))
        return {"server": {"id": "runtime-one", **body}}

    def delete(self, path: str) -> dict[str, Any]:
        self.calls.append(("DELETE", path, None))
        return {"deleted": True}


def test_agent_runtime_resource_uses_canonical_encoded_paths() -> None:
    client = RecordingClient()
    runtimes = AgentRuntimesResource(client)  # type: ignore[arg-type]

    assert runtimes.create(name="Production runtime")["id"] == "runtime-one"
    assert runtimes.list(project_id="project-one", limit=20, offset=10)[0]["id"] == "runtime-one"
    assert runtimes.get("runtime/one")["id"] == "runtime-one"
    assert runtimes.get_deployment("runtime/one")["deployed"] is True
    assert runtimes.update("runtime/one", name="Renamed")["name"] == "Renamed"
    assert runtimes.delete("runtime/one") is True

    assert client.calls == [
        ("POST", "/agent-runtimes", {"name": "Production runtime"}),
        (
            "GET",
            "/agent-runtimes",
            {"projectId": "project-one", "limit": 20, "offset": 10},
        ),
        ("GET", "/agent-runtimes/runtime%2Fone", None),
        ("GET", "/agent-runtimes/runtime%2Fone", None),
        ("PATCH", "/agent-runtimes/runtime%2Fone", {"name": "Renamed"}),
        ("DELETE", "/agent-runtimes/runtime%2Fone", None),
    ]


def test_agent_runtime_resource_exposes_lifecycle_and_thread_backed_runs() -> None:
    client = RecordingClient()
    runtimes = AgentRuntimesResource(client)  # type: ignore[arg-type]

    runtimes.deploy("runtime/one")
    runtimes.decommission("runtime/one")
    assert runtimes.list_deployments("runtime/one")[0]["id"] == "deployment-one"
    assert runtimes.list_runs("runtime/one", limit=5)[0]["id"] == "run-one"
    runtimes.start_run(
        "runtime/one",
        content="Hello",
        title="Production request",
        mode="async",
        metadata={"requestId": "request-one"},
    )
    runtimes.get_run("runtime/one", "run/one")
    runtimes.send_input("runtime/one", "run/one", prompt="Continue", mode="sync")
    assert runtimes.get_events("runtime/one", "run/one")[0]["type"] == "completed"
    runtimes.cancel_run("runtime/one", "run/one")

    assert client.calls == [
        ("POST", "/agent-runtimes/runtime%2Fone/deploy", {}),
        ("POST", "/agent-runtimes/runtime%2Fone/decommission", {}),
        ("GET", "/agent-runtimes/runtime%2Fone/deployments", None),
        ("GET", "/agent-runtimes/runtime%2Fone/runs", {"limit": 5}),
        (
            "POST",
            "/agent-runtimes/runtime%2Fone/runs",
            {
                "content": "Hello",
                "title": "Production request",
                "mode": "async",
                "metadata": {"requestId": "request-one"},
            },
        ),
        ("GET", "/agent-runtimes/runtime%2Fone/runs/run%2Fone", None),
        (
            "POST",
            "/agent-runtimes/runtime%2Fone/runs/run%2Fone/input",
            {"prompt": "Continue", "mode": "sync"},
        ),
        ("GET", "/agent-runtimes/runtime%2Fone/runs/run%2Fone/events", None),
        ("POST", "/agent-runtimes/runtime%2Fone/runs/run%2Fone/cancel", {}),
    ]
