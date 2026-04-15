import Link from "next/link";
import { Phase3Home } from "@/components/phase3-home";

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
            <div className="orbit-context__text">Focus orchestration</div>
          </div>

          <nav className="orbit-nav" aria-label="Primary">
            <Link className="orbit-nav__item orbit-nav__item--active" href="/">
              <span className="material-symbols-outlined">calendar_today</span>
              <span>Today</span>
            </a>
            <Link className="orbit-nav__item" href="/tasks">
              <span className="material-symbols-outlined">checklist</span>
              <span>Tasks</span>
            </Link>
            <Link className="orbit-nav__item" href="/projects">
              <span className="material-symbols-outlined">folder</span>
              <span>Projects</span>
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
          <p>Phase 3: do-now planning + focus execution</p>
        </div>
      </header>

      <main className="orbit-main">
        <div className="orbit-grid">
          <Phase3Home />
        </div>
      </main>

      <button className="orbit-floating-focus" aria-label="Focus timer">
        <span className="material-symbols-outlined">timer</span>
      </button>
    </div>
  );
}
