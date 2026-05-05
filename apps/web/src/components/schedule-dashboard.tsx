"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { EmptyState, ScreenHeader, SectionCard, StatusPill } from "@/components/ui-kit";
import { DEFAULT_UI_LANGUAGE, translate, type UiLanguage } from "@/lib/i18n";

type DailySchedule = {
  id: string;
  schedule_date: string;
  status: "proposed" | "accepted" | "adjusted";
  items: Array<{ id: string; task_id: string; planned_minutes: number; outcome_status: string }>;
};

type WeeklySchedule = {
  id: string;
  week_start_date: string;
  status: "proposed" | "accepted" | "rejected";
  days: DailySchedule[];
};
type WeeklyProposal = {
  id: string;
  week_start_date: string;
  status: "proposed" | "approved" | "rejected" | "generated" | "draft";
  items: Array<{ id: string; task_id: string; task_title?: string | null; suggested_day: string; suggested_date?: string | null; suggested_minutes: number; rationale: string; rank: number }>;
};
type NoteExtraction = {
  id: string;
  source_title: string;
  source_ref: string | null;
  status: "proposed" | "accepted" | "dismissed";
  candidate_tasks: Array<{ title: string; notes: string | null }>;
};

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api/v1";
const authHeaders = (token: string): Record<string, string> => (token ? { Authorization: `Bearer ${token}` } : {});

function mondayIso(baseDate: Date) {
  const normalized = new Date(baseDate);
  const weekday = normalized.getUTCDay() || 7;
  normalized.setUTCDate(normalized.getUTCDate() - weekday + 1);
  return normalized.toISOString().slice(0, 10);
}

