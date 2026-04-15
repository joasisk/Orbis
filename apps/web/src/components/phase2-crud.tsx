"use client";

import Link from "next/link";
import { FormEvent, useEffect, useMemo, useState } from "react";

import { TimeProgressArc } from "@/components/organic-chronos";

type EntityType = "projects" | "tasks";

type BaseEntity = {
  id: string;
  name?: string;
  title?: string;
  status: string;
  is_private: boolean;
  visibility_scope: string;
  priority: number | null;
  urgency: number | null;
  deadline: string | null;
  spouse_priority: number | null;
  spouse_urgency: number | null;
  spouse_deadline: string | null;
};

const defaultApiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";
const getAuthHeaders = (token: string): Record<string, string> => (token ? { Authorization: `Bearer ${token}` } : {});

const visibilityOptions = ["shared", "owner", "spouse"];

export function Phase2Crud({ entityType }: { entityType: EntityType }) {
  const [apiBase, setApiBase] = useState(defaultApiBase);
  const [token, setToken] = useState("");
  const [rows, setRows] = useState<BaseEntity[]>([]);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const entityLabel = entityType === "projects" ? "Project" : "Task";

  const [form, setForm] = useState({
    area_id: "",
    project_id: "",
    name: "",
    title: "",
    status: entityType === "projects" ? "active" : "todo",
    is_private: false,
    visibility_scope: "shared",
    priority: "",
    urgency: "",
    deadline: "",
    spouse_priority: "",
    spouse_urgency: "",
    spouse_deadline: "",
    description: "",
    notes: "",
  });

  const endpoint = useMemo(() => `${apiBase}/${entityType}`, [apiBase, entityType]);

  async function fetchRows() {
    setError("");
    try {
      const response = await fetch(endpoint, {
        headers: getAuthHeaders(token),
        cache: "no-store",
      });
      if (!response.ok) {
        throw new Error(`${response.status} ${response.statusText}`);
      }
      const payload = (await response.json()) as BaseEntity[];
      setRows(payload);
    } catch (err) {
      setError(`Could not load ${entityType}: ${err instanceof Error ? err.message : "unknown error"}`);
    }
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSuccess("");

    const payload: Record<string, unknown> = {
      status: form.status,
      is_private: form.is_private,
      visibility_scope: form.visibility_scope,
      priority: form.priority === "" ? null : Number(form.priority),
      urgency: form.urgency === "" ? null : Number(form.urgency),
      deadline: form.deadline === "" ? null : form.deadline,
      spouse_priority: form.spouse_priority === "" ? null : Number(form.spouse_priority),
      spouse_urgency: form.spouse_urgency === "" ? null : Number(form.spouse_urgency),
      spouse_deadline: form.spouse_deadline === "" ? null : form.spouse_deadline,
    };

    if (entityType === "projects") {
      payload.area_id = form.area_id;
      payload.name = form.name;
      payload.description = form.description;
    } else {
      payload.project_id = form.project_id || null;
      payload.title = form.title;
      payload.notes = form.notes;
    }

    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeaders(token),
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const text = await response.text();
      setError(`Create failed (${response.status}): ${text}`);
      return;
    }

    setSuccess(`${entityLabel} created.`);
    await fetchRows();
  }

  useEffect(() => {
    fetchRows();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <section className="shell-page">
      <div className="organic-grid">
          <article className="panel panel--focus focus-halo">
            <p className="stamp-label">{entityLabel} atelier</p>
            <h1 className="display-title">{entityLabel} list + create</h1>
            <p className="body-copy">
              Manage {entityType} with gentle tonal hierarchy and no hard visual fences.
            </p>

            <form onSubmit={onSubmit} className="field-grid" style={{ marginTop: "1rem" }}>
              <input
                className="input-field"
                value={apiBase}
                onChange={(e) => setApiBase(e.target.value)}
                placeholder="API base URL"
              />
              <input
                className="input-field"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                placeholder="Bearer token"
              />

              {entityType === "projects" ? (
                <>
                  <input
                    className="input-field"
                    required
                    placeholder="Area ID"
                    value={form.area_id}
                    onChange={(e) => setForm({ ...form, area_id: e.target.value })}
                  />
                  <input
                    className="input-field"
                    required
                    placeholder="Project name"
                    value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                  />
                  <textarea
                    className="text-area"
                    placeholder="Description"
                    value={form.description}
                    onChange={(e) => setForm({ ...form, description: e.target.value })}
                  />
                </>
              ) : (
                <>
                  <input
                    className="input-field"
                    placeholder="Project ID (optional)"
                    value={form.project_id}
                    onChange={(e) => setForm({ ...form, project_id: e.target.value })}
                  />
                  <input
                    className="input-field"
                    required
                    placeholder="Task title"
                    value={form.title}
                    onChange={(e) => setForm({ ...form, title: e.target.value })}
                  />
                  <textarea
                    className="text-area"
                    placeholder="Notes"
                    value={form.notes}
                    onChange={(e) => setForm({ ...form, notes: e.target.value })}
                  />
                </>
              )}

              <input
                className="input-field"
                placeholder="Status"
                value={form.status}
                onChange={(e) => setForm({ ...form, status: e.target.value })}
              />

              <div className="chip-row">
                {visibilityOptions.map((option) => (
                  <button
                    key={option}
                    type="button"
                    className={`chip ${form.visibility_scope === option ? "is-selected" : ""}`}
                    onClick={() => setForm({ ...form, visibility_scope: option })}
                  >
                    {option}
                  </button>
                ))}
                <button
                  type="button"
                  className={`chip ${form.is_private ? "is-selected" : ""}`}
                  onClick={() => setForm({ ...form, is_private: !form.is_private })}
                >
                  {form.is_private ? "Private" : "Shared"}
                </button>
              </div>

              <div className="row-3">
                <input
                  className="input-field"
                  placeholder="Priority"
                  value={form.priority}
                  onChange={(e) => setForm({ ...form, priority: e.target.value })}
                />
                <input
                  className="input-field"
                  placeholder="Urgency"
                  value={form.urgency}
                  onChange={(e) => setForm({ ...form, urgency: e.target.value })}
                />
                <input
                  className="input-field"
                  placeholder="Deadline ISO"
                  value={form.deadline}
                  onChange={(e) => setForm({ ...form, deadline: e.target.value })}
                />
              </div>

              <div className="row-3">
                <input
                  className="input-field"
                  placeholder="Spouse priority"
                  value={form.spouse_priority}
                  onChange={(e) => setForm({ ...form, spouse_priority: e.target.value })}
                />
                <input
                  className="input-field"
                  placeholder="Spouse urgency"
                  value={form.spouse_urgency}
                  onChange={(e) => setForm({ ...form, spouse_urgency: e.target.value })}
                />
                <input
                  className="input-field"
                  placeholder="Spouse deadline ISO"
                  value={form.spouse_deadline}
                  onChange={(e) => setForm({ ...form, spouse_deadline: e.target.value })}
                />
              </div>

              <div className="button-row">
                <button onClick={fetchRows} className="btn btn-secondary" type="button">
                  Refresh list
                </button>
                <button type="submit" className="btn btn-primary">
                  Create {entityLabel}
                </button>
              </div>
            </form>

            {error && <p className="message-error">{error}</p>}
            {success && <p className="message-success">{success}</p>}
          </article>

          <aside className="panel">
            <p className="stamp-label">Live cadence</p>
            <h2 className="headline">Focus arc</h2>
            <TimeProgressArc progress={0.35 + Math.min(rows.length, 10) * 0.05} />
            <ul className="list">
              {rows.map((row) => {
                const text = entityType === "projects" ? row.name : row.title;
                return (
                  <li key={row.id} className="list-item">
                    <Link href={`/${entityType}/${row.id}`}>
                      <strong>{text}</strong>
                    </Link>
                    <p className="body-copy">
                      {row.status} · priority {row.priority ?? "n/a"} · {row.visibility_scope}
                    </p>
                  </li>
                );
              })}
            </ul>
          </aside>
      </div>
    </section>
  );
}

