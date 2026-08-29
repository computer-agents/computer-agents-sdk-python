"""Product-shaped resource managers built on top of the generic resources API."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from .._api_client import ApiClient
from .resources import ResourcesResource


class _KindScopedResource:
    def __init__(self, client: ApiClient, kind: str) -> None:
        self._resources = ResourcesResource(client)
        self._kind = kind

    def create(self, **params: Any) -> dict[str, Any]:
        body = dict(params)
        body["kind"] = self._kind
        return self._resources.create(**body)

    def list(
        self,
        *,
        project_id: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        resources = self._resources.list(
            kind=self._kind,
            project_id=project_id,
            limit=limit,
            offset=offset,
        )
        return [resource for resource in resources if resource.get("kind") == self._kind]

    def get(self, server_id: str) -> dict[str, Any]:
        return self._resources.get(server_id)

    def update(self, server_id: str, **params: Any) -> dict[str, Any]:
        body = dict(params)
        body["kind"] = self._kind
        return self._resources.update(server_id, **body)

    def delete(self, server_id: str) -> bool:
        return self._resources.delete(server_id)

    def list_versions(self, server_id: str) -> list[dict[str, Any]]:
        return self._resources.list_versions(server_id)

    def get_version(self, server_id: str, version_id: str) -> dict[str, Any]:
        return self._resources.get_version(server_id, version_id)

    def create_version(self, server_id: str, **params: Any) -> dict[str, Any]:
        return self._resources.create_version(server_id, **params)

    def update_version(self, server_id: str, version_id: str, **params: Any) -> dict[str, Any]:
        return self._resources.update_version(server_id, version_id, **params)

    def delete_version(self, server_id: str, version_id: str) -> bool:
        return self._resources.delete_version(server_id, version_id)

    def publish_version(self, server_id: str, version_id: str) -> dict[str, Any]:
        return self._resources.publish_version(server_id, version_id)

    def unpublish_version(self, server_id: str, version_id: str) -> dict[str, Any]:
        return self._resources.unpublish_version(server_id, version_id)

    def restore_version(self, server_id: str, version_id: str) -> dict[str, Any]:
        return self._resources.restore_version(server_id, version_id)

    def compare_versions(self, server_id: str, *, base_version_id: str, target_version_id: str) -> dict[str, Any]:
        return self._resources.compare_versions(
            server_id,
            base_version_id=base_version_id,
            target_version_id=target_version_id,
        )

    def deploy(self, server_id: str) -> dict[str, Any]:
        return self._resources.deploy(server_id)

    def list_deployments(self, server_id: str) -> list[dict[str, Any]]:
        return self._resources.list_deployments(server_id)

    def rollback_deployment(
        self,
        server_id: str,
        *,
        deployment_id: str | None = None,
        revision: str | None = None,
    ) -> dict[str, Any]:
        return self._resources.rollback_deployment(
            server_id,
            deployment_id=deployment_id,
            revision=revision,
        )

    def invoke(self, server_id: str, **params: Any) -> dict[str, Any]:
        return self._resources.invoke(server_id, **params)

    def get_analytics(
        self,
        server_id: str,
        *,
        period: str | None = None,
    ) -> dict[str, Any]:
        return self._resources.get_analytics(server_id, period=period)

    def get_logs(
        self,
        server_id: str,
        *,
        kind: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        return self._resources.get_logs(server_id, kind=kind, limit=limit)

    def list_bindings(self, server_id: str) -> list[dict[str, Any]]:
        return self._resources.list_bindings(server_id)

    def upsert_binding(
        self,
        server_id: str,
        target_type: str,
        *,
        target_id: str,
        alias: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        return self._resources.upsert_binding(
            server_id,
            target_type,
            target_id=target_id,
            alias=alias,
            metadata=metadata,
        )

    def delete_binding(self, server_id: str, target_type: str) -> list[dict[str, Any]]:
        return self._resources.delete_binding(server_id, target_type)

    def get_context(self, server_id: str) -> dict[str, Any]:
        return self._resources.get_context(server_id)

    def get_runtime_config(self, server_id: str) -> dict[str, Any]:
        return self._resources.get_runtime_config(server_id)

    def get_runtime(self, server_id: str) -> dict[str, Any]:
        return self._resources.get_runtime(server_id)

    def list_files(
        self,
        server_id: str,
        *,
        path: str | None = None,
        depth: int | None = None,
    ) -> list[dict[str, Any]]:
        return self._resources.list_files(server_id, path=path, depth=depth)

    def get_file_content(self, server_id: str, file_path: str) -> str:
        return self._resources.get_file_content(server_id, file_path)

    def write_file_content(self, server_id: str, file_path: str, content: str) -> dict[str, Any]:
        return self._resources.write_file_content(server_id, file_path, content)

    def download_file(self, server_id: str, file_path: str) -> bytes:
        return self._resources.download_file(server_id, file_path)

    def upload_file(
        self,
        server_id: str,
        *,
        filename: str,
        content: str | bytes,
        path: str | None = None,
        content_type: str | None = None,
    ) -> dict[str, Any]:
        return self._resources.upload_file(
            server_id,
            filename=filename,
            content=content,
            path=path,
            content_type=content_type,
        )

    def delete_file(self, server_id: str, file_path: str) -> dict[str, Any]:
        return self._resources.delete_file(server_id, file_path)

    def list_secrets(self, server_id: str) -> list[dict[str, Any]]:
        return self._resources.list_secrets(server_id)

    def get_secret(self, server_id: str, secret_id: str) -> dict[str, Any]:
        return self._resources.get_secret(server_id, secret_id)

    def create_secret(
        self,
        server_id: str,
        *,
        name: str,
        value: str,
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._resources.create_secret(
            server_id,
            name=name,
            value=value,
            description=description,
            metadata=metadata,
        )

    def update_secret(
        self,
        server_id: str,
        secret_id: str,
        *,
        name: str | None = None,
        value: str | None = None,
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._resources.update_secret(
            server_id,
            secret_id,
            name=name,
            value=value,
            description=description,
            metadata=metadata,
        )

    def delete_secret(self, server_id: str, secret_id: str) -> bool:
        return self._resources.delete_secret(server_id, secret_id)


class WebAppsResource(_KindScopedResource):
    def __init__(self, client: ApiClient) -> None:
        super().__init__(client, "web_app")

    def create_ai_chat_app_template(self, **params: Any) -> dict[str, Any]:
        return self._resources.create_ai_chat_app_template(**params)


class FunctionsResource(_KindScopedResource):
    def __init__(self, client: ApiClient) -> None:
        super().__init__(client, "function")


class AuthResource(_KindScopedResource):
    def __init__(self, client: ApiClient) -> None:
        super().__init__(client, "auth")

    def list_users(
        self,
        server_id: str,
        *,
        limit: int | None = None,
        next_page_token: str | None = None,
    ) -> list[dict[str, Any]]:
        return self._resources.list_auth_users(server_id, limit=limit, next_page_token=next_page_token)

    def create_user(
        self,
        server_id: str,
        *,
        email: str,
        password: str,
        display_name: str | None = None,
    ) -> dict[str, Any]:
        return self._resources.create_auth_user(
            server_id,
            email=email,
            password=password,
            display_name=display_name,
        )

    def sign_up(
        self,
        server_id: str,
        *,
        email: str,
        password: str,
        display_name: str | None = None,
    ) -> dict[str, Any]:
        return self._resources.sign_up(
            server_id,
            email=email,
            password=password,
            display_name=display_name,
        )

    def sign_in(self, server_id: str, *, email: str, password: str) -> dict[str, Any]:
        return self._resources.sign_in(server_id, email=email, password=password)


class AgentRuntimesResource(_KindScopedResource):
    def __init__(self, client: ApiClient) -> None:
        super().__init__(client, "agent_runtime")
        self._client = client

    @staticmethod
    def _path(runtime_id: str) -> str:
        return f"/agent-runtimes/{quote(runtime_id, safe='')}"

    def create(self, **params: Any) -> dict[str, Any]:
        response = self._client.post("/agent-runtimes", params)
        return response["server"]

    def list(
        self,
        *,
        project_id: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        query: dict[str, Any] = {}
        if project_id is not None:
            query["projectId"] = project_id
        if limit is not None:
            query["limit"] = limit
        if offset is not None:
            query["offset"] = offset
        response = self._client.get("/agent-runtimes", query=query or None)
        return response.get("data") or response.get("servers") or []

    def get(self, runtime_id: str) -> dict[str, Any]:
        response = self._client.get(self._path(runtime_id))
        return response["server"]

    def get_deployment(self, runtime_id: str) -> dict[str, Any]:
        response = self._client.get(self._path(runtime_id))
        return response["agentRuntime"]

    def update(  # type: ignore[override]
        self,
        runtime_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        response = self._client.patch(self._path(runtime_id), params)
        return response["server"]

    def delete(self, runtime_id: str) -> bool:
        response = self._client.delete(self._path(runtime_id))
        return bool(response.get("deleted"))

    def deploy(self, runtime_id: str) -> dict[str, Any]:
        return self._client.post(f"{self._path(runtime_id)}/deploy", {})

    def decommission(self, runtime_id: str) -> dict[str, Any]:
        return self._client.post(f"{self._path(runtime_id)}/decommission", {})

    def list_deployments(self, runtime_id: str) -> list[dict[str, Any]]:
        response = self._client.get(f"{self._path(runtime_id)}/deployments")
        return response.get("deployments") or response.get("data") or []

    def list_runs(self, runtime_id: str, *, limit: int | None = None) -> list[dict[str, Any]]:
        query = {"limit": limit} if limit is not None else None
        response = self._client.get(f"{self._path(runtime_id)}/runs", query=query)
        return response.get("runs") or []

    def start_run(
        self,
        runtime_id: str,
        *,
        content: str | None = None,
        prompt: str | None = None,
        title: str | None = None,
        mode: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body = {
            key: value
            for key, value in {
                "content": content,
                "prompt": prompt,
                "title": title,
                "mode": mode,
                "metadata": metadata,
            }.items()
            if value is not None
        }
        return self._client.post(f"{self._path(runtime_id)}/runs", body)

    def get_run(self, runtime_id: str, run_id: str) -> dict[str, Any]:
        return self._client.get(f"{self._path(runtime_id)}/runs/{quote(run_id, safe='')}")

    def send_input(
        self,
        runtime_id: str,
        run_id: str,
        *,
        content: str | None = None,
        prompt: str | None = None,
        mode: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body = {
            key: value
            for key, value in {
                "content": content,
                "prompt": prompt,
                "mode": mode,
                "metadata": metadata,
            }.items()
            if value is not None
        }
        return self._client.post(
            f"{self._path(runtime_id)}/runs/{quote(run_id, safe='')}/input",
            body,
        )

    def get_events(self, runtime_id: str, run_id: str) -> list[dict[str, Any]]:
        response = self._client.get(
            f"{self._path(runtime_id)}/runs/{quote(run_id, safe='')}/events",
        )
        return response.get("events") or []

    def cancel_run(self, runtime_id: str, run_id: str) -> dict[str, Any]:
        return self._client.post(
            f"{self._path(runtime_id)}/runs/{quote(run_id, safe='')}/cancel",
            {},
        )


class SecretsResource(_KindScopedResource):
    def __init__(self, client: ApiClient) -> None:
        super().__init__(client, "secrets")


RuntimesResource = AgentRuntimesResource
