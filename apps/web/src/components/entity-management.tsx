"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { EmptyState, ScreenHeader, SectionCard, StatusPill } from "@/components/ui-kit";

type UserRole = "owner" | "spouse";
type DeadlineType = "soft" | "hard";
type VisibilityScope = "owner" | "spouse" | "shared";

type AreaRecord = {
  id: string;
  name: string;
  description: string | null;
};

type ProjectRecord = {
  id: string;
  area_id: string;
  name: string;
  description: string | null;
  status: string;
  priority: number | null;
  urgency: number | null;
  deadline: string | null;
  deadline_type: DeadlineType | null;
  spouse_priority: number | null;
  spouse_urgency: number | null;
  spouse_deadline: string | null;
  spouse_deadline_type: DeadlineType | null;
  is_private: boolean;
  visibility_scope: VisibilityScope;
};

type TaskRecord = {
  id: string;
  project_id: string | null;
  title: string;
  notes: string | null;
  status: string;
  priority: number | null;
  urgency: number | null;
  deadline: string | null;
  deadline_type: DeadlineType | null;
  spouse_priority: number | null;
  spouse_urgency: number | null;
  spouse_deadline: string | null;
  spouse_deadline_type: DeadlineType | null;
  is_private: boolean;
  visibility_scope: VisibilityScope;
};

type TaskModalEventDetail = {
  mode: "create" | "edit";
  taskId?: string;
  presetAreaId?: string;
  presetProjectId?: string;
};

const defaultApiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";
const headers = (token: string): Record<string, string> => (token ? { Authorization: `Bearer ${token}` } : {});

const TASK_MODAL_EVENT = "orbis:task-modal";
const TASK_SAVED_EVENT = "orbis:task-saved";

const EMPTY_PRIORITY = "";
const EMPTY_DEADLINE = "";

function toDateTimeInput(value: string | null): string {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  const offset = date.getTimezoneOffset();
  const localDate = new Date(date.getTime() - offset * 60000);
  return localDate.toISOString().slice(0, 16);
}

function parseNumeric(value: string): number | null {
  if (!value.trim()) return null;
  const parsed = Number(value);
  return Number.isNaN(parsed) ? null : parsed;
}

function parseDateTime(value: string): string | null {
  if (!value.trim()) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return date.toISOString();
}

export function openTaskModal(detail: TaskModalEventDetail) {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new CustomEvent<TaskModalEventDetail>(TASK_MODAL_EVENT, { detail }));
}

