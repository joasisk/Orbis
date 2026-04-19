import httpx
import pytest
from orbis_sdk import OrbisClient, OrbisSDKError


def test_get_health_uses_api_key_header() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v1/health"
        assert request.headers.get("X-API-Key") == "test-key"
        return httpx.Response(200, json={"status": "ok"})

    transport = httpx.MockTransport(handler)

    with OrbisClient(base_url="http://orbis.local", api_key="test-key", transport=transport) as client:
        result = client.get_health()

    assert result == {"status": "ok"}


def test_list_tasks_passes_filters() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v1/tasks"
        assert request.url.params["project_id"] == "proj_123"
        assert request.url.params["status"] == "todo"
        assert request.url.params["include_private"] == "true"
        return httpx.Response(200, json=[{"id": "task_1"}])

    transport = httpx.MockTransport(handler)

    with OrbisClient(base_url="http://orbis.local", api_key="key", transport=transport) as client:
        result = client.list_tasks(project_id="proj_123", status="todo", include_private=True)

    assert result == [{"id": "task_1"}]


def test_http_status_errors_raise_orbis_sdk_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, json={"detail": "forbidden"})

    transport = httpx.MockTransport(handler)

    with OrbisClient(base_url="http://orbis.local", api_key="key", transport=transport) as client:
        with pytest.raises(OrbisSDKError, match="403"):
            client.list_projects()
