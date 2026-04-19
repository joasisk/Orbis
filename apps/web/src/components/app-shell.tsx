"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";
import { openTaskModal, TaskModalHost } from "@/components/entity-management";

type NavItem = {
  href: string;
  label: string;
  match: (pathname: string) => boolean;
};

const navItems: NavItem[] = [
  { href: "/", label: "Day", match: (pathname) => pathname === "/" },
  { href: "/schedule", label: "Week", match: (pathname) => pathname.startsWith("/schedule") },
  { href: "/areas", label: "Areas", match: (pathname) => pathname.startsWith("/areas") },
  { href: "/projects", label: "Long Term Plan", match: (pathname) => pathname.startsWith("/projects") || pathname.startsWith("/tasks") },
];

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";
const ACCESS_TOKEN_COOKIE = "orbis_access_token";
const ACCESS_TOKEN_KEY = "orbis_access_token";
const REFRESH_TOKEN_KEY = "orbis_refresh_token";

type MeResponse = {
  email: string;
  role: "owner" | "spouse";
};

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [me, setMe] = useState<MeResponse | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const authRoute = pathname.startsWith("/login") || pathname.startsWith("/claim");

  const clearAuthState = useCallback((redirectToLogin = true) => {
    window.localStorage.removeItem(ACCESS_TOKEN_KEY);
    window.localStorage.removeItem(REFRESH_TOKEN_KEY);
    document.cookie = `${ACCESS_TOKEN_COOKIE}=; Max-Age=0; Path=/; SameSite=Lax`;
    document.cookie = `${ACCESS_TOKEN_COOKIE}=; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Path=/; SameSite=Lax`;
    setMe(null);
    if (redirectToLogin) {
      router.replace("/login");
    }
  }, [router]);

  useEffect(() => {
    if (authRoute) return;
    const accessToken = window.localStorage.getItem(ACCESS_TOKEN_KEY) ?? "";
    if (!accessToken) {
      clearAuthState();
      return;
    }

    const loadMe = async () => {
      const response = await fetch(`${apiBase}/users/me`, {
        headers: { Authorization: `Bearer ${accessToken}` },
        cache: "no-store",
      });
      if (!response.ok) {
        if (response.status === 401) clearAuthState();
        return;
      }
      setMe((await response.json()) as MeResponse);
    };

    void loadMe();
  }, [authRoute, clearAuthState]);

  useEffect(() => {
    const onEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setMenuOpen(false);
      }
    };
    window.addEventListener("keydown", onEscape);
    return () => window.removeEventListener("keydown", onEscape);
  }, []);

  const displayName = useMemo(() => {
    if (!me?.email) return "John Doe";
    const localPart = me.email.split("@")[0] ?? "";
    return localPart
      .split(/[._-]/g)
      .filter(Boolean)
      .map((part) => part[0].toUpperCase() + part.slice(1))
      .join(" ");
  }, [me]);

  const avatarLabel = useMemo(() => {
    const letters = displayName
      .split(" ")
      .filter(Boolean)
      .map((chunk) => chunk[0]?.toUpperCase() ?? "")
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
    clearAuthState();
  };

  if (authRoute) {
    return <main className="auth-layout">{children}</main>;
  }

  return (
    <div className="layout-root" onClick={() => setMenuOpen(false)}>
      <aside className="sidebar" aria-label="Main navigation">
        <div className="sidebar-brand">
          <p>ORBIS</p>
          <span>v0.1.0</span>
        </div>

        <nav className="sidebar-nav" aria-label="Primary">
          {navItems.map((item) => {
            const isActive = item.match(pathname);
            return (
              <Link key={item.href} className={`sidebar-link${isActive ? " is-active" : ""}`} href={item.href}>
                {item.label}
              </Link>
            );
          })}
        </nav>

        <button className="app-button app-button--primary sidebar-cta" type="button" onClick={() => openTaskModal({ mode: "create" })}>
          Add Task
        </button>

        <div className="sidebar-user" onClick={(event) => event.stopPropagation()}>
          <button className="user-trigger" type="button" onClick={() => setMenuOpen((open) => !open)} aria-expanded={menuOpen}>
            <span className="avatar">{avatarLabel}</span>
            <span>{displayName}</span>
            <span>▾</span>
          </button>
          {menuOpen ? (
            <div className="user-menu" role="menu">
              <Link href="/settings" role="menuitem">User Settings</Link>
              <Link href="/settings" role="menuitem">App Settings</Link>
              <button type="button" onClick={handleLogout} role="menuitem">Logout</button>
            </div>
          ) : null}
        </div>
      </aside>
      <main className="content-region">{children}</main>
      <TaskModalHost />
    </div>
  );
}
