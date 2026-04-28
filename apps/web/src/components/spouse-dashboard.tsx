"use client";

import { useEffect, useMemo, useState } from "react";
import { EmptyState, ScreenHeader, SectionCard, StatusPill } from "@/components/ui-kit";

type SpouseDashboardItem = {
  id: string;
  task_id: string;
  task_title: string;
  planned_minutes: number;
  outcome_status: "planned" | "done" | "postponed" | "failed" | "partial" | "skipped";
  owner_priority: number | null;
  owner_urgency: number | null;
  spouse_priority: number | null;
  spouse_urgency: number | null;
  spouse_deadline: string | null;
  spouse_deadline_type: "soft" | "hard" | null;
};

type SpouseDashboardDay = {
  daily_schedule_id: string;
  schedule_date: string;
  status: "proposed" | "accepted" | "adjusted";
  visible_items: SpouseDashboardItem[];
  compressed_item_count: number;
};

type SpouseDashboardPayload = {
  weekly_schedule_id: string;
  week_start_date: string;
  accepted_at: string | null;
  days: SpouseDashboardDay[];
};

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api/v1";
const authHeaders = (token: string): Record<string, string> => (token ? { Authorization: `Bearer ${token}` } : {});

export function SpouseDashboard() {
  const [token, setToken] = useState("");
  const [dashboard, setDashboard] = useState<SpouseDashboardPayload | null>(null);
  const [error, setError] = useState("");
  const [savingTaskId, setSavingTaskId] = useState<string | null>(null);
  const [influenceDrafts, setInfluenceDrafts] = useState<Record<string, {
    spouse_priority: string;
    spouse_urgency: string;
    spouse_deadline: string;
    spouse_deadline_type: "soft" | "hard" | "";
  }>>({});

  useEffect(() => {
    const localToken = window.localStorage.getItem("orbis_access_token") ?? "";
    if (localToken) setToken(localToken);
  }, []);

  async function loadDashboard() {
    if (!token) {
      setError("Access token is required.");
      return;
    }

    setError("");
    const response = await fetch(`${apiBase}/schedules/spouse-dashboard`, { headers: authHeaders(token), cache: "no-store" });
    if (!response.ok) {
      setDashboard(null);
      setError(response.status === 404 ? "No accepted schedule shared yet." : `Could not load spouse dashboard (${response.status}).`);
      return;
    }

    setDashboard((await response.json()) as SpouseDashboardPayload);
  }

  useEffect(() => {
    if (!token || dashboard) return;
    void loadDashboard();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const visibleItems = useMemo(() => dashboard?.days.flatMap((day) => day.visible_items) ?? [], [dashboard]);

  useEffect(() => {
    const nextDrafts: Record<string, {
      spouse_priority: string;
      spouse_urgency: string;
      spouse_deadline: string;
      spouse_deadline_type: "soft" | "hard" | "";
    }> = {};
    for (const item of visibleItems) {
      nextDrafts[item.id] = {
        spouse_priority: item.spouse_priority?.toString() ?? "",
        spouse_urgency: item.spouse_urgency?.toString() ?? "",
        spouse_deadline: item.spouse_deadline ? item.spouse_deadline.slice(0, 16) : "",
        spouse_deadline_type: item.spouse_deadline_type ?? "",
      };
    }
    setInfluenceDrafts(nextDrafts);
  }, [visibleItems]);

  async function saveInfluence(item: SpouseDashboardItem) {
    if (!token) return;
    const draft = influenceDrafts[item.id];
    if (!draft) return;

    const spousePriority = draft.spouse_priority.trim() === "" ? null : Number(draft.spouse_priority);
    if (spousePriority !== null && (Number.isNaN(spousePriority) || spousePriority < 0 || spousePriority > 10)) {
      setError("Could not update influence.");
      return;
    }

    const spouseUrgency = draft.spouse_urgency.trim() === "" ? null : Number(draft.spouse_urgency);
    if (spouseUrgency !== null && (Number.isNaN(spouseUrgency) || spouseUrgency < 0 || spouseUrgency > 10)) {
      setError("Could not update influence.");
      return;
    }

    setError("");
    setSavingTaskId(item.id);
    const response = await fetch(`${apiBase}/tasks/${item.task_id}/spouse-influence`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        ...authHeaders(token),
      },
      body: JSON.stringify({
        spouse_priority: spousePriority,
        spouse_urgency: spouseUrgency,
        spouse_deadline: draft.spouse_deadline ? new Date(draft.spouse_deadline).toISOString() : null,
        spouse_deadline_type: draft.spouse_deadline_type || null,
      }),
    });
    setSavingTaskId(null);

    if (!response.ok) {
      setError(`Could not update influence (${response.status}).`);
      return;
    }

    await loadDashboard();
  }

  return (
    <section className="screen-flow">
      <ScreenHeader
        title="Spouse Dashboard"
        subtitle="Shared, accepted schedule items with influence controls"
        actions={(
          <>
            <input className="app-input" placeholder="Access token" value={token} onChange={(event) => setToken(event.target.value)} />
            <button className="app-button app-button--primary" onClick={loadDashboard} type="button">Load Shared Schedule</button>
          </>
        )}
      />

      <SectionCard title="Shared Accepted Week">
        {dashboard ? (
          <>
            <p>Week starts {dashboard.week_start_date}</p>
            <p><StatusPill label="accepted" /> {dashboard.accepted_at ? `Accepted at ${new Date(dashboard.accepted_at).toLocaleString()}` : null}</p>
            <ul className="stack-list">
              {dashboard.days.map((day) => (
                <li key={day.daily_schedule_id} className="task-row">
                  <span>{day.schedule_date} · {day.visible_items.length} visible</span>
                  <span>{day.compressed_item_count} compressed low-importance items</span>
                </li>
              ))}
            </ul>
          </>
        ) : <EmptyState message="Load shared schedule context to see spouse-visible items." />}
      </SectionCard>

      <SectionCard title="Influence Inputs">
        {visibleItems.length ? (
          <ul className="stack-list">
            {visibleItems.map((item) => (
              <li key={item.id} className="task-row task-row--interactive">
                <div>
                  <strong>{item.task_title}</strong>
                  <p>{item.planned_minutes}m · owner p/u {item.owner_priority ?? "-"}/{item.owner_urgency ?? "-"}</p>
                </div>
                <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
                  <input
                    className="app-input app-input--short"
                    type="number"
                    min={0}
                    max={10}
                    value={influenceDrafts[item.id]?.spouse_priority ?? ""}
                    onChange={(event) => setInfluenceDrafts((prev) => ({ ...prev, [item.id]: { ...prev[item.id], spouse_priority: event.target.value } }))}
                  />
                  <input
                    className="app-input app-input--short"
                    type="number"
                    min={0}
                    max={10}
                    value={influenceDrafts[item.id]?.spouse_urgency ?? ""}
                    onChange={(event) => setInfluenceDrafts((prev) => ({ ...prev, [item.id]: { ...prev[item.id], spouse_urgency: event.target.value } }))}
                  />
                  <input
                    className="app-input"
                    type="datetime-local"
                    value={influenceDrafts[item.id]?.spouse_deadline ?? ""}
                    onChange={(event) => setInfluenceDrafts((prev) => ({ ...prev, [item.id]: { ...prev[item.id], spouse_deadline: event.target.value } }))}
                  />
                  <select
                    className="app-input app-input--short"
                    value={influenceDrafts[item.id]?.spouse_deadline_type ?? ""}
                    onChange={(event) => setInfluenceDrafts((prev) => ({ ...prev, [item.id]: { ...prev[item.id], spouse_deadline_type: event.target.value as "soft" | "hard" | "" } }))}
                  >
                    <option value="">-</option>
                    <option value="soft">soft</option>
                    <option value="hard">hard</option>
                  </select>
                  <button className="app-button" type="button" onClick={() => saveInfluence(item)}>✓</button>
                  <StatusPill label={item.outcome_status} />
                </div>
              </li>
            ))}
          </ul>
        ) : <EmptyState message="No spouse-visible actionable items for the accepted week." />}
      </SectionCard>
      {savingTaskId ? <p>Saving influence…</p> : null}
      {error ? <p className="error-text">{error}</p> : null}
    </section>
  );
}
