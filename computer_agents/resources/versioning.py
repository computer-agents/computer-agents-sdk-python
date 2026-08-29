"""Shared resource versioning helpers."""

from __future__ import annotations

from typing import Any

from .._api_client import ApiClient


def normalize_version_number(value: Any, fallback: int = 0) -> int:
    """Return a non-negative integer resource version number."""
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized.startswith("version"):
            normalized = normalized[7:].strip()
        elif normalized.startswith("v"):
            normalized = normalized[1:].strip()
        value = normalized
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = int(fallback)
    return max(0, parsed)


def format_version_label(value: Any) -> str:
    """Return the canonical zero-based vN resource version label."""
    return f"v{normalize_version_number(value)}"


def format_version_title(value: Any, description: Any = None) -> str:
    """Return vN, optionally followed by a short human description."""
    label = format_version_label(value)
    normalized_description = str(description or "").strip()
    return f"{label} | {normalized_description}" if normalized_description else label


class VersioningResource:
    """Reusable REST wrapper for publishable, versioned resources."""

    def __init__(self, client: ApiClient, base_path: str) -> None:
        self._client = client
        self._base_path = base_path.rstrip("/")

    @staticmethod
    def _unwrap_list(response: Any, *keys: str) -> list[dict[str, Any]]:
        if isinstance(response, list):
            return response
        if not isinstance(response, dict):
            return []
        for key in ("data", "items", *keys):
            value = response.get(key)
            if isinstance(value, list):
                return value
        return []

    @staticmethod
    def _unwrap_object(response: Any, *keys: str) -> dict[str, Any]:
        if not isinstance(response, dict):
            return {}
        for key in ("data", *keys):
            value = response.get(key)
            if isinstance(value, dict):
                return value
        return response

    def list(self, resource_id: str) -> list[dict[str, Any]]:
        response = self._client.get(f"{self._base_path}/{resource_id}/versions")
        return self._unwrap_list(response, "versions")

    def get(self, resource_id: str, version_id: str) -> dict[str, Any]:
        response = self._client.get(f"{self._base_path}/{resource_id}/versions/{version_id}")
        return self._unwrap_object(response, "version")

    def create(self, resource_id: str, **params: Any) -> dict[str, Any]:
        response = self._client.post(f"{self._base_path}/{resource_id}/versions", params)
        return self._unwrap_object(response, "version")

    def update(self, resource_id: str, version_id: str, **params: Any) -> dict[str, Any]:
        response = self._client.patch(f"{self._base_path}/{resource_id}/versions/{version_id}", params)
        return self._unwrap_object(response, "version")

    def delete(self, resource_id: str, version_id: str) -> bool:
        response = self._client.delete(f"{self._base_path}/{resource_id}/versions/{version_id}")
        if not isinstance(response, dict):
            return True
        return bool(response.get("deleted", response.get("success", True)))

    def publish(self, resource_id: str, version_id: str, **params: Any) -> dict[str, Any]:
        response = self._client.post(
            f"{self._base_path}/{resource_id}/versions/{version_id}/publish",
            params,
        )
        return self._unwrap_object(response)

    def unpublish(self, resource_id: str, version_id: str) -> dict[str, Any]:
        response = self._client.post(f"{self._base_path}/{resource_id}/versions/{version_id}/unpublish", {})
        return self._unwrap_object(response)

    def restore(self, resource_id: str, version_id: str) -> dict[str, Any]:
        response = self._client.post(f"{self._base_path}/{resource_id}/versions/{version_id}/restore", {})
        return self._unwrap_object(response)

    def compare(self, resource_id: str, *, base_version_id: str, target_version_id: str) -> dict[str, Any]:
        return self._client.get(
            f"{self._base_path}/{resource_id}/versions/compare",
            query={
                "baseVersionId": base_version_id,
                "targetVersionId": target_version_id,
            },
        )
