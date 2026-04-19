# Orbis Python SDK (Phase 8 candidate)

This SDK provides a lightweight API-key client for post-MVP integrations.

## Supported methods
- `get_health()`
- `list_projects()`
- `list_tasks(...)`
- `create_task(payload)`
- `get_daily_plan()`
- `start_focus_session(...)`

## Example
```python
from orbis_sdk import OrbisClient

with OrbisClient(base_url="http://localhost", api_key="orbis_...") as client:
    print(client.get_health())
    tasks = client.list_tasks(status="todo")
    print(tasks)
```

## Notes
- Auth uses `X-API-Key` to align with Phase 7 API-key flow.
- This is intentionally thin and maps directly to existing REST endpoints.
