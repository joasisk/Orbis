"use client";

import Link from "next/link";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { EmptyState, ScreenHeader, SectionCard, StatusPill } from "@/components/ui-kit";

type EntityType = "areas" | "projects" | "tasks";
type UserRole = "owner" | "spouse";

type EntityRecord = {
  id: string;
  name?: string;
  title?: string;
  status?: string;
  description?: string | null;
  notes?: string | null;
  deadline: string | null;
  spouse_priority?: number | null;
  spouse_urgency?: number | null;
  spouse_deadline?: string | null;
  spouse_deadline_type?: "soft" | "hard" | null;
};

const defaultApiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";
const headers = (token: string): Record<string, string> => (token ? { Authorization: `Bearer ${token}` } : {});

export function EntityManagement({ entityType }: { entityType: EntityType }) {
  const [apiBase, setApiBase] = useState(defaultApiBase);
  const [token, setToken] = useState("");
  const [entities, setEntities] = useState<EntityRecord[]>([]);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const entityLabel = entityType === "projects" ? "Project" : entityType === "tasks" ? "Task" : "Area";
  const endpoint = useMemo(() => `${apiBase}/${entityType}`, [apiBase, entityType]);

  const [form, setForm] = useState({ area_id: "", project_id: "", name: "", title: "", status: entityType === "projects" ? "active" : "todo" });

  async function loadEntities() {
    if (!token || isLoading) return;
    setError("");
    setIsLoading(true);
    const response = await fetch(endpoint, { headers: headers(token), cache: "no-store" });
    setIsLoading(false);
    if (!response.ok) {
      setError(`Could not load ${entityType}.`);
      return;
    }
    setEntities((await response.json()) as EntityRecord[]);
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload: Record<string, unknown> = {};
    if (entityType === "projects") {
      payload.area_id = form.area_id;
      payload.name = form.name;
      payload.status = form.status;
    } else if (entityType === "tasks") {
      payload.project_id = form.project_id || null;
      payload.title = form.title;
      payload.status = form.status;
    } else {
      payload.name = form.name;
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

  useEffect(() => {
    if (!token || entities.length) return;
    void loadEntities();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const title = entityType === "projects" ? "Long Term Plan — Projects" : entityType === "tasks" ? "Long Term Plan — Tasks" : "Long Term Plan — Areas";
  const subtitle = entityType === "projects" ? "Life area strategy" : entityType === "tasks" ? "Project execution list" : "Life area catalog";

  return (
    <section className="screen-flow">
      <ScreenHeader
        title={title}
        subtitle={subtitle}
        actions={(
          <>
            <input className="app-input" value={apiBase} onChange={(event) => setApiBase(event.target.value)} placeholder="API base URL" />
            <input className="app-input" value={token} onChange={(event) => setToken(event.target.value)} placeholder="Access token" />
            <button className="app-button app-button--primary" type="button" onClick={loadEntities}>{isLoading ? "Loading..." : "Refresh"}</button>
          </>
        )}
      />

      <div className="two-col">
        <SectionCard title={`${entityLabel} list`}>
          {entities.length ? (
            <ul className="stack-list">
              {entities.map((entity) => (
                <li key={entity.id} className="task-row">
                  {entityType === "areas" ? (
                    <span>{entity.name ?? "Untitled"}</span>
                  ) : (
                    <Link href={`/${entityType}/${entity.id}`}>{entity.name ?? entity.title ?? "Untitled"}</Link>
                  )}
                  {entity.status ? <StatusPill label={entity.status} /> : null}
                </li>
              ))}
            </ul>
          ) : <EmptyState message={isLoading ? `Loading ${entityType}...` : `No ${entityType} found.`} />}
        </SectionCard>

        <SectionCard title={`Create ${entityLabel}`} tone="accent">
          <form className="stack-form" onSubmit={onSubmit}>
            {entityType === "projects" ? (
              <>
                <input className="app-input" placeholder="Area ID" required value={form.area_id} onChange={(event) => setForm({ ...form, area_id: event.target.value })} />
                <input className="app-input" placeholder="Project name" required value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />
                <input className="app-input" placeholder="Status" value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value })} />
              </>
            ) : entityType === "tasks" ? (
              <>
                <input className="app-input" placeholder="Project ID" value={form.project_id} onChange={(event) => setForm({ ...form, project_id: event.target.value })} />
                <input className="app-input" placeholder="Task title" required value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} />
                <input className="app-input" placeholder="Status" value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value })} />
              </>
            ) : (
              <input className="app-input" placeholder="Area name" required value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />
            )}
            <button className="app-button app-button--primary" type="submit">Create</button>
          </form>
        </SectionCard>
      </div>
      {error ? <p className="error-text">{error}</p> : null}
    </section>
  );
}

