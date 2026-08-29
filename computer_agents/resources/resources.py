"""Resources resource manager.

Managed resources include web apps, functions, auth modules, and agent runtimes.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from .._api_client import ApiClient
from .versioning import VersioningResource


def _id(value: str) -> str:
    return quote(value, safe="")


def _query(params: dict[str, Any], **values: Any) -> dict[str, Any] | None:
    query = dict(params)
    query.update({key: value for key, value in values.items() if value is not None})
    return query or None


class ResourcesResource:
    def __init__(self, client: ApiClient) -> None:
        self._client = client
        self._versions = VersioningResource(client, "/servers")

    def create(self, **params: Any) -> dict[str, Any]:
        resp = self._client.post("/servers", params)
        return resp["server"]

    def list(
        self,
        *,
        kind: str | None = None,
        project_id: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        query: dict[str, Any] = {}
        if kind is not None:
            query["kind"] = kind
        if project_id is not None:
            query["projectId"] = project_id
        if limit is not None:
            query["limit"] = limit
        if offset is not None:
            query["offset"] = offset
        resp = self._client.get("/servers", query=query or None)
        return resp.get("data") or resp.get("servers") or []

    def get(self, server_id: str) -> dict[str, Any]:
        resp = self._client.get(f"/servers/{server_id}")
        return resp["server"]

    def update(self, server_id: str, **params: Any) -> dict[str, Any]:
        resp = self._client.patch(f"/servers/{server_id}", params)
        return resp["server"]

    def delete(self, server_id: str) -> bool:
        resp = self._client.delete(f"/servers/{server_id}")
        return bool(resp.get("deleted"))

    def list_versions(self, server_id: str) -> list[dict[str, Any]]:
        """List saved resource versions."""
        return self._versions.list(server_id)

    def get_version(self, server_id: str, version_id: str) -> dict[str, Any]:
        """Get one saved resource version."""
        return self._versions.get(server_id, version_id)

    def create_version(self, server_id: str, **params: Any) -> dict[str, Any]:
        """Save the current resource or a supplied snapshot as a version."""
        return self._versions.create(server_id, **params)

    def update_version(self, server_id: str, version_id: str, **params: Any) -> dict[str, Any]:
        """Rename or update a saved resource version."""
        return self._versions.update(server_id, version_id, **params)

    def delete_version(self, server_id: str, version_id: str) -> bool:
        """Delete a saved resource version."""
        return self._versions.delete(server_id, version_id)

    def publish_version(self, server_id: str, version_id: str, **params: Any) -> dict[str, Any]:
        """Publish a saved resource version."""
        return self._versions.publish(server_id, version_id, **params)

    def unpublish_version(self, server_id: str, version_id: str) -> dict[str, Any]:
        """Unpublish a saved resource version."""
        return self._versions.unpublish(server_id, version_id)

    def restore_version(self, server_id: str, version_id: str) -> dict[str, Any]:
        """Restore a saved version into the editable resource configuration."""
        return self._versions.restore(server_id, version_id)

    def compare_versions(self, server_id: str, *, base_version_id: str, target_version_id: str) -> dict[str, Any]:
        """Compare two resource versions."""
        return self._versions.compare(
            server_id,
            base_version_id=base_version_id,
            target_version_id=target_version_id,
        )

    def deploy(
        self,
        server_id: str,
        *,
        version_id: str | None = None,
        release_id: str | None = None,
        project_delivery_promotion_id: str | None = None,
        project_delivery_resource_candidate_id: str | None = None,
    ) -> dict[str, Any]:
        body = {
            key: value
            for key, value in {
                "versionId": version_id,
                "releaseId": release_id,
                "projectDeliveryPromotionId": project_delivery_promotion_id,
                "projectDeliveryResourceCandidateId": project_delivery_resource_candidate_id,
            }.items()
            if value is not None
        }
        return self._client.post(f"/servers/{server_id}/deploy", body)

    def decommission(self, server_id: str) -> dict[str, Any]:
        """Decommission a deployed agent-runtime resource."""
        return self._client.post(f"/servers/{server_id}/decommission", {})

    def list_deployments(self, server_id: str) -> list[dict[str, Any]]:
        resp = self._client.get(f"/servers/{server_id}/deployments")
        return resp.get("deployments") or resp.get("data") or []

    def rollback_deployment(
        self,
        server_id: str,
        *,
        deployment_id: str | None = None,
        revision: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if deployment_id is not None:
            body["deploymentId"] = deployment_id
        if revision is not None:
            body["revision"] = revision
        return self._client.post(f"/servers/{server_id}/rollback", body)

    def invoke(self, server_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(f"/servers/{server_id}/invoke", params)

    def create_ai_chat_app_template(self, **params: Any) -> dict[str, Any]:
        return self._client.post("/servers/templates/ai-chat-app", params)

    def get_analytics(
        self,
        server_id: str,
        *,
        period: str | None = None,
    ) -> dict[str, Any]:
        query = {"period": period} if period is not None else None
        return self._client.get(f"/servers/{server_id}/analytics", query=query)

    def get_logs(
        self,
        server_id: str,
        *,
        kind: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        query: dict[str, Any] = {}
        if kind is not None:
            query["kind"] = kind
        if limit is not None:
            query["limit"] = limit
        resp = self._client.get(f"/servers/{server_id}/logs", query=query or None)
        return resp["logs"]

    def list_bindings(self, server_id: str) -> list[dict[str, Any]]:
        resp = self._client.get(f"/servers/{server_id}/bindings")
        return resp["bindings"]

    def upsert_binding(
        self,
        server_id: str,
        target_type: str,
        *,
        target_id: str,
        alias: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        body: dict[str, Any] = {"targetId": target_id}
        if alias is not None:
            body["alias"] = alias
        if metadata is not None:
            body["metadata"] = metadata
        resp = self._client.put(f"/servers/{server_id}/bindings/{target_type}", body)
        return resp["bindings"]

    def delete_binding(self, server_id: str, target_type: str) -> list[dict[str, Any]]:
        resp = self._client.delete(f"/servers/{server_id}/bindings/{target_type}")
        return resp["bindings"]

    def list_auth_users(
        self,
        server_id: str,
        *,
        limit: int | None = None,
        next_page_token: str | None = None,
    ) -> list[dict[str, Any]]:
        query: dict[str, Any] = {}
        if limit is not None:
            query["limit"] = limit
        if next_page_token is not None:
            query["nextPageToken"] = next_page_token
        resp = self._client.get(f"/servers/{server_id}/auth-users", query=query or None)
        return resp["users"]

    def create_auth_user(
        self,
        server_id: str,
        *,
        email: str,
        password: str,
        display_name: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"email": email, "password": password}
        if display_name is not None:
            body["displayName"] = display_name
        return self._client.post(f"/servers/{server_id}/auth-users", body)

    def sign_up(
        self,
        server_id: str,
        *,
        email: str,
        password: str,
        display_name: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"email": email, "password": password}
        if display_name is not None:
            body["displayName"] = display_name
        return self._client.post(f"/servers/{server_id}/auth/sign-up", body)

    def sign_in(self, server_id: str, *, email: str, password: str) -> dict[str, Any]:
        return self._client.post(f"/servers/{server_id}/auth/sign-in", {"email": email, "password": password})

    def get_context(self, server_id: str) -> dict[str, Any]:
        return self._client.get(f"/servers/{server_id}/context")

    def get_runtime_config(self, server_id: str) -> dict[str, Any]:
        return self._client.get(f"/servers/{server_id}/runtime-config")

    def get_runtime(self, server_id: str) -> dict[str, Any]:
        return self._client.get(f"/servers/{server_id}/runtime")

    def list_files(
        self,
        server_id: str,
        *,
        path: str | None = None,
        depth: int | None = None,
    ) -> list[dict[str, Any]]:
        query: dict[str, Any] = {}
        if path is not None:
            query["path"] = path
        if depth is not None:
            query["depth"] = depth
        resp = self._client.get(f"/servers/{server_id}/files", query=query or None)
        return resp.get("files") or resp.get("data") or []

    def get_file_content(self, server_id: str, file_path: str) -> str:
        normalized = file_path.lstrip("/")
        encoded = "/".join(quote(part, safe="") for part in normalized.split("/"))
        resp = self._client.get(f"/servers/{server_id}/files/content/{encoded}")
        return resp["content"]

    def write_file_content(self, server_id: str, file_path: str, content: str) -> dict[str, Any]:
        normalized = file_path.lstrip("/")
        encoded = "/".join(quote(part, safe="") for part in normalized.split("/"))
        return self._client.put(f"/servers/{server_id}/files/content/{encoded}", {"content": content})

    def download_file(self, server_id: str, file_path: str) -> bytes:
        normalized = file_path.lstrip("/")
        encoded = "/".join(quote(part, safe="") for part in normalized.split("/"))
        resp = self._client.request_raw("GET", f"/servers/{server_id}/files/download/{encoded}")
        return resp.content

    def upload_file(
        self,
        server_id: str,
        *,
        filename: str,
        content: str | bytes,
        path: str | None = None,
        content_type: str | None = None,
    ) -> dict[str, Any]:
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
            f"/servers/{server_id}/files/upload",
            data=data,
            files=files,
        )

    def delete_file(self, server_id: str, file_path: str) -> dict[str, Any]:
        normalized = file_path.lstrip("/")
        encoded = "/".join(quote(part, safe="") for part in normalized.split("/"))
        return self._client.delete(f"/servers/{server_id}/files/{encoded}")

    def list_secrets(self, server_id: str) -> list[dict[str, Any]]:
        resp = self._client.get(f"/servers/{server_id}/secrets")
        return resp.get("secrets") or resp.get("data") or []

    def get_secret(self, server_id: str, secret_id: str) -> dict[str, Any]:
        resp = self._client.get(f"/servers/{server_id}/secrets/{secret_id}")
        return resp["secret"]

    def create_secret(
        self,
        server_id: str,
        *,
        name: str,
        value: str,
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"name": name, "value": value}
        if description is not None:
            body["description"] = description
        if metadata is not None:
            body["metadata"] = metadata
        resp = self._client.post(f"/servers/{server_id}/secrets", body)
        return resp["secret"]

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
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if value is not None:
            body["value"] = value
        if description is not None:
            body["description"] = description
        if metadata is not None:
            body["metadata"] = metadata
        resp = self._client.put(f"/servers/{server_id}/secrets/{secret_id}", body)
        return resp["secret"]

    def delete_secret(self, server_id: str, secret_id: str) -> bool:
        resp = self._client.delete(f"/servers/{server_id}/secrets/{secret_id}")
        return bool(resp.get("deleted"))

    def get_custom_domain(
        self,
        server_id: str,
        *,
        domain: str | None = None,
    ) -> dict[str, Any]:
        return self._client.get(
            f"/servers/{_id(server_id)}/custom-domain",
            query={"domain": domain},
        )

    def set_custom_domain(self, server_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(f"/servers/{_id(server_id)}/custom-domain", params)

    def delete_custom_domain(
        self,
        server_id: str,
        *,
        domain: str | None = None,
    ) -> dict[str, Any]:
        return self._client.request(
            "DELETE",
            f"/servers/{_id(server_id)}/custom-domain",
            query={"domain": domain},
        )

    def check_custom_domain(self, server_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(
            f"/servers/{_id(server_id)}/custom-domain/check",
            params,
        )

    def get_overview_analytics(
        self,
        *,
        kind: str | None = None,
        period: str | None = None,
    ) -> dict[str, Any]:
        query: dict[str, Any] = {}
        if kind is not None:
            query["kind"] = kind
        if period is not None:
            query["period"] = period
        return self._client.get("/servers/analytics/overview", query=query or None)

    def connect_payment_account(self, server_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(
            f"/servers/{_id(server_id)}/payments/connect-account",
            params,
        )

    def sync_payments(self, server_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(f"/servers/{_id(server_id)}/payments/sync", params)

    def get_current_auth_user(self, server_id: str) -> dict[str, Any]:
        return self._client.get(f"/servers/{_id(server_id)}/auth/me")

    def list_runs(
        self,
        server_id: str,
        *,
        limit: int | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.get(
            f"/servers/{_id(server_id)}/runs",
            query=_query(params, limit=limit),
        )

    def start_run(self, server_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(f"/servers/{_id(server_id)}/runs", params)

    def get_run(self, server_id: str, run_id: str) -> dict[str, Any]:
        return self._client.get(f"/servers/{_id(server_id)}/runs/{_id(run_id)}")

    def send_run_input(
        self,
        server_id: str,
        run_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.post(
            f"/servers/{_id(server_id)}/runs/{_id(run_id)}/input",
            params,
        )

    def get_run_events(self, server_id: str, run_id: str) -> dict[str, Any]:
        return self._client.get(
            f"/servers/{_id(server_id)}/runs/{_id(run_id)}/events"
        )

    def cancel_run(self, server_id: str, run_id: str) -> dict[str, Any]:
        return self._client.post(
            f"/servers/{_id(server_id)}/runs/{_id(run_id)}/cancel",
            {},
        )

    def download_runtime_sdk(self, server_id: str, target: str) -> str:
        response = self._client.request_raw(
            "GET",
            f"/servers/{_id(server_id)}/runtime-sdk/{_id(target)}",
        )
        return response.text

    def list_runtime_agent_runs(
        self,
        server_id: str,
        *,
        limit: int | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.get(
            f"/servers/{_id(server_id)}/runtime/agent/runs",
            query=_query(params, limit=limit),
        )

    def start_runtime_agent_run(self, server_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(
            f"/servers/{_id(server_id)}/runtime/agent/runs",
            params,
        )

    def get_runtime_agent_run(self, server_id: str, run_id: str) -> dict[str, Any]:
        return self._client.get(
            f"/servers/{_id(server_id)}/runtime/agent/runs/{_id(run_id)}"
        )

    def send_runtime_agent_run_input(
        self,
        server_id: str,
        run_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.post(
            f"/servers/{_id(server_id)}/runtime/agent/runs/{_id(run_id)}/input",
            params,
        )

    def get_runtime_agent_run_events(
        self,
        server_id: str,
        run_id: str,
    ) -> dict[str, Any]:
        return self._client.get(
            f"/servers/{_id(server_id)}/runtime/agent/runs/{_id(run_id)}/events"
        )

    def cancel_runtime_agent_run(self, server_id: str, run_id: str) -> dict[str, Any]:
        return self._client.post(
            f"/servers/{_id(server_id)}/runtime/agent/runs/{_id(run_id)}/cancel",
            {},
        )

    def list_runtime_secrets(self, server_id: str) -> dict[str, Any]:
        return self._client.get(f"/servers/{_id(server_id)}/runtime/secrets")

    def get_runtime_secret(self, server_id: str, secret_id: str) -> dict[str, Any]:
        return self._client.get(
            f"/servers/{_id(server_id)}/runtime/secrets/{_id(secret_id)}"
        )

    def get_runtime_payments(self, server_id: str) -> dict[str, Any]:
        return self._client.get(f"/servers/{_id(server_id)}/runtime/payments")

    def create_runtime_checkout_session(
        self,
        server_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.post(
            f"/servers/{_id(server_id)}/runtime/payments/checkout-sessions",
            params,
        )

    def commit_runtime_database(self, server_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(
            f"/servers/{_id(server_id)}/runtime/database/commit",
            params,
        )

    def list_runtime_database_collections(self, server_id: str) -> dict[str, Any]:
        return self._client.get(
            f"/servers/{_id(server_id)}/runtime/database/collections"
        )

    def create_runtime_database_collection(
        self,
        server_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.post(
            f"/servers/{_id(server_id)}/runtime/database/collections",
            params,
        )

    def list_runtime_database_documents(
        self,
        server_id: str,
        collection_id: str,
        *,
        limit: int | None = None,
        page_token: str | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.get(
            f"/servers/{_id(server_id)}/runtime/database/collections/"
            f"{_id(collection_id)}/documents",
            query=_query(params, limit=limit, pageToken=page_token),
        )

    def create_runtime_database_document(
        self,
        server_id: str,
        collection_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.post(
            f"/servers/{_id(server_id)}/runtime/database/collections/"
            f"{_id(collection_id)}/documents",
            params,
        )

    def get_runtime_database_document(
        self,
        server_id: str,
        collection_id: str,
        document_id: str,
    ) -> dict[str, Any]:
        return self._client.get(
            f"/servers/{_id(server_id)}/runtime/database/collections/"
            f"{_id(collection_id)}/documents/{_id(document_id)}"
        )

    def update_runtime_database_document(
        self,
        server_id: str,
        collection_id: str,
        document_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.put(
            f"/servers/{_id(server_id)}/runtime/database/collections/"
            f"{_id(collection_id)}/documents/{_id(document_id)}",
            params,
        )

    def delete_runtime_database_document(
        self,
        server_id: str,
        collection_id: str,
        document_id: str,
    ) -> dict[str, Any]:
        return self._client.delete(
            f"/servers/{_id(server_id)}/runtime/database/collections/"
            f"{_id(collection_id)}/documents/{_id(document_id)}"
        )
