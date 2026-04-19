from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


class OrbisSDKError(RuntimeError):
    """Raised when the Orbis API request fails."""


@dataclass(frozen=True)
class OrbisClientConfig:
    base_url: str
    api_key: str
    timeout_seconds: float = 10.0


class OrbisClient:
    """Small public SDK client for Orbis API-key integrations."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        timeout_seconds: float = 10.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._config = OrbisClientConfig(base_url=base_url.rstrip("/"), api_key=api_key, timeout_seconds=timeout_seconds)
        self._client = httpx.Client(
            base_url=self._config.base_url,
            timeout=self._config.timeout_seconds,
            headers={"X-API-Key": self._config.api_key},
            transport=transport,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> OrbisClient:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def get_health(self) -> dict[str, Any]:
        return self._request("GET", "/api/v1/health")

    def list_projects(self) -> list[dict[str, Any]]:
        return self._request("GET", "/api/v1/projects")

    def list_tasks(
        self,
        *,
        project_id: str | None = None,
        status: str | None = None,
        include_private: bool | None = None,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if project_id:
            params["project_id"] = project_id
        if status:
            params["status"] = status
        if include_private is not None:
            params["include_private"] = include_private

        return self._request("GET", "/api/v1/tasks", params=params or None)

    def create_task(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/api/v1/tasks", json=payload)

    def get_daily_plan(self) -> dict[str, Any]:
        return self._request("GET", "/api/v1/focus/daily-plan")

    def start_focus_session(
        self,
        *,
        task_id: str,
        planned_minutes: int | None = None,
        energy_before: int | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"task_id": task_id}
        if planned_minutes is not None:
            payload["planned_minutes"] = planned_minutes
        if energy_before is not None:
            payload["energy_before"] = energy_before

        return self._request("POST", "/api/v1/focus/start", json=payload)

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        try:
            response = self._client.request(method, path, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise OrbisSDKError(
                f"Orbis API returned {exc.response.status_code} for {method} {path}: {exc.response.text}"
            ) from exc
        except httpx.RequestError as exc:
            raise OrbisSDKError(f"Orbis API request failed for {method} {path}: {exc}") from exc
