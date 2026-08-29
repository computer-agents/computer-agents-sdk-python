"""Organization tenancy, membership, invitations, and ownership."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from .._api_client import ApiClient


def _id(value: str) -> str:
    return quote(value, safe="")


def _data(response: dict[str, Any], key: str) -> list[dict[str, Any]]:
    return response.get("data", response.get(key, []))


class OrganizationsResource:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def list(self) -> list[dict[str, Any]]:
        return _data(self._client.get("/organizations"), "organizations")

    def current(self) -> dict[str, Any]:
        response = self._client.get("/organizations/current")
        return response.get("data", response.get("organization", response))

    def create(self, name: str, **params: Any) -> dict[str, Any]:
        response = self._client.post("/organizations", {"name": name, **params})
        return response.get("data", response.get("organization", response))

    def get(self, organization_id: str) -> dict[str, Any]:
        response = self._client.get(f"/organizations/{_id(organization_id)}")
        return response.get("data", response.get("organization", response))

    def update(self, organization_id: str, **params: Any) -> dict[str, Any]:
        response = self._client.patch(
            f"/organizations/{_id(organization_id)}",
            params,
        )
        return response.get("data", response.get("organization", response))

    def list_members(self, organization_id: str) -> list[dict[str, Any]]:
        return _data(
            self._client.get(f"/organizations/{_id(organization_id)}/members"),
            "members",
        )

    def lookup_member_profiles(
        self,
        organization_id: str,
        user_ids: list[str] | None = None,
        *,
        members: list[dict[str, Any]] | None = None,
        emails: list[str] | None = None,
    ) -> dict[str, Any]:
        body = {
            key: value
            for key, value in {
                "members": members,
                "userIds": user_ids,
                "emails": emails,
            }.items()
            if value is not None
        }
        return self._client.post(
            f"/organizations/{_id(organization_id)}/member-profiles/lookup",
            body,
        )

    def update_member(
        self,
        organization_id: str,
        member_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.patch(
            f"/organizations/{_id(organization_id)}/members/{_id(member_id)}",
            params,
        )

    def remove_member(self, organization_id: str, member_id: str) -> None:
        self._client.delete(
            f"/organizations/{_id(organization_id)}/members/{_id(member_id)}"
        )

    def transfer_ownership(
        self,
        organization_id: str,
        member_id: str,
    ) -> dict[str, Any]:
        return self._client.post(
            f"/organizations/{_id(organization_id)}/transfer-ownership",
            {"memberId": member_id},
        )

    def list_resources(self, organization_id: str) -> list[dict[str, Any]]:
        return _data(
            self._client.get(f"/organizations/{_id(organization_id)}/resources"),
            "resources",
        )

    def list_pending_invitations(self) -> list[dict[str, Any]]:
        return _data(
            self._client.get("/organizations/invitations/pending"),
            "invitations",
        )

    def accept_invitation(self, invitation_id: str) -> dict[str, Any]:
        return self._client.post(
            f"/organizations/invitations/{_id(invitation_id)}/accept",
            {},
        )

    def decline_invitation(self, invitation_id: str) -> dict[str, Any]:
        return self._client.post(
            f"/organizations/invitations/{_id(invitation_id)}/decline",
            {},
        )

    def list_invitations(self, organization_id: str) -> list[dict[str, Any]]:
        return _data(
            self._client.get(f"/organizations/{_id(organization_id)}/invitations"),
            "invitations",
        )

    def invite(self, organization_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(
            f"/organizations/{_id(organization_id)}/invitations",
            params,
        )

    def revoke_invitation(
        self,
        organization_id: str,
        invitation_id: str,
    ) -> dict[str, Any]:
        return self._client.post(
            f"/organizations/{_id(organization_id)}/invitations/{_id(invitation_id)}/revoke",
            {},
        )
