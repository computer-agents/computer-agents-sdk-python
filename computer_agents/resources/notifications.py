"""Notifications resource manager."""

from __future__ import annotations

from typing import Any

from .._api_client import ApiClient
from ..types import (
    InAppNotification,
    PushTokenDeleteResponse,
    PushTokenDescriptor,
    PushTokenRegistrationResponse,
)


class NotificationsResource:
    """In-app product notifications and push token registration."""

    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def list_in_app(self) -> list[InAppNotification]:
        """List active in-app product notifications."""
        resp = self._client.get("/notifications/in-app")
        return resp["data"]

    def register_push_token(
        self,
        token: str,
        bundle_id: str,
        *,
        platform: str | None = None,
    ) -> PushTokenRegistrationResponse:
        """Register a push notification token for the current user."""
        body: dict[str, Any] = {"token": token, "bundleId": bundle_id}
        if platform is not None:
            body["platform"] = platform
        return self._client.post("/notifications/push-token", body)

    def unregister_push_token(self, token: str) -> PushTokenDeleteResponse:
        """Unregister a push notification token."""
        return self._client.request(
            "DELETE",
            "/notifications/push-token",
            body={"token": token},
        )

    def list_push_tokens(self) -> list[PushTokenDescriptor]:
        """List active push token descriptors for the current user."""
        resp = self._client.get("/notifications/push-tokens")
        return resp["tokens"]
