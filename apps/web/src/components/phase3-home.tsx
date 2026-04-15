"use client";

import { useMemo, useState } from "react";

type OverloadRiskLevel = "low" | "medium" | "high";
type BlockerReason =
  | "unclear_requirement"
  | "missing_dependency"
  | "external_wait"
  | "low_energy_focus"
  | "time_fragmentation"
  | "mental_resistance"
  | "context_not_available";

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
  recommendations: DailyPlanRecommendation[];
  overload_risk_level: OverloadRiskLevel;
  drivers: string[];
  recommended_reset_actions: string[];
};

type FocusSessionResponse = {
  id: string;
  task_id: string;
  status: "active" | "completed" | "unable";
  started_at: string;
  ended_at: string | null;
  pre_task_energy: number;
  post_task_energy: number | null;
  sidetrack_count: number;
  sidetrack_note: string | null;
  unable_reason: string | null;
};

const defaultApiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

const blockerReasons: Array<{ value: BlockerReason; label: string }> = [
  { value: "unclear_requirement", label: "Unclear requirement" },
  { value: "missing_dependency", label: "Missing dependency" },
  { value: "external_wait", label: "External wait" },
  { value: "low_energy_focus", label: "Low energy/focus" },
  { value: "time_fragmentation", label: "Time fragmentation" },
  { value: "mental_resistance", label: "Mental resistance" },
  { value: "context_not_available", label: "Context not available" },
];

