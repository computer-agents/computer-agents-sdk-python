"""Administration, identity, communication, and system SDK surfaces."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from .._api_client import ApiClient


def _id(value: str) -> str:
    return quote(value, safe="")


def _data(response: dict[str, Any], key: str) -> list[dict[str, Any]]:
    return response.get("data", response.get(key, []))


class ApiKeysResource:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def list(self) -> list[dict[str, Any]]:
        return _data(self._client.get("/api-keys"), "apiKeys")

    def create(self, **params: Any) -> dict[str, Any]:
        return self._client.post("/api-keys", params)

    def reveal(self, api_key_id: str) -> dict[str, Any]:
        return self._client.get(f"/api-keys/{_id(api_key_id)}/reveal")

    def revoke(self, api_key_id: str) -> dict[str, Any]:
        return self._client.post(f"/api-keys/{_id(api_key_id)}/revoke", {})

    def analytics(self, *, period: str | None = None) -> dict[str, Any]:
        return self._client.get(
            "/api-keys/analytics/overview",
            query={"period": period},
        )


class VoiceAgentsResource:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def list(self) -> list[dict[str, Any]]:
        return _data(self._client.get("/voice-agents"), "agents")

    def get(self, agent_id: str) -> dict[str, Any]:
        return self._client.get(f"/voice-agents/agents/{_id(agent_id)}")

    def update(self, agent_id: str, **params: Any) -> dict[str, Any]:
        return self._client.patch(f"/voice-agents/agents/{_id(agent_id)}", params)

    def provision_phone_number(self, agent_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(
            f"/voice-agents/agents/{_id(agent_id)}/phone-number",
            params,
        )

    def release_phone_number(self, agent_id: str) -> None:
        self._client.delete(f"/voice-agents/agents/{_id(agent_id)}/phone-number")

    def create_session(self, agent_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(
            f"/voice-agents/agents/{_id(agent_id)}/sessions",
            params,
        )

    def list_sessions(
        self,
        *,
        agent_id: str | None = None,
        thread_id: str | None = None,
        channel: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        return _data(
            self._client.get(
                "/voice-agents/sessions",
                query={
                    "agentId": agent_id,
                    "threadId": thread_id,
                    "channel": channel,
                    "limit": limit,
                    "offset": offset,
                },
            ),
            "sessions",
        )

    def send_message(self, session_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(
            f"/voice-agents/sessions/{_id(session_id)}/messages",
            params,
        )

    def get_grounding(self, session_id: str) -> dict[str, Any]:
        return self._client.get(
            f"/voice-agents/sessions/{_id(session_id)}/grounding"
        )

    def end_session(self, session_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(
            f"/voice-agents/sessions/{_id(session_id)}/end",
            params,
        )


class TeamsResource:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def list(self) -> list[dict[str, Any]]:
        return _data(self._client.get("/teams"), "teams")

    def create(self, **params: Any) -> dict[str, Any]:
        return self._client.post("/teams", params)

    def get(self, team_id: str) -> dict[str, Any]:
        return self._client.get(f"/teams/{_id(team_id)}")

    def update(self, team_id: str, **params: Any) -> dict[str, Any]:
        return self._client.patch(f"/teams/{_id(team_id)}", params)

    def delete(self, team_id: str) -> None:
        self._client.delete(f"/teams/{_id(team_id)}")

    def list_members(self, team_id: str) -> list[dict[str, Any]]:
        return _data(self._client.get(f"/teams/{_id(team_id)}/members"), "members")

    def lookup_member_profiles(
        self,
        team_id: str,
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
            f"/teams/{_id(team_id)}/member-profiles/lookup",
            body,
        )

    def update_member(self, team_id: str, member_id: str, **params: Any) -> dict[str, Any]:
        return self._client.patch(
            f"/teams/{_id(team_id)}/members/{_id(member_id)}",
            params,
        )

    def remove_member(self, team_id: str, member_id: str) -> None:
        self._client.delete(f"/teams/{_id(team_id)}/members/{_id(member_id)}")

    def list_pending_invitations(self) -> list[dict[str, Any]]:
        return _data(self._client.get("/teams/invitations/pending"), "invitations")

    def accept_invitation(self, invitation_id: str) -> dict[str, Any]:
        return self._client.post(
            f"/teams/invitations/{_id(invitation_id)}/accept",
            {},
        )

    def decline_invitation(self, invitation_id: str) -> dict[str, Any]:
        return self._client.post(
            f"/teams/invitations/{_id(invitation_id)}/decline",
            {},
        )

    def list_invitations(self, team_id: str) -> list[dict[str, Any]]:
        return _data(
            self._client.get(f"/teams/{_id(team_id)}/invitations"),
            "invitations",
        )

    def invite(self, team_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(f"/teams/{_id(team_id)}/invitations", params)

    def revoke_invitation(self, team_id: str, invitation_id: str) -> dict[str, Any]:
        return self._client.post(
            f"/teams/{_id(team_id)}/invitations/{_id(invitation_id)}/revoke",
            {},
        )

    def list_resource_shares(self, team_id: str) -> list[dict[str, Any]]:
        return _data(
            self._client.get(f"/teams/{_id(team_id)}/resource-shares"),
            "shares",
        )

    def share_resource(self, team_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(
            f"/teams/{_id(team_id)}/resource-shares",
            params,
        )

    def unshare_resource(self, team_id: str, share_id: str) -> None:
        self._client.delete(
            f"/teams/{_id(team_id)}/resource-shares/{_id(share_id)}"
        )


class AuthorizationResource:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def check(self, **params: Any) -> dict[str, Any]:
        return self._client.post("/authorization/check", params)

    def batch_check(self, **params: Any) -> dict[str, Any]:
        return self._client.post("/authorization/batch-check", params)

    def explain(self, **params: Any) -> dict[str, Any]:
        return self._client.post("/authorization/explain", params)

    def policy_versions(
        self,
        *,
        resource_type: str,
        resource_id: str,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return self._client.get(
            "/authorization/policy-versions",
            query={
                "resourceType": resource_type,
                "resourceId": resource_id,
                "limit": limit,
            },
        )

    def list_delegations(
        self,
        *,
        principal_id: str | None = None,
        status: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        return _data(
            self._client.get(
                "/authorization/delegations",
                query={"principalId": principal_id, "status": status, "limit": limit},
            ),
            "delegations",
        )

    def create_delegation(self, **params: Any) -> dict[str, Any]:
        return self._client.post("/authorization/delegations", params)

    def delete_delegation(
        self,
        delegation_id: str,
        *,
        reason: str | None = None,
    ) -> None:
        self._client.delete(
            f"/authorization/delegations/{_id(delegation_id)}",
            {"reason": reason} if reason is not None else None,
        )

    def list_approvals(
        self,
        *,
        principal_id: str | None = None,
        status: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        return _data(
            self._client.get(
                "/authorization/approvals",
                query={"principalId": principal_id, "status": status, "limit": limit},
            ),
            "approvals",
        )

    def resolve_approval(self, approval_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(
            f"/authorization/approvals/{_id(approval_id)}/resolve",
            params,
        )

    def list_decisions(
        self,
        *,
        resource_type: str | None = None,
        resource_id: str | None = None,
        principal_id: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        return _data(
            self._client.get(
                "/authorization/decisions",
                query={
                    "resourceType": resource_type,
                    "resourceId": resource_id,
                    "principalId": principal_id,
                    "limit": limit,
                },
            ),
            "decisions",
        )


class IdentityConnectionsResource:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def list(self) -> list[dict[str, Any]]:
        return _data(self._client.get("/identity-connections"), "connections")

    def create(self, **params: Any) -> dict[str, Any]:
        return self._client.post("/identity-connections", params)

    def get(self, connection_id: str) -> dict[str, Any]:
        return self._client.get(f"/identity-connections/{_id(connection_id)}")

    def update(self, connection_id: str, **params: Any) -> dict[str, Any]:
        return self._client.patch(
            f"/identity-connections/{_id(connection_id)}",
            params,
        )

    def delete(self, connection_id: str) -> None:
        self._client.delete(f"/identity-connections/{_id(connection_id)}")

    def validate(self, connection_id: str) -> dict[str, Any]:
        return self._client.post(
            f"/identity-connections/{_id(connection_id)}/validate",
            {},
        )

    def create_scim_token(self, connection_id: str) -> dict[str, Any]:
        return self._client.post(
            f"/identity-connections/{_id(connection_id)}/scim-token",
            {},
        )

    def revoke_scim_token(self, connection_id: str) -> None:
        self._client.delete(
            f"/identity-connections/{_id(connection_id)}/scim-token"
        )

    def list_group_mappings(self, connection_id: str) -> list[dict[str, Any]]:
        return _data(
            self._client.get(
                f"/identity-connections/{_id(connection_id)}/group-mappings"
            ),
            "mappings",
        )

    def create_group_mapping(self, connection_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(
            f"/identity-connections/{_id(connection_id)}/group-mappings",
            params,
        )

    def delete_group_mapping(self, connection_id: str, mapping_id: str) -> None:
        self._client.delete(
            f"/identity-connections/{_id(connection_id)}/group-mappings/{_id(mapping_id)}"
        )


class AccountResource:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def get(self) -> dict[str, Any]:
        return self._client.get("/account")

    def update_profile(self, **params: Any) -> dict[str, Any]:
        return self._client.patch("/account/profile", params)

    def get_avatar(self, user_id: str) -> bytes:
        return self._client.request_raw(
            "GET",
            f"/account/avatar/{_id(user_id)}",
        ).content

    def get_data_controls(self) -> dict[str, Any]:
        return self._client.get("/account/data-controls")

    def delete_data_category(self, category: str) -> dict[str, Any]:
        return self._client.delete(
            f"/account/data-controls/{_id(category)}",
            {"confirmation": category},
        )

    def delete(self) -> None:
        self._client.delete("/account")


class ReportsResource:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        return _data(
            self._client.get("/reports", query={"limit": limit, "offset": offset}),
            "reports",
        )

    def create(self, **params: Any) -> dict[str, Any]:
        return self._client.post("/reports", params)


class EmailResource:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def status(self) -> dict[str, Any]:
        return self._client.get("/email/status")

    def list_messages_page(
        self,
        *,
        limit: int | None = None,
        max_results: int | None = None,
        q: str | None = None,
        page_token: str | None = None,
        include_body: bool | None = None,
        label_ids: list[str] | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """List Gmail messages while preserving pagination metadata.

        ``max_results`` and ``cursor`` are deprecated aliases for ``limit`` and
        ``page_token`` respectively.
        """
        return self._client.get(
            "/email/messages",
            query={
                "limit": limit if limit is not None else max_results,
                "q": q,
                "pageToken": page_token or cursor,
                "includeBody": include_body,
                "labelIds": label_ids,
            },
        )

    def list_messages(self, **params: Any) -> list[dict[str, Any]]:
        return _data(self.list_messages_page(**params), "messages")

    def get_message(
        self,
        message_id: str,
        *,
        include_body: bool | None = None,
    ) -> dict[str, Any]:
        return self._client.get(
            f"/email/messages/{_id(message_id)}",
            query={"includeBody": include_body},
        )

    def send(self, **params: Any) -> dict[str, Any]:
        return self._client.post("/email/send", params)


class AttachmentsResource:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def upload(self, **params: Any) -> dict[str, Any]:
        return self._client.post("/attachments/upload", params)

    def download(self, attachment_id: str) -> bytes:
        return self._client.request_raw(
            "GET",
            f"/attachments/{_id(attachment_id)}",
        ).content

    def delete(self, attachment_id: str) -> None:
        self._client.delete(f"/attachments/{_id(attachment_id)}")


class SystemResource:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def version(self) -> dict[str, Any]:
        return self._client.get("/version")

    def deployment_profile(self) -> dict[str, Any]:
        return self._client.get("/deployment-profile")
