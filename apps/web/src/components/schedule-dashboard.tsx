"use client";

import { useEffect, useMemo, useState } from "react";

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
  const [selectedDay, setSelectedDay] = useState("");
  const [dailySchedule, setDailySchedule] = useState<DailySchedule | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const localToken = window.localStorage.getItem("orbis_access_token") ?? "";
    if (localToken) {
      setToken(localToken);
    }
  }, []);

  const dayOptions = useMemo(() => weeklySchedule?.days ?? [], [weeklySchedule]);

  async function loadWeek() {
    setMessage("");
    setError("");
    if (!token) {
      setError("Access token is required.");
      return;
    }

    const response = await fetch(`${apiBase}/schedules/weeks/${weekDate}`, {
      headers: authHeaders(token),
      cache: "no-store",
    });

    if (!response.ok) {
      setError(`Could not load weekly schedule (${response.status}).`);
      return;
    }

    const payload = (await response.json()) as WeeklySchedule;
    setWeeklySchedule(payload);
    setSelectedDay((current) => current || payload.days[0]?.schedule_date || "");
    setMessage("Weekly schedule loaded.");
  }

  async function loadDay(scheduleDate: string) {
    setError("");
    setMessage("");
    if (!token) {
      setError("Access token is required.");
      return;
    }

    const response = await fetch(`${apiBase}/schedules/days/${scheduleDate}`, {
      headers: authHeaders(token),
      cache: "no-store",
    });

    if (!response.ok) {
      setError(`Could not load daily schedule (${response.status}).`);
      return;
    }

    const payload = (await response.json()) as DailySchedule;
    setDailySchedule(payload);
    setSelectedDay(payload.schedule_date);
    setMessage("Daily schedule loaded.");
  }

  async function acceptWeeklySchedule() {
    if (!weeklySchedule) return;
    const response = await fetch(`${apiBase}/schedules/weeks/${weeklySchedule.id}/accept`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders(token) },
      body: JSON.stringify({}),
    });

    if (!response.ok) {
      setError(`Could not accept weekly schedule (${response.status}).`);
      return;
    }

    setWeeklySchedule((await response.json()) as WeeklySchedule);
    setMessage("Weekly schedule accepted.");
  }

  async function rejectWeeklySchedule() {
    if (!weeklySchedule) return;
    const response = await fetch(`${apiBase}/schedules/weeks/${weeklySchedule.id}/reject`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders(token) },
      body: JSON.stringify({ reason: "Rejected from schedule dashboard" }),
    });

    if (!response.ok) {
      setError(`Could not reject weekly schedule (${response.status}).`);
      return;
    }

    setWeeklySchedule((await response.json()) as WeeklySchedule);
    setMessage("Weekly schedule rejected.");
  }

  async function acceptDailySchedule() {
    if (!dailySchedule) return;
    const response = await fetch(`${apiBase}/schedules/days/${dailySchedule.id}/accept`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders(token) },
      body: JSON.stringify({}),
    });

    if (!response.ok) {
      setError(`Could not accept daily schedule (${response.status}).`);
      return;
    }

    const payload = (await response.json()) as DailySchedule;
    setDailySchedule(payload);
    setMessage("Daily schedule accepted.");
    await loadWeek();
  }

  return (
    <section className="shell-page">
      <p className="stamp-label">Phase 4.5</p>
      <h1 className="display-title">Weekly and daily schedule context</h1>

      <div className="field-grid" style={{ marginTop: "1rem" }}>
        <input className="input-field" value={token} onChange={(event) => setToken(event.target.value)} placeholder="Access token" />
        <input className="input-field" value={weekDate} onChange={(event) => setWeekDate(event.target.value)} placeholder="Week start date (YYYY-MM-DD)" />
        <button className="btn btn-primary" type="button" onClick={loadWeek}>Load week</button>
      </div>

      {weeklySchedule ? (
        <article className="panel" style={{ marginTop: "1rem" }}>
          <h2 className="headline">Weekly schedule</h2>
          <p className="body-copy">Week start: {weeklySchedule.week_start_date}</p>
          <p className="body-copy">Status: {weeklySchedule.status}</p>
          <div className="button-row">
            <button className="btn btn-primary" type="button" onClick={acceptWeeklySchedule} disabled={weeklySchedule.status !== "proposed"}>
              Accept weekly schedule
            </button>
            <button className="btn btn-secondary" type="button" onClick={rejectWeeklySchedule} disabled={weeklySchedule.status !== "proposed"}>
              Reject weekly schedule
            </button>
          </div>
        </article>
      ) : null}

      {dayOptions.length ? (
        <article className="panel" style={{ marginTop: "1rem" }}>
          <h2 className="headline">Days</h2>
          <div className="button-row">
            {dayOptions.map((day) => (
              <button
                className="btn btn-secondary"
                type="button"
                key={day.id}
                onClick={() => loadDay(day.schedule_date)}
                aria-pressed={selectedDay === day.schedule_date}
              >
                {day.schedule_date} · {day.status}
              </button>
            ))}
          </div>
        </article>
      ) : null}

      {dailySchedule ? (
        <article className="panel" style={{ marginTop: "1rem" }}>
          <h2 className="headline">Daily schedule</h2>
          <p className="body-copy">Date: {dailySchedule.schedule_date}</p>
          <p className="body-copy">Status: {dailySchedule.status}</p>
          <div className="button-row">
            <button className="btn btn-primary" type="button" onClick={acceptDailySchedule} disabled={dailySchedule.status !== "proposed"}>
              Accept daily schedule
            </button>
          </div>
          <ul className="list" style={{ marginTop: "0.75rem" }}>
            {dailySchedule.items.map((item) => (
              <li className="list-item" key={item.id}>
                <strong>{item.task_id.slice(0, 8)}</strong>
                <p className="body-copy">{item.planned_minutes}m planned · outcome {item.outcome_status}</p>
              </li>
            ))}
          </ul>
        </article>
      ) : null}

      {error ? <p className="message-error">{error}</p> : null}
      {message ? <p className="message-success">{message}</p> : null}
    </section>
  );
}
