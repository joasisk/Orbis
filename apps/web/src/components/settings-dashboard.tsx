"use client";

import { useEffect, useState } from "react";
import { EmptyState, ScreenHeader, SectionCard } from "@/components/ui-kit";

type SettingsPayload = {
  reminder_enabled: boolean;
  reminder_window_start: string;
  reminder_window_end: string;
  calendar_connected: boolean;
  calendar_provider: string | null;
  notes_connected: boolean;
  notes_provider: string | null;
  ai_planning_enabled: boolean;
  ai_auto_generate_weekly: boolean;
  ai_require_manual_approval: boolean;
  ai_preferred_provider: string | null;
  session_note: string | null;
};

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";
const headers = (token: string): Record<string, string> => (token ? { Authorization: `Bearer ${token}` } : {});

export function SettingsDashboard() {
  const [token, setToken] = useState("");
  const [form, setForm] = useState<SettingsPayload | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const localToken = window.localStorage.getItem("orbis_access_token") ?? "";
    if (localToken) setToken(localToken);
  }, []);

  async function loadSettings() {
    const response = await fetch(`${apiBase}/settings/me`, { headers: headers(token), cache: "no-store" });
    if (!response.ok) {
      setError("Could not load settings.");
      return;
    }
    setForm((await response.json()) as SettingsPayload);
  }

  async function saveSettings() {
    if (!form) return;
    const response = await fetch(`${apiBase}/settings/me`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", ...headers(token) },
      body: JSON.stringify(form),
    });
    if (!response.ok) {
      setError("Save failed.");
      return;
    }
    setForm((await response.json()) as SettingsPayload);
  }

  return (
    <section className="screen-flow">
      <ScreenHeader
        title="Settings"
        subtitle="User and app configuration"
        actions={(
          <>
            <input className="app-input" value={token} onChange={(event) => setToken(event.target.value)} placeholder="Access token" />
            <button className="app-button app-button--primary" type="button" onClick={loadSettings}>Load</button>
          </>
        )}
      />

      {!form ? <EmptyState message="Load settings to edit notification and planning controls." /> : (
        <div className="two-col">
          <SectionCard title="Notification Settings">
            <label><input type="checkbox" checked={form.reminder_enabled} onChange={(event) => setForm({ ...form, reminder_enabled: event.target.checked })} /> Reminder enabled</label>
            <input className="app-input" value={form.reminder_window_start} onChange={(event) => setForm({ ...form, reminder_window_start: event.target.value })} />
            <input className="app-input" value={form.reminder_window_end} onChange={(event) => setForm({ ...form, reminder_window_end: event.target.value })} />
          </SectionCard>

          <SectionCard title="AI / Planning Settings" tone="accent">
            <label><input type="checkbox" checked={form.ai_planning_enabled} onChange={(event) => setForm({ ...form, ai_planning_enabled: event.target.checked })} /> AI planning enabled</label>
            <label><input type="checkbox" checked={form.ai_auto_generate_weekly} onChange={(event) => setForm({ ...form, ai_auto_generate_weekly: event.target.checked })} /> Auto-generate weekly</label>
            <label><input type="checkbox" checked={form.ai_require_manual_approval} onChange={(event) => setForm({ ...form, ai_require_manual_approval: event.target.checked })} /> Require manual approval</label>
            <input className="app-input" value={form.ai_preferred_provider ?? ""} onChange={(event) => setForm({ ...form, ai_preferred_provider: event.target.value || null })} placeholder="Preferred provider" />
            <button className="app-button app-button--primary" type="button" onClick={saveSettings}>Save settings</button>
          </SectionCard>
        </div>
      )}
      {error ? <p className="error-text">{error}</p> : null}
    </section>
  );
}
