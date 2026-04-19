"use client";

import { useEffect, useState } from "react";
import { EmptyState, ScreenHeader, SectionCard, StatusPill } from "@/components/ui-kit";

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

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";
const authHeaders = (token: string): Record<string, string> => (token ? { Authorization: `Bearer ${token}` } : {});

function mondayIso(baseDate: Date) {
  const normalized = new Date(baseDate);
  const weekday = normalized.getUTCDay() || 7;
  normalized.setUTCDate(normalized.getUTCDate() - weekday + 1);
  return normalized.toISOString().slice(0, 10);
}

export function ScheduleDashboard() {
  const [token, setToken] = useState("");
  const [weekDate, setWeekDate] = useState(mondayIso(new Date()));
  const [weeklySchedule, setWeeklySchedule] = useState<WeeklySchedule | null>(null);
  const [dailySchedule, setDailySchedule] = useState<DailySchedule | null>(null);
  const [weekMode, setWeekMode] = useState<"current" | "future">("current");
  const [error, setError] = useState("");
  const [isLoadingWeek, setIsLoadingWeek] = useState(false);

  useEffect(() => {
    const localToken = window.localStorage.getItem("orbis_access_token") ?? "";
    if (localToken) setToken(localToken);
  }, []);

  async function loadWeek() {
    if (!token || isLoadingWeek) return;
    setError("");
    setIsLoadingWeek(true);
    const response = await fetch(`${apiBase}/schedules/weeks/${weekDate}`, { headers: authHeaders(token), cache: "no-store" });
    if (!response.ok) {
      setIsLoadingWeek(false);
      setError(`Could not load week (${response.status}).`);
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

  return (
    <section className="screen-flow">
      <ScreenHeader
        title={weekMode === "current" ? "Week — Current Week" : "Week — Future Weeks"}
        subtitle="Execution and planning"
        actions={(
          <>
            <button className={`app-button ${weekMode === "current" ? "app-button--secondary" : ""}`} onClick={() => setWeekMode("current")} type="button">Current Week</button>
            <button className={`app-button ${weekMode === "future" ? "app-button--secondary" : ""}`} onClick={() => setWeekMode("future")} type="button">Future Weeks</button>
            <input className="app-input" placeholder="Access token" value={token} onChange={(event) => setToken(event.target.value)} />
            <input className="app-input app-input--short" value={weekDate} onChange={(event) => setWeekDate(event.target.value)} />
            <button className="app-button app-button--primary" onClick={loadWeek} type="button">{isLoadingWeek ? "Loading..." : "Load Week"}</button>
          </>
        )}
      />

      <SectionCard title="Week Grid">
        {weeklySchedule ? (
          <>
            <p className="lead-copy">Week of {weeklySchedule.week_start_date}</p>
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
        ) : <EmptyState message={isLoadingWeek ? "Loading current week..." : "Load a week to see execution and planning context."} />}
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
        ) : <EmptyState message="Pick a day to inspect details." />}
      </SectionCard>
      {error ? <p className="error-text">{error}</p> : null}
    </section>
  );
}
