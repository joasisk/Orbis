"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

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

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";
const ACCESS_TOKEN_COOKIE = "orbis_access_token";
const ACCESS_TOKEN_KEY = "orbis_access_token";
const REFRESH_TOKEN_KEY = "orbis_refresh_token";

type MeResponse = {
  email: string;
};

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [me, setMe] = useState<MeResponse | null>(null);
  const authRoute = pathname.startsWith("/login") || pathname.startsWith("/claim");
  const token = typeof window === "undefined" ? "" : window.localStorage.getItem(ACCESS_TOKEN_KEY) ?? "";

  useEffect(() => {
    if (authRoute) return;
    const accessToken = window.localStorage.getItem(ACCESS_TOKEN_KEY) ?? "";
    if (!accessToken) return;

    const loadMe = async () => {
      const response = await fetch(`${apiBase}/users/me`, {
        headers: { Authorization: `Bearer ${accessToken}` },
        cache: "no-store",
      });
      if (!response.ok) return;
      const payload = (await response.json()) as MeResponse;
      setMe(payload);
    };

    void loadMe();
  }, [authRoute]);

  const displayName = useMemo(() => {
    if (!me?.email) return "Your account";
    const localPart = me.email.split("@")[0] ?? "";
    if (!localPart) return me.email;
    return localPart
      .split(/[._-]/g)
      .filter(Boolean)
      .map((part) => part[0].toUpperCase() + part.slice(1))
      .join(" ");
  }, [me]);

  const avatarLabel = useMemo(() => {
    if (!displayName) return "OR";
    const letters = displayName
      .split(" ")
      .filter(Boolean)
      .map((tokenPart) => tokenPart[0]?.toUpperCase() ?? "")
      .join("");
    return letters.slice(0, 2) || "OR";
  }, [displayName]);

  const handleLogout = async () => {
    const refreshToken = window.localStorage.getItem(REFRESH_TOKEN_KEY) ?? "";
    if (refreshToken) {
      await fetch(`${apiBase}/auth/logout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
    }
    window.localStorage.removeItem(ACCESS_TOKEN_KEY);
    window.localStorage.removeItem(REFRESH_TOKEN_KEY);
    document.cookie = `${ACCESS_TOKEN_COOKIE}=; Max-Age=0; Path=/`;
    setMe(null);
    router.push("/login");
  };

  if (authRoute) {
    return <main className="app-shell__auth-main">{children}</main>;
  }

  return (
    <div className="app-shell">
      <aside className="app-shell__sidebar" aria-label="Main navigation">
        <div className="app-shell__top">
          <div className="app-shell__brand">Orbis</div>

          <div className="app-shell__context">
            <div className="app-shell__avatar" aria-hidden>
              {avatarLabel}
            </div>
            <button className="app-shell__user-button" onClick={handleLogout} type="button" disabled={!token}>
              <span className="app-shell__user-name">{displayName}</span>
              <span className="app-shell__user-email">{me?.email ?? "Sign in to continue"}</span>
            </button>
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
