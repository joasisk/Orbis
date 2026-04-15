import Link from "next/link";

export default function HomePage() {
  return (
    <main style={{ fontFamily: "sans-serif", maxWidth: "48rem", margin: "2rem auto", lineHeight: 1.6 }}>
      <h1>Orbis Phase 2 workspace</h1>
      <p>Phase 2 CRUD and detail workflows are now scaffolded for areas, projects, tasks, dependencies, and history.</p>
      <ul>
        <li>
          <Link href="/projects">Projects list + create</Link>
        </li>
        <li>
          <Link href="/tasks">Tasks list + create</Link>
        </li>
      </ul>
      <p>Tip: set API base URL and a bearer token from `/api/v1/auth/login` on each page.</p>
    </main>
  );
}
