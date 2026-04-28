"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { DEFAULT_UI_LANGUAGE, type UiLanguage, translate } from "@/lib/i18n";

type Mode = "login" | "claim";

type BootstrapStatusResponse = { requires_bootstrap: boolean };

const ACCESS_TOKEN_COOKIE = "orbis_access_token";
const REFRESH_TOKEN_KEY = "orbis_refresh_token";
const ACCESS_TOKEN_KEY = "orbis_access_token";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api/v1";

function saveAuthTokens(accessToken: string, refreshToken: string): void {
  window.localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  window.localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  document.cookie = `${ACCESS_TOKEN_COOKIE}=${accessToken}; Path=/; SameSite=Lax`;
}

export function AuthEntry({ mode }: { mode: Mode }) {
  const router = useRouter();
  const [language, setLanguage] = useState<UiLanguage>(DEFAULT_UI_LANGUAGE);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isCheckingStatus, setIsCheckingStatus] = useState(true);
  const [requiresBootstrap, setRequiresBootstrap] = useState(false);

  const title = useMemo(() => (mode === "claim" ? "Claim this Orbis server" : "Sign in to Orbis"), [mode]);

  useEffect(() => {
    const localLanguage = (window.localStorage.getItem("orbis_ui_language") as UiLanguage | null) ?? DEFAULT_UI_LANGUAGE;
    setLanguage(localLanguage);
  }, []);

  useEffect(() => {
    if (mode !== "login") return;
    const params = new URLSearchParams(window.location.search);
    if (params.get("reason") !== "session_expired") return;
    setError(translate(language, "authSessionExpired"));
  }, [language, mode]);

  useEffect(() => {
    const run = async () => {
      try {
        const response = await fetch(`${apiBase}/auth/bootstrap-status`, { cache: "no-store" });
        if (!response.ok) throw new Error("Unable to check server status.");
        const payload = (await response.json()) as BootstrapStatusResponse;
        setRequiresBootstrap(payload.requires_bootstrap);
        if (mode === "claim" && !payload.requires_bootstrap) router.replace("/login");
        if (mode === "login" && payload.requires_bootstrap) router.replace("/claim");
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to check server status.");
      } finally {
        setIsCheckingStatus(false);
      }
    };
    void run();
  }, [mode, router]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (mode === "claim" && password !== confirmPassword) {
      setError(translate(language, "authPasswordMismatch"));
      return;
    }
    setIsSubmitting(true);
    setError("");

    try {
      if (mode === "claim") {
        const bootstrapResponse = await fetch(`${apiBase}/auth/bootstrap-owner`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });
        if (!bootstrapResponse.ok) throw new Error("Unable to create owner account.");
      }

      const loginResponse = await fetch(`${apiBase}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!loginResponse.ok) throw new Error("Unable to sign in.");

      const payload = (await loginResponse.json()) as { access_token: string; refresh_token: string };
      saveAuthTokens(payload.access_token, payload.refresh_token);
      router.replace("/");
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="auth-page-card">
      <form className="auth-form" onSubmit={handleSubmit}>
        <p className="screen-kicker">Welcome</p>
        <h1>{title}</h1>
        {isCheckingStatus ? <p>Checking server status…</p> : null}
        <label>Email<input className="app-input" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required /></label>
        <label>
          Password
          <span className="password-input-row">
            <input className="app-input" type={showPassword ? "text" : "password"} value={password} onChange={(event) => setPassword(event.target.value)} required minLength={8} />
            <button
              className="app-button password-toggle"
              type="button"
              aria-label={showPassword ? translate(language, "authHidePassword") : translate(language, "authShowPassword")}
              title={showPassword ? translate(language, "authHidePassword") : translate(language, "authShowPassword")}
              onClick={() => setShowPassword((value) => !value)}
            >
              👁
            </button>
          </span>
        </label>
        {mode === "claim" ? (
          <label>
            {translate(language, "authRetypePassword")}
            <span className="password-input-row">
              <input className="app-input" type={showConfirmPassword ? "text" : "password"} value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} required minLength={8} />
              <button
                className="app-button password-toggle"
                type="button"
                aria-label={showConfirmPassword ? translate(language, "authHidePassword") : translate(language, "authShowPassword")}
                title={showConfirmPassword ? translate(language, "authHidePassword") : translate(language, "authShowPassword")}
                onClick={() => setShowConfirmPassword((value) => !value)}
              >
                👁
              </button>
            </span>
          </label>
        ) : null}
        {error ? <p className="error-text">{error}</p> : null}
        <button className="app-button app-button--primary" type="submit" disabled={isSubmitting || (mode === "claim" && !requiresBootstrap)}>
          {isSubmitting ? "Working…" : mode === "claim" ? "Create owner account" : "Sign in"}
        </button>
      </form>
    </section>
  );
}
