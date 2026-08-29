"""Guardrails resource manager."""

from __future__ import annotations

from typing import Any

from .._api_client import ApiClient
from .versioning import VersioningResource


class GuardrailsResource:
    """Reusable invisible prompt adaptation sets."""

    def __init__(self, client: ApiClient) -> None:
        self._client = client
        self._versions = VersioningResource(client, "/guardrails")

    @staticmethod
    def _unwrap(response: Any, *keys: str) -> Any:
        if not isinstance(response, dict):
            return response
        for key in ("data", *keys):
            value = response.get(key)
            if value is not None:
                return value
        return response

    def list(
        self,
        *,
        type: str | None = None,
        q: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        query = {
            "type": None if type == "all" else type,
            "q": q,
            "limit": limit,
            "offset": offset,
        }
        response = self._client.get("/guardrails", query=query)
        return self._unwrap(response, "guardrails", "sets") or []

    def get(self, guardrail_id: str) -> dict[str, Any]:
        response = self._client.get(f"/guardrails/{guardrail_id}")
        return self._unwrap(response, "guardrail", "set")

    def get_evaluation_target(
        self,
        guardrail_id: str,
        *,
        version_id: str | None = None,
    ) -> dict[str, Any]:
        """Resolve the immutable Evaluation target configured for this Guardrail."""
        return self._client.get(
            f"/guardrails/{guardrail_id}/evaluation-target",
            query={"versionId": version_id},
        )

    def create(
        self,
        *,
        name: str,
        description: str | None = None,
        prompts: list[dict[str, Any]] | None = None,
        policy: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"name": name}
        if description is not None:
            body["description"] = description
        if prompts is not None:
            body["prompts"] = prompts
        if policy is not None:
            body["policy"] = policy
        if metadata is not None:
            body["metadata"] = metadata
        response = self._client.post("/guardrails", body)
        return self._unwrap(response, "guardrail", "set")

    def update(self, guardrail_id: str, **params: Any) -> dict[str, Any]:
        response = self._client.patch(f"/guardrails/{guardrail_id}", params)
        return self._unwrap(response, "guardrail", "set")

    def delete(self, guardrail_id: str) -> bool:
        response = self._client.delete(f"/guardrails/{guardrail_id}")
        if not isinstance(response, dict):
            return True
        return bool(response.get("deleted", response.get("success", True)))

    def attach_to_agent(self, agent_id: str, guardrail_id: str) -> dict[str, Any]:
        return self._client.put(f"/agents/{agent_id}/guardrails/{guardrail_id}", {})

    def detach_from_agent(self, agent_id: str, guardrail_id: str) -> dict[str, Any] | None:
        response = self._client.delete(f"/agents/{agent_id}/guardrails/{guardrail_id}")
        return response if isinstance(response, dict) else None

    def set_agent_guardrails(self, agent_id: str, guardrail_set_ids: list[str]) -> dict[str, Any]:
        return self._client.put(
            f"/agents/{agent_id}/guardrails",
            {"guardrailSetIds": guardrail_set_ids},
        )

    def list_versions(self, guardrail_id: str) -> list[dict[str, Any]]:
        return self._versions.list(guardrail_id)

    def get_version(self, guardrail_id: str, version_id: str) -> dict[str, Any]:
        return self._versions.get(guardrail_id, version_id)

    def create_version(self, guardrail_id: str, **params: Any) -> dict[str, Any]:
        return self._versions.create(guardrail_id, **params)

    def update_version(self, guardrail_id: str, version_id: str, **params: Any) -> dict[str, Any]:
        return self._versions.update(guardrail_id, version_id, **params)

    def delete_version(self, guardrail_id: str, version_id: str) -> bool:
        return self._versions.delete(guardrail_id, version_id)

    def publish_version(
        self,
        guardrail_id: str,
        version_id: str,
        *,
        snapshot: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        params = {"snapshot": snapshot} if snapshot is not None else {}
        return self._versions.publish(guardrail_id, version_id, **params)

    def unpublish_version(self, guardrail_id: str, version_id: str) -> dict[str, Any]:
        return self._versions.unpublish(guardrail_id, version_id)

    def restore_version(self, guardrail_id: str, version_id: str) -> dict[str, Any]:
        return self._versions.restore(guardrail_id, version_id)

    def compare_versions(self, guardrail_id: str, *, base_version_id: str, target_version_id: str) -> dict[str, Any]:
        return self._versions.compare(
            guardrail_id,
            base_version_id=base_version_id,
            target_version_id=target_version_id,
        )
