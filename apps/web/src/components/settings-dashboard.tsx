"use client";

import { useEffect, useState } from "react";
import { EmptyState, ScreenHeader, SectionCard } from "@/components/ui-kit";
import { DEFAULT_UI_LANGUAGE, translate, type UiLanguage } from "@/lib/i18n";

type UserRole = "owner" | "spouse";

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
  ui_language: UiLanguage;
  session_note: string | null;
};

type MePayload = {
  role: UserRole;
};

type SpouseStatusPayload = {
  spouse: {
    id: string;
    email: string;
    created_at: string;
  } | null;
};

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";
const headers = (token: string): Record<string, string> => (token ? { Authorization: `Bearer ${token}` } : {});

export function SettingsDashboard() {
  const [token, setToken] = useState("");
  const [form, setForm] = useState<SettingsPayload | null>(null);
  const [role, setRole] = useState<UserRole | null>(null);
  const [spouseStatus, setSpouseStatus] = useState<SpouseStatusPayload | null>(null);
  const [spouseForm, setSpouseForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const language = form?.ui_language ?? DEFAULT_UI_LANGUAGE;

  useEffect(() => {
    const localToken = window.localStorage.getItem("orbis_access_token") ?? "";
    if (localToken) setToken(localToken);
  }, []);

  async function loadSettings() {
    const [settingsResponse, meResponse] = await Promise.all([
      fetch(`${apiBase}/settings/me`, { headers: headers(token), cache: "no-store" }),
      fetch(`${apiBase}/users/me`, { headers: headers(token), cache: "no-store" }),
    ]);

    if (!settingsResponse.ok || !meResponse.ok) {
      setError(translate(language, "couldNotLoadSettings"));
      return;
    }

    const me = (await meResponse.json()) as MePayload;
    setRole(me.role);
    setForm((await settingsResponse.json()) as SettingsPayload);

    if (me.role === "owner") {
      const spouseResponse = await fetch(`${apiBase}/users/spouse`, { headers: headers(token), cache: "no-store" });
      if (spouseResponse.ok) {
        setSpouseStatus((await spouseResponse.json()) as SpouseStatusPayload);
      }
    }
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

  async function createSpouse() {
    const response = await fetch(`${apiBase}/users/spouse`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...headers(token) },
      body: JSON.stringify(spouseForm),
    });
    if (!response.ok) {
      setError(`Could not create spouse (${response.status}).`);
      return;
    }
    setSpouseForm({ email: "", password: "" });
    const spouseResponse = await fetch(`${apiBase}/users/spouse`, { headers: headers(token), cache: "no-store" });
    if (spouseResponse.ok) {
      setSpouseStatus((await spouseResponse.json()) as SpouseStatusPayload);
    }
  }

  useEffect(() => {
    if (!token || form) return;
    void loadSettings();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  return (
    <section className="screen-flow">
      <ScreenHeader
        title={translate(language, "settingsTitle")}
        subtitle={translate(language, "settingsSubtitle")}
        actions={(
          <>
            <input className="app-input" value={token} onChange={(event) => setToken(event.target.value)} placeholder={translate(language, "accessToken")} />
            <button className="app-button app-button--primary" type="button" onClick={loadSettings}>{translate(language, "load")}</button>
          </>
        )}
      />

      {!form ? <EmptyState message={translate(language, "loadSettingsEmpty")} /> : (
        <div className="two-col">
          <SectionCard title={translate(language, "notificationSettings")}>
            <label><input type="checkbox" checked={form.reminder_enabled} onChange={(event) => setForm({ ...form, reminder_enabled: event.target.checked })} /> {translate(language, "reminderEnabled")}</label>
            <input className="app-input" value={form.reminder_window_start} onChange={(event) => setForm({ ...form, reminder_window_start: event.target.value })} />
            <input className="app-input" value={form.reminder_window_end} onChange={(event) => setForm({ ...form, reminder_window_end: event.target.value })} />
          </SectionCard>

          <SectionCard title={translate(language, "aiPlanningSettings")} tone="accent">
            <label><input type="checkbox" checked={form.ai_planning_enabled} onChange={(event) => setForm({ ...form, ai_planning_enabled: event.target.checked })} /> {translate(language, "aiPlanningEnabled")}</label>
            <label><input type="checkbox" checked={form.ai_auto_generate_weekly} onChange={(event) => setForm({ ...form, ai_auto_generate_weekly: event.target.checked })} /> {translate(language, "autoGenerateTrajectory")}</label>
            <label><input type="checkbox" checked={form.ai_require_manual_approval} onChange={(event) => setForm({ ...form, ai_require_manual_approval: event.target.checked })} /> {translate(language, "requireManualApproval")}</label>
            <input className="app-input" value={form.ai_preferred_provider ?? ""} onChange={(event) => setForm({ ...form, ai_preferred_provider: event.target.value || null })} placeholder={translate(language, "preferredProvider")} />
            <button className="app-button app-button--primary" type="button" onClick={saveSettings}>{translate(language, "saveSettings")}</button>
          </SectionCard>

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
            </select>
          </SectionCard>

          {role === "owner" ? (
            <SectionCard title={translate(language, "spouseManagement")}>
              {spouseStatus?.spouse ? (
                <p>{translate(language, "linkedSpouse")}: {spouseStatus.spouse.email}</p>
              ) : (
                <p>{translate(language, "noSpouse")}</p>
              )}
              <div className="stack-form">
                <input className="app-input" placeholder={translate(language, "spouseEmail")} value={spouseForm.email} onChange={(event) => setSpouseForm({ ...spouseForm, email: event.target.value })} />
                <input className="app-input" type="password" placeholder={translate(language, "spousePassword")} value={spouseForm.password} onChange={(event) => setSpouseForm({ ...spouseForm, password: event.target.value })} />
                <button className="app-button app-button--primary" type="button" onClick={createSpouse}>{translate(language, "createSpouse")}</button>
              </div>
            </SectionCard>
          ) : (
            <SectionCard title={translate(language, "spouseManagement")}>
              <p>{translate(language, "ownerOnlySpouse")}</p>
            </SectionCard>
          )}
        </div>
      )}
      {error ? <p className="error-text">{error}</p> : null}
    </section>
  );
}
