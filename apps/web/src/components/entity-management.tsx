"use client";

import Link from "next/link";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { EmptyState, ScreenHeader, SectionCard, StatusPill } from "@/components/ui-kit";

type EntityType = "projects" | "tasks";

type EntityRecord = {
  id: string;
  name?: string;
  title?: string;
  status: string;
  description?: string | null;
  notes?: string | null;
  deadline: string | null;
};

const defaultApiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";
const headers = (token: string): Record<string, string> => (token ? { Authorization: `Bearer ${token}` } : {});

export function EntityManagement({ entityType }: { entityType: EntityType }) {
  const [apiBase, setApiBase] = useState(defaultApiBase);
  const [token, setToken] = useState("");
  const [entities, setEntities] = useState<EntityRecord[]>([]);
  const [error, setError] = useState("");

  const entityLabel = entityType === "projects" ? "Project" : "Task";
  const endpoint = useMemo(() => `${apiBase}/${entityType}`, [apiBase, entityType]);

  const [form, setForm] = useState({ area_id: "", project_id: "", name: "", title: "", status: entityType === "projects" ? "active" : "todo" });

  async function loadEntities() {
    setError("");
    const response = await fetch(endpoint, { headers: headers(token), cache: "no-store" });
    if (!response.ok) {
      setError(`Could not load ${entityType}.`);
      return;
    }
    setEntities((await response.json()) as EntityRecord[]);
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload: Record<string, unknown> = { status: form.status };
    if (entityType === "projects") {
      payload.area_id = form.area_id;
      payload.name = form.name;
    } else {
      payload.project_id = form.project_id || null;
      payload.title = form.title;
    }

    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...headers(token) },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      setError(`Create failed (${response.status}).`);
      return;
    }

    await loadEntities();
  }

  useEffect(() => {
    const localToken = window.localStorage.getItem("orbis_access_token") ?? "";
    if (localToken) setToken(localToken);
  }, []);

  return (
    <section className="screen-flow">
      <ScreenHeader
        title={entityType === "projects" ? "Long Term Plan — Projects" : "Long Term Plan — Tasks"}
        subtitle={entityType === "projects" ? "Life area strategy" : "Project execution list"}
        actions={(
          <>
            <input className="app-input" value={apiBase} onChange={(event) => setApiBase(event.target.value)} placeholder="API base URL" />
            <input className="app-input" value={token} onChange={(event) => setToken(event.target.value)} placeholder="Access token" />
            <button className="app-button app-button--primary" type="button" onClick={loadEntities}>Refresh</button>
          </>
        )}
      />

      <div className="two-col">
        <SectionCard title={`${entityLabel} list`}>
          {entities.length ? (
            <ul className="stack-list">
              {entities.map((entity) => (
                <li key={entity.id} className="task-row">
                  <Link href={`/${entityType}/${entity.id}`}>{entity.name ?? entity.title ?? "Untitled"}</Link>
                  <StatusPill label={entity.status} />
                </li>
              ))}
            </ul>
          ) : <EmptyState message={`No ${entityType} found.`} />}
        </SectionCard>

        <SectionCard title={`Create ${entityLabel}`} tone="accent">
          <form className="stack-form" onSubmit={onSubmit}>
            {entityType === "projects" ? (
              <>
                <input className="app-input" placeholder="Area ID" required value={form.area_id} onChange={(event) => setForm({ ...form, area_id: event.target.value })} />
                <input className="app-input" placeholder="Project name" required value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />
              </>
            ) : (
              <>
                <input className="app-input" placeholder="Project ID" value={form.project_id} onChange={(event) => setForm({ ...form, project_id: event.target.value })} />
                <input className="app-input" placeholder="Task title" required value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} />
              </>
            )}
            <input className="app-input" placeholder="Status" value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value })} />
            <button className="app-button app-button--primary" type="submit">Create</button>
          </form>
        </SectionCard>
      </div>
      {error ? <p className="error-text">{error}</p> : null}
    </section>
  );
}

export function EntityDetailView({ entityType, id }: { entityType: EntityType; id: string }) {
  const [token, setToken] = useState("");
  const [entity, setEntity] = useState<EntityRecord | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    setToken(window.localStorage.getItem("orbis_access_token") ?? "");
  }, []);

  useEffect(() => {
    if (!token) return;
    const run = async () => {
      const response = await fetch(`${defaultApiBase}/${entityType}/${id}`, { headers: headers(token), cache: "no-store" });
      if (!response.ok) {
        setError(`Could not load ${entityType.slice(0, -1)} detail.`);
        return;
      }
      setEntity((await response.json()) as EntityRecord);
    };
    void run();
  }, [entityType, id, token]);

  return (
    <section className="screen-flow">
      <ScreenHeader title={entityType === "projects" ? "Project Detail" : "Task Detail"} subtitle="Detail panel content" />
      <SectionCard title="Overview">
        {entity ? (
          <div className="stack-list">
            <p className="lead-copy">{entity.name ?? entity.title}</p>
            <p>{entity.description ?? entity.notes ?? "No description."}</p>
            <p>Deadline: {entity.deadline ?? "None"}</p>
            <StatusPill label={entity.status} />
          </div>
        ) : <EmptyState message="Loading detail…" />}
      </SectionCard>
      {error ? <p className="error-text">{error}</p> : null}
    </section>
  );
}
