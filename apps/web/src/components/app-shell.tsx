"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

type NavItem = {
  href: string;
  label: string;
  icon: string;
  match?: (pathname: string) => boolean;
};

const navItems: NavItem[] = [
  {
    href: "/",
    label: "Today",
    icon: "calendar_today",
    match: (pathname) => pathname === "/",
  },
  {
    href: "/tasks",
    label: "Week",
    icon: "calendar_month",
    match: (pathname) => pathname.startsWith("/tasks"),
  },
  {
    href: "/projects",
    label: "Scope",
    icon: "explore",
    match: (pathname) => pathname.startsWith("/projects"),
  },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="app-shell">
      <aside className="app-shell__sidebar" aria-label="Main navigation">
        <div className="app-shell__top">
          <div className="app-shell__brand">Orbis</div>

          <div className="app-shell__context">
            <div className="app-shell__avatar" aria-hidden>
              ORB
            </div>
            <p className="app-shell__context-text">The Sun-Drenched Atelier</p>
          </div>

          <nav className="app-shell__nav" aria-label="Primary">
            {navItems.map((item) => {
              const isActive = item.match ? item.match(pathname) : pathname.startsWith(item.href);
              return (
                <Link key={item.href} className={`app-shell__nav-item${isActive ? " app-shell__nav-item--active" : ""}`} href={item.href}>
                  <span className="material-symbols-outlined" aria-hidden>
                    {item.icon}
                  </span>
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="app-shell__bottom">
          <Link className={`app-shell__nav-item${pathname.startsWith("/settings") ? " app-shell__nav-item--active" : ""}`} href="/settings">
            <span className="material-symbols-outlined" aria-hidden>
              settings
            </span>
            <span>Settings</span>
          </Link>
          <div className="app-shell__art" aria-hidden />
        </div>
      </aside>

      <main className="app-shell__main">{children}</main>
    </div>
  );
}
