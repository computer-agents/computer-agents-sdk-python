"""Low-level HTTP client for the Computer Agents Cloud API.

Handles authentication, request/response processing, SSE streaming,
and error handling. Higher-level resource managers use this client.
"""

from __future__ import annotations

import json
import os
from typing import Any, Generator, Iterator
from urllib.parse import SplitResult, urlsplit, urlunsplit

import httpx

from ._exceptions import ApiClientError


DEFAULT_BASE_URL = "https://api.computer-agents.com"
DEFAULT_TIMEOUT = 60.0  # seconds
API_VERSION_PATH = "/v1"


def _normalize_configured_base_url(base_url: str) -> str:
    """Validate and normalize a cloud or appliance deployment URL."""
    base_url = base_url.strip()
    try:
        parsed = urlsplit(base_url)
        # Accessing hostname and port validates malformed authorities and IPv6 hosts.
        hostname = parsed.hostname
        _ = parsed.port
    except ValueError as exc:
        raise ValueError("The Computer Agents base URL must be a valid absolute URL.") from exc

    if (
        parsed.scheme not in {"http", "https"}
        or not hostname
        or any(character.isspace() for character in hostname)
    ):
        raise ValueError("The Computer Agents base URL must be an absolute http or https URL.")
    if parsed.username or parsed.password:
        raise ValueError("The Computer Agents base URL cannot contain credentials.")
    if parsed.query or parsed.fragment:
        raise ValueError("The Computer Agents base URL cannot contain a query or fragment.")

    normalized = SplitResult(
        scheme=parsed.scheme,
        netloc=parsed.netloc,
        path=parsed.path.rstrip("/"),
        query="",
        fragment="",
    )
    return urlunsplit(normalized).rstrip("/")


def _resolve_api_base_url(base_url: str) -> str:
    parsed = urlsplit(base_url)
    path = parsed.path.rstrip("/")
    api_path = path if path.endswith(API_VERSION_PATH) else f"{path}{API_VERSION_PATH}"
    return urlunsplit(parsed._replace(path=api_path)).rstrip("/")


def _resolve_request_path(path: str) -> str:
    parsed = urlsplit(path)
    if parsed.scheme in {"http", "https"}:
        return path
    normalized = path if path.startswith("/") else f"/{path}"
    if normalized == API_VERSION_PATH:
        return "/"
    if normalized.startswith(f"{API_VERSION_PATH}/"):
        return normalized[len(API_VERSION_PATH) :]
    return normalized


