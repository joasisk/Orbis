import json
from collections.abc import Sequence
from dataclasses import dataclass

import httpx

from app.core.config import settings
from app.models.domain import Task

PROMPT_TEMPLATE_VERSION = "planning.weekly.v1"


@dataclass(slots=True)
class WeeklyPlanSuggestion:
    task_id: str
    suggested_day: str
    suggested_minutes: int
    rationale: str


@dataclass(slots=True)
class NoteTaskCandidate:
    title: str
    notes: str | None = None


class AIProvider:
    provider_key = "base"

    def generate_weekly_plan(self, tasks: Sequence[Task]) -> list[WeeklyPlanSuggestion]:
        raise NotImplementedError

    def extract_task_candidates(self, note_content: str) -> list[NoteTaskCandidate]:
        raise NotImplementedError


class HeuristicAIProvider(AIProvider):
    provider_key = "heuristic-local"

    def generate_weekly_plan(self, tasks: Sequence[Task]) -> list[WeeklyPlanSuggestion]:
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

        def score(task: Task) -> float:
            priority = float(task.priority or 0)
            urgency = float(task.urgency or 0)
            spouse = float(task.spouse_priority or 0)
            hard_bonus = 10 if task.deadline_type == "hard" else 0
            return (priority * 1.5) + (urgency * 1.2) + spouse + hard_bonus

        ranked = sorted(tasks, key=score, reverse=True)
        suggestions: list[WeeklyPlanSuggestion] = []
        for i, task in enumerate(ranked[:12]):
            suggestions.append(
                WeeklyPlanSuggestion(
                    task_id=task.id,
                    suggested_day=days[i % len(days)],
                    suggested_minutes=45 if (task.priority or 0) >= 7 else 30,
                    rationale=f"ranked_for_weekly_plan_priority_{int(score(task))}",
                )
            )
        return suggestions

    def extract_task_candidates(self, note_content: str) -> list[NoteTaskCandidate]:
        candidates: list[NoteTaskCandidate] = []
        for raw_line in note_content.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            normalized = line.removeprefix("- ").removeprefix("* ").strip()
            if len(normalized) < 4:
                continue
            candidates.append(NoteTaskCandidate(title=normalized[:200]))
            if len(candidates) >= 8:
                break
        return candidates


class OpenAIProvider(AIProvider):
    provider_key = "openai"

    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when ai_preferred_provider=openai")

    def generate_weekly_plan(self, tasks: Sequence[Task]) -> list[WeeklyPlanSuggestion]:
        tasks_payload = [
            {
                "task_id": task.id,
                "title": task.title,
                "priority": task.priority,
                "urgency": task.urgency,
                "deadline_type": task.deadline_type,
                "deadline_at": task.deadline_at.isoformat() if task.deadline_at else None,
                "spouse_priority": task.spouse_priority,
                "spouse_urgency": task.spouse_urgency,
            }
            for task in tasks
        ]
        raw = self._chat_json(
            (
                "Return strict JSON only as an array. Each item: "
                '{"task_id":"string","suggested_day":"monday..sunday","suggested_minutes":integer,"rationale":"string"}. '
                "Include max 12 items."
            ),
            json.dumps({"tasks": tasks_payload}),
        )
        suggestions: list[WeeklyPlanSuggestion] = []
        for item in raw[:12]:
            suggestions.append(
                WeeklyPlanSuggestion(
                    task_id=str(item["task_id"]),
                    suggested_day=str(item["suggested_day"]).lower(),
                    suggested_minutes=max(10, min(int(item["suggested_minutes"]), 360)),
                    rationale=str(item.get("rationale", "openai_suggested")),
                )
            )
        return suggestions

    def extract_task_candidates(self, note_content: str) -> list[NoteTaskCandidate]:
        raw = self._chat_json(
            ('Return strict JSON only as an array. Each item: {"title":"string","notes":"string|null"}. Include max 8 items.'),
            note_content,
        )
        return [NoteTaskCandidate(title=str(item["title"])[:200], notes=item.get("notes")) for item in raw[:8] if item.get("title")]

    def _chat_json(self, system_prompt: str, user_prompt: str) -> list[dict]:
        response = httpx.post(
            f"{settings.openai_base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.openai_model,
                "temperature": 0.3,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            },
            timeout=settings.openai_timeout_seconds,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        normalized = content.strip()
        if normalized.startswith("```"):
            normalized = normalized.strip("`")
            normalized = normalized.replace("json\n", "", 1)
        parsed = json.loads(normalized)
        if not isinstance(parsed, list):
            raise ValueError("OpenAI provider must return a JSON array")
        return [item for item in parsed if isinstance(item, dict)]


def get_default_provider(preferred_provider: str | None = None) -> AIProvider:
    selected = (preferred_provider or "heuristic-local").strip().lower()
    if selected in {"", "heuristic-local"}:
        return HeuristicAIProvider()
    if selected == "openai":
        return OpenAIProvider()
    return HeuristicAIProvider()