function getAuthHeaders(token: string): Record<string, string> {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export function Phase3Home() {
  const [apiBase, setApiBase] = useState(defaultApiBase);
  const [token, setToken] = useState("");
  const [currentEnergy, setCurrentEnergy] = useState("5");
  const [plan, setPlan] = useState<DailyPlanResponse | null>(null);
  const [activeSession, setActiveSession] = useState<FocusSessionResponse | null>(null);
  const [preEnergy, setPreEnergy] = useState("5");
  const [postEnergy, setPostEnergy] = useState("5");
  const [unableReason, setUnableReason] = useState("");
  const [blockerReason, setBlockerReason] = useState<BlockerReason>("mental_resistance");
  const [note, setNote] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const doNowTask = useMemo(() => plan?.primary_recommendation ?? plan?.recommendations[0] ?? null, [plan]);

  async function loadPlan() {
    setError("");
    setSuccess("");

    const params = new URLSearchParams({ limit: "5" });
    if (currentEnergy !== "") {
      params.set("current_energy", currentEnergy);
    }

    const response = await fetch(`${apiBase}/planning/daily-plan?${params.toString()}`, {
      cache: "no-store",
      headers: {
        ...getAuthHeaders(token),
      },
    });

    if (!response.ok) {
      setError(`Could not load daily plan (${response.status})`);
      return;
    }

    setPlan((await response.json()) as DailyPlanResponse);
    setSuccess("Daily plan loaded.");
  }

  async function startFocus() {
    if (!doNowTask) {
      setError("No recommendation available to start.");
      return;
    }

    setError("");
    setSuccess("");

    const response = await fetch(`${apiBase}/focus/start`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeaders(token),
      },
      body: JSON.stringify({
        task_id: doNowTask.task_id,
        pre_task_energy: Number(preEnergy),
      }),
    });

    if (!response.ok) {
      setError(`Could not start focus (${response.status})`);
      return;
    }

    setActiveSession((await response.json()) as FocusSessionResponse);
    setSuccess("Focus session started.");
  }

  async function stopFocus() {
    if (!activeSession) {
      setError("No active focus session.");
      return;
    }

    setError("");
    setSuccess("");

    const response = await fetch(`${apiBase}/focus/stop`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeaders(token),
      },
      body: JSON.stringify({
        session_id: activeSession.id,
        post_task_energy: Number(postEnergy),
      }),
    });

    if (!response.ok) {
      setError(`Could not stop focus (${response.status})`);
      return;
    }

    const payload = (await response.json()) as FocusSessionResponse;
    setActiveSession(payload);
    setSuccess("Focus session completed.");
    await loadPlan();
  }

  async function sidetrack() {
    if (!activeSession) {
      setError("No active focus session.");
      return;
    }

    setError("");
    setSuccess("");

    const response = await fetch(`${apiBase}/focus/sidetrack`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeaders(token),
      },
      body: JSON.stringify({
        session_id: activeSession.id,
        blocker_reason: blockerReason,
        note: note || null,
      }),
    });

    if (!response.ok) {
      setError(`Could not save sidetrack (${response.status})`);
      return;
    }

    setSuccess("Sidetrack captured.");
    setNote("");
  }

  async function unableToFinish() {
    if (!activeSession) {
      setError("No active focus session.");
      return;
    }

    if (unableReason.trim().length < 3) {
      setError("Unable reason must be at least 3 characters.");
      return;
    }

    setError("");
    setSuccess("");

    const response = await fetch(`${apiBase}/focus/unable`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeaders(token),
      },
      body: JSON.stringify({
        session_id: activeSession.id,
        unable_reason: unableReason,
        blocker_reason: blockerReason,
        post_task_energy: Number(postEnergy),
        note: note || null,
      }),
    });

    if (!response.ok) {
      setError(`Could not save unable-to-finish (${response.status})`);
      return;
    }

    setSuccess("Unable-to-finish captured.");
    setUnableReason("");
    setNote("");
    setActiveSession(null);
    await loadPlan();
  }

  return (
    <>
      <section className="orbit-timeline">
        <h2 className="orbit-section-label">Do now</h2>

        <div className="timeline-list">
          <article className="timeline-item timeline-item--active">
            <div className="timeline-item__dot" aria-hidden />
            <div className="timeline-item__card">
              <div className="timeline-item__meta">
                <span>Primary recommendation</span>
                <span>{plan ? new Date(plan.generated_at).toLocaleTimeString() : "Not loaded"}</span>
              </div>
              <h3>{doNowTask?.title ?? "Load your daily plan"}</h3>
              <p>
                {doNowTask
                  ? `Score ${doNowTask.score.toFixed(2)} · Status ${doNowTask.status}`
                  : "Request your plan to see a ranked recommendation and fallback options."}
              </p>
              {doNowTask?.reasons?.length ? (
                <ul className="orbit-checklist" style={{ marginTop: "0.75rem" }}>
                  {doNowTask.reasons.slice(0, 3).map((reason) => (
                    <li key={reason}>{reason}</li>
                  ))}
                </ul>
              ) : null}
            </div>
          </article>

          {plan?.fallback_recommendations.slice(0, 2).map((item) => (
            <article className="timeline-item" key={item.task_id}>
              <div className="timeline-item__dot" aria-hidden />
              <div className="timeline-item__card timeline-item__card--upcoming">
                <div className="timeline-item__meta">
                  <span>Fallback</span>
                  <span>Score {item.score.toFixed(2)}</span>
                </div>
                <h3>{item.title}</h3>
                <p>Status: {item.status}</p>
              </div>
            </article>
          ))}
        </div>
      </section>

      <aside className="orbit-panels">
        <section className="orbit-panel">
          <h2 className="orbit-section-label">Planner controls</h2>
          <div className="field-grid">
            <input className="input-field" value={apiBase} onChange={(e) => setApiBase(e.target.value)} placeholder="API base URL" />
            <input className="input-field" value={token} onChange={(e) => setToken(e.target.value)} placeholder="Bearer token" />
            <input
              className="input-field"
              type="number"
              min="0"
              max="10"
              step="0.5"
              value={currentEnergy}
              onChange={(e) => setCurrentEnergy(e.target.value)}
              placeholder="Current energy (0-10)"
            />
            <button className="btn btn-primary" type="button" onClick={loadPlan}>
              Refresh do-now plan
            </button>
          </div>
        </section>

        <section className="orbit-panel">
          <h2 className="orbit-section-label">Focus actions</h2>
          <p>
            Session: {activeSession ? `${activeSession.status} (${activeSession.id.slice(0, 8)})` : "No active session"}
          </p>
          <div className="field-grid" style={{ marginTop: "0.8rem" }}>
            <input
              className="input-field"
              type="number"
              min="0"
              max="10"
              step="0.5"
              value={preEnergy}
              onChange={(e) => setPreEnergy(e.target.value)}
              placeholder="Pre-task energy"
            />
            <button className="btn btn-primary" type="button" onClick={startFocus}>
              Start focus
            </button>

            <input
              className="input-field"
              type="number"
              min="0"
              max="10"
              step="0.5"
              value={postEnergy}
              onChange={(e) => setPostEnergy(e.target.value)}
              placeholder="Post-task energy"
            />
            <button className="btn btn-secondary" type="button" onClick={stopFocus}>
              Stop focus
            </button>
          </div>
        </section>

        <section className="orbit-panel orbit-panel--warning">
          <h2 className="orbit-section-label">Blocker capture</h2>
          <div className="field-grid">
            <select className="input-field" value={blockerReason} onChange={(e) => setBlockerReason(e.target.value as BlockerReason)}>
              {blockerReasons.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <input
              className="input-field"
              value={unableReason}
              onChange={(e) => setUnableReason(e.target.value)}
              placeholder="Unable reason (required for unable flow)"
            />
            <textarea className="text-area" value={note} onChange={(e) => setNote(e.target.value)} placeholder="Optional blocker note" />
            <div className="button-row">
              <button className="btn btn-secondary" type="button" onClick={sidetrack}>
                Record sidetrack
              </button>
              <button className="btn btn-primary" type="button" onClick={unableToFinish}>
                Unable to finish
              </button>
            </div>
          </div>
        </section>

        {plan ? (
          <section className="orbit-panel">
            <h2 className="orbit-section-label">Overload signal</h2>
            <p>
              Risk level: <strong>{plan.overload_risk_level}</strong>
            </p>
            {plan.drivers.length > 0 ? (
              <ul className="orbit-checklist">
                {plan.drivers.map((driver) => (
                  <li key={driver}>{driver}</li>
                ))}
              </ul>
            ) : null}
          </section>
        ) : null}

        {error ? <p className="message-error">{error}</p> : null}
        {success ? <p className="message-success">{success}</p> : null}
      </aside>
    </>
  );
}