export function TaskModalHost() {
  const [token, setToken] = useState("");
  const [areas, setAreas] = useState<AreaRecord[]>([]);
  const [projects, setProjects] = useState<ProjectRecord[]>([]);
  const [openState, setOpenState] = useState<TaskModalEventDetail | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [dirty, setDirty] = useState(false);

  const [form, setForm] = useState({
    areaId: "",
    projectId: "",
    title: "",
    notes: "",
    status: "todo",
    priority: EMPTY_PRIORITY,
    urgency: EMPTY_PRIORITY,
    deadline: EMPTY_DEADLINE,
    deadlineType: "",
    isPrivate: false,
    visibilityScope: "shared" as VisibilityScope,
    spousePriority: EMPTY_PRIORITY,
    spouseUrgency: EMPTY_PRIORITY,
    spouseDeadline: EMPTY_DEADLINE,
    spouseDeadlineType: "",
  });

  const open = Boolean(openState);

  useEffect(() => {
    setToken(window.localStorage.getItem("orbis_access_token") ?? "");
  }, []);

  useEffect(() => {
    const onOpen = (event: Event) => {
      const customEvent = event as CustomEvent<TaskModalEventDetail>;
      setOpenState(customEvent.detail);
      setError("");
      setDirty(false);
    };
    window.addEventListener(TASK_MODAL_EVENT, onOpen as EventListener);
    return () => window.removeEventListener(TASK_MODAL_EVENT, onOpen as EventListener);
  }, []);

  useEffect(() => {
    if (!open || !token) return;

    const load = async () => {
      setLoading(true);
      setError("");

      const [areasResponse, projectsResponse] = await Promise.all([
        fetch(`${defaultApiBase}/areas`, { headers: headers(token), cache: "no-store" }),
        fetch(`${defaultApiBase}/projects`, { headers: headers(token), cache: "no-store" }),
      ]);

      if (!areasResponse.ok || !projectsResponse.ok) {
        setError("Could not load area/project options.");
        setLoading(false);
        return;
      }

      const loadedAreas = (await areasResponse.json()) as AreaRecord[];
      const loadedProjects = (await projectsResponse.json()) as ProjectRecord[];
      setAreas(loadedAreas);
      setProjects(loadedProjects);

      const nextForm = {
        areaId: openState?.presetAreaId ?? "",
        projectId: openState?.presetProjectId ?? "",
        title: "",
        notes: "",
        status: "todo",
        priority: EMPTY_PRIORITY,
        urgency: EMPTY_PRIORITY,
        deadline: EMPTY_DEADLINE,
        deadlineType: "",
        isPrivate: false,
        visibilityScope: "shared" as VisibilityScope,
        spousePriority: EMPTY_PRIORITY,
        spouseUrgency: EMPTY_PRIORITY,
        spouseDeadline: EMPTY_DEADLINE,
        spouseDeadlineType: "",
      };

      if (openState?.mode === "edit" && openState.taskId) {
        const taskResponse = await fetch(`${defaultApiBase}/tasks/${openState.taskId}`, { headers: headers(token), cache: "no-store" });
        if (!taskResponse.ok) {
          setError("Could not load task detail.");
          setLoading(false);
          return;
        }
        const task = (await taskResponse.json()) as TaskRecord;
        const taskProject = loadedProjects.find((item) => item.id === task.project_id);
        nextForm.areaId = taskProject?.area_id ?? nextForm.areaId;
        nextForm.projectId = task.project_id ?? "";
        nextForm.title = task.title;
        nextForm.notes = task.notes ?? "";
        nextForm.status = task.status;
        nextForm.priority = task.priority?.toString() ?? EMPTY_PRIORITY;
        nextForm.urgency = task.urgency?.toString() ?? EMPTY_PRIORITY;
        nextForm.deadline = toDateTimeInput(task.deadline);
        nextForm.deadlineType = task.deadline_type ?? "";
        nextForm.isPrivate = task.is_private;
        nextForm.visibilityScope = task.visibility_scope;
        nextForm.spousePriority = task.spouse_priority?.toString() ?? EMPTY_PRIORITY;
        nextForm.spouseUrgency = task.spouse_urgency?.toString() ?? EMPTY_PRIORITY;
        nextForm.spouseDeadline = toDateTimeInput(task.spouse_deadline);
        nextForm.spouseDeadlineType = task.spouse_deadline_type ?? "";
      }

      setForm(nextForm);
      setLoading(false);
    };

    void load();
  }, [open, openState, token]);

  useEffect(() => {
    if (!open) return;
    const previous = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    const onEscape = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return;
      if (dirty && !window.confirm("Discard task changes?")) return;
      setOpenState(null);
    };

    window.addEventListener("keydown", onEscape);
    return () => {
      document.body.style.overflow = previous;
      window.removeEventListener("keydown", onEscape);
    };
  }, [dirty, open]);

  const modalProjects = useMemo(() => projects.filter((project) => project.area_id === form.areaId), [projects, form.areaId]);

  function closeModal() {
    if (dirty && !window.confirm("Discard task changes?")) return;
    setOpenState(null);
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !openState) return;
    setError("");

    const payload = {
      project_id: form.projectId || null,
      title: form.title,
      notes: form.notes || null,
      status: form.status,
      priority: parseNumeric(form.priority),
      urgency: parseNumeric(form.urgency),
      deadline: parseDateTime(form.deadline),
      deadline_type: (form.deadlineType || null) as DeadlineType | null,
      is_private: form.isPrivate,
      visibility_scope: (form.isPrivate ? "owner" : form.visibilityScope) as VisibilityScope,
      spouse_priority: parseNumeric(form.spousePriority),
      spouse_urgency: parseNumeric(form.spouseUrgency),
      spouse_deadline: parseDateTime(form.spouseDeadline),
      spouse_deadline_type: (form.spouseDeadlineType || null) as DeadlineType | null,
    };

    const method = openState.mode === "edit" ? "PATCH" : "POST";
    const endpoint = openState.mode === "edit" ? `${defaultApiBase}/tasks/${openState.taskId}` : `${defaultApiBase}/tasks`;

    const response = await fetch(endpoint, {
      method,
      headers: { "Content-Type": "application/json", ...headers(token) },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      setError(`Task save failed (${response.status}).`);
      return;
    }

    setOpenState(null);
    setDirty(false);
    window.dispatchEvent(new Event(TASK_SAVED_EVENT));
  }

  if (!open) return null;

  return (
    <div className="modal-backdrop" role="presentation" onClick={closeModal}>
      <div className="modal-shell" role="dialog" aria-modal="true" aria-label={openState?.mode === "edit" ? "Edit task" : "Add task"} onClick={(event) => event.stopPropagation()}>
        <h2>{openState?.mode === "edit" ? "Edit task" : "Add task"}</h2>
        {loading ? <p>Loading…</p> : null}
        <form className="stack-form" onSubmit={onSubmit}>
          <input className="app-input" placeholder="Title" required value={form.title} onChange={(event) => { setForm({ ...form, title: event.target.value }); setDirty(true); }} />
          <select className="app-input" value={form.areaId} onChange={(event) => { setForm({ ...form, areaId: event.target.value, projectId: "" }); setDirty(true); }}>
            <option value="">Select life area</option>
            {areas.map((area) => <option key={area.id} value={area.id}>{area.name}</option>)}
          </select>
          <select className="app-input" value={form.projectId} onChange={(event) => { setForm({ ...form, projectId: event.target.value }); setDirty(true); }} disabled={!form.areaId}>
            <option value="">No project</option>
            {modalProjects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}
          </select>
          <textarea className="app-input app-input--text" placeholder="Notes" value={form.notes} onChange={(event) => { setForm({ ...form, notes: event.target.value }); setDirty(true); }} />
          <input className="app-input" placeholder="Status" value={form.status} onChange={(event) => { setForm({ ...form, status: event.target.value }); setDirty(true); }} />
          <input className="app-input" type="number" min="0" max="10" placeholder="Priority" value={form.priority} onChange={(event) => { setForm({ ...form, priority: event.target.value }); setDirty(true); }} />
          <input className="app-input" type="number" min="0" max="10" placeholder="Urgency" value={form.urgency} onChange={(event) => { setForm({ ...form, urgency: event.target.value }); setDirty(true); }} />
          <input className="app-input" type="datetime-local" value={form.deadline} onChange={(event) => { setForm({ ...form, deadline: event.target.value }); setDirty(true); }} />
          <select className="app-input" value={form.deadlineType} onChange={(event) => { setForm({ ...form, deadlineType: event.target.value }); setDirty(true); }}>
            <option value="">No deadline type</option>
            <option value="soft">Soft</option>
            <option value="hard">Hard</option>
          </select>
          <label className="app-check">
            <input type="checkbox" checked={form.isPrivate} onChange={(event) => { setForm({ ...form, isPrivate: event.target.checked, visibilityScope: event.target.checked ? "owner" : form.visibilityScope }); setDirty(true); }} />
            Private task
          </label>
          <select className="app-input" value={form.visibilityScope} onChange={(event) => { setForm({ ...form, visibilityScope: event.target.value as VisibilityScope }); setDirty(true); }} disabled={form.isPrivate}>
            <option value="owner">Owner</option>
            <option value="spouse">Spouse</option>
            <option value="shared">Shared</option>
          </select>
          <input className="app-input" type="number" min="0" max="10" placeholder="Spouse priority" value={form.spousePriority} onChange={(event) => { setForm({ ...form, spousePriority: event.target.value }); setDirty(true); }} />
          <input className="app-input" type="number" min="0" max="10" placeholder="Spouse urgency" value={form.spouseUrgency} onChange={(event) => { setForm({ ...form, spouseUrgency: event.target.value }); setDirty(true); }} />
          <input className="app-input" type="datetime-local" value={form.spouseDeadline} onChange={(event) => { setForm({ ...form, spouseDeadline: event.target.value }); setDirty(true); }} />
          <select className="app-input" value={form.spouseDeadlineType} onChange={(event) => { setForm({ ...form, spouseDeadlineType: event.target.value }); setDirty(true); }}>
            <option value="">No spouse deadline type</option>
            <option value="soft">Soft</option>
            <option value="hard">Hard</option>
          </select>
          <div className="modal-actions">
            <button className="app-button" type="button" onClick={closeModal}>Cancel</button>
            <button className="app-button app-button--primary" type="submit">{openState?.mode === "edit" ? "Save" : "Create"}</button>
          </div>
        </form>
        {error ? <p className="error-text">{error}</p> : null}
      </div>
    </div>
  );
}