export function formatProposalStatus(status: WeeklyProposal["status"]): string {
  if (status === "proposed") return "Awaiting review";
  if (status === "approved") return "Approved";
  if (status === "generated" || status === "draft") return "Draft ready";
  return status.replace(/[-_]+/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

export function formatProposalTaskTitle(taskId: string, taskTitle?: string | null): string {
  if (taskTitle && taskTitle.trim()) return taskTitle.trim();
  if (taskId.startsWith("ranked_for_weekly_plan")) return "Priority planning task";
  return `Task ${taskId.slice(0, 8)}`;
}

export function formatProposalReason(rationale: string): string {
  if (!rationale) return "Suggested because it matches your weekly priorities.";
  if (rationale.startsWith("ranked_for_weekly_plan_priority")) {
    const priorityMatch = rationale.match(/priority_(\d+)/);
    if (priorityMatch) return `Suggested because it supports your weekly priorities (#${priorityMatch[1]}).`;
    return "Suggested because it matches your weekly priorities.";
  }
  if (rationale.startsWith("ranked_for_weekly_plan")) return "Suggested because it matches your weekly priorities.";
  const rationaleParts = rationale.split("_");
  return rationaleParts
    .filter(Boolean)
    .map((part, idx) => (/^\d+$/.test(part) && idx > 0 && ["priority", "minutes", "rank"].includes(rationaleParts[idx - 1]) ? `#${part}` : part))
    .join(" ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

export function formatDurationSummary(minutes: number): string {
  if (minutes < 60) return `${minutes} min`;
  const hours = Math.floor(minutes / 60);
  const remaining = minutes % 60;
  if (!remaining) return `${hours} hour${hours > 1 ? "s" : ""}`;
  return `${hours}h ${remaining}m`;
}

function parseDurationMinutes(value: number | string): number {
  if (typeof value === "number") return Number.isFinite(value) ? value : 0;
  const normalized = value.trim().toLowerCase();
  const exact = Number(normalized);
  if (!Number.isNaN(exact)) return exact;
  const match = normalized.match(/(\d+)/);
  return match ? Number(match[1]) : 0;
}

export function getTotalDurationMinutes(items: WeeklyProposal["items"]): number {
  return items.reduce((sum, item) => sum + parseDurationMinutes(item.suggested_minutes), 0);
}

function formatSuggestedDayLabel(suggestedDay: string, suggestedDate?: string | null): string {
  if (suggestedDate) return new Date(`${suggestedDate}T00:00:00Z`).toLocaleDateString("en-US", { weekday: "long", timeZone: "UTC" });
  return suggestedDay.replace(/[-_]+/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

export function ScheduleDashboard() {
  const [token, setToken] = useState("");
  const [weekDate, setWeekDate] = useState(mondayIso(new Date()));
  const [weeklySchedule, setWeeklySchedule] = useState<WeeklySchedule | null>(null);
  const [dailySchedule, setDailySchedule] = useState<DailySchedule | null>(null);
  const [weekMode, setWeekMode] = useState<"current" | "future">("current");
  const [error, setError] = useState("");
  const [isLoadingWeek, setIsLoadingWeek] = useState(false);
  const [language, setLanguage] = useState<UiLanguage>(DEFAULT_UI_LANGUAGE);
  const [proposal, setProposal] = useState<WeeklyProposal | null>(null);
  const [proposalLoading, setProposalLoading] = useState(false);
  const [proposalError, setProposalError] = useState("");
  const [noteTitle, setNoteTitle] = useState("");
  const [noteRef, setNoteRef] = useState("");
  const [noteContent, setNoteContent] = useState("");
  const [extraction, setExtraction] = useState<NoteExtraction | null>(null);
  const [selectedCandidateIdx, setSelectedCandidateIdx] = useState<number[]>([]);

  useEffect(() => {
    const localToken = window.localStorage.getItem("orbis_access_token") ?? "";
    if (localToken) setToken(localToken);
    const localLanguage = (window.localStorage.getItem("orbis_ui_language") as UiLanguage | null) ?? DEFAULT_UI_LANGUAGE;
    setLanguage(localLanguage);
  }, []);

  async function loadWeek() {
    if (!token || isLoadingWeek) return;
    setError("");
    setIsLoadingWeek(true);
    const response = await fetch(`${apiBase}/schedules/weeks/${weekDate}`, { headers: authHeaders(token), cache: "no-store" });
    if (!response.ok) {
      setIsLoadingWeek(false);
      setError(`Could not load Trajectory (${response.status}).`);
      return;
    }
    const payload = (await response.json()) as WeeklySchedule;
    setWeeklySchedule(payload);
    setDailySchedule(payload.days[0] ?? null);
    setIsLoadingWeek(false);
  }

  async function loadDay(scheduleDate: string) {
    if (!token) return;
    const response = await fetch(`${apiBase}/schedules/days/${scheduleDate}`, { headers: authHeaders(token), cache: "no-store" });
    if (!response.ok) return;
    setDailySchedule((await response.json()) as DailySchedule);
  }

  useEffect(() => {
    if (!token || weeklySchedule || isLoadingWeek) return;
    void loadWeek();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, weekDate]);

  useEffect(() => {
    if (!token || proposal || proposalLoading) return;
    void loadLatestProposal();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  async function generateProposal() {
    if (!token || proposalLoading) return;
    setProposalError("");
    setProposalLoading(true);
    const response = await fetch(`${apiBase}/planning/weekly-proposals/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders(token) },
      body: JSON.stringify({ week_start_date: weekDate }),
    });
    setProposalLoading(false);
    if (!response.ok) {
      setProposalError(`${translate(language, "weeklyProposalError")} (${response.status}).`);
      return;
    }
    setProposal((await response.json()) as WeeklyProposal);
  }

  async function loadLatestProposal() {
    if (!token || proposalLoading) return;
    setProposalError("");
    setProposalLoading(true);
    const response = await fetch(`${apiBase}/planning/weekly-proposals/latest`, { headers: authHeaders(token), cache: "no-store" });
    setProposalLoading(false);
    if (!response.ok) {
      setProposalError(`${translate(language, "weeklyProposalError")} (${response.status}).`);
      return;
    }
    setProposal((await response.json()) as WeeklyProposal);
  }

  async function approveProposal() {
    if (!token || !proposal) return;
    setProposalError("");
    const response = await fetch(`${apiBase}/planning/weekly-proposals/${proposal.id}/approve`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders(token) },
      body: JSON.stringify({ edits: [] }),
    });
    if (!response.ok) {
      setProposalError(`${translate(language, "weeklyProposalApproveError")} (${response.status}).`);
      return;
    }
    setProposal((await response.json()) as WeeklyProposal);
  }

  async function previewNoteExtraction() {
    if (!token || !noteTitle || !noteContent) return;
    const response = await fetch(`${apiBase}/planning/note-extractions/preview`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders(token) },
      body: JSON.stringify({ source_title: noteTitle, source_ref: noteRef || null, note_content: noteContent }),
    });
    if (!response.ok) {
      setError(`${translate(language, "noteExtractionError")} (${response.status}).`);
      return;
    }
    setExtraction((await response.json()) as NoteExtraction);
    setSelectedCandidateIdx([]);
  }

  async function submitExtractionDecision(decision: "accept" | "dismiss") {
    if (!token || !extraction) return;
    const response = await fetch(`${apiBase}/planning/note-extractions/${extraction.id}/decision`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders(token) },
      body: JSON.stringify({ decision, selected_indices: decision === "accept" ? selectedCandidateIdx : [] }),
    });
    if (!response.ok) {
      setError(`${translate(language, "noteExtractionDecisionError")} (${response.status}).`);
      return;
    }
    setExtraction((await response.json()) as NoteExtraction);
  }

  return (
    <section className="screen-flow">
      <ScreenHeader
        title={weekMode === "current" ? "Trajectory — This Week" : "Trajectory — Future Weeks"}
        subtitle="Trajectory planning and execution"
        actions={(
          <>
            <button className={`app-button ${weekMode === "current" ? "app-button--secondary" : ""}`} onClick={() => setWeekMode("current")} type="button">This Week’s Trajectory</button>
            <button className={`app-button ${weekMode === "future" ? "app-button--secondary" : ""}`} onClick={() => setWeekMode("future")} type="button">Future Trajectories</button>
            <input className="app-input" placeholder="Access token" value={token} onChange={(event) => setToken(event.target.value)} />
            <input className="app-input app-input--short" value={weekDate} onChange={(event) => setWeekDate(event.target.value)} />
            <button className="app-button app-button--primary" onClick={loadWeek} type="button">{isLoadingWeek ? "Loading..." : "Load Trajectory"}</button>
          </>
        )}
      />

      <SectionCard title="Trajectory Grid">
        {weeklySchedule ? (
          <>
            <p className="lead-copy">This week’s Trajectory starts {weeklySchedule.week_start_date}</p>
            <p><StatusPill label={weeklySchedule.status} /></p>
            <div className="week-grid">
              {weeklySchedule.days.map((day) => (
                <button key={day.id} className="day-card" type="button" onClick={() => loadDay(day.schedule_date)}>
                  <strong>{day.schedule_date}</strong>
                  <span>{day.items.length} items</span>
                  <StatusPill label={day.status} />
                </button>
              ))}
            </div>
          </>
        ) : <EmptyState message={isLoadingWeek ? "Loading this week’s Trajectory..." : "Load a Trajectory to see planning and execution context."} />}
      </SectionCard>

      <SectionCard title={weekMode === "current" ? "Overload / blockers strip" : "Planning Suggestions"}>
        {dailySchedule ? (
          <ul className="stack-list">
            {dailySchedule.items.map((item) => (
              <li className="task-row" key={item.id}>
                <span>Task {item.task_id.slice(0, 8)} · {item.planned_minutes}m</span>
                <StatusPill label={item.outcome_status} />
              </li>
            ))}
          </ul>
        ) : <EmptyState message="Pick a Burn to inspect details." />}
      </SectionCard>
      <SectionCard title={translate(language, "weeklyProposalTitle")} tone="accent">
        <section className="weekly-proposal-card" aria-live="polite">
          <header className="weekly-proposal-card__header">
            <div>
              <h3>{translate(language, "weeklyProposalTitle")}</h3>
              <p>{translate(language, "weeklyProposalGuardrail")}</p>
            </div>
            <StatusPill label={formatProposalStatus(proposal?.status ?? "draft")} />
          </header>
          <div className="button-row weekly-proposal-card__actions">
            <button className="app-button app-button--primary" type="button" onClick={approveProposal} disabled={!proposal || proposal.status !== "proposed"}>{translate(language, "weeklyProposalApprove")}</button>
            <button className="app-button app-button--secondary" type="button" disabled>{translate(language, "weeklyProposalEdit")}</button>
            <button className="app-button" type="button" onClick={generateProposal} disabled={proposalLoading}>{proposalLoading ? "..." : proposal ? translate(language, "weeklyProposalRegenerate") : translate(language, "weeklyProposalGenerate")}</button>
            <button className="app-button app-button--ghost" type="button" onClick={loadLatestProposal} disabled={proposalLoading}>{translate(language, "weeklyProposalLoadLatest")}</button>
          </div>
        </section>
        {proposalError ? <p className="error-text">{proposalError}</p> : null}
        {proposal ? <div className="weekly-proposal-summary"><span>{proposal.items.length} {translate(language, "weeklyProposalSuggestedSessions")}</span><span>{formatDurationSummary(getTotalDurationMinutes(proposal.items))} {translate(language, "weeklyProposalTotal")}</span></div> : null}
        {proposalLoading ? <EmptyState message={translate(language, "weeklyProposalLoading")} /> : null}
        {!proposalLoading && proposal ? (
          <div className="stack-list">
            {proposal.items.length ? proposal.items.map((item) => (
              <article className="weekly-proposal-item" key={item.id}>
                <span className="weekly-proposal-item__day">{formatSuggestedDayLabel(item.suggested_day, item.suggested_date)}</span>
                <div>
                  <p><strong><Link href={`/tasks/${item.task_id}`}>{formatProposalTaskTitle(item.task_id, item.task_title)}</Link></strong></p>
                  <p className="weekly-proposal-item__meta">{formatDurationSummary(item.suggested_minutes)}</p>
                  <p>{formatProposalReason(item.rationale)}</p>
                </div>
              </article>
            )) : <EmptyState message={translate(language, "weeklyProposalNoItems")} />}
          </div>
        ) : null}
        {!proposalLoading && !proposal ? <EmptyState message={translate(language, "weeklyProposalEmpty")} /> : null}
      </SectionCard>

      <SectionCard title={translate(language, "noteExtractionTitle")}>
        <div className="stack-form">
          <input className="app-input" value={noteTitle} onChange={(event) => setNoteTitle(event.target.value)} placeholder={translate(language, "noteSourceTitle")} />
          <input className="app-input" value={noteRef} onChange={(event) => setNoteRef(event.target.value)} placeholder={translate(language, "noteSourceRef")} />
          <textarea className="app-input" value={noteContent} onChange={(event) => setNoteContent(event.target.value)} placeholder={translate(language, "noteContent")} />
          <button className="app-button app-button--primary" type="button" onClick={previewNoteExtraction}>{translate(language, "previewExtraction")}</button>
        </div>
        {extraction ? (
          <>
            <p><strong>{translate(language, "statusLabel")}:</strong> {extraction.status}</p>
            <ul className="stack-list">
              {extraction.candidate_tasks.map((candidate, idx) => (
                <li key={`${candidate.title}-${idx}`}>
                  <label>
                    <input
                      type="checkbox"
                      checked={selectedCandidateIdx.includes(idx)}
                      onChange={(event) => setSelectedCandidateIdx((prev) => event.target.checked ? [...prev, idx] : prev.filter((value) => value !== idx))}
                    />
                    {` ${candidate.title}`}
                  </label>
                </li>
              ))}
            </ul>
            <div className="button-row">
              <button className="app-button app-button--primary" type="button" onClick={() => submitExtractionDecision("accept")}>{translate(language, "acceptSelected")}</button>
              <button className="app-button" type="button" onClick={() => submitExtractionDecision("dismiss")}>{translate(language, "dismissExtraction")}</button>
            </div>
          </>
        ) : <EmptyState message={translate(language, "noteExtractionEmpty")} />}
      </SectionCard>
      {error ? <p className="error-text">{error}</p> : null}
    </section>
  );
}
