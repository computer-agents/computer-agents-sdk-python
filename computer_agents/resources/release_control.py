"""Standalone evidence-bound publication and deployment control."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from .._api_client import ApiClient
from ..types import (
    ProjectDeliveryPromotion,
    ProjectDeliveryReleaseAuthorization,
    Release,
    ReleaseAction,
    ReleaseTargetKind,
)


def _id(value: str) -> str:
    return quote(value, safe="")


class ReleaseControlResource:
    """Operate releases without depending on Mission Control."""

    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def list(
        self,
        *,
        project_id: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        response = self._client.get(
            "/release-control",
            query={
                "projectId": project_id,
                "limit": limit,
                "offset": offset,
            },
        )
        return {
            "data": response.get("data", response.get("releases", [])),
            "hasMore": response.get("hasMore", False),
            "limit": response.get("limit", limit if limit is not None else 50),
            "offset": response.get(
                "offset",
                offset if offset is not None else 0,
            ),
        }

    def create(
        self,
        *,
        target_kind: ReleaseTargetKind,
        target_resource_id: str,
        candidate_id: str,
        acceptance_fingerprint: str,
        action: ReleaseAction,
        idempotency_key: str,
        project_id: str | None = None,
    ) -> dict[str, Any]:
        return self._client.post(
            "/release-control",
            {
                "schemaVersion": "computer_agents_release_request_v1",
                "target": {
                    "kind": target_kind,
                    "resourceId": target_resource_id,
                },
                "candidate": {
                    "id": candidate_id,
                    "acceptanceFingerprint": acceptance_fingerprint,
                },
                "action": action,
                "projectId": project_id,
                "idempotencyKey": idempotency_key,
            },
        )

    def get(self, release_id: str) -> Release:
        response = self._client.get(
            f"/release-control/{_id(release_id)}",
        )
        return response["release"]

    def execute(
        self,
        release_id: str,
        *,
        expected_revision: int | None = None,
    ) -> dict[str, Any]:
        return self._client.post(
            f"/release-control/{_id(release_id)}/execute",
            (
                {"expectedRevision": expected_revision}
                if expected_revision is not None
                else {}
            ),
        )

    def reconcile(self, release_id: str) -> dict[str, Any]:
        return self._client.post(
            f"/release-control/{_id(release_id)}/reconcile",
            {},
        )

    def cancel(
        self,
        release_id: str,
        *,
        reason: str | None = None,
    ) -> Release:
        response = self._client.post(
            f"/release-control/{_id(release_id)}/cancel",
            {"reason": reason} if reason else {},
        )
        return response["release"]

    def list_project_delivery_authorizations(
        self,
        *,
        project_id: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        response = self._client.get(
            "/release-control/project-deliveries",
            query={
                "projectId": project_id,
                "limit": limit,
                "offset": offset,
            },
        )
        return {
            "data": response.get(
                "data",
                response.get("authorizations", []),
            ),
            "hasMore": response.get("hasMore", False),
            "limit": response.get(
                "limit",
                limit if limit is not None else 50,
            ),
            "offset": response.get(
                "offset",
                offset if offset is not None else 0,
            ),
        }

    def authorize_project_delivery(
        self,
        *,
        delivery_execution_id: str,
        idempotency_key: str,
    ) -> dict[str, Any]:
        return self._client.post(
            "/release-control/project-deliveries",
            {
                "schemaVersion":
                    "computer_agents_project_delivery_release_request_v1",
                "deliveryExecutionId": delivery_execution_id,
                "idempotencyKey": idempotency_key,
            },
        )

    def get_project_delivery_authorization(
        self,
        authorization_id: str,
    ) -> ProjectDeliveryReleaseAuthorization:
        response = self._client.get(
            "/release-control/project-deliveries/"
            f"{_id(authorization_id)}",
        )
        return response["authorization"]

    def promote_project_delivery(
        self,
        authorization_id: str,
        *,
        idempotency_key: str,
    ) -> dict[str, Any]:
        return self._client.post(
            "/release-control/project-deliveries/"
            f"{_id(authorization_id)}/promote",
            {
                "schemaVersion":
                    "computer_agents_project_delivery_promotion_request_v1",
                "idempotencyKey": idempotency_key,
            },
        )

    def get_project_delivery_promotion(
        self,
        promotion_id: str,
    ) -> ProjectDeliveryPromotion:
        response = self._client.get(
            "/release-control/project-delivery-promotions/"
            f"{_id(promotion_id)}",
        )
        return response["promotion"]

    def activate_project_delivery_promotion(
        self,
        promotion_id: str,
    ) -> dict[str, Any]:
        return self._client.post(
            "/release-control/project-delivery-promotions/"
            f"{_id(promotion_id)}/activate",
            {},
        )