export function EntityDetailView({ entityType, id }: { entityType: Extract<EntityType, "projects" | "tasks">; id: string }) {
  const [token, setToken] = useState("");
  const [entity, setEntity] = useState<EntityRecord | null>(null);
  const [error, setError] = useState("");
  const [role, setRole] = useState<UserRole | null>(null);
  const [influenceDraft, setInfluenceDraft] = useState({ spouse_priority: "", spouse_urgency: "", spouse_deadline: "", spouse_deadline_type: "" });

  useEffect(() => {
    setToken(window.localStorage.getItem("orbis_access_token") ?? "");
  }, []);

  useEffect(() => {
    if (!token) return;
    const run = async () => {
      const [entityResponse, meResponse] = await Promise.all([
        fetch(`${defaultApiBase}/${entityType}/${id}`, { headers: headers(token), cache: "no-store" }),
        fetch(`${defaultApiBase}/users/me`, { headers: headers(token), cache: "no-store" }),
      ]);
      if (!entityResponse.ok) {
        setError(`Could not load ${entityType.slice(0, -1)} detail.`);
        return;
      }
      if (meResponse.ok) {
        const mePayload = (await meResponse.json()) as { role: UserRole };
        setRole(mePayload.role);
      }
      const loadedEntity = (await entityResponse.json()) as EntityRecord;
      setEntity(loadedEntity);
      setInfluenceDraft({
        spouse_priority: loadedEntity.spouse_priority?.toString() ?? "",
        spouse_urgency: loadedEntity.spouse_urgency?.toString() ?? "",
        spouse_deadline: loadedEntity.spouse_deadline ? loadedEntity.spouse_deadline.slice(0, 16) : "",
        spouse_deadline_type: loadedEntity.spouse_deadline_type ?? "",
      });
    };
    void run();
  }, [entityType, id, token]);

  async function saveSpouseInfluence() {
    if (!token || !entity || entityType !== "tasks") return;
    setError("");
    const payload: Record<string, unknown> = {
      spouse_priority: influenceDraft.spouse_priority ? Number(influenceDraft.spouse_priority) : null,
      spouse_urgency: influenceDraft.spouse_urgency ? Number(influenceDraft.spouse_urgency) : null,
      spouse_deadline: influenceDraft.spouse_deadline ? new Date(influenceDraft.spouse_deadline).toISOString() : null,
      spouse_deadline_type: influenceDraft.spouse_deadline_type || null,
    };
    const response = await fetch(`${defaultApiBase}/tasks/${entity.id}/spouse-influence`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", ...headers(token) },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      setError(`Could not save spouse influence (${response.status}).`);
      return;
    }
    setEntity((await response.json()) as EntityRecord);
  }

  return (
    <section className="screen-flow">
      <ScreenHeader title={entityType === "projects" ? "Project Detail" : "Task Detail"} subtitle="Detail panel content" />
      <SectionCard title="Overview">
        {entity ? (
          <div className="stack-list">
            <p className="lead-copy">{entity.name ?? entity.title}</p>
            <p>{entity.description ?? entity.notes ?? "No description."}</p>
            <p>Deadline: {entity.deadline ?? "None"}</p>
            {entity.status ? <StatusPill label={entity.status} /> : null}
          </div>
        ) : <EmptyState message="Loading detail…" />}
      </SectionCard>
      {entityType === "tasks" && entity ? (
        <SectionCard title="Spouse influence" tone="accent">
          {role === "spouse" ? (
            <div className="stack-form">
              <input className="app-input" type="number" min="0" max="10" value={influenceDraft.spouse_priority} onChange={(event) => setInfluenceDraft({ ...influenceDraft, spouse_priority: event.target.value })} placeholder="Spouse priority (0-10)" />
              <input className="app-input" type="number" min="0" max="10" value={influenceDraft.spouse_urgency} onChange={(event) => setInfluenceDraft({ ...influenceDraft, spouse_urgency: event.target.value })} placeholder="Spouse urgency (0-10)" />
              <input className="app-input" type="datetime-local" value={influenceDraft.spouse_deadline} onChange={(event) => setInfluenceDraft({ ...influenceDraft, spouse_deadline: event.target.value })} />
              <select className="app-input" value={influenceDraft.spouse_deadline_type} onChange={(event) => setInfluenceDraft({ ...influenceDraft, spouse_deadline_type: event.target.value })}>
                <option value="">No deadline type</option>
                <option value="soft">Soft</option>
                <option value="hard">Hard</option>
              </select>
              <button className="app-button app-button--primary" type="button" onClick={saveSpouseInfluence}>Save spouse influence</button>
            </div>
          ) : (
            <div className="stack-list">
              <p>Priority: {entity.spouse_priority ?? "not set"}</p>
              <p>Urgency: {entity.spouse_urgency ?? "not set"}</p>
              <p>Deadline: {entity.spouse_deadline ?? "not set"}</p>
              <p>Deadline type: {entity.spouse_deadline_type ?? "not set"}</p>
            </div>
          )}
        </SectionCard>
      ) : null}
      {error ? <p className="error-text">{error}</p> : null}
    </section>
  );
}
