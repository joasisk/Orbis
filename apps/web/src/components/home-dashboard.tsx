"use client";

import { useEffect, useMemo, useState } from "react";

type Area = { id: string; name: string; description: string | null };
type Project = { id: string; name: string; status: string };
type Task = { id: string; title: string; status: string; priority: number | null };
type DailyPlanRecommendation = { task_id: string; title: string; status: string; score: number; reasons: string[] };
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
  outcome_status: string;
  distraction_count: number;
  distraction_notes: string | null;
};
type DailySchedule = { id: string; status: string; schedule_date: string; items: DailyScheduleItem[] };
type WeeklySchedule = { id: string; week_start_date: string; status: string; days: DailySchedule[] };

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

const authHeaders = (token: string): Record<string, string> => {
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
};

export function HomeDashboard() {
  const [token, setToken] = useState("");
  const [energy, setEnergy] = useState("5");
  const [areas, setAreas] = useState<Area[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [dailyPlan, setDailyPlan] = useState<DailyPlanResponse | null>(null);
  const [weeklySchedule, setWeeklySchedule] = useState<WeeklySchedule | null>(null);
  const [dailySchedule, setDailySchedule] = useState<DailySchedule | null>(null);
  const [preTaskEnergy, setPreTaskEnergy] = useState("5");
  const [postTaskEnergy, setPostTaskEnergy] = useState("5");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const doNow = useMemo(() => dailyPlan?.primary_recommendation ?? dailyPlan?.fallback_recommendations[0] ?? null, [dailyPlan]);

  useEffect(() => {
    const localToken = window.localStorage.getItem("orbis_access_token") ?? "";
    if (localToken) {
      setToken(localToken);
    }
  }, []);

  const getMondayIso = () => {
    const now = new Date();
    const day = now.getUTCDay() || 7;
    now.setUTCDate(now.getUTCDate() - day + 1);
    return now.toISOString().slice(0, 10);
  };

  const todayIso = () => new Date().toISOString().slice(0, 10);

  async function loadDashboard() {
    setError("");
    setMessage("");
    if (!token) {
      setError("Access token is required.");
      return;
    }

    const [areasRes, projectsRes, tasksRes, planRes, weekRes, dayRes] = await Promise.all([
      fetch(`${apiBase}/areas`, { headers: authHeaders(token), cache: "no-store" }),
      fetch(`${apiBase}/projects`, { headers: authHeaders(token), cache: "no-store" }),
      fetch(`${apiBase}/tasks`, { headers: authHeaders(token), cache: "no-store" }),
      fetch(`${apiBase}/planning/daily-plan?limit=5&current_energy=${energy}`, { headers: authHeaders(token), cache: "no-store" }),
      fetch(`${apiBase}/schedules/weeks/${getMondayIso()}`, { headers: authHeaders(token), cache: "no-store" }),
      fetch(`${apiBase}/schedules/days/${todayIso()}`, { headers: authHeaders(token), cache: "no-store" }),
    ]);

    if (!areasRes.ok || !projectsRes.ok || !tasksRes.ok || !planRes.ok || !weekRes.ok || !dayRes.ok) {
      setError("One or more dashboard requests failed. Check token and seed data.");
      return;
    }

    setAreas((await areasRes.json()) as Area[]);
    setProjects((await projectsRes.json()) as Project[]);
    setTasks((await tasksRes.json()) as Task[]);
    setDailyPlan((await planRes.json()) as DailyPlanResponse);
    setWeeklySchedule((await weekRes.json()) as WeeklySchedule);
    setDailySchedule((await dayRes.json()) as DailySchedule);
    setMessage("Dashboard refreshed.");
  }

  async function patchItem(itemId: string, payload: Record<string, unknown>) {
    const response = await fetch(`${apiBase}/schedules/day-items/${itemId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", ...authHeaders(token) },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      setError(`Failed to update day item (${response.status}).`);
      return;
    }
    const updated = (await response.json()) as DailySchedule;
    setDailySchedule(updated);
    setMessage("Execution telemetry saved.");
  }

  async function startFocus(itemId: string) {
    const response = await fetch(`${apiBase}/schedules/day-items/${itemId}/start-focus`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders(token) },
      body: JSON.stringify({ pre_task_energy: Number(preTaskEnergy) }),
    });
    if (!response.ok) {
      setError(`Start focus failed (${response.status}).`);
      return;
    }
    setDailySchedule((await response.json()) as DailySchedule);
    setMessage("Focus started from schedule item.");
  }

  async function endFocus(itemId: string) {
    const response = await fetch(`${apiBase}/schedules/day-items/${itemId}/end-focus`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders(token) },
      body: JSON.stringify({ post_task_energy: Number(postTaskEnergy) }),
    });
    if (!response.ok) {
      setError(`End focus failed (${response.status}).`);
      return;
    }
    setDailySchedule((await response.json()) as DailySchedule);
    setMessage("Focus ended from schedule item.");
  }

  return (
    <section className="shell-page">
      <p className="stamp-label">Phase 4.5</p>
      <h1 className="display-title">Today dashboard</h1>
      <div className="field-grid" style={{ marginTop: "1rem" }}>
        <input className="input-field" placeholder="Access token" value={token} onChange={(e) => setToken(e.target.value)} />
        <input className="input-field" type="number" min="0" max="10" step="0.5" value={energy} onChange={(e) => setEnergy(e.target.value)} />
        <button className="btn btn-primary" type="button" onClick={loadDashboard}>
          Refresh dashboard
        </button>
      </div>

      <div className="organic-grid" style={{ marginTop: "1rem" }}>
        <article className="panel panel--focus">
          <h2 className="headline">Do now</h2>
          <p>{doNow ? `${doNow.title} (${doNow.status})` : "Load plan data"}</p>
          <p className="body-copy">{doNow ? `Score ${doNow.score.toFixed(2)}` : ""}</p>
        </article>

        <article className="panel">
          <h2 className="headline">Schedule</h2>
          <p className="body-copy">Week: {weeklySchedule?.week_start_date ?? "-"}</p>
          <p className="body-copy">Weekly status: {weeklySchedule?.status ?? "-"}</p>
          <p className="body-copy">Today status: {dailySchedule?.status ?? "-"}</p>
        </article>

        <article className="panel">
          <h2 className="headline">Core data</h2>
          <ul className="list">
            <li className="list-item">Areas: {areas.length}</li>
            <li className="list-item">Projects: {projects.length}</li>
            <li className="list-item">Tasks: {tasks.length}</li>
          </ul>
        </article>
      </div>

      <article className="panel" style={{ marginTop: "1rem" }}>
        <h2 className="headline">Daily schedule items (telemetry + focus)</h2>
        <div className="field-grid" style={{ marginBottom: "0.75rem" }}>
          <input
            className="input-field"
            type="number"
            min="0"
            max="10"
            step="0.5"
            value={preTaskEnergy}
            onChange={(e) => setPreTaskEnergy(e.target.value)}
            placeholder="Pre-task energy"
          />
          <input
            className="input-field"
            type="number"
            min="0"
            max="10"
            step="0.5"
            value={postTaskEnergy}
            onChange={(e) => setPostTaskEnergy(e.target.value)}
            placeholder="Post-task energy"
          />
        </div>
        <ul className="list">
          {dailySchedule?.items.map((item) => (
            <li className="list-item" key={item.id}>
              <strong>{item.task_id.slice(0, 8)}</strong>
              <p className="body-copy">
                planned {item.planned_minutes}m · actual {item.actual_minutes ?? "-"} · outcome {item.outcome_status}
              </p>
              <div className="button-row">
                <button className="btn btn-secondary" type="button" onClick={() => patchItem(item.id, { outcome_status: "done" })}>
                  Mark done
                </button>
                <button className="btn btn-secondary" type="button" onClick={() => patchItem(item.id, { actual_minutes: item.planned_minutes, distraction_count: 0 })}>
                  Save telemetry
                </button>
                <button className="btn btn-primary" type="button" onClick={() => startFocus(item.id)}>
                  Start focus
                </button>
                <button className="btn btn-secondary" type="button" onClick={() => endFocus(item.id)}>
                  End focus
                </button>
              </div>
            </li>
          ))}
        </ul>
      </article>

      {error ? <p className="message-error">{error}</p> : null}
      {message ? <p className="message-success">{message}</p> : null}
    </section>
  );
}
