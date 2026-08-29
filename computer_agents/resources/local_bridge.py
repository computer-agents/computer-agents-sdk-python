"""Low-level local-appliance and workspace bridge control plane."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from .._api_client import ApiClient


def _id(value: str) -> str:
    return quote(value, safe="")


def _list(response: dict[str, Any]) -> dict[str, Any]:
    return {
        "data": response.get("data", []),
        "total": response.get("total_count", response.get("total", 0)),
    }


def _query(params: dict[str, Any], **values: Any) -> dict[str, Any] | None:
    query = dict(params)
    query.update({key: value for key, value in values.items() if value is not None})
    return query or None


class LocalBridgeResource:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def list_devices(
        self,
        *,
        status: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        return _list(self._client.get(
            "/devices",
            query=_query(params, status=status, limit=limit, offset=offset),
        ))

    def create_device(self, **params: Any) -> dict[str, Any]:
        return self._client.post("/devices", params)["device"]

    def get_device(self, device_id: str) -> dict[str, Any]:
        return self._client.get(f"/devices/{_id(device_id)}")["device"]

    def update_device(self, device_id: str, **params: Any) -> dict[str, Any]:
        return self._client.patch(f"/devices/{_id(device_id)}", params)["device"]

    def heartbeat_device(self, device_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(
            f"/devices/{_id(device_id)}/heartbeat",
            params,
        )["device"]

    def delete_device(self, device_id: str) -> None:
        self._client.delete(f"/devices/{_id(device_id)}")

    def list_runtime_targets(self) -> dict[str, Any]:
        return self._client.get("/runtime-targets")

    def create_runner_pairing_token(self, **params: Any) -> dict[str, Any]:
        return self._client.post("/local-runner-pairing-tokens", params)

    def get_runner_pairing_token(self, pairing_token_id: str) -> dict[str, Any]:
        return self._client.get(
            f"/local-runner-pairing-tokens/{_id(pairing_token_id)}"
        )["pairingToken"]

    def exchange_runner_pairing_token(self, **params: Any) -> dict[str, Any]:
        return self._client.post("/local-runner-pairing-tokens/exchange", params)

    def list_bindings(
        self,
        *,
        device_id: str | None = None,
        environment_id: str | None = None,
        project_id: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        query = _query(
            params,
            deviceId=device_id,
            environmentId=environment_id,
            projectId=project_id,
            limit=limit,
            offset=offset,
        )
        if query is not None and query.get("projectId") is None and "projectId" in query:
            query["projectId"] = "none"
        return _list(self._client.get("/workspace-bindings", query=query))

    def create_binding(self, **params: Any) -> dict[str, Any]:
        return self._client.post("/workspace-bindings", params)["binding"]

    def get_binding(self, binding_id: str) -> dict[str, Any]:
        return self._client.get(f"/workspace-bindings/{_id(binding_id)}")["binding"]

    def update_binding(self, binding_id: str, **params: Any) -> dict[str, Any]:
        return self._client.patch(
            f"/workspace-bindings/{_id(binding_id)}",
            params,
        )["binding"]

    def delete_binding(self, binding_id: str) -> None:
        self._client.delete(f"/workspace-bindings/{_id(binding_id)}")

    def list_push_sessions(
        self,
        binding_id: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
        status: str | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        return _list(
            self._client.get(
                f"/workspace-bindings/{_id(binding_id)}/push-sessions",
                query=_query(params, limit=limit, offset=offset, status=status),
            )
        )

    def get_push_session(self, binding_id: str, session_id: str) -> dict[str, Any]:
        return self._client.get(
            f"/workspace-bindings/{_id(binding_id)}/push-sessions/{_id(session_id)}"
        )["pushSession"]

    def prepare_push_session(self, binding_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(
            f"/workspace-bindings/{_id(binding_id)}/push-sessions",
            params,
        )

    def list_pull_sessions(
        self,
        binding_id: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
        status: str | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        return _list(
            self._client.get(
                f"/workspace-bindings/{_id(binding_id)}/pull-sessions",
                query=_query(params, limit=limit, offset=offset, status=status),
            )
        )

    def get_pull_session(self, binding_id: str, session_id: str) -> dict[str, Any]:
        return self._client.get(
            f"/workspace-bindings/{_id(binding_id)}/pull-sessions/{_id(session_id)}"
        )["pullSession"]

    def prepare_pull_session(self, binding_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(
            f"/workspace-bindings/{_id(binding_id)}/pull-sessions",
            params,
        )

    def attach_pull_session_apply_preview(
        self,
        binding_id: str,
        session_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.post(
            f"/workspace-bindings/{_id(binding_id)}/pull-sessions/"
            f"{_id(session_id)}/apply-preview",
            params,
        )

    def attach_pull_session_apply_result(
        self,
        binding_id: str,
        session_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.post(
            f"/workspace-bindings/{_id(binding_id)}/pull-sessions/"
            f"{_id(session_id)}/apply-result",
            params,
        )

    def list_local_sessions(
        self,
        thread_id: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
        status: str | None = None,
        device_id: str | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        return _list(
            self._client.get(
                f"/threads/{_id(thread_id)}/local-sessions",
                query=_query(
                    params,
                    limit=limit,
                    offset=offset,
                    status=status,
                    deviceId=device_id,
                ),
            )
        )

    def create_local_session(self, thread_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(
            f"/threads/{_id(thread_id)}/local-sessions",
            params,
        )["session"]

    def get_local_session(self, thread_id: str, session_id: str) -> dict[str, Any]:
        return self._client.get(
            f"/threads/{_id(thread_id)}/local-sessions/{_id(session_id)}"
        )["session"]

    def heartbeat_local_session(
        self,
        thread_id: str,
        session_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.post(
            f"/threads/{_id(thread_id)}/local-sessions/{_id(session_id)}/heartbeat",
            params,
        )["session"]

    def complete_local_session(
        self,
        thread_id: str,
        session_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.post(
            f"/threads/{_id(thread_id)}/local-sessions/{_id(session_id)}/complete",
            params,
        )["session"]

    def poll_local_session_commands(
        self,
        thread_id: str,
        session_id: str,
        *,
        limit: int | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        return _list(
            self._client.get(
                f"/threads/{_id(thread_id)}/local-sessions/{_id(session_id)}/control/poll",
                query=_query(params, limit=limit),
            )
        )

    def enqueue_local_session_command(
        self,
        thread_id: str,
        session_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.post(
            f"/threads/{_id(thread_id)}/local-sessions/{_id(session_id)}/control",
            params,
        )["command"]

    def acknowledge_local_session_command(
        self,
        thread_id: str,
        session_id: str,
        command_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.post(
            f"/threads/{_id(thread_id)}/local-sessions/{_id(session_id)}/control/"
            f"{_id(command_id)}/ack",
            params,
        )["command"]

    def ingest_thread_events(
        self,
        thread_id: str,
        events: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return self._client.post(
            f"/threads/{_id(thread_id)}/events/ingest",
            {"events": events},
        )
