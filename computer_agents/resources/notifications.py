"""Notifications resource manager."""

from __future__ import annotations

from typing import Any

from .._api_client import ApiClient
from ..types import (
    InAppNotification,
    NotificationCatalog,
    NotificationInboxItem,
    NotificationInboxListResponse,
    NotificationInboxSummary,
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

    def list(
        self,
        *,
        state: str | None = None,
        category: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> NotificationInboxListResponse:
        """List the current user's durable, organization-aware notification inbox."""
        query = {
            key: value
            for key, value in {
                "state": state,
                "category": category,
                "cursor": cursor,
                "limit": limit,
            }.items()
            if value is not None
        }
        return self._client.get("/notifications", query=query)

    def get_catalog(self) -> NotificationCatalog:
        """Read the versioned notification event and preference taxonomy."""
        return self._client.get("/notifications/catalog")

    def get_summary(self) -> NotificationInboxSummary:
        """Return total and unread counts for the active organization."""
        return self._client.get("/notifications/summary")

    def update(self, notification_id: str, **state: bool) -> NotificationInboxItem:
        """Persist read, dismissed, archived, or acted state for one item."""
        resp = self._client.patch(f"/notifications/{notification_id}", state)
        return resp["notification"]

    def mark_all_read(self) -> dict[str, Any]:
        """Mark every unread notification in the active organization as read."""
        return self._client.post("/notifications/read-all", {})

    def get_preferences(self) -> dict[str, Any]:
        """Get notification delivery preferences for the current user."""
        return self._client.get("/notifications/preferences")

    def update_preferences(self, **preferences: bool) -> dict[str, Any]:
        """Patch notification delivery preferences for the current user."""
        return self._client.put("/notifications/preferences", {"preferences": preferences})

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