export function ProjectsWorkspace() {
  const [token, setToken] = useState("");
  const [areas, setAreas] = useState<AreaRecord[]>([]);
  const [projects, setProjects] = useState<ProjectRecord[]>([]);
  const [selectedAreaId, setSelectedAreaId] = useState("");
  const [error, setError] = useState("");

  const [areaModal, setAreaModal] = useState<{ mode: "create" | "edit"; entity?: AreaRecord } | null>(null);
  const [areaForm, setAreaForm] = useState({ name: "", description: "" });

  const [projectModal, setProjectModal] = useState<{ mode: "create" | "edit"; entity?: ProjectRecord } | null>(null);
  const [projectForm, setProjectForm] = useState({
    area_id: "",
    name: "",
    description: "",
    status: "active",
    is_private: false,
    visibility_scope: "shared" as VisibilityScope,
    priority: EMPTY_PRIORITY,
    urgency: EMPTY_PRIORITY,
    deadline: EMPTY_DEADLINE,
    deadline_type: "",
    spouse_priority: EMPTY_PRIORITY,
    spouse_urgency: EMPTY_PRIORITY,
    spouse_deadline: EMPTY_DEADLINE,
    spouse_deadline_type: "",
  });

  useEffect(() => {
    setToken(window.localStorage.getItem("orbis_access_token") ?? "");
  }, []);

  const load = useCallback(async () => {
    if (!token) return;
    setError("");
    const [areasResponse, projectsResponse] = await Promise.all([
      fetch(`${defaultApiBase}/areas`, { headers: headers(token), cache: "no-store" }),
      fetch(`${defaultApiBase}/projects`, { headers: headers(token), cache: "no-store" }),
    ]);
    if (!areasResponse.ok || !projectsResponse.ok) {
      setError("Could not load long term plan data.");
      return;
    }
    setAreas((await areasResponse.json()) as AreaRecord[]);
    setProjects((await projectsResponse.json()) as ProjectRecord[]);
  }, [token]);

  useEffect(() => {
    if (!token) return;
    void load();
  }, [load, token]);

  const visibleProjects = useMemo(() => {
    if (!selectedAreaId) return projects;
    return projects.filter((project) => project.area_id === selectedAreaId);
  }, [projects, selectedAreaId]);

  async function submitArea(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !areaModal) return;
    const endpoint = areaModal.mode === "edit" ? `${defaultApiBase}/areas/${areaModal.entity?.id}` : `${defaultApiBase}/areas`;
    const method = areaModal.mode === "edit" ? "PATCH" : "POST";
    const response = await fetch(endpoint, {
      method,
      headers: { "Content-Type": "application/json", ...headers(token) },
      body: JSON.stringify({ name: areaForm.name, description: areaForm.description || null }),
    });
    if (!response.ok) {
      setError(`Could not save area (${response.status}).`);
      return;
    }
    setAreaModal(null);
    await load();
  }

  async function submitProject(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !projectModal) return;
    const payload = {
      area_id: projectForm.area_id,
      name: projectForm.name,
      description: projectForm.description || null,
      status: projectForm.status,
      is_private: projectForm.is_private,
      visibility_scope: (projectForm.is_private ? "owner" : projectForm.visibility_scope) as VisibilityScope,
      priority: parseNumeric(projectForm.priority),
      urgency: parseNumeric(projectForm.urgency),
      deadline: parseDateTime(projectForm.deadline),
      deadline_type: (projectForm.deadline_type || null) as DeadlineType | null,
      spouse_priority: parseNumeric(projectForm.spouse_priority),
      spouse_urgency: parseNumeric(projectForm.spouse_urgency),
      spouse_deadline: parseDateTime(projectForm.spouse_deadline),
      spouse_deadline_type: (projectForm.spouse_deadline_type || null) as DeadlineType | null,
    };
    const endpoint = projectModal.mode === "edit" ? `${defaultApiBase}/projects/${projectModal.entity?.id}` : `${defaultApiBase}/projects`;
    const method = projectModal.mode === "edit" ? "PATCH" : "POST";
    const response = await fetch(endpoint, {
      method,
      headers: { "Content-Type": "application/json", ...headers(token) },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      setError(`Could not save project (${response.status}).`);
      return;
    }
    setProjectModal(null);
    await load();
  }

  function openAreaCreate() {
    setAreaForm({ name: "", description: "" });
    setAreaModal({ mode: "create" });
  }

  function openAreaEdit(area: AreaRecord) {
    setAreaForm({ name: area.name, description: area.description ?? "" });
    setAreaModal({ mode: "edit", entity: area });
  }

  function openProjectCreate() {
    setProjectForm({
      area_id: selectedAreaId || areas[0]?.id || "",
      name: "",
      description: "",
      status: "active",
      is_private: false,
      visibility_scope: "shared",
      priority: EMPTY_PRIORITY,
      urgency: EMPTY_PRIORITY,
      deadline: EMPTY_DEADLINE,
      deadline_type: "",
      spouse_priority: EMPTY_PRIORITY,
      spouse_urgency: EMPTY_PRIORITY,
      spouse_deadline: EMPTY_DEADLINE,
      spouse_deadline_type: "",
    });
    setProjectModal({ mode: "create" });
  }

  function openProjectEdit(project: ProjectRecord) {
    setProjectForm({
      area_id: project.area_id,
      name: project.name,
      description: project.description ?? "",
      status: project.status,
      is_private: project.is_private,
      visibility_scope: project.visibility_scope,
      priority: project.priority?.toString() ?? EMPTY_PRIORITY,
      urgency: project.urgency?.toString() ?? EMPTY_PRIORITY,
      deadline: toDateTimeInput(project.deadline),
      deadline_type: project.deadline_type ?? "",
      spouse_priority: project.spouse_priority?.toString() ?? EMPTY_PRIORITY,
      spouse_urgency: project.spouse_urgency?.toString() ?? EMPTY_PRIORITY,
      spouse_deadline: toDateTimeInput(project.spouse_deadline),
      spouse_deadline_type: project.spouse_deadline_type ?? "",
    });
    setProjectModal({ mode: "edit", entity: project });
  }

  return (
    <section className="screen-flow">
      <ScreenHeader title="Long Term Plan" subtitle="Areas and projects workspace" />
      <div className="two-col">
        <SectionCard title="Life areas">
          <div className="inline-actions">
            <button className="app-button app-button--primary" type="button" onClick={openAreaCreate}>Add life area</button>
            {selectedAreaId ? <button className="app-button" type="button" onClick={() => setSelectedAreaId("")}>Clear filter</button> : null}
          </div>
          {areas.length ? (
            <ul className="stack-list">
              {areas.map((area) => (
                <li key={area.id} className={`task-row${selectedAreaId === area.id ? " task-row--selected" : ""}`}>
                  <button type="button" className="text-button" onClick={() => setSelectedAreaId(area.id)}>{area.name}</button>
                  <button className="app-button" type="button" onClick={() => openAreaEdit(area)}>Edit</button>
                </li>
              ))}
            </ul>
          ) : <EmptyState message="No areas yet. Create your first life area." />}
        </SectionCard>

        <SectionCard title="Projects">
          <div className="inline-actions">
            <button className="app-button app-button--primary" type="button" onClick={openProjectCreate}>Add project</button>
          </div>
          {visibleProjects.length ? (
            <ul className="stack-list">
              {visibleProjects.map((project) => (
                <li key={project.id} className="task-row">
                  <div>
                    <p className="lead-copy">{project.name}</p>
                    <p className="footnote">{project.description || "No description"}</p>
                  </div>
                  <div className="inline-actions">
                    <StatusPill label={project.status} />
                    <button className="app-button" type="button" onClick={() => openProjectEdit(project)}>Edit</button>
                  </div>
                </li>
              ))}
            </ul>
          ) : <EmptyState message={selectedAreaId ? "No projects in this area yet." : "No projects found."} />}
        </SectionCard>
      </div>

      {areaModal ? (
        <div className="modal-backdrop" role="presentation" onClick={() => setAreaModal(null)}>
          <div className="modal-shell" role="dialog" aria-modal="true" onClick={(event) => event.stopPropagation()}>
            <h2>{areaModal.mode === "edit" ? "Edit life area" : "Add life area"}</h2>
            <form className="stack-form" onSubmit={submitArea}>
              <input className="app-input" required placeholder="Name" value={areaForm.name} onChange={(event) => setAreaForm({ ...areaForm, name: event.target.value })} />
              <textarea className="app-input app-input--text" placeholder="Description" value={areaForm.description} onChange={(event) => setAreaForm({ ...areaForm, description: event.target.value })} />
              <div className="modal-actions">
                <button className="app-button" type="button" onClick={() => setAreaModal(null)}>Cancel</button>
                <button className="app-button app-button--primary" type="submit">{areaModal.mode === "edit" ? "Save" : "Create"}</button>
              </div>
            </form>
          </div>
        </div>
      ) : null}

      {projectModal ? (
        <div className="modal-backdrop" role="presentation" onClick={() => setProjectModal(null)}>
          <div className="modal-shell" role="dialog" aria-modal="true" onClick={(event) => event.stopPropagation()}>
            <h2>{projectModal.mode === "edit" ? "Edit project" : "Add project"}</h2>
            <form className="stack-form" onSubmit={submitProject}>
              <select className="app-input" required value={projectForm.area_id} onChange={(event) => setProjectForm({ ...projectForm, area_id: event.target.value })}>
                <option value="">Select life area</option>
                {areas.map((area) => <option key={area.id} value={area.id}>{area.name}</option>)}
              </select>
              <input className="app-input" required placeholder="Name" value={projectForm.name} onChange={(event) => setProjectForm({ ...projectForm, name: event.target.value })} />
              <textarea className="app-input app-input--text" placeholder="Description" value={projectForm.description} onChange={(event) => setProjectForm({ ...projectForm, description: event.target.value })} />
              <input className="app-input" placeholder="Status" value={projectForm.status} onChange={(event) => setProjectForm({ ...projectForm, status: event.target.value })} />
              <input className="app-input" type="number" min="0" max="10" placeholder="Priority" value={projectForm.priority} onChange={(event) => setProjectForm({ ...projectForm, priority: event.target.value })} />
              <input className="app-input" type="number" min="0" max="10" placeholder="Urgency" value={projectForm.urgency} onChange={(event) => setProjectForm({ ...projectForm, urgency: event.target.value })} />
              <input className="app-input" type="datetime-local" value={projectForm.deadline} onChange={(event) => setProjectForm({ ...projectForm, deadline: event.target.value })} />
              <select className="app-input" value={projectForm.deadline_type} onChange={(event) => setProjectForm({ ...projectForm, deadline_type: event.target.value })}>
                <option value="">No deadline type</option>
                <option value="soft">Soft</option>
                <option value="hard">Hard</option>
              </select>
              <label className="app-check">
                <input type="checkbox" checked={projectForm.is_private} onChange={(event) => setProjectForm({ ...projectForm, is_private: event.target.checked, visibility_scope: event.target.checked ? "owner" : projectForm.visibility_scope })} />
                Private project
              </label>
              <select className="app-input" disabled={projectForm.is_private} value={projectForm.visibility_scope} onChange={(event) => setProjectForm({ ...projectForm, visibility_scope: event.target.value as VisibilityScope })}>
                <option value="owner">Owner</option>
                <option value="spouse">Spouse</option>
                <option value="shared">Shared</option>
              </select>
              <input className="app-input" type="number" min="0" max="10" placeholder="Spouse priority" value={projectForm.spouse_priority} onChange={(event) => setProjectForm({ ...projectForm, spouse_priority: event.target.value })} />
              <input className="app-input" type="number" min="0" max="10" placeholder="Spouse urgency" value={projectForm.spouse_urgency} onChange={(event) => setProjectForm({ ...projectForm, spouse_urgency: event.target.value })} />
              <input className="app-input" type="datetime-local" value={projectForm.spouse_deadline} onChange={(event) => setProjectForm({ ...projectForm, spouse_deadline: event.target.value })} />
              <select className="app-input" value={projectForm.spouse_deadline_type} onChange={(event) => setProjectForm({ ...projectForm, spouse_deadline_type: event.target.value })}>
                <option value="">No spouse deadline type</option>
                <option value="soft">Soft</option>
                <option value="hard">Hard</option>
              </select>
              <div className="modal-actions">
                <button className="app-button" type="button" onClick={() => setProjectModal(null)}>Cancel</button>
                <button className="app-button app-button--primary" type="submit">{projectModal.mode === "edit" ? "Save" : "Create"}</button>
              </div>
            </form>
          </div>
        </div>
      ) : null}

      {error ? <p className="error-text">{error}</p> : null}
    </section>
  );
}

