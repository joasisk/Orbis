import Link from "next/link";

export function GlassNav() {
  return (
    <nav className="glass-nav">
      <div>
        <p className="stamp-label">The Organic Chronos</p>
        <h1 className="headline">Orbis Atelier</h1>
      </div>
      <div className="chip-row">
        <Link className="chip" href="/">
          Home
        </Link>
        <Link className="chip" href="/projects">
          Projects
        </Link>
        <Link className="chip" href="/tasks">
          Tasks
        </Link>
      </div>
    </nav>
  );
}

export function TimeProgressArc({ progress = 0.6 }: { progress?: number }) {
  const clamped = Math.min(1, Math.max(0, progress));
  const circumference = 2 * Math.PI * 90;
  const offset = circumference * (1 - clamped);

  return (
    <div className="progress-wrap" aria-hidden>
      <svg className="progress-arc" viewBox="0 0 220 220" role="img" aria-label="Time progress arc">
        <circle className="progress-arc-track" cx="110" cy="110" r="90" />
        <circle className="progress-arc-fill" cx="110" cy="110" r="90" style={{ strokeDasharray: circumference, strokeDashoffset: offset }} />
      </svg>
    </div>
  );
}
