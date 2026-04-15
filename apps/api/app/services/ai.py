from collections.abc import Sequence
from dataclasses import dataclass

from app.models.phase2 import Task

PROMPT_TEMPLATE_VERSION = "phase4.weekly.v1"


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


def get_default_provider() -> AIProvider:
    return HeuristicAIProvider()
