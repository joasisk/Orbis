"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { EmptyState, ScreenHeader, SectionCard, StatusPill } from "@/components/ui-kit";

type Area = { id: string; name: string };
type Task = { id: string; title: string; status: string; deadline: string | null };

type DailyPlanRecommendation = {
  task_id: string;
  title: string;
  status: string;
  score: number;
  reasons: string[];
};

type DailyPlanResponse = {
  generated_at: string;
  primary_recommendation: DailyPlanRecommendation | null;
  fallback_recommendations: DailyPlanRecommendation[];
};

type DailyScheduleItem = {
  id: string;
  task_id: string;
  planned_minutes: number;
  actual_minutes: number | null;
  outcome_status: "planned" | "done" | "postponed" | "failed" | "partial" | "skipped";
  distraction_count: number;
  distraction_notes: string | null;
  failure_reason: string | null;
};

type DailySchedule = {
  id: string;
  schedule_date: string;
  status: "proposed" | "accepted" | "adjusted";
  items: DailyScheduleItem[];
};

type WeeklySchedule = {
  id: string;
  week_start_date: string;
  status: "proposed" | "accepted" | "rejected";
  days: DailySchedule[];
};

type FocusSessionResponse = {
  id: string;
  task_id: string;
  status: "active" | "completed" | "unable";
  started_at: string;
  ended_at: string | null;
};

type BlockerReason =
  | "unclear_requirement"
  | "missing_dependency"
  | "external_wait"
  | "low_energy_focus"
  | "time_fragmentation"
  | "mental_resistance"
  | "context_not_available";

const blockerReasons: Array<{ value: BlockerReason; label: string }> = [
  { value: "mental_resistance", label: "Mental resistance" },
  { value: "unclear_requirement", label: "Unclear requirement" },
  { value: "missing_dependency", label: "Missing dependency" },
  { value: "external_wait", label: "External wait" },
  { value: "low_energy_focus", label: "Low energy/focus" },
  { value: "time_fragmentation", label: "Time fragmentation" },
  { value: "context_not_available", label: "Context unavailable" },
];

const outcomeOptions: Array<DailyScheduleItem["outcome_status"]> = ["planned", "done", "partial", "failed", "postponed", "skipped"];

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";
const authHeaders = (token: string): Record<string, string> => (token ? { Authorization: `Bearer ${token}` } : {});

function mondayIso(baseDate: Date) {
  const normalized = new Date(baseDate);
  const weekday = normalized.getUTCDay() || 7;
  normalized.setUTCDate(normalized.getUTCDate() - weekday + 1);
  return normalized.toISOString().slice(0, 10);
}

function todayIso(baseDate: Date) {
  return baseDate.toISOString().slice(0, 10);
}

