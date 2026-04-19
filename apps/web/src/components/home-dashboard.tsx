"use client";

import { useEffect, useMemo, useState } from "react";
import { EmptyState, ScreenHeader, SectionCard, StatusPill } from "@/components/ui-kit";

type Area = { id: string; name: string };
type Task = { id: string; title: string; status: string; deadline: string | null };
type DailyPlanRecommendation = { task_id: string; title: string; status: string; score: number; reasons: string[] };
type DailyPlanResponse = {
  generated_at: string;
  primary_recommendation: DailyPlanRecommendation | null;
  fallback_recommendations: DailyPlanRecommendation[];
};

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";
const authHeaders = (token: string): Record<string, string> => (token ? { Authorization: `Bearer ${token}` } : {});

export function HomeDashboard() {
  const [token, setToken] = useState("");
  const [energy, setEnergy] = useState("5");
  const [areas, setAreas] = useState<Area[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [dailyPlan, setDailyPlan] = useState<DailyPlanResponse | null>(null);
  const [error, setError] = useState("");

  const doNow = useMemo(() => dailyPlan?.primary_recommendation ?? dailyPlan?.fallback_recommendations[0] ?? null, [dailyPlan]);

  useEffect(() => {
    const localToken = window.localStorage.getItem("orbis_access_token") ?? "";
    if (localToken) setToken(localToken);
  }, []);

  async function loadDashboard() {
    setError("");
    if (!token) {
      setError("Access token is required.");
      return;
    }

    const [areasRes, tasksRes, planRes] = await Promise.all([
      fetch(`${apiBase}/areas`, { headers: authHeaders(token), cache: "no-store" }),
      fetch(`${apiBase}/tasks`, { headers: authHeaders(token), cache: "no-store" }),
      fetch(`${apiBase}/planning/daily-plan?limit=5&current_energy=${energy}`, { headers: authHeaders(token), cache: "no-store" }),
    ]);

    if (!areasRes.ok || !tasksRes.ok || !planRes.ok) {
      setError("Could not load Day context.");
      return;
    }

    setAreas((await areasRes.json()) as Area[]);
    setTasks((await tasksRes.json()) as Task[]);
    setDailyPlan((await planRes.json()) as DailyPlanResponse);
  }

  return (
    <section className="screen-flow">
      <ScreenHeader
        title="Today’s Orbit"
        subtitle={new Date().toLocaleDateString(undefined, { weekday: "long", month: "long", day: "numeric" })}
        actions={(
          <>
            <input className="app-input" placeholder="Access token" value={token} onChange={(event) => setToken(event.target.value)} />
            <input className="app-input app-input--short" type="number" min="0" max="10" step="0.5" value={energy} onChange={(event) => setEnergy(event.target.value)} />
            <button className="app-button app-button--primary" type="button" onClick={loadDashboard}>Refresh</button>
          </>
        )}
      />

      <SectionCard title="Morning Brief" tone="accent">
        {doNow ? (
          <>
            <p className="lead-copy">Primary focus: {doNow.title}</p>
            <p>Score {doNow.score.toFixed(2)} · {doNow.status}</p>
          </>
        ) : <EmptyState message="No recommendation yet. Refresh to generate a Day plan." />}
      </SectionCard>

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
        ) : <EmptyState message="No tasks for the Day timeline." />}
      </SectionCard>

      <div className="two-col">
        <SectionCard title="Needs Attention">
          {tasks.filter((task) => ["blocked", "failed", "overdue"].includes(task.status)).slice(0, 4).length ? (
            <ul className="stack-list">
              {tasks.filter((task) => ["blocked", "failed", "overdue"].includes(task.status)).slice(0, 4).map((task) => (
                <li key={task.id} className="task-row"><span>{task.title}</span><StatusPill label={task.status} /></li>
              ))}
            </ul>
          ) : <EmptyState message="No blocked or overdue tasks right now." />}
        </SectionCard>

        <SectionCard title="Suggestions">
          {dailyPlan?.fallback_recommendations.length ? (
            <ul className="stack-list">
              {dailyPlan.fallback_recommendations.map((item) => (
                <li key={item.task_id} className="task-row"><span>{item.title}</span><StatusPill label={`score ${item.score.toFixed(1)}`} /></li>
              ))}
            </ul>
          ) : <EmptyState message="No additional suggestions available." />}
        </SectionCard>
      </div>

      {areas.length ? <p className="footnote">Life areas in scope: {areas.map((area) => area.name).join(" · ")}</p> : null}
      {error ? <p className="error-text">{error}</p> : null}
    </section>
  );
}
