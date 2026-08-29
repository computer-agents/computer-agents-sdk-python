"""Evidence-bound Assurance policies and release decisions."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from .._api_client import ApiClient


def _id(value: str) -> str:
    return quote(value, safe="")


class AssuranceResource:
    """Versioned release policies across Tests, Evaluations, and Optimization."""

    def __init__(self, client: ApiClient) -> None:
        self._client = client

    @staticmethod
    def _unwrap(response: Any, *keys: str) -> Any:
        if not isinstance(response, dict):
            return response
        for key in keys:
            value = response.get(key)
            if value is not None:
                return value
        return response

    def list_policies(
        self,
        *,
        project_id: str | None = None,
        status: str | None = None,
        q: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        response = self._client.get(
            "/assurance/policies",
            query={
                "projectId": project_id,
                "status": status,
                "q": q,
                "limit": limit,
                "offset": offset,
            },
        )
        return self._unwrap(response, "data", "assurancePolicies") or []

    def get_policy(self, policy_id: str) -> dict[str, Any]:
        response = self._client.get(f"/assurance/policies/{_id(policy_id)}")
        return self._unwrap(response, "assurancePolicy", "data")

    def create_policy(
        self,
        *,
        name: str,
        definition: dict[str, Any],
        policy_id: str | None = None,
        description: str | None = None,
        project_id: str | None = None,
        status: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body = {
            key: value
            for key, value in {
                "id": policy_id,
                "name": name,
                "definition": definition,
                "description": description,
                "projectId": project_id,
                "status": status,
                "metadata": metadata,
            }.items()
            if value is not None
        }
        response = self._client.post("/assurance/policies", body)
        return self._unwrap(response, "assurancePolicy", "data")

    def update_policy(
        self,
        policy_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        project_id: str | None = None,
        status: str | None = None,
        definition: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body = {
            key: value
            for key, value in {
                "name": name,
                "description": description,
                "projectId": project_id,
                "status": status,
                "definition": definition,
                "metadata": metadata,
            }.items()
            if value is not None
        }
        response = self._client.patch(
            f"/assurance/policies/{_id(policy_id)}",
            body,
        )
        return self._unwrap(response, "assurancePolicy", "data")

    def delete_policy(self, policy_id: str) -> bool:
        response = self._client.delete(f"/assurance/policies/{_id(policy_id)}")
        return response is None or response.get("deleted", True)

    def create_policy_version(
        self,
        policy_id: str,
        *,
        label: str | None = None,
        description: str | None = None,
        snapshot: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body = {
            key: value
            for key, value in {
                "label": label,
                "description": description,
                "snapshot": snapshot,
                "metadata": metadata,
            }.items()
            if value is not None
        }
        response = self._client.post(
            f"/assurance/policies/{_id(policy_id)}/versions",
            body,
        )
        return self._unwrap(response, "version", "data")

    def publish_policy_version(
        self,
        policy_id: str,
        version_id: str,
    ) -> dict[str, Any]:
        response = self._client.post(
            (
                f"/assurance/policies/{_id(policy_id)}"
                f"/versions/{_id(version_id)}/publish"
            ),
            {},
        )
        return self._unwrap(response, "assurancePolicy", "data")

    def list_runs(
        self,
        *,
        assurance_policy_id: str | None = None,
        project_id: str | None = None,
        status: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        response = self._client.get(
            "/assurance/runs",
            query={
                "assurancePolicyId": assurance_policy_id,
                "projectId": project_id,
                "status": status,
                "limit": limit,
                "offset": offset,
            },
        )
        return self._unwrap(response, "data", "assuranceRuns") or []

    def get_run(self, run_id: str) -> dict[str, Any]:
        response = self._client.get(f"/assurance/runs/{_id(run_id)}")
        return self._unwrap(response, "assuranceRun", "data")

    def run(
        self,
        policy_id: str,
        *,
        run_id: str | None = None,
        policy_version_id: str | None = None,
        project_id: str | None = None,
        release_id: str | None = None,
        commit_sha: str | None = None,
        agent_id: str | None = None,
        agent_version_id: str | None = None,
        evidence_references: dict[str, list[str]] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body = {
            key: value
            for key, value in {
                "id": run_id,
                "policyVersionId": policy_version_id,
                "projectId": project_id,
                "releaseId": release_id,
                "commitSha": commit_sha,
                "agentId": agent_id,
                "agentVersionId": agent_version_id,
                "evidenceReferences": evidence_references,
                "metadata": metadata,
            }.items()
            if value is not None
        }
        response = self._client.post(
            f"/assurance/policies/{_id(policy_id)}/runs",
            body,
        )
        return self._unwrap(response, "assuranceRun", "data")

    def attach_evidence(
        self,
        run_id: str,
        evidence_references: dict[str, list[str]],
        *,
        expected_revision: int | None = None,
    ) -> dict[str, Any]:
        response = self._client.post(
            f"/assurance/runs/{_id(run_id)}/evidence",
            {
                "evidenceReferences": evidence_references,
                "expectedRevision": expected_revision,
            },
        )
        return self._unwrap(response, "assuranceRun", "data")

    def evaluate(self, run_id: str) -> dict[str, Any]:
        response = self._client.post(
            f"/assurance/runs/{_id(run_id)}/evaluate",
            {},
        )
        return self._unwrap(response, "assuranceRun", "data")

    def approve(
        self,
        run_id: str,
        evidence_fingerprint: str,
    ) -> dict[str, Any]:
        response = self._client.post(
            f"/assurance/runs/{_id(run_id)}/approve",
            {"evidenceFingerprint": evidence_fingerprint},
        )
        return self._unwrap(response, "assuranceRun", "data")

    def cancel(self, run_id: str) -> dict[str, Any]:
        response = self._client.post(
            f"/assurance/runs/{_id(run_id)}/cancel",
            {},
        )
        return self._unwrap(response, "assuranceRun", "data")
