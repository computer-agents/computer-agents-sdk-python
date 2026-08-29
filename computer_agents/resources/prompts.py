"""Versioned prompt templates."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from .._api_client import ApiClient


def _id(value: str) -> str:
    return quote(value, safe="")


class PromptsResource:
    """Manage Prompt resources from Configure mode."""

    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def list(self) -> list[dict[str, Any]]:
        response = self._client.get("/prompts")
        return response.get("data", response.get("prompts", []))

    def get(self, prompt_id: str) -> dict[str, Any]:
        return self._client.get(f"/prompts/{_id(prompt_id)}")["prompt"]

    def create(self, name: str, **params: Any) -> dict[str, Any]:
        return self._client.post("/prompts", {"name": name, **params})

    def update(self, prompt_id: str, **params: Any) -> dict[str, Any]:
        return self._client.patch(f"/prompts/{_id(prompt_id)}", params)["prompt"]

    def delete(self, prompt_id: str) -> bool:
        response = self._client.delete(f"/prompts/{_id(prompt_id)}")
        return response is None or response.get("deleted", True)

    def create_version(self, prompt_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(f"/prompts/{_id(prompt_id)}/versions", params)

    def update_version(
        self,
        prompt_id: str,
        version_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.patch(
            f"/prompts/{_id(prompt_id)}/versions/{_id(version_id)}",
            params,
        )

    def publish_version(self, prompt_id: str, version_id: str) -> dict[str, Any]:
        return self._client.post(
            f"/prompts/{_id(prompt_id)}/versions/{_id(version_id)}/publish",
            {},
        )

    def update_version_publication(
        self,
        prompt_id: str,
        version_id: str,
        *,
        published: bool,
    ) -> dict[str, Any]:
        """Update publication state for a prompt version."""
        return self._client.patch(
            f"/prompts/{_id(prompt_id)}/versions/{_id(version_id)}/publish",
            {"published": published},
        )

    def unpublish_version(self, prompt_id: str, version_id: str) -> dict[str, Any]:
        """Unpublish a prompt version."""
        return self.update_version_publication(
            prompt_id,
            version_id,
            published=False,
        )