class ApiClient:
    """Low-level HTTP client for the Computer Agents API.

    Args:
        api_key: API key for authentication.
        base_url: Base URL for the API. Defaults to ``https://api.computer-agents.com``.
        timeout: Request timeout in seconds. Defaults to 60.
        debug: Enable debug logging. Defaults to False.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str | None = None,
        timeout: float | None = None,
        debug: bool = False,
        organization_id: str | None = None,
    ) -> None:
        if not api_key:
            raise ValueError(
                "API key is required. Provide it via:\n"
                '1. Constructor: ApiClient(api_key="...")\n'
                "2. Environment variable: COMPUTER_AGENTS_API_KEY"
            )

        self._api_key = api_key
        configured_base_url = (
            base_url
            or os.environ.get("COMPUTER_AGENTS_BASE_URL")
            or os.environ.get("COMPUTER_AGENTS_API_URL")
            or DEFAULT_BASE_URL
        )
        self._base_url = _normalize_configured_base_url(configured_base_url)
        self._api_base_url = _resolve_api_base_url(self._base_url)
        self._timeout = timeout or DEFAULT_TIMEOUT
        self._debug = debug
        self._organization_id = organization_id.strip() if organization_id else None

        default_headers = {
            "Authorization": f"Bearer {self._api_key}",
        }
        if self._organization_id:
            default_headers["X-Computer-Agents-Organization"] = self._organization_id

        self._client = httpx.Client(
            base_url=self._api_base_url,
            timeout=httpx.Timeout(self._timeout, connect=10.0),
            headers=default_headers,
        )

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    @property
    def organization_id(self) -> str | None:
        """Active organization sent with tenant-scoped requests."""
        return self._organization_id

    def __enter__(self) -> "ApiClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    # =========================================================================
    # Core request methods
    # =========================================================================

    def request(
        self,
        method: str,
        path: str,
        *,
        body: Any | None = None,
        query: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> Any:
        """Make an HTTP request to the API and return parsed JSON."""
        # Filter out None values from query params
        params = None
        if query:
            params = {k: v for k, v in query.items() if v is not None}

        request_headers: dict[str, str] = {}
        if headers:
            request_headers.update(headers)
        if body is not None and "Content-Type" not in request_headers:
            request_headers["Content-Type"] = "application/json"

        request_path = _resolve_request_path(path)

        if self._debug:
            request_url = (
                request_path
                if request_path.startswith(("http://", "https://"))
                else f"{self._api_base_url}{request_path}"
            )
            print(f"[ApiClient] {method} {request_url}")

        try:
            response = self._client.request(
                method,
                request_path,
                json=body if body is not None else None,
                params=params,
                headers=request_headers,
                timeout=timeout or self._timeout,
            )
        except httpx.TimeoutException:
            raise ApiClientError(
                f"Request timeout after {timeout or self._timeout}s",
                408,
                "TIMEOUT",
            )
        except httpx.HTTPError as e:
            raise ApiClientError(str(e), 500, "NETWORK_ERROR")

        if not response.is_success:
            raise self._parse_error(response)

        # Handle 204 No Content
        if response.status_code == 204:
            return None

        return response.json()

    def request_stream(
        self,
        method: str,
        path: str,
        *,
        body: Any | None = None,
        query: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> Iterator[dict[str, Any]]:
        """Make a streaming SSE request and yield parsed events."""
        request_headers = {
            "Accept": "text/event-stream",
            **(headers or {}),
        }
        if body is not None:
            request_headers.setdefault("Content-Type", "application/json")

        content = json.dumps(body).encode() if body is not None else None
        request_path = _resolve_request_path(path)

        try:
            with self._client.stream(
                method,
                request_path,
                content=content,
                params={key: value for key, value in (query or {}).items() if value is not None},
                headers=request_headers,
                timeout=timeout or 600.0,  # 10 minutes for streaming
            ) as response:
                if not response.is_success:
                    # Read error body
                    response.read()
                    raise self._parse_error(response)

                yield from self._parse_sse(response.iter_lines())
        except httpx.TimeoutException:
            raise ApiClientError(
                f"Stream timeout after {timeout or 600.0}s",
                408,
                "TIMEOUT",
            )

    def request_raw(
        self,
        method: str,
        path: str,
        *,
        query: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        """Make a raw HTTP request and return the response object."""
        request_path = _resolve_request_path(path)
        try:
            response = self._client.request(
                method,
                request_path,
                params={key: value for key, value in (query or {}).items() if value is not None},
                headers=headers,
                timeout=timeout or self._timeout,
            )
        except httpx.TimeoutException:
            raise ApiClientError(
                f"Request timeout after {timeout or self._timeout}s",
                408,
                "TIMEOUT",
            )

        if not response.is_success:
            raise self._parse_error(response)

        return response

    def request_form(
        self,
        method: str,
        path: str,
        *,
        data: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> Any:
        """Make a multipart form request."""
        request_path = _resolve_request_path(path)
        try:
            response = self._client.request(
                method,
                request_path,
                data=data,
                files=files,
                timeout=timeout or self._timeout,
            )
        except httpx.TimeoutException:
            raise ApiClientError(
                f"Request timeout after {timeout or self._timeout}s",
                408,
                "TIMEOUT",
            )

        if not response.is_success:
            raise self._parse_error(response)

        return response.json()

    # =========================================================================
    # Convenience methods
    # =========================================================================

    def get(
        self,
        path: str,
        query: dict[str, Any] | None = None,
    ) -> Any:
        return self.request("GET", path, query=query)

    def post(
        self,
        path: str,
        body: Any | None = None,
    ) -> Any:
        return self.request("POST", path, body=body)

    def patch(
        self,
        path: str,
        body: Any | None = None,
    ) -> Any:
        return self.request("PATCH", path, body=body)

    def put(
        self,
        path: str,
        body: Any | None = None,
    ) -> Any:
        return self.request("PUT", path, body=body)

    def delete(self, path: str, body: Any | None = None) -> Any:
        return self.request("DELETE", path, body=body)

    # =========================================================================
    # Accessors
    # =========================================================================

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def api_base_url(self) -> str:
        """Return the canonical versioned URL used for API requests."""
        return self._api_base_url

    @property
    def api_key(self) -> str:
        return self._api_key

    @property
    def timeout(self) -> float:
        return self._timeout

    @property
    def debug(self) -> bool:
        return self._debug

    # =========================================================================
    # Internal helpers
    # =========================================================================

    @staticmethod
    def _parse_sse(lines: Iterator[str]) -> Generator[dict[str, Any], None, None]:
        """Parse SSE event stream lines into dicts."""
        for line in lines:
            if line.startswith("data: "):
                data_str = line[6:]
                if not data_str.strip():
                    continue
                try:
                    yield json.loads(data_str)
                except json.JSONDecodeError:
                    continue

    def _parse_error(self, response: httpx.Response) -> ApiClientError:
        try:
            error_data = response.json()
        except Exception:
            error_data = {
                "error": response.reason_phrase or "Unknown error",
                "message": f"HTTP {response.status_code}",
            }

        return ApiClientError(
            message=error_data.get("message") or error_data.get("error", "Unknown error"),
            status=response.status_code,
            code=error_data.get("code"),
            details=error_data.get("details"),
        )
