"""Agents resource manager.

Handles agent configuration including CRUD operations
and model/skill configuration.
"""

from __future__ import annotations

from typing import Any

from .._api_client import ApiClient
from ..types import AgentModelCatalogResponse, CloudAgent
from .versioning import VersioningResource


class AgentsResource:
    """Agent configuration.

    Create and manage agent configurations, instructions, skills,
    and workspace model selection.

    Example::

        agent = client.agents.create(
            name="Code Assistant",
            model="claude-sonnet-4-5",
            instructions="You are a helpful coding assistant.",
        )
    """

    def __init__(self, client: ApiClient) -> None:
        self._client = client
        self._versions = VersioningResource(client, "/agents")

    def create(
        self,
        name: str,
        model: str,
        *,
        description: str | None = None,
        instructions: str | None = None,
        agent_id: str | None = None,
        binary: str | None = None,
        execution_engine: str | None = None,
        reasoning_effort: str | None = None,
        enabled_skills: list[str] | None = None,
        deep_research_model: str | None = None,
        permission_set: dict[str, Any] | None = None,
        voice_mode: str | None = None,
        voice_provider: str | None = None,
        voice_model: str | None = None,
        voice_id: str | None = None,
        voice_instructions: str | None = None,
        voice_language_hint: str | None = None,
        voice_turn_detection: dict[str, Any] | None = None,
        voice_pronunciation_replacements: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        is_default: bool | None = None,
        is_system: bool | None = None,
    ) -> CloudAgent:
        """Create a new agent."""
        body: dict[str, Any] = {"name": name, "model": model}
        if agent_id is not None:
            body["id"] = agent_id
        if description is not None:
            body["description"] = description
        if instructions is not None:
            body["instructions"] = instructions
        if binary is not None:
            body["binary"] = binary
        if execution_engine is not None:
            body["executionEngine"] = execution_engine
        if reasoning_effort is not None:
            body["reasoningEffort"] = reasoning_effort
        if enabled_skills is not None:
            body["enabledSkills"] = enabled_skills
        if deep_research_model is not None:
            body["deepResearchModel"] = deep_research_model
        if permission_set is not None:
            body["permissionSet"] = permission_set
        if voice_mode is not None:
            body["voiceMode"] = voice_mode
        if voice_provider is not None:
            body["voiceProvider"] = voice_provider
        if voice_model is not None:
            body["voiceModel"] = voice_model
        if voice_id is not None:
            body["voiceId"] = voice_id
        if voice_instructions is not None:
            body["voiceInstructions"] = voice_instructions
        if voice_language_hint is not None:
            body["voiceLanguageHint"] = voice_language_hint
        if voice_turn_detection is not None:
            body["voiceTurnDetection"] = voice_turn_detection
        if voice_pronunciation_replacements is not None:
            body["voicePronunciationReplacements"] = voice_pronunciation_replacements
        if metadata is not None:
            body["metadata"] = metadata
        if is_default is not None:
            body["isDefault"] = is_default
        if is_system is not None:
            body["isSystem"] = is_system
        resp = self._client.post("/agents", body)
        return resp["agent"]

    def list(self, *, limit: int | None = None, view: str | None = None) -> list[CloudAgent]:
        """List all agents."""
        query: dict[str, Any] = {}
        if limit is not None:
            query["limit"] = limit
        if view is not None:
            query["view"] = view
        resp = self._client.get("/agents", query=query or None)
        return resp["data"]

    def list_models(self) -> AgentModelCatalogResponse:
        """List built-in and external model entries available to this workspace."""
        return self._client.get("/agents/models")

    def get(self, agent_id: str) -> CloudAgent:
        """Get an agent by ID."""
        resp = self._client.get(f"/agents/{agent_id}")
        return resp["agent"]

    def update(self, agent_id: str, **params: Any) -> CloudAgent:
        """Update an agent.

        Args:
            agent_id: Agent ID.
            name: New name.
            description: New description.
            model: New model.
            instructions: New instructions.
            execution_engine: Execution engine (`computer-agents-cli`, `native-claude`, or `grok-build`).
            reasoning_effort: New reasoning effort.
            enabled_skills: New list of enabled skills.
            metadata: New metadata.
        """
        body: dict[str, Any] = {}
        key_map = {
            "name": "name",
            "description": "description",
            "model": "model",
            "instructions": "instructions",
            "binary": "binary",
            "execution_engine": "executionEngine",
            "reasoning_effort": "reasoningEffort",
            "enabled_skills": "enabledSkills",
            "deep_research_model": "deepResearchModel",
            "permission_set": "permissionSet",
            "voice_mode": "voiceMode",
            "voice_provider": "voiceProvider",
            "voice_model": "voiceModel",
            "voice_id": "voiceId",
            "voice_instructions": "voiceInstructions",
            "voice_language_hint": "voiceLanguageHint",
            "voice_turn_detection": "voiceTurnDetection",
            "voice_pronunciation_replacements": "voicePronunciationReplacements",
            "metadata": "metadata",
        }
        for py_key, api_key in key_map.items():
            if py_key in params:
                body[api_key] = params[py_key]
        resp = self._client.patch(f"/agents/{agent_id}", body)
        return resp["agent"]

    def get_analytics(self, agent_id: str) -> dict[str, Any]:
        """Summarize recent activity for an agent or team."""
        return self._client.get(f"/agents/{agent_id}/analytics")

    def get_analytics_overview(self, *, period: str | None = None) -> dict[str, Any]:
        """Get aggregate analytics across every accessible Agent."""
        query = {"period": period} if period is not None else None
        return self._client.get("/agents/analytics/overview", query=query)

    def list_versions(self, agent_id: str) -> list[dict[str, Any]]:
        """List saved agent versions."""
        return self._versions.list(agent_id)

    def get_version(self, agent_id: str, version_id: str) -> dict[str, Any]:
        """Get one saved agent version."""
        return self._versions.get(agent_id, version_id)

    def create_version(self, agent_id: str, **params: Any) -> dict[str, Any]:
        """Save the current agent or a supplied snapshot as a version."""
        return self._versions.create(agent_id, **params)

    def update_version(self, agent_id: str, version_id: str, **params: Any) -> dict[str, Any]:
        """Rename or update a saved agent version."""
        return self._versions.update(agent_id, version_id, **params)

    def delete_version(self, agent_id: str, version_id: str) -> bool:
        """Delete a saved agent version."""
        return self._versions.delete(agent_id, version_id)

    def publish_version(self, agent_id: str, version_id: str, **params: Any) -> dict[str, Any]:
        """Publish a saved agent version."""
        return self._versions.publish(agent_id, version_id, **params)

    def unpublish_version(self, agent_id: str, version_id: str) -> dict[str, Any]:
        """Unpublish a saved agent version."""
        return self._versions.unpublish(agent_id, version_id)

    def restore_version(self, agent_id: str, version_id: str) -> dict[str, Any]:
        """Restore a saved version into the editable agent configuration."""
        return self._versions.restore(agent_id, version_id)

    def compare_versions(self, agent_id: str, *, base_version_id: str, target_version_id: str) -> dict[str, Any]:
        """Compare two agent versions."""
        return self._versions.compare(
            agent_id,
            base_version_id=base_version_id,
            target_version_id=target_version_id,
        )

    def list_guardrails(self, agent_id: str) -> list[dict[str, Any]]:
        """List guardrail sets attached to an agent."""
        response = self._client.get(f"/agents/{agent_id}/guardrails")
        if isinstance(response, dict):
            return response.get("data") or response.get("guardrails") or response.get("sets") or []
        return []

    def set_guardrails(self, agent_id: str, guardrail_set_ids: list[str]) -> CloudAgent:
        """Replace the guardrail sets attached to an agent."""
        response = self._client.put(
            f"/agents/{agent_id}/guardrails",
            {"guardrailSetIds": guardrail_set_ids},
        )
        return response["agent"]

    def add_guardrail(self, agent_id: str, guardrail_id: str) -> CloudAgent:
        """Attach one guardrail set to an agent."""
        response = self._client.put(f"/agents/{agent_id}/guardrails/{guardrail_id}", {})
        return response["agent"]

    def remove_guardrail(self, agent_id: str, guardrail_id: str) -> CloudAgent | None:
        """Detach one guardrail set from an agent."""
        response = self._client.delete(f"/agents/{agent_id}/guardrails/{guardrail_id}")
        if isinstance(response, dict):
            return response.get("agent")
        return None

    def delete(self, agent_id: str, *, hard: bool = False) -> None:
        """Delete an agent."""
        self._client.request(
            "DELETE",
            f"/agents/{agent_id}",
            query={"hard": True} if hard else None,
        )
