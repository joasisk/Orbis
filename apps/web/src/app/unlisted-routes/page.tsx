import Link from "next/link";

export default function UnlistedRoutesPage() {
  return (
    <div className="screen-flow">
      <header className="screen-header">
        <div>
          <p className="screen-kicker">Temporary</p>
          <h1>Unlisted route index</h1>
        </div>
      </header>

      <section className="section-card">
        <p>
          This temporary index lists currently accessible routes that are not present in the main sidebar navigation.
        </p>
        <ul className="stack-list">
          <li><Link href="/projects">/projects — Long Term Plan workspace</Link></li>
          <li><Link href="/tasks">/tasks — Task workspace</Link></li>
          <li><Link href="/settings">/settings — User & app settings</Link></li>
          <li>/projects/[id] — Project detail route (accessible when an id is known)</li>
          <li>/tasks/[id] — Task detail route (accessible when an id is known)</li>
        </ul>
      </section>
    </div>
  );
}
