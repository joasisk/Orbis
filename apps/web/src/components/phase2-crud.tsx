"use client";

import Link from "next/link";
import { FormEvent, useEffect, useMemo, useState } from "react";

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
    <main style={{ fontFamily: "sans-serif", maxWidth: 900, margin: "2rem auto", lineHeight: 1.5 }}>
      <h1>{entityLabel} list + create</h1>
      <p>
        API base URL and bearer token are required for authenticated CRUD. This page implements Phase 2 list/detail
        workflows.
      </p>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 16 }}>
        <input value={apiBase} onChange={(e) => setApiBase(e.target.value)} placeholder="API base URL" />
        <input value={token} onChange={(e) => setToken(e.target.value)} placeholder="Bearer token" />
      </div>
      <button onClick={fetchRows} type="button">
        Refresh list
      </button>

      <form onSubmit={onSubmit} style={{ marginTop: 20, border: "1px solid #ddd", padding: 12, borderRadius: 8 }}>
        {entityType === "projects" ? (
          <>
            <input required placeholder="Area ID" value={form.area_id} onChange={(e) => setForm({ ...form, area_id: e.target.value })} />
            <input required placeholder="Project name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            <textarea placeholder="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </>
        ) : (
          <>
            <input placeholder="Project ID (optional)" value={form.project_id} onChange={(e) => setForm({ ...form, project_id: e.target.value })} />
            <input required placeholder="Task title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
            <textarea placeholder="Notes" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
          </>
        )}
        <input placeholder="Status" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })} />
        <label>
          <input
            type="checkbox"
            checked={form.is_private}
            onChange={(e) => setForm({ ...form, is_private: e.target.checked })}
          />
          Private
        </label>
        <input
          placeholder="Visibility (owner/spouse/shared)"
          value={form.visibility_scope}
          onChange={(e) => setForm({ ...form, visibility_scope: e.target.value })}
        />
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 8 }}>
          <input placeholder="Priority" value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })} />
          <input placeholder="Urgency" value={form.urgency} onChange={(e) => setForm({ ...form, urgency: e.target.value })} />
          <input placeholder="Deadline ISO" value={form.deadline} onChange={(e) => setForm({ ...form, deadline: e.target.value })} />
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 8 }}>
          <input
            placeholder="Spouse priority"
            value={form.spouse_priority}
            onChange={(e) => setForm({ ...form, spouse_priority: e.target.value })}
          />
          <input
            placeholder="Spouse urgency"
            value={form.spouse_urgency}
            onChange={(e) => setForm({ ...form, spouse_urgency: e.target.value })}
          />
          <input
            placeholder="Spouse deadline ISO"
            value={form.spouse_deadline}
            onChange={(e) => setForm({ ...form, spouse_deadline: e.target.value })}
          />
        </div>
        <button type="submit">Create {entityLabel}</button>
      </form>

      {error && <p style={{ color: "crimson" }}>{error}</p>}
      {success && <p style={{ color: "green" }}>{success}</p>}

      <ul>
        {rows.map((row) => {
          const text = entityType === "projects" ? row.name : row.title;
          return (
            <li key={row.id} style={{ marginBottom: 8 }}>
              <Link href={`/${entityType}/${row.id}`}>{text}</Link> - {row.status} - prio:{" "}
              {row.priority ?? "n/a"}
            </li>
          );
        })}
      </ul>
    </main>
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
    <main style={{ fontFamily: "sans-serif", maxWidth: 900, margin: "2rem auto", lineHeight: 1.5 }}>
      <h1>{entityType === "projects" ? "Project" : "Task"} detail</h1>
      <p>ID: {id}</p>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 16 }}>
        <input value={apiBase} onChange={(e) => setApiBase(e.target.value)} placeholder="API base URL" />
        <input value={token} onChange={(e) => setToken(e.target.value)} placeholder="Bearer token" />
      </div>
      <button type="button" onClick={refresh}>
        Refresh detail
      </button>
      {error && <p style={{ color: "crimson" }}>{error}</p>}
      {entity && <pre>{JSON.stringify(entity, null, 2)}</pre>}
      <h2>Version history</h2>
      <ul>
        {history.map((entry, index) => (
          <li key={`${entry.created_at}-${index}`}>
            {entry.event_type} at {entry.created_at}
          </li>
        ))}
      </ul>
    </main>
  );
}