export function EntityDetail({ entityType, id }: { entityType: EntityType; id: string }) {
  const [apiBase, setApiBase] = useState(defaultApiBase);
  const [token, setToken] = useState("");
  const [entity, setEntity] = useState<BaseEntity | null>(null);
  const [history, setHistory] = useState<Array<{ event_type: string; created_at: string }>>([]);
  const [error, setError] = useState("");

  async function refresh() {
    setError("");
    const headers = getAuthHeaders(token);

    const [entityRes, historyRes] = await Promise.all([
      fetch(`${apiBase}/${entityType}/${id}`, { headers, cache: "no-store" }),
      fetch(`${apiBase}/history/${entityType === "projects" ? "project" : "task"}/${id}`, { headers, cache: "no-store" }),
    ]);

    if (!entityRes.ok) {
      setError(`Could not load ${entityType} ${id}`);
      return;
    }

    setEntity((await entityRes.json()) as BaseEntity);
    setHistory(historyRes.ok ? ((await historyRes.json()) as Array<{ event_type: string; created_at: string }>) : []);
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <section className="shell-page">
      <div className="organic-grid">
          <article className="panel panel--focus">
            <p className="stamp-label">detail view</p>
            <h1 className="display-title">{entityType === "projects" ? "Project" : "Task"} detail</h1>
            <p className="body-copy">ID: {id}</p>

            <div className="field-grid" style={{ marginTop: "1rem" }}>
              <input
                className="input-field"
                value={apiBase}
                onChange={(e) => setApiBase(e.target.value)}
                placeholder="API base URL"
              />
              <input
                className="input-field"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                placeholder="Bearer token"
              />
            </div>

            <div className="button-row">
              <button type="button" onClick={refresh} className="btn btn-primary">
                Refresh detail
              </button>
            </div>

            {error && <p className="message-error">{error}</p>}
            {entity && <pre className="list-item">{JSON.stringify(entity, null, 2)}</pre>}
          </article>

          <aside className="panel">
            <p className="stamp-label">Version flow</p>
            <h2 className="headline">History</h2>
            <ul className="list">
              {history.map((entry, index) => (
                <li key={`${entry.created_at}-${index}`} className="list-item">
                  <strong>{entry.event_type}</strong>
                  <p className="body-copy">{entry.created_at}</p>
                </li>
              ))}
            </ul>
          </aside>
      </div>
    </section>
  );
}
