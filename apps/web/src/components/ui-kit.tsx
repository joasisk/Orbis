import type { ReactNode } from "react";

export function ScreenHeader({ title, subtitle, actions }: { title: string; subtitle?: string; actions?: ReactNode }) {
  return (
    <header className="screen-header">
      <div>
        <p className="screen-kicker">{subtitle ?? "Orbis"}</p>
        <h1>{title}</h1>
      </div>
      {actions ? <div className="screen-actions">{actions}</div> : null}
    </header>
  );
}

export function SectionCard({ title, children, tone = "default" }: { title: string; children: ReactNode; tone?: "default" | "accent" }) {
  return (
    <section className={`section-card${tone === "accent" ? " section-card--accent" : ""}`}>
      <h2>{title}</h2>
      {children}
    </section>
  );
}

export function StatusPill({ label }: { label: string }) {
  return <span className="status-pill">{label}</span>;
}

export function EmptyState({ message }: { message: string }) {
  return <p className="empty-state">{message}</p>;
}
