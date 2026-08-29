from __future__ import annotations

import httpx
import pytest

from computer_agents._api_client import ApiClient
from computer_agents.client import ComputerAgentsClient


def test_api_client_uses_appliance_url_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("COMPUTER_AGENTS_API_URL", "https://stockifi.computer-agents.com/")
    monkeypatch.delenv("COMPUTER_AGENTS_BASE_URL", raising=False)

    with ApiClient(api_key="tb_test") as client:
        assert client.base_url == "https://stockifi.computer-agents.com"


def test_api_client_constructor_url_overrides_environment(monkeypatch) -> None:
    monkeypatch.setenv("COMPUTER_AGENTS_API_URL", "https://stockifi.computer-agents.com")

    with ApiClient(api_key="tb_test", base_url="http://127.0.0.1:4177/") as client:
        assert client.base_url == "http://127.0.0.1:4177"


def test_api_client_prefers_canonical_base_url_environment_variable(monkeypatch) -> None:
    monkeypatch.setenv("COMPUTER_AGENTS_BASE_URL", "https://stockifi.computer-agents.com")
    monkeypatch.setenv("COMPUTER_AGENTS_API_URL", "https://api.legacy.example")

    with ApiClient(api_key="tb_test") as client:
        assert client.base_url == "https://stockifi.computer-agents.com"


def test_api_client_routes_resource_paths_through_appliance_v1() -> None:
    requested_paths: list[str] = []

    def respond(request: httpx.Request) -> httpx.Response:
        requested_paths.append(request.url.path)
        return httpx.Response(200, json={"data": []})

    with ApiClient(
        api_key="tb_test",
        base_url="https://stockifi.computer-agents.com/",
    ) as client:
        client._client.close()
        client._client = httpx.Client(
            base_url=client.api_base_url,
            transport=httpx.MockTransport(respond),
        )

        client.get("/agents")
        client.get("/v1/organizations")

        assert client.base_url == "https://stockifi.computer-agents.com"
        assert client.api_base_url == "https://stockifi.computer-agents.com/v1"
        assert requested_paths == ["/v1/agents", "/v1/organizations"]


def test_high_level_client_exposes_configured_base_url() -> None:
    with ComputerAgentsClient(
        api_key="tb_test",
        base_url="https://stockifi.computer-agents.com/",
    ) as client:
        assert client.base_url == "https://stockifi.computer-agents.com"
        assert client.api.api_base_url == "https://stockifi.computer-agents.com/v1"


def test_api_client_does_not_duplicate_versioned_base_url() -> None:
    with ApiClient(
        api_key="tb_test",
        base_url="https://stockifi.computer-agents.com/v1/",
    ) as client:
        request = client._client.build_request("GET", "/agents")

        assert client.base_url == "https://stockifi.computer-agents.com/v1"
        assert client.api_base_url == "https://stockifi.computer-agents.com/v1"
        assert request.url.path == "/v1/agents"


@pytest.mark.parametrize(
    "base_url, message",
    [
        ("stockifi.computer-agents.com", "absolute http or https"),
        ("ftp://stockifi.computer-agents.com", "absolute http or https"),
        ("https://user:password@stockifi.computer-agents.com", "cannot contain credentials"),
        ("https://stockifi.computer-agents.com?tenant=other", "query or fragment"),
    ],
)
def test_api_client_rejects_unsafe_base_urls(base_url: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        ApiClient(api_key="tb_test", base_url=base_url)


def test_api_client_supports_destructive_confirmation_bodies() -> None:
    requests: list[httpx.Request] = []

    def respond(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"deleted": True})

    with ApiClient(api_key="tb_test") as client:
        client._client.close()
        client._client = httpx.Client(
            base_url=client.api_base_url,
            transport=httpx.MockTransport(respond),
        )

        client.delete(
            "/account/data-controls/threads",
            {"confirmation": "threads"},
        )

    assert len(requests) == 1
    assert requests[0].method == "DELETE"
    assert requests[0].url.path == "/v1/account/data-controls/threads"
    assert requests[0].read() == b'{"confirmation":"threads"}'
