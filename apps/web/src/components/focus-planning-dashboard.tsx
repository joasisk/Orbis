"use client";

import { useEffect, useMemo, useState } from "react";

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
};

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

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

export function FocusPlanningDashboard() {
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
  const [isLoadingPlan, setIsLoadingPlan] = useState(false);

  const doNowTask = useMemo(() => plan?.primary_recommendation ?? plan?.recommendations[0] ?? null, [plan]);

  useEffect(() => {
    const localToken = window.localStorage.getItem("orbis_access_token") ?? "";
    if (localToken) {
      setToken(localToken);
    }
  }, []);

  async function loadPlan() {
    setError("");
    setSuccess("");

    if (!token) {
      setError("Add an access token to load your Burn plan.");
      return;
    }

    setIsLoadingPlan(true);
    const params = new URLSearchParams({ limit: "5", current_energy: currentEnergy });

    const response = await fetch(`${apiBase}/planning/daily-plan?${params.toString()}`, {
      cache: "no-store",
      headers: getAuthHeaders(token),
    });

    setIsLoadingPlan(false);
    if (!response.ok) {
      setError(`Could not load Burn plan (${response.status}).`);
      return;
    }

    setPlan((await response.json()) as DailyPlanResponse);
    setSuccess("Burn plan refreshed.");
  }

  async function callFocusEndpoint(path: string, payload: Record<string, unknown>) {
    if (!token) {
      setError("Add an access token to run Burn actions.");
      return null;
    }

    const response = await fetch(`${apiBase}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeaders(token),
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      setError(`Action failed on ${path} (${response.status}).`);
      return null;
    }

    return response;
  }

  async function startFocus() {
    if (!doNowTask) {
      setError("Load your plan first to pick a recommended task.");
      return;
    }

    setError("");
    const response = await callFocusEndpoint("/focus/start", {
      task_id: doNowTask.task_id,
      pre_task_energy: Number(preEnergy),
    });
    if (!response) {
      return;
    }

    setActiveSession((await response.json()) as FocusSessionResponse);
    setSuccess("Burn started.");
  }

  async function stopFocus() {
    if (!activeSession) {
      setError("No active Burn session.");
      return;
    }

    setError("");
    const response = await callFocusEndpoint("/focus/stop", {
      session_id: activeSession.id,
      post_task_energy: Number(postEnergy),
    });
    if (!response) {
      return;
    }

    const payload = (await response.json()) as FocusSessionResponse;
    setActiveSession(payload.status === "active" ? payload : null);
    setSuccess("Burn stopped.");
    await loadPlan();
  }

  async function sidetrack() {
    if (!activeSession) {
      setError("No active Burn session.");
      return;
    }

    setError("");
    const response = await callFocusEndpoint("/focus/sidetrack", {
      session_id: activeSession.id,
      blocker_reason: blockerReason,
      note: note || null,
    });
    if (!response) {
      return;
    }

    setSuccess("Sidetrack captured.");
    setNote("");
  }

  async function unableToFinish() {
    if (!activeSession) {
      setError("No active Burn session.");
      return;
    }
    if (unableReason.trim().length < 3) {
      setError("Unable reason must be at least 3 characters.");
      return;
    }

    setError("");
    const response = await callFocusEndpoint("/focus/unable", {
      session_id: activeSession.id,
      unable_reason: unableReason,
      blocker_reason: blockerReason,
      post_task_energy: Number(postEnergy),
      note: note || null,
    });
    if (!response) {
      return;
    }

    setSuccess("Unable-to-finish captured.");
    setActiveSession(null);
    setUnableReason("");
    setNote("");
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
              <h3>{doNowTask?.title ?? "Load your Burn plan"}</h3>
              <p>
                {doNowTask
                  ? `Score ${doNowTask.score.toFixed(2)} · Status ${doNowTask.status}`
                  : "Request your Burn plan to see your current best next task and fallback options."}
              </p>
              {doNowTask?.reasons.length ? (
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
          <h2 className="orbit-section-label">Burn planning</h2>
          <div className="field-grid">
            <input
              className="input-field"
              value={token}
              onChange={(event) => setToken(event.target.value)}
              placeholder="Access token"
            />
            <input
              className="input-field"
              type="number"
              min="0"
              max="10"
              step="0.5"
              value={currentEnergy}
              onChange={(event) => setCurrentEnergy(event.target.value)}
              placeholder="Current energy (0-10)"
            />
            <button className="btn btn-primary" type="button" onClick={loadPlan} disabled={isLoadingPlan}>
              {isLoadingPlan ? "Loading..." : "Refresh do-now plan"}
            </button>
          </div>
        </section>

        <section className="orbit-panel">
          <h2 className="orbit-section-label">Burn actions</h2>
          <p>Session: {activeSession ? `${activeSession.status} (${activeSession.id.slice(0, 8)})` : "No active session"}</p>
          <div className="field-grid" style={{ marginTop: "0.8rem" }}>
            <input
              className="input-field"
              type="number"
              min="0"
              max="10"
              step="0.5"
              value={preEnergy}
              onChange={(event) => setPreEnergy(event.target.value)}
              placeholder="Pre-task energy"
            />
            <button className="btn btn-primary" type="button" onClick={startFocus}>
              Start Burn
            </button>

            <input
              className="input-field"
              type="number"
              min="0"
              max="10"
              step="0.5"
              value={postEnergy}
              onChange={(event) => setPostEnergy(event.target.value)}
              placeholder="Post-task energy"
            />
            <button className="btn btn-secondary" type="button" onClick={stopFocus}>
              Stop Burn
            </button>
          </div>
        </section>

        <section className="orbit-panel orbit-panel--warning">
          <h2 className="orbit-section-label">Blocker capture</h2>
          <div className="field-grid">
            <select className="input-field" value={blockerReason} onChange={(event) => setBlockerReason(event.target.value as BlockerReason)}>
              {blockerReasons.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <input
              className="input-field"
              value={unableReason}
              onChange={(event) => setUnableReason(event.target.value)}
              placeholder="Unable reason (required for unable flow)"
            />
            <textarea className="text-area" value={note} onChange={(event) => setNote(event.target.value)} placeholder="Optional blocker note" />
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
            {plan.recommended_reset_actions.length > 0 ? (
              <ul className="orbit-checklist">
                {plan.recommended_reset_actions.map((action) => (
                  <li key={action}>{action}</li>
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
