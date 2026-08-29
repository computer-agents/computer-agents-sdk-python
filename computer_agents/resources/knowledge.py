"""Versioned Knowledge libraries and citation-ready retrieval."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from .._api_client import ApiClient


def _id(value: str) -> str:
    return quote(value, safe="")


class KnowledgeResource:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def parse_document(
        self,
        filename: str,
        content: str | bytes,
        *,
        content_type: str | None = None,
    ) -> dict[str, Any]:
        """Convert a supported source document to editable Markdown staging data."""
        payload = content.encode() if isinstance(content, str) else content
        return self._client.request_form(
            "POST",
            "/knowledge/parse",
            files={
                "file": (
                    filename,
                    payload,
                    content_type or "application/octet-stream",
                )
            },
        )

    def list(self) -> list[dict[str, Any]]:
        response = self._client.get("/knowledge")
        return response.get("data", response.get("libraries", []))

    def get(self, library_id: str) -> dict[str, Any]:
        return self._client.get(f"/knowledge/{_id(library_id)}")["library"]

    def create(self, name: str, **params: Any) -> dict[str, Any]:
        return self._client.post("/knowledge", {"name": name, **params})["library"]

    def update(self, library_id: str, **params: Any) -> dict[str, Any]:
        return self._client.patch(f"/knowledge/{_id(library_id)}", params)["library"]

    def delete(self, library_id: str) -> bool:
        response = self._client.delete(f"/knowledge/{_id(library_id)}")
        return response is None or response.get("deleted", True)

    def search(self, query: str, **params: Any) -> dict[str, Any]:
        return self._client.post("/knowledge/search", {"query": query, **params})

    def list_documents(
        self,
        library_id: str,
        *,
        version_id: str | None = None,
    ) -> list[dict[str, Any]]:
        response = self._client.get(
            f"/knowledge/{_id(library_id)}/documents",
            query={"versionId": version_id},
        )
        return response.get("data", response.get("documents", []))

    def get_document(
        self,
        library_id: str,
        document_id: str,
        *,
        version_id: str | None = None,
    ) -> dict[str, Any]:
        response = self._client.get(
            f"/knowledge/{_id(library_id)}/documents/{_id(document_id)}",
            query={"versionId": version_id},
        )
        return response.get("document", response)

    def create_document(
        self,
        library_id: str,
        title: str,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.post(
            f"/knowledge/{_id(library_id)}/documents",
            {"title": title, **params},
        )

    def update_document(
        self,
        library_id: str,
        document_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.patch(
            f"/knowledge/{_id(library_id)}/documents/{_id(document_id)}",
            params,
        )

    def archive_document(self, library_id: str, document_id: str) -> bool:
        response = self._client.delete(
            f"/knowledge/{_id(library_id)}/documents/{_id(document_id)}"
        )
        return response is None or response.get("deleted", True)

    def propose_document(self, library_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(
            f"/knowledge/{_id(library_id)}/proposals",
            params,
        )

    def list_versions(self, library_id: str) -> list[dict[str, Any]]:
        response = self._client.get(f"/knowledge/{_id(library_id)}/versions")
        return response.get("data", response.get("versions", []))

    def get_version(self, library_id: str, version_id: str) -> dict[str, Any]:
        return self._client.get(
            f"/knowledge/{_id(library_id)}/versions/{_id(version_id)}"
        )

    def create_version(self, library_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(f"/knowledge/{_id(library_id)}/versions", params)

    def publish_version(self, library_id: str, version_id: str) -> dict[str, Any]:
        return self._client.post(
            f"/knowledge/{_id(library_id)}/versions/{_id(version_id)}/publish",
            {},
        )

    def restore_version(self, library_id: str, version_id: str) -> dict[str, Any]:
        return self._client.post(
            f"/knowledge/{_id(library_id)}/versions/{_id(version_id)}/restore",
            {},
        )

    def compare_versions(
        self,
        library_id: str,
        *,
        base_version_id: str,
        target_version_id: str,
    ) -> dict[str, Any]:
        return self._client.get(
            f"/knowledge/{_id(library_id)}/versions/compare",
            query={
                "baseVersionId": base_version_id,
                "targetVersionId": target_version_id,
            },
        )
