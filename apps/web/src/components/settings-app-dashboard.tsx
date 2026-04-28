"use client";

import { useEffect, useMemo, useState } from "react";
import { EmptyState, ScreenHeader, SectionCard } from "@/components/ui-kit";
import { DEFAULT_UI_LANGUAGE, translate, type UiLanguage } from "@/lib/i18n";

type UserRole = "owner" | "spouse";

type SettingsPayload = {
  calendar_connected: boolean;
  calendar_provider: string | null;
  notes_connected: boolean;
  notes_provider: string | null;
  ui_language: UiLanguage;
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

type AuditEventPayload = {
  id: string;
  actor_user_id: string | null;
  event_type: string;
  event_metadata: Record<string, unknown>;
  created_at: string;
};

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api/v1";
const headers = (token: string): Record<string, string> => (token ? { Authorization: `Bearer ${token}` } : {});

export function SettingsAppDashboard() {
  const [token, setToken] = useState("");
  const [form, setForm] = useState<SettingsPayload | null>(null);
  const [role, setRole] = useState<UserRole | null>(null);
  const [spouseStatus, setSpouseStatus] = useState<SpouseStatusPayload | null>(null);
  const [spouseForm, setSpouseForm] = useState({ email: "", password: "" });
  const [auditEvents, setAuditEvents] = useState<AuditEventPayload[]>([]);
  const [authOnly, setAuthOnly] = useState(false);
  const [error, setError] = useState("");
  const language = form?.ui_language ?? DEFAULT_UI_LANGUAGE;

  useEffect(() => {
    const localToken = window.localStorage.getItem("orbis_access_token") ?? "";
    if (localToken) setToken(localToken);
  }, []);

  async function loadAppSettings() {
    const [settingsResponse, meResponse] = await Promise.all([
      fetch(`${apiBase}/settings/me`, { headers: headers(token), cache: "no-store" }),
      fetch(`${apiBase}/users/me`, { headers: headers(token), cache: "no-store" }),
    ]);

    if (!settingsResponse.ok || !meResponse.ok) {
      setError(translate(language, "couldNotLoadSettings"));
      return;
    }

    setForm((await settingsResponse.json()) as SettingsPayload);
    const me = (await meResponse.json()) as MePayload;
    setRole(me.role);

    if (me.role === "owner") {
      const [spouseResponse, auditResponse] = await Promise.all([
        fetch(`${apiBase}/users/spouse`, { headers: headers(token), cache: "no-store" }),
        fetch(`${apiBase}/settings/audit-events`, { headers: headers(token), cache: "no-store" }),
      ]);
      if (spouseResponse.ok) {
        setSpouseStatus((await spouseResponse.json()) as SpouseStatusPayload);
      }
      if (auditResponse.ok) {
        setAuditEvents((await auditResponse.json()) as AuditEventPayload[]);
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
    await loadAppSettings();
  }

  const visibleAuditEvents = useMemo(
    () => (authOnly ? auditEvents.filter((event) => event.event_type.startsWith("auth.")) : auditEvents),
    [auditEvents, authOnly],
  );

  useEffect(() => {
    if (!token || form) return;
    void loadAppSettings();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  return (
    <section className="screen-flow">
      <ScreenHeader
        title={translate(language, "appSettingsTitle")}
        subtitle={translate(language, "appSettingsSubtitle")}
        actions={(
          <>
            <input className="app-input" value={token} onChange={(event) => setToken(event.target.value)} placeholder={translate(language, "accessToken")} />
            <button className="app-button app-button--primary" type="button" onClick={loadAppSettings}>{translate(language, "load")}</button>
          </>
        )}
      />

      {!form ? <EmptyState message={translate(language, "loadSettingsEmpty")} /> : (
        <div className="two-col">
          <SectionCard title={translate(language, "integrationsSettings")} className="settings-form-card">
            <label>
              <input type="checkbox" checked={form.calendar_connected} onChange={(event) => setForm({ ...form, calendar_connected: event.target.checked })} />
              {` ${translate(language, "calendarIntegration")} — ${translate(language, "connectedLabel")}`}
            </label>
            <input className="app-input" value={form.calendar_provider ?? ""} onChange={(event) => setForm({ ...form, calendar_provider: event.target.value || null })} placeholder={`${translate(language, "calendarIntegration")} ${translate(language, "providerLabel")}`} />
            <label>
              <input type="checkbox" checked={form.notes_connected} onChange={(event) => setForm({ ...form, notes_connected: event.target.checked })} />
              {` ${translate(language, "notesIntegration")} — ${translate(language, "connectedLabel")}`}
            </label>
            <input className="app-input" value={form.notes_provider ?? ""} onChange={(event) => setForm({ ...form, notes_provider: event.target.value || null })} placeholder={`${translate(language, "notesIntegration")} ${translate(language, "providerLabel")}`} />
            <button className="app-button app-button--primary" type="button" onClick={saveSettings}>{translate(language, "saveSettings")}</button>
          </SectionCard>

          <SectionCard title={translate(language, "auditSettings")} tone="accent" className="settings-form-card">
            <label>
              <input type="checkbox" checked={authOnly} onChange={(event) => setAuthOnly(event.target.checked)} /> {translate(language, "auditOnlyAuthEvents")}
            </label>
            <button className="app-button" type="button" onClick={loadAppSettings}>{translate(language, "loadAuditEvents")}</button>
          </SectionCard>

          <SectionCard title={translate(language, "auditViewer")}>
            {!visibleAuditEvents.length ? <EmptyState message={translate(language, "noAuditEvents")} /> : (
              <div className="stack-form">
                {visibleAuditEvents.map((event) => (
                  <article key={event.id} className="section-card">
                    <p><strong>{translate(language, "eventType")}:</strong> {event.event_type}</p>
                    <p><strong>{translate(language, "eventAt")}:</strong> {new Date(event.created_at).toLocaleString()}</p>
                    <p><strong>{translate(language, "eventMetadata")}:</strong> <code>{JSON.stringify(event.event_metadata)}</code></p>
                  </article>
                ))}
              </div>
            )}
          </SectionCard>

          {role === "owner" ? (
            <SectionCard title={translate(language, "spouseManagement")} className="settings-form-card">
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
