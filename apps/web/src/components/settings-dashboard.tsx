"use client";

import { useEffect, useState } from "react";

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

const headers = (token: string): Record<string, string> => {
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
};

export function SettingsDashboard() {
  const [token, setToken] = useState("");
  const [form, setForm] = useState<SettingsPayload | null>(null);
  const [profile, setProfile] = useState<{ email: string; role: string } | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    const localToken = window.localStorage.getItem("orbis_access_token") ?? "";
    if (localToken) {
      setToken(localToken);
    }
  }, []);

  async function loadSettings() {
    setError("");
    setMessage("");
    if (!token) {
      setError("Access token is required.");
      return;
    }

    const [settingsRes, meRes] = await Promise.all([
      fetch(`${apiBase}/settings/me`, { headers: headers(token), cache: "no-store" }),
      fetch(`${apiBase}/users/me`, { headers: headers(token), cache: "no-store" }),
    ]);

    if (!settingsRes.ok || !meRes.ok) {
      setError("Could not load settings/profile.");
      return;
    }

    setForm((await settingsRes.json()) as SettingsPayload);
    setProfile((await meRes.json()) as { email: string; role: string });
    setMessage("Settings loaded.");
  }

  async function saveSettings() {
    setError("");
    setMessage("");
    if (!form) {
      return;
    }

    const response = await fetch(`${apiBase}/settings/me`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", ...headers(token) },
      body: JSON.stringify(form),
    });

    if (!response.ok) {
      setError(`Save failed (${response.status}).`);
      return;
    }

    setForm((await response.json()) as SettingsPayload);
    setMessage("Settings saved through API.");
  }

  return (
    <section className="shell-page">
      <p className="stamp-label">Owner settings</p>
      <h1 className="display-title">Settings</h1>

      <div className="field-grid" style={{ marginTop: "1rem" }}>
        <input className="input-field" value={token} onChange={(e) => setToken(e.target.value)} placeholder="Access token" />
        <button className="btn btn-primary" type="button" onClick={loadSettings}>
          Load settings
        </button>
      </div>

      {profile ? (
        <article className="panel" style={{ marginTop: "1rem" }}>
          <h2 className="headline">Profile/session basics</h2>
          <p className="body-copy">{profile.email}</p>
          <p className="body-copy">Role: {profile.role}</p>
        </article>
      ) : null}

      {form ? (
        <div className="organic-grid" style={{ marginTop: "1rem" }}>
          <article className="panel">
            <h2 className="headline">Reminder preferences</h2>
            <label className="body-copy"><input type="checkbox" checked={form.reminder_enabled} onChange={(e) => setForm({ ...form, reminder_enabled: e.target.checked })} /> Enabled</label>
            <div className="row-3">
              <input className="input-field" value={form.reminder_window_start} onChange={(e) => setForm({ ...form, reminder_window_start: e.target.value })} />
              <input className="input-field" value={form.reminder_window_end} onChange={(e) => setForm({ ...form, reminder_window_end: e.target.value })} />
            </div>
          </article>

          <article className="panel">
            <h2 className="headline">Integrations</h2>
            <label className="body-copy"><input type="checkbox" checked={form.calendar_connected} onChange={(e) => setForm({ ...form, calendar_connected: e.target.checked })} /> Calendar connected</label>
            <input className="input-field" value={form.calendar_provider ?? ""} placeholder="Calendar provider" onChange={(e) => setForm({ ...form, calendar_provider: e.target.value || null })} />
            <label className="body-copy"><input type="checkbox" checked={form.notes_connected} onChange={(e) => setForm({ ...form, notes_connected: e.target.checked })} /> Notes connected</label>
            <input className="input-field" value={form.notes_provider ?? ""} placeholder="Notes provider" onChange={(e) => setForm({ ...form, notes_provider: e.target.value || null })} />
          </article>

          <article className="panel panel--focus">
            <h2 className="headline">AI planning controls</h2>
            <label className="body-copy"><input type="checkbox" checked={form.ai_planning_enabled} onChange={(e) => setForm({ ...form, ai_planning_enabled: e.target.checked })} /> AI planning enabled</label>
            <label className="body-copy"><input type="checkbox" checked={form.ai_auto_generate_weekly} onChange={(e) => setForm({ ...form, ai_auto_generate_weekly: e.target.checked })} /> Auto-generate weekly proposal</label>
            <label className="body-copy"><input type="checkbox" checked={form.ai_require_manual_approval} onChange={(e) => setForm({ ...form, ai_require_manual_approval: e.target.checked })} /> Require manual approval</label>
            <input className="input-field" value={form.ai_preferred_provider ?? ""} placeholder="Preferred AI provider" onChange={(e) => setForm({ ...form, ai_preferred_provider: e.target.value || null })} />
            <textarea className="text-area" value={form.session_note ?? ""} placeholder="Session note" onChange={(e) => setForm({ ...form, session_note: e.target.value || null })} />
          </article>
        </div>
      ) : null}

      {form ? (
        <div className="button-row" style={{ marginTop: "1rem" }}>
          <button className="btn btn-primary" type="button" onClick={saveSettings}>
            Save settings
          </button>
        </div>
      ) : null}

      {error ? <p className="message-error">{error}</p> : null}
      {message ? <p className="message-success">{message}</p> : null}
    </section>
  );
}
