"""Files resource manager.

Handles file operations within environment workspaces.
Files are scoped to environments.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from .._api_client import ApiClient


class FilesResource:
    """File operations on environment workspaces.

    Upload, download, and manage files in environment workspaces.

    Example::

        files = client.files.list("env_xxx")
        content = client.files.get_file("env_xxx", "src/app.py")
    """

    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def list(
        self,
        environment_id: str,
        *,
        path: str | None = None,
        depth: int | None = None,
    ) -> dict[str, Any]:
        """List all files in an environment workspace.

        Returns the API's path-aware listing envelope.
        """
        query: dict[str, Any] = {}
        if path is not None:
            query["path"] = path
        if depth is not None:
            query["depth"] = depth
        resp = self._client.get(
            f"/environments/{environment_id}/files",
            query=query or None,
        )
        files = resp.get("files", resp.get("data", []))
        return {
            "environmentId": resp.get("environmentId", environment_id),
            "path": resp.get("path", path or ""),
            "depth": resp.get("depth", depth if depth is not None else 1),
            "files": files,
            "count": resp.get("count", len(files)),
        }

    def list_files(
        self,
        environment_id: str,
        *,
        path: str | None = None,
        depth: int | None = None,
    ) -> list[dict[str, Any]]:
        """List files (returns just the file list)."""
        return self.list(environment_id, path=path, depth=depth)["files"]

    def get_file(self, environment_id: str, file_path: str) -> str:
        """Download a file as text.

        Args:
            environment_id: Environment ID.
            file_path: Path to the file (e.g. ``"src/app.py"``).
        """
        normalized = file_path.lstrip("/")
        encoded = "/".join(quote(part, safe="") for part in normalized.split("/"))
        resp = self._client.request_raw(
            "GET",
            f"/environments/{environment_id}/files/download/{encoded}",
        )
        return resp.text

    def download_file(self, environment_id: str, file_path: str) -> bytes:
        """Download a file as bytes."""
        normalized = file_path.lstrip("/")
        encoded = "/".join(quote(part, safe="") for part in normalized.split("/"))
        resp = self._client.request_raw(
            "GET",
            f"/environments/{environment_id}/files/download/{encoded}",
        )
        return resp.content

    def download_thumbnail(
        self,
        environment_id: str,
        file_path: str,
        *,
        width: int | None = None,
        height: int | None = None,
    ) -> bytes:
        """Download the server-generated thumbnail for a workspace file."""
        normalized = file_path.lstrip("/")
        encoded = "/".join(quote(part, safe="") for part in normalized.split("/"))
        response = self._client.request_raw(
            "GET",
            f"/environments/{quote(environment_id, safe='')}/files/thumbnail/{encoded}",
            query={"w": width, "h": height},
        )
        return response.content

    def download_directory(self, environment_id: str, folder_path: str) -> bytes:
        """Download a directory as a zip archive."""
        return self.download_file(environment_id, folder_path)

    def upload_file(
        self,
        environment_id: str,
        filename: str,
        content: str | bytes,
        *,
        path: str | None = None,
        content_type: str | None = None,
    ) -> dict[str, Any]:
        """Upload a file to an environment workspace.

        Example::

            client.files.upload_file(
                "env_xxx",
                filename="app.py",
                content='print("hello")',
                path="src",
            )
        """
        if isinstance(content, str):
            content_bytes = content.encode("utf-8")
        else:
            content_bytes = content

        data: dict[str, Any] = {}
        if path is not None:
            data["path"] = path

        files = {
            "file": (filename, content_bytes, content_type or "application/octet-stream"),
        }

        return self._client.request_form(
            "POST",
            f"/environments/{environment_id}/files/upload",
            data=data,
            files=files,
        )

    def delete_file(self, environment_id: str, file_path: str) -> dict[str, Any]:
        """Delete a file from an environment workspace."""
        normalized = file_path.lstrip("/")
        encoded = "/".join(quote(part, safe="") for part in normalized.split("/"))
        return self._client.delete(f"/environments/{environment_id}/files/{encoded}")

    def move_file(
        self,
        environment_id: str,
        source_path: str,
        dest_path: str,
    ) -> dict[str, Any]:
        """Move or rename a file.

        Example::

            client.files.move_file("env_xxx", "old.py", "new.py")
        """
        return self._client.post(
            f"/environments/{environment_id}/files/move",
            {"sourcePath": source_path, "destPath": dest_path},
        )

    def send_files_to_computer(
        self,
        environment_id: str,
        destination_environment_id: str,
        paths: list[str],
    ) -> dict[str, Any]:
        """Copy one or more files to another computer workspace.

        Source files remain in the original environment. Destination paths match
        the source workspace-relative paths and existing files are overwritten.

        Example::

            client.files.send_files_to_computer(
                "env_source",
                "env_destination",
                ["src/app.py", "README.md"],
            )
        """
        return self._client.post(
            f"/environments/{environment_id}/files/send",
            {
                "destinationEnvironmentId": destination_environment_id,
                "paths": paths,
            },
        )

    def send_files_to_environment(
        self,
        environment_id: str,
        destination_environment_id: str,
        paths: list[str],
    ) -> dict[str, Any]:
        """Alias for :meth:`send_files_to_computer`."""
        return self.send_files_to_computer(
            environment_id,
            destination_environment_id,
            paths,
        )

    def make_files_available_to_team(
        self,
        environment_id: str,
        team_id: str,
        paths: list[str],
        access_level: str = "use",
    ) -> dict[str, Any]:
        """Make one or more files available to a workspace team.

        Source files remain in the original environment. The team receives
        access only to the selected workspace-relative paths.

        Example::

            client.files.make_files_available_to_team(
                "env_source",
                "team_abc",
                ["src/app.py", "README.md"],
            )
        """
        return self._client.post(
            f"/environments/{environment_id}/files/share-with-team",
            {
                "teamId": team_id,
                "paths": paths,
                "accessLevel": access_level,
            },
        )

    def share_files_with_team(
        self,
        environment_id: str,
        team_id: str,
        paths: list[str],
        access_level: str = "use",
    ) -> dict[str, Any]:
        """Alias for :meth:`make_files_available_to_team`."""
        return self.make_files_available_to_team(
            environment_id,
            team_id,
            paths,
            access_level,
        )

    def create_directory(
        self, environment_id: str, path: str
    ) -> dict[str, Any]:
        """Create a directory. Parent directories are created automatically."""
        normalized = path.lstrip("/")
        return self._client.post(
            f"/environments/{environment_id}/files/mkdir",
            {"path": normalized},
        )