export function HomeDashboard() {
  const [token, setToken] = useState("");
  const [energy, setEnergy] = useState("5");
  const [postEnergy, setPostEnergy] = useState("5");
  const [areas, setAreas] = useState<Area[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [dailyPlan, setDailyPlan] = useState<DailyPlanResponse | null>(null);
  const [weeklySchedule, setWeeklySchedule] = useState<WeeklySchedule | null>(null);
  const [dailySchedule, setDailySchedule] = useState<DailySchedule | null>(null);
  const [activeSession, setActiveSession] = useState<FocusSessionResponse | null>(null);
  const [blockerReason, setBlockerReason] = useState<BlockerReason>("mental_resistance");
  const [unableReason, setUnableReason] = useState("");
  const [note, setNote] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const doNow = useMemo(() => dailyPlan?.primary_recommendation ?? dailyPlan?.fallback_recommendations[0] ?? null, [dailyPlan]);
  const weekStart = useMemo(() => mondayIso(new Date()), []);
  const today = useMemo(() => todayIso(new Date()), []);

  useEffect(() => {
    const localToken = window.localStorage.getItem("orbis_access_token") ?? "";
    if (localToken) setToken(localToken);
  }, []);

  async function loadDashboard() {
    if (isLoading) return;
    setError("");
    setSuccess("");
    if (!token) {
      setError("Access token is required.");
      return;
    }

    setIsLoading(true);
    const [areasRes, tasksRes, planRes, weekRes, dayRes] = await Promise.all([
      fetch(`${apiBase}/areas`, { headers: authHeaders(token), cache: "no-store" }),
      fetch(`${apiBase}/tasks`, { headers: authHeaders(token), cache: "no-store" }),
      fetch(`${apiBase}/planning/daily-plan?limit=5&current_energy=${energy}`, { headers: authHeaders(token), cache: "no-store" }),
      fetch(`${apiBase}/schedules/weeks/${weekStart}`, { headers: authHeaders(token), cache: "no-store" }),
      fetch(`${apiBase}/schedules/days/${today}`, { headers: authHeaders(token), cache: "no-store" }),
    ]);

    if (!areasRes.ok || !tasksRes.ok || !planRes.ok || !weekRes.ok || !dayRes.ok) {
      setIsLoading(false);
      setError("Could not load dashboard context from API.");
      return;
    }

    setAreas((await areasRes.json()) as Area[]);
    setTasks((await tasksRes.json()) as Task[]);
    setDailyPlan((await planRes.json()) as DailyPlanResponse);
    setWeeklySchedule((await weekRes.json()) as WeeklySchedule);
    setDailySchedule((await dayRes.json()) as DailySchedule);
    setIsLoading(false);
  }

  async function callFocusEndpoint(path: string, payload: Record<string, unknown>) {
    if (!token) {
      setError("Access token is required.");
      return null;
    }

    const response = await fetch(`${apiBase}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authHeaders(token),
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      setError(`Focus action failed (${response.status}).`);
      return null;
    }

    return response;
  }

  async function startFocus() {
    if (!doNow) {
      setError("Load your do-now plan first.");
      return;
    }

    const response = await callFocusEndpoint("/focus/start", {
      task_id: doNow.task_id,
      pre_task_energy: Number(energy),
    });
    if (!response) return;

    setActiveSession((await response.json()) as FocusSessionResponse);
    setSuccess("Focus session started.");
  }

  async function stopFocus() {
    if (!activeSession) {
      setError("No active focus session.");
      return;
    }

    const response = await callFocusEndpoint("/focus/stop", {
      session_id: activeSession.id,
      post_task_energy: Number(postEnergy),
    });
    if (!response) return;

    setActiveSession(null);
    setSuccess("Focus session stopped.");
    await loadDashboard();
  }

  async function sidetrackFocus() {
    if (!activeSession) {
      setError("No active focus session.");
      return;
    }

    const response = await callFocusEndpoint("/focus/sidetrack", {
      session_id: activeSession.id,
      blocker_reason: blockerReason,
      note: note || null,
    });
    if (!response) return;

    setNote("");
    setSuccess("Sidetrack captured.");
  }

  async function unableFocus() {
    if (!activeSession) {
      setError("No active focus session.");
      return;
    }
    if (unableReason.trim().length < 3) {
      setError("Unable reason must be at least 3 characters.");
      return;
    }

    const response = await callFocusEndpoint("/focus/unable", {
      session_id: activeSession.id,
      unable_reason: unableReason,
      blocker_reason: blockerReason,
      post_task_energy: Number(postEnergy),
      note: note || null,
    });
    if (!response) return;

    setActiveSession(null);
    setUnableReason("");
    setNote("");
    setSuccess("Unable-to-finish recorded.");
    await loadDashboard();
  }

  async function patchDayItem(itemId: string, payload: { outcome_status: DailyScheduleItem["outcome_status"]; actual_minutes: number; distraction_count: number }) {
    if (!token) {
      setError("Access token is required.");
      return;
    }

    const response = await fetch(`${apiBase}/schedules/day-items/${itemId}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        ...authHeaders(token),
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      setError(`Could not update schedule telemetry (${response.status}).`);
      return;
    }

    setDailySchedule((await response.json()) as DailySchedule);
    setSuccess("Daily telemetry updated.");
  }

  useEffect(() => {
    if (!token || (areas.length && tasks.length && dailyPlan && weeklySchedule && dailySchedule) || isLoading) return;
    void loadDashboard();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  return (
    <section className="screen-flow">
      <ScreenHeader
        title="Today’s Orbit"
        subtitle={new Date().toLocaleDateString(undefined, { weekday: "long", month: "long", day: "numeric" })}
        actions={(
          <>
            <input className="app-input" placeholder="Access token" value={token} onChange={(event) => setToken(event.target.value)} />
            <input className="app-input app-input--short" type="number" min="0" max="10" step="0.5" value={energy} onChange={(event) => setEnergy(event.target.value)} />
            <button className="app-button app-button--primary" type="button" onClick={loadDashboard}>{isLoading ? "Loading..." : "Refresh"}</button>
          </>
        )}
      />

      <SectionCard title="Do now + Focus actions" tone="accent">
        {doNow ? (
          <>
            <p className="lead-copy">Primary burn: {doNow.title}</p>
            <p>Score {doNow.score.toFixed(2)} · {doNow.status}</p>
            <p>Session: {activeSession ? `${activeSession.status} (${activeSession.id.slice(0, 8)})` : "No active focus session"}</p>
            <div className="inline-actions" style={{ marginTop: "0.75rem" }}>
              <button className="app-button app-button--primary" type="button" onClick={startFocus}>Start Focus</button>
              <button className="app-button" type="button" onClick={stopFocus}>Stop Focus</button>
            </div>
            <div className="two-col" style={{ marginTop: "0.75rem" }}>
              <input className="app-input app-input--short" type="number" min="0" max="10" step="0.5" value={postEnergy} onChange={(event) => setPostEnergy(event.target.value)} placeholder="Post energy" />
              <select className="app-input" value={blockerReason} onChange={(event) => setBlockerReason(event.target.value as BlockerReason)}>
                {blockerReasons.map((reason) => <option key={reason.value} value={reason.value}>{reason.label}</option>)}
              </select>
              <input className="app-input" value={note} onChange={(event) => setNote(event.target.value)} placeholder="Sidetrack note (optional)" />
              <button className="app-button" type="button" onClick={sidetrackFocus}>Sidetrack</button>
              <input className="app-input" value={unableReason} onChange={(event) => setUnableReason(event.target.value)} placeholder="Unable reason" />
              <button className="app-button" type="button" onClick={unableFocus}>Unable to finish</button>
            </div>
          </>
        ) : <EmptyState message={isLoading ? "Loading do-now plan..." : "No recommendation yet. Refresh to generate a plan."} />}
      </SectionCard>

      <div className="two-col">
        <SectionCard title="Weekly + daily schedule context">
          {weeklySchedule ? (
            <>
              <p>Trajectory status: <StatusPill label={weeklySchedule.status} /></p>
              <p>Week starts {weeklySchedule.week_start_date} · {weeklySchedule.days.length} days planned</p>
              <p>Today: <StatusPill label={dailySchedule?.status ?? "missing"} /> · {dailySchedule?.items.length ?? 0} items</p>
              <p className="footnote">Proposed vs accepted state is shown directly from schedule status.</p>
            </>
          ) : <EmptyState message="Schedule context not loaded." />}
          <div className="inline-actions" style={{ marginTop: "0.75rem" }}>
            <Link className="app-button" href="/schedule">Open schedule workspace</Link>
            <Link className="app-button" href="/tasks">Open task workspace</Link>
          </div>
        </SectionCard>

        <SectionCard title="Execution telemetry (today)">
          {dailySchedule?.items.length ? (
            <ul className="stack-list">
              {dailySchedule.items.slice(0, 3).map((item) => (
                <li key={item.id} className="task-row" style={{ display: "block" }}>
                  <p><strong>Task {item.task_id.slice(0, 8)}</strong> · planned {item.planned_minutes}m</p>
                  <div className="two-col" style={{ marginTop: "0.5rem" }}>
                    <select
                      className="app-input"
                      defaultValue={item.outcome_status}
                      onChange={(event) => {
                        void patchDayItem(item.id, {
                          outcome_status: event.target.value as DailyScheduleItem["outcome_status"],
                          actual_minutes: item.actual_minutes ?? item.planned_minutes,
                          distraction_count: item.distraction_count,
                        });
                      }}
                    >
                      {outcomeOptions.map((outcome) => <option key={outcome} value={outcome}>{outcome}</option>)}
                    </select>
                    <button className="app-button" type="button" onClick={() => void patchDayItem(item.id, {
                      outcome_status: item.outcome_status,
                      actual_minutes: item.actual_minutes ?? item.planned_minutes,
                      distraction_count: item.distraction_count + 1,
                    })}>+1 distraction</button>
                    <button className="app-button" type="button" onClick={() => void patchDayItem(item.id, {
                      outcome_status: "done",
                      actual_minutes: item.actual_minutes ?? item.planned_minutes,
                      distraction_count: item.distraction_count,
                    })}>Mark done</button>
                  </div>
                  <small>Actual minutes: {item.actual_minutes ?? "not set"} · Distractions: {item.distraction_count}</small>
                </li>
              ))}
            </ul>
          ) : <EmptyState message="No daily schedule items for telemetry yet." />}
        </SectionCard>
      </div>

      <SectionCard title="Timeline">
        {tasks.length ? (
          <ul className="stack-list">
            {tasks.slice(0, 8).map((task) => (
              <li key={task.id} className="task-row">
                <div>
                  <p>{task.title}</p>
                  <small>{task.deadline ? `Deadline ${task.deadline}` : "No deadline"}</small>
                </div>
                <StatusPill label={task.status} />
              </li>
            ))}
          </ul>
        ) : <EmptyState message="No tasks in the timeline." />}
      </SectionCard>

      {areas.length ? <p className="footnote">Orbits in scope: {areas.map((area) => area.name).join(" · ")}</p> : null}
      {success ? <p>{success}</p> : null}
      {error ? <p className="error-text">{error}</p> : null}
    </section>
  );
}