export function TasksWorkspace() {
  const [token, setToken] = useState("");
  const [areas, setAreas] = useState<AreaRecord[]>([]);
  const [projects, setProjects] = useState<ProjectRecord[]>([]);
  const [tasks, setTasks] = useState<TaskRecord[]>([]);
  const [error, setError] = useState("");

  const [filters, setFilters] = useState({
    areaId: "",
    projectId: "",
    status: "",
    priority: "",
    urgency: "",
    visibilityScope: "",
    privacy: "",
    deadlineBucket: "",
  });

  useEffect(() => {
    setToken(window.localStorage.getItem("orbis_access_token") ?? "");
  }, []);

  const load = useCallback(async () => {
    if (!token) return;
    setError("");
    const [areasResponse, projectsResponse, tasksResponse] = await Promise.all([
      fetch(`${defaultApiBase}/areas`, { headers: headers(token), cache: "no-store" }),
      fetch(`${defaultApiBase}/projects`, { headers: headers(token), cache: "no-store" }),
      fetch(`${defaultApiBase}/tasks`, { headers: headers(token), cache: "no-store" }),
    ]);

    if (!areasResponse.ok || !projectsResponse.ok || !tasksResponse.ok) {
      setError("Could not load tasks.");
      return;
    }

    setAreas((await areasResponse.json()) as AreaRecord[]);
    setProjects((await projectsResponse.json()) as ProjectRecord[]);
    setTasks((await tasksResponse.json()) as TaskRecord[]);
  }, [token]);

  useEffect(() => {
    if (!token) return;
    void load();
  }, [load, token]);

  useEffect(() => {
    const handler = () => { void load(); };
    window.addEventListener(TASK_SAVED_EVENT, handler);
    return () => window.removeEventListener(TASK_SAVED_EVENT, handler);
  }, [load]);

  const projectById = useMemo(() => new Map(projects.map((project) => [project.id, project])), [projects]);
  const projectsForArea = useMemo(() => projects.filter((project) => !filters.areaId || project.area_id === filters.areaId), [filters.areaId, projects]);

  const filteredTasks = useMemo(() => {
    const now = new Date();
    const soonCutoff = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);

    return tasks.filter((task) => {
      const project = task.project_id ? projectById.get(task.project_id) : undefined;
      const taskAreaId = project?.area_id ?? "";

      if (filters.areaId && taskAreaId !== filters.areaId) return false;
      if (filters.projectId && task.project_id !== filters.projectId) return false;
      if (filters.status && task.status !== filters.status) return false;
      if (filters.priority && String(task.priority ?? "") !== filters.priority) return false;
      if (filters.urgency && String(task.urgency ?? "") !== filters.urgency) return false;
      if (filters.visibilityScope && task.visibility_scope !== filters.visibilityScope) return false;
      if (filters.privacy === "private" && !task.is_private) return false;
      if (filters.privacy === "public" && task.is_private) return false;

      if (filters.deadlineBucket) {
        if (!task.deadline) return filters.deadlineBucket === "none";
        const deadline = new Date(task.deadline);
        if (filters.deadlineBucket === "has") return true;
        if (filters.deadlineBucket === "overdue") return deadline < now;
        if (filters.deadlineBucket === "soon") return deadline >= now && deadline <= soonCutoff;
      }

      return true;
    });
  }, [filters, projectById, tasks]);

  return (
    <section className="screen-flow">
      <ScreenHeader
        title="Tasks"
        subtitle="Task management"
        actions={<button className="app-button app-button--primary" type="button" onClick={() => openTaskModal({ mode: "create", presetAreaId: filters.areaId || undefined, presetProjectId: filters.projectId || undefined })}>Add task</button>}
      />

      <SectionCard title="Filters">
        <div className="filter-grid">
          <select className="app-input" value={filters.areaId} onChange={(event) => setFilters({ ...filters, areaId: event.target.value, projectId: "" })}>
            <option value="">All life areas</option>
            {areas.map((area) => <option key={area.id} value={area.id}>{area.name}</option>)}
          </select>
          <select className="app-input" value={filters.projectId} onChange={(event) => setFilters({ ...filters, projectId: event.target.value })}>
            <option value="">All projects</option>
            {projectsForArea.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}
          </select>
          <input className="app-input" placeholder="Status" value={filters.status} onChange={(event) => setFilters({ ...filters, status: event.target.value })} />
          <input className="app-input" type="number" min="0" max="10" placeholder="Priority" value={filters.priority} onChange={(event) => setFilters({ ...filters, priority: event.target.value })} />
          <input className="app-input" type="number" min="0" max="10" placeholder="Urgency" value={filters.urgency} onChange={(event) => setFilters({ ...filters, urgency: event.target.value })} />
          <select className="app-input" value={filters.deadlineBucket} onChange={(event) => setFilters({ ...filters, deadlineBucket: event.target.value })}>
            <option value="">Any deadline</option>
            <option value="overdue">Overdue</option>
            <option value="soon">Due soon</option>
            <option value="has">Has deadline</option>
            <option value="none">No deadline</option>
          </select>
          <select className="app-input" value={filters.visibilityScope} onChange={(event) => setFilters({ ...filters, visibilityScope: event.target.value })}>
            <option value="">Any visibility</option>
            <option value="owner">Owner</option>
            <option value="spouse">Spouse</option>
            <option value="shared">Shared</option>
          </select>
          <select className="app-input" value={filters.privacy} onChange={(event) => setFilters({ ...filters, privacy: event.target.value })}>
            <option value="">Any privacy</option>
            <option value="private">Private</option>
            <option value="public">Not private</option>
          </select>
        </div>
      </SectionCard>

      <SectionCard title="Task list">
        {filteredTasks.length ? (
          <ul className="stack-list">
            {filteredTasks.map((task) => (
              <li key={task.id} className="task-row">
                <div>
                  <p className="lead-copy">{task.title}</p>
                  <p className="footnote">{task.notes || "No notes"}</p>
                </div>
                <div className="inline-actions">
                  <StatusPill label={task.status} />
                  <button className="app-button" type="button" onClick={() => openTaskModal({ mode: "edit", taskId: task.id })}>Edit</button>
                  <Link className="app-button" href={`/tasks/${task.id}`}>Detail</Link>
                </div>
              </li>
            ))}
          </ul>
        ) : <EmptyState message="No tasks found. Try clearing filters." />}
      </SectionCard>
      {error ? <p className="error-text">{error}</p> : null}
    </section>
  );
}

