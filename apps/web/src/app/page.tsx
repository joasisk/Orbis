import Link from "next/link";

import { GlassNav, TimeProgressArc } from "@/components/organic-chronos";

export default function HomePage() {
  return (
    <main className="organic-shell">
      <div className="organic-layout">
        <GlassNav />
        <section className="organic-grid">
          <article className="panel panel--focus focus-halo">
            <p className="stamp-label">Creative North Star</p>
            <h2 className="display-title">The Sun-Drenched Atelier</h2>
            <p className="body-copy">
              A calm, Mediterranean-inspired workspace where time and tasks are guided by tonal layering, generous
              breathing room, and slow transitions.
            </p>
            <div className="button-row">
              <Link href="/projects" className="btn btn-primary">
                Open Projects
              </Link>
              <Link href="/tasks" className="btn btn-secondary">
                Open Tasks
              </Link>
            </div>
          </article>
          <aside className="panel">
            <p className="stamp-label">Daily Pace</p>
            <h3 className="headline">Organic Time Progress</h3>
            <TimeProgressArc progress={0.62} />
            <p className="body-copy">Use gentle visual rhythm instead of hard countdown pressure.</p>
          </aside>
        </section>
      </div>
    </main>
  );
}
