import Link from "next/link";

export default function HomePage() {
  return (
    <div className="orbit-page">
      <aside className="orbit-sidenav">
        <div className="orbit-sidenav__top">
          <div className="orbit-brand">Orbis</div>
          <div className="orbit-context">
            <div className="orbit-context__avatar" aria-hidden>
              <span className="material-symbols-outlined">spa</span>
            </div>
            <div className="orbit-context__text">The Sun-Drenched Atelier</div>
          </div>

          <nav className="orbit-nav" aria-label="Primary">
            <Link className="orbit-nav__item orbit-nav__item--active" href="/">
              <span className="material-symbols-outlined">calendar_today</span>
              <span>Today</span>
            </Link>
            <Link className="orbit-nav__item" href="/tasks">
              <span className="material-symbols-outlined">date_range</span>
              <span>Week</span>
            </Link>
            <Link className="orbit-nav__item" href="/projects">
              <span className="material-symbols-outlined">explore</span>
              <span>Scope</span>
            </Link>
          </nav>
        </div>

        <div className="orbit-sidenav__bottom">
          <Link className="orbit-nav__item" href="/settings">
            <span className="material-symbols-outlined">settings</span>
            <span>Settings</span>
          </Link>
        </div>
      </aside>

      <header className="orbit-topbar">
        <div>
          <h1>Today&apos;s Orbit</h1>
          <p>4 primary focuses today</p>
        </div>
        <div className="orbit-topbar__actions">
          <label className="orbit-search" htmlFor="orbit-search-input">
            <span className="material-symbols-outlined">search</span>
            <input id="orbit-search-input" type="text" placeholder="Search orbit..." />
          </label>
          <button className="orbit-icon-btn" aria-label="Notifications">
            <span className="material-symbols-outlined">notifications</span>
          </button>
          <button className="orbit-icon-btn" aria-label="Wellbeing">
            <span className="material-symbols-outlined">spa</span>
          </button>
        </div>
      </header>

      <main className="orbit-main">
        <div className="orbit-grid">
          <section className="orbit-timeline">
            <h2 className="orbit-section-label">Flow Timeline</h2>
            <div className="timeline-list">
              <article className="timeline-item timeline-item--active">
                <div className="timeline-item__dot" aria-hidden />
                <div className="timeline-item__card">
                  <div className="timeline-item__meta">
                    <span>In Progress</span>
                    <span>09:00 — 11:30</span>
                  </div>
                  <h3>Creative Concepting</h3>
                  <p>Deep work session for the Atelier architectural proposal. Focus on spatial flow and materiality.</p>
                </div>
              </article>

              <article className="timeline-item">
                <div className="timeline-item__dot" aria-hidden />
                <div className="timeline-item__card timeline-item__card--muted">
                  <div className="timeline-item__meta">
                    <span>Recharge</span>
                    <span>12:00 — 13:30</span>
                  </div>
                  <h3>Garden Lunch &amp; Rest</h3>
                  <p>Offline restoration. No digital inputs.</p>
                </div>
              </article>

              <article className="timeline-item timeline-item--last">
                <div className="timeline-item__dot" aria-hidden />
                <div className="timeline-item__card timeline-item__card--upcoming">
                  <div className="timeline-item__meta">
                    <span>Upcoming</span>
                    <span>14:00 — 15:00</span>
                  </div>
                  <h3>Client Alignment Call</h3>
                  <p>Reviewing phase one milestones with the Florentine team. Focus on budget clarity.</p>
                </div>
              </article>
            </div>
          </section>

          <aside className="orbit-panels">
            <section className="orbit-panel">
              <h2 className="orbit-section-label">Morning Brief</h2>
              <p className="orbit-panel__lead">You have a clear morning ahead. 2 tasks were carried over from yesterday.</p>
              <ul className="orbit-checklist">
                <li>Finalize moodboard exports</li>
                <li>Email follow-up with marble supplier</li>
              </ul>
            </section>

            <section className="orbit-panel orbit-panel--warning">
              <h2 className="orbit-section-label">Needs Attention</h2>
              <h3>Design Review: Guest Suite</h3>
              <p>This was due 4 hours ago. Consider bumping to tomorrow morning if focus is low.</p>
            </section>

            <section className="orbit-panel">
              <h2 className="orbit-section-label">AI Suggestions</h2>
              <div className="orbit-suggestions">
                <article>
                  <h3>Optimize Focus Time</h3>
                  <p>Your signal data suggests peak focus at 10:15 AM. Move Creative Concepting earlier?</p>
                </article>
                <article>
                  <h3>Bundle Tasks</h3>
                  <p>Group short emails after your lunch break.</p>
                </article>
                <article>
                  <h3>Light Anchor</h3>
                  <p>UV index is high. Garden lunch will boost serotonin.</p>
                </article>
              </div>
            </section>
          </aside>
        </div>
      </main>

      <button className="orbit-floating-focus" aria-label="Focus timer">
        <span className="material-symbols-outlined">timer</span>
      </button>
    </div>
  );
}