export function EntityDetailView({ entityType, id }: { entityType: "projects" | "tasks"; id: string }) {
  const [token, setToken] = useState("");
  const [error, setError] = useState("");
  const [role, setRole] = useState<UserRole | null>(null);
  const [entity, setEntity] = useState<ProjectRecord | TaskRecord | null>(null);

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
      const loadedEntity = (await entityResponse.json()) as ProjectRecord | TaskRecord;
      setEntity(loadedEntity);
      setInfluenceDraft({
        spouse_priority: loadedEntity.spouse_priority?.toString() ?? "",
        spouse_urgency: loadedEntity.spouse_urgency?.toString() ?? "",
        spouse_deadline: toDateTimeInput(loadedEntity.spouse_deadline),
        spouse_deadline_type: loadedEntity.spouse_deadline_type ?? "",
      });
    };
    void run();
  }, [entityType, id, token]);

  async function saveSpouseInfluence() {
    if (!token || !entity || entityType !== "tasks") return;
    setError("");
    const payload: Record<string, unknown> = {
      spouse_priority: parseNumeric(influenceDraft.spouse_priority),
      spouse_urgency: parseNumeric(influenceDraft.spouse_urgency),
      spouse_deadline: parseDateTime(influenceDraft.spouse_deadline),
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
    setEntity((await response.json()) as TaskRecord);
  }

  return (
    <section className="screen-flow">
      <ScreenHeader title={entityType === "projects" ? "Project Detail" : "Task Detail"} subtitle="Detail panel" />
      <SectionCard title="Overview">
        {entity ? (
          <div className="stack-list">
            <p className="lead-copy">{"name" in entity ? entity.name : entity.title}</p>
            <p>{"description" in entity ? (entity.description ?? "No description.") : (entity.notes ?? "No description.")}</p>
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
