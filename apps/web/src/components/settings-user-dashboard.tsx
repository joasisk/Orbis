"use client";

import { useEffect, useState } from "react";
import { EmptyState, ScreenHeader, SectionCard } from "@/components/ui-kit";
import { DEFAULT_UI_LANGUAGE, translate, type UiLanguage } from "@/lib/i18n";

type SettingsPayload = {
  reminder_enabled: boolean;
  reminder_window_start: string;
  reminder_window_end: string;
  ai_planning_enabled: boolean;
  ai_auto_generate_weekly: boolean;
  ai_require_manual_approval: boolean;
  ai_preferred_provider: string | null;
  app_timezone: string;
  weekly_planning_enabled: boolean;
  weekly_planning_day_of_week: number;
  weekly_planning_time_local: string;
  notes_scan_enabled: boolean;
  notes_scan_frequency: "daily" | "weekly";
  notes_scan_day_of_week: number | null;
  notes_scan_time_local: string | null;
  reminder_scan_interval_minutes: number;
  automation_pause_until: string | null;
  ui_language: UiLanguage;
};

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";
const headers = (token: string): Record<string, string> => (token ? { Authorization: `Bearer ${token}` } : {});

export function SettingsUserDashboard() {
  const [token, setToken] = useState("");
  const [form, setForm] = useState<SettingsPayload | null>(null);
  const [error, setError] = useState("");
  const language = form?.ui_language ?? DEFAULT_UI_LANGUAGE;

  useEffect(() => {
    const localToken = window.localStorage.getItem("orbis_access_token") ?? "";
    if (localToken) setToken(localToken);
  }, []);

  async function loadSettings() {
    const response = await fetch(`${apiBase}/settings/me`, { headers: headers(token), cache: "no-store" });
    if (!response.ok) {
      setError(translate(language, "couldNotLoadSettings"));
      return;
    }

    const data = (await response.json()) as SettingsPayload;
    setForm(data);
  }

  async function saveSettings() {
    if (!form) return;
    const response = await fetch(`${apiBase}/settings/me`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", ...headers(token) },
      body: JSON.stringify(form),
    });
    if (!response.ok) {
      setError(translate(language, "saveFailed"));
      return;
    }
    setForm((await response.json()) as SettingsPayload);
  }

  useEffect(() => {
    if (!token || form) return;
    void loadSettings();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  return (
    <section className="screen-flow">
      <ScreenHeader
        title={translate(language, "userSettingsTitle")}
        subtitle={translate(language, "userSettingsSubtitle")}
        actions={(
          <>
            <input className="app-input" value={token} onChange={(event) => setToken(event.target.value)} placeholder={translate(language, "accessToken")} />
            <button className="app-button app-button--primary" type="button" onClick={loadSettings}>{translate(language, "load")}</button>
          </>
        )}
      />

      {!form ? <EmptyState message={translate(language, "loadSettingsEmpty")} /> : (
        <div className="two-col">
          <SectionCard title={translate(language, "languageSettings")}>
            <label htmlFor="ui-language">{translate(language, "languageLabel")}</label>
            <select
              id="ui-language"
              className="app-input"
              value={form.ui_language}
              onChange={(event) => setForm({ ...form, ui_language: event.target.value as UiLanguage })}
            >
              <option value="en">{translate(language, "languageEnglish")}</option>
              <option value="sk">{translate(language, "languageSlovak")}</option>
              <option value="de">{translate(language, "languageGerman")}</option>
              <option value="it">{translate(language, "languageItalian")}</option>
              <option value="es">{translate(language, "languageSpanish")}</option>
              <option value="pl">{translate(language, "languagePolish")}</option>
            </select>
          </SectionCard>

          <SectionCard title={translate(language, "notificationSettings")}>
            <label><input type="checkbox" checked={form.reminder_enabled} onChange={(event) => setForm({ ...form, reminder_enabled: event.target.checked })} /> {translate(language, "reminderEnabled")}</label>
            <label htmlFor="reminder-start">{translate(language, "reminderWindowStart")}</label>
            <input id="reminder-start" className="app-input" value={form.reminder_window_start} onChange={(event) => setForm({ ...form, reminder_window_start: event.target.value })} />
            <label htmlFor="reminder-end">{translate(language, "reminderWindowEnd")}</label>
            <input id="reminder-end" className="app-input" value={form.reminder_window_end} onChange={(event) => setForm({ ...form, reminder_window_end: event.target.value })} />
          </SectionCard>

          <SectionCard title={translate(language, "aiPlanningSettings")} tone="accent">
            <label><input type="checkbox" checked={form.ai_planning_enabled} onChange={(event) => setForm({ ...form, ai_planning_enabled: event.target.checked })} /> {translate(language, "aiPlanningEnabled")}</label>
            <label><input type="checkbox" checked={form.ai_auto_generate_weekly} onChange={(event) => setForm({ ...form, ai_auto_generate_weekly: event.target.checked })} /> {translate(language, "autoGenerateTrajectory")}</label>
            <label><input type="checkbox" checked={form.ai_require_manual_approval} onChange={(event) => setForm({ ...form, ai_require_manual_approval: event.target.checked })} /> {translate(language, "requireManualApproval")}</label>
            <input className="app-input" value={form.ai_preferred_provider ?? ""} onChange={(event) => setForm({ ...form, ai_preferred_provider: event.target.value || null })} placeholder={translate(language, "preferredProvider")} />
          </SectionCard>

          <SectionCard title={translate(language, "scheduleAutomationSettings")} tone="accent">
            <label htmlFor="app-timezone">{translate(language, "appTimezone")}</label>
            <input id="app-timezone" className="app-input" value={form.app_timezone} onChange={(event) => setForm({ ...form, app_timezone: event.target.value })} />
            <label><input type="checkbox" checked={form.weekly_planning_enabled} onChange={(event) => setForm({ ...form, weekly_planning_enabled: event.target.checked })} /> {translate(language, "weeklyPlanningEnabled")}</label>
            <label htmlFor="weekly-day">{translate(language, "weeklyPlanningDay")}</label>
            <input id="weekly-day" className="app-input" type="number" min="0" max="6" value={form.weekly_planning_day_of_week} onChange={(event) => setForm({ ...form, weekly_planning_day_of_week: Number(event.target.value) })} />
            <label htmlFor="weekly-time">{translate(language, "weeklyPlanningTime")}</label>
            <input id="weekly-time" className="app-input" value={form.weekly_planning_time_local} onChange={(event) => setForm({ ...form, weekly_planning_time_local: event.target.value })} />
            <label><input type="checkbox" checked={form.notes_scan_enabled} onChange={(event) => setForm({ ...form, notes_scan_enabled: event.target.checked })} /> {translate(language, "notesScanEnabled")}</label>
            <select className="app-input" value={form.notes_scan_frequency} onChange={(event) => setForm({ ...form, notes_scan_frequency: event.target.value as "daily" | "weekly" })}>
              <option value="daily">{translate(language, "cadenceDaily")}</option>
              <option value="weekly">{translate(language, "cadenceWeekly")}</option>
            </select>
            <label htmlFor="notes-day">{translate(language, "notesScanDay")}</label>
            <input id="notes-day" className="app-input" type="number" min="0" max="6" value={form.notes_scan_day_of_week ?? ""} onChange={(event) => setForm({ ...form, notes_scan_day_of_week: event.target.value === "" ? null : Number(event.target.value) })} />
            <label htmlFor="notes-time">{translate(language, "notesScanTime")}</label>
            <input id="notes-time" className="app-input" value={form.notes_scan_time_local ?? ""} onChange={(event) => setForm({ ...form, notes_scan_time_local: event.target.value || null })} />
            <label htmlFor="scan-interval">{translate(language, "reminderScanInterval")}</label>
            <input id="scan-interval" className="app-input" type="number" min="5" max="240" value={form.reminder_scan_interval_minutes} onChange={(event) => setForm({ ...form, reminder_scan_interval_minutes: Number(event.target.value) })} />
            <label htmlFor="pause-until">{translate(language, "automationPauseUntil")}</label>
            <input id="pause-until" className="app-input" type="datetime-local" value={form.automation_pause_until ? form.automation_pause_until.slice(0, 16) : ""} onChange={(event) => setForm({ ...form, automation_pause_until: event.target.value ? new Date(event.target.value).toISOString() : null })} />
          </SectionCard>

          <SectionCard title={translate(language, "settingsTitle")}>
            <button className="app-button app-button--primary" type="button" onClick={saveSettings}>{translate(language, "saveSettings")}</button>
          </SectionCard>
        </div>
      )}
      {error ? <p className="error-text">{error}</p> : null}
    </section>
  );
}
