"""Security Agents repositories, scans, findings, and remediation."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from .._api_client import ApiClient


def _id(value: str) -> str:
    return quote(value, safe="")


def _data(response: dict[str, Any]) -> list[dict[str, Any]]:
    return response.get("data", [])


def _query(params: dict[str, Any], **values: Any) -> dict[str, Any] | None:
    query = dict(params)
    query.update({key: value for key, value in values.items() if value is not None})
    return query or None


class SecurityResource:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def overview(self) -> dict[str, Any]:
        return self._client.get("/security/overview")

    def list_repositories(self) -> list[dict[str, Any]]:
        return _data(self._client.get("/security/repositories"))

    def create_repository(self, **params: Any) -> dict[str, Any]:
        return self._client.post("/security/repositories", params)

    def get_repository(self, repository_id: str) -> dict[str, Any]:
        return self._client.get(f"/security/repositories/{_id(repository_id)}")

    def update_repository(self, repository_id: str, **params: Any) -> dict[str, Any]:
        return self._client.patch(
            f"/security/repositories/{_id(repository_id)}",
            params,
        )

    def delete_repository(self, repository_id: str) -> None:
        self._client.delete(f"/security/repositories/{_id(repository_id)}")

    def set_policy(
        self,
        repository_id: str,
        value: Any,
        *,
        change_summary: str | None = None,
    ) -> dict[str, Any]:
        return self._client.put(
            f"/security/repositories/{_id(repository_id)}/policy",
            {"value": value, "changeSummary": change_summary},
        )

    def set_threat_model(
        self,
        repository_id: str,
        value: Any,
        *,
        change_summary: str | None = None,
    ) -> dict[str, Any]:
        return self._client.put(
            f"/security/repositories/{_id(repository_id)}/threat-model",
            {"value": value, "changeSummary": change_summary},
        )

    def list_repository_versions(self, repository_id: str) -> list[dict[str, Any]]:
        return _data(
            self._client.get(f"/security/repositories/{_id(repository_id)}/versions")
        )

    def get_repository_version(
        self,
        repository_id: str,
        version_id: str,
    ) -> dict[str, Any]:
        return self._client.get(
            f"/security/repositories/{_id(repository_id)}/versions/{_id(version_id)}"
        )

    def create_repository_version(
        self,
        repository_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.post(
            f"/security/repositories/{_id(repository_id)}/versions",
            params,
        )

    def update_repository_version(
        self,
        repository_id: str,
        version_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.patch(
            f"/security/repositories/{_id(repository_id)}/versions/{_id(version_id)}",
            params,
        )

    def publish_repository_version(
        self,
        repository_id: str,
        version_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.post(
            f"/security/repositories/{_id(repository_id)}/versions/{_id(version_id)}/publish",
            params,
        )

    def compare_repository_versions(
        self,
        repository_id: str,
        *,
        base_version_id: str,
        target_version_id: str,
    ) -> dict[str, Any]:
        return self._client.get(
            f"/security/repositories/{_id(repository_id)}/versions/compare",
            query={
                "baseVersionId": base_version_id,
                "targetVersionId": target_version_id,
            },
        )

    def delete_repository_version(self, repository_id: str, version_id: str) -> None:
        self._client.delete(
            f"/security/repositories/{_id(repository_id)}/versions/{_id(version_id)}"
        )

    def list_runs(
        self,
        *,
        repository_id: str | None = None,
        status: str | None = None,
        limit: int | None = None,
        **params: Any,
    ) -> list[dict[str, Any]]:
        return _data(self._client.get(
            "/security/runs",
            query=_query(
                params,
                repositoryId=repository_id,
                status=status,
                limit=limit,
            ),
        ))

    def list_repository_runs(
        self,
        repository_id: str,
        *,
        status: str | None = None,
        limit: int | None = None,
        **params: Any,
    ) -> list[dict[str, Any]]:
        return _data(
            self._client.get(
                f"/security/repositories/{_id(repository_id)}/runs",
                query=_query(params, status=status, limit=limit),
            )
        )

    def queue_run(
        self,
        repository_id: str,
        *,
        idempotency_key: str | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.request(
            "POST",
            f"/security/repositories/{_id(repository_id)}/runs",
            body=params,
            headers={"Idempotency-Key": idempotency_key} if idempotency_key else None,
        )

    def get_run(self, run_id: str) -> dict[str, Any]:
        return self._client.get(f"/security/runs/{_id(run_id)}")

    def execute_run(self, run_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(f"/security/runs/{_id(run_id)}/execute", params)

    def cancel_run(self, run_id: str) -> dict[str, Any]:
        return self._client.post(f"/security/runs/{_id(run_id)}/cancel", {})

    def create_remediation(
        self,
        run_id: str,
        finding_ids: list[str],
        *,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        return self._client.request(
            "POST",
            f"/security/runs/{_id(run_id)}/remediations",
            body={"findingIds": finding_ids},
            headers={"Idempotency-Key": idempotency_key} if idempotency_key else None,
        )

    def reconcile_remediation(self, remediation_id: str) -> dict[str, Any]:
        return self._client.post(
            f"/security/remediations/{_id(remediation_id)}/reconcile",
            {},
        )

    def execute_remediation(self, remediation_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(
            f"/security/remediations/{_id(remediation_id)}/execute",
            params,
        )

    def start_remediation_thread(
        self,
        remediation_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.post(
            f"/security/remediations/{_id(remediation_id)}/thread",
            params,
        )

    def complete_remediation(self, remediation_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(
            f"/security/remediations/{_id(remediation_id)}/complete",
            params,
        )

    def fail_remediation(self, remediation_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(
            f"/security/remediations/{_id(remediation_id)}/fail",
            params,
        )

    def list_findings(
        self,
        *,
        repository_id: str | None = None,
        run_id: str | None = None,
        status: str | None = None,
        severity: str | None = None,
        limit: int | None = None,
        **params: Any,
    ) -> list[dict[str, Any]]:
        return _data(self._client.get(
            "/security/findings",
            query=_query(
                params,
                repositoryId=repository_id,
                runId=run_id,
                status=status,
                severity=severity,
                limit=limit,
            ),
        ))

    def get_finding(self, finding_id: str) -> dict[str, Any]:
        return self._client.get(f"/security/findings/{_id(finding_id)}")

    def update_finding(self, finding_id: str, **params: Any) -> dict[str, Any]:
        return self._client.patch(f"/security/findings/{_id(finding_id)}", params)

    def list_audit_events(
        self,
        *,
        repository_id: str | None = None,
        run_id: str | None = None,
        finding_id: str | None = None,
        limit: int | None = None,
        **params: Any,
    ) -> list[dict[str, Any]]:
        return _data(self._client.get(
            "/security/audit-events",
            query=_query(
                params,
                repositoryId=repository_id,
                runId=run_id,
                findingId=finding_id,
                limit=limit,
            ),
        ))

    def github_status(self) -> dict[str, Any]:
        return self._client.get("/github/security/status")

    def setup_github(self, **params: Any) -> dict[str, Any]:
        return self._client.post("/github/security/setup", params)

    def sync_github_oauth(self, **params: Any) -> dict[str, Any]:
        return self._client.post("/github/security/oauth/sync", params)

    def list_github_installations(self) -> list[dict[str, Any]]:
        return _data(self._client.get("/github/security/installations"))

    def list_github_repositories(self, **params: Any) -> list[dict[str, Any]]:
        return _data(self._client.get("/github/security/repositories", query=params))

    def list_github_installation_repositories(
        self,
        installation_id: str,
    ) -> list[dict[str, Any]]:
        return _data(
            self._client.get(
                f"/github/security/installations/{_id(installation_id)}/repositories"
            )
        )

    def sync_github_installation(self, installation_id: str) -> dict[str, Any]:
        return self._client.post(
            f"/github/security/installations/{_id(installation_id)}/sync",
            {},
        )
