"use client";

import { useEffect, useState } from "react";
import { DEFAULT_UI_LANGUAGE, type UiLanguage } from "@/lib/i18n";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api/v1";
const ACCESS_TOKEN_KEY = "orbis_access_token";

type SettingsLanguagePayload = {
  ui_language: UiLanguage;
};

export function useUiLanguage() {
  const [language, setLanguage] = useState<UiLanguage>(DEFAULT_UI_LANGUAGE);

  useEffect(() => {
    const accessToken = window.localStorage.getItem(ACCESS_TOKEN_KEY) ?? "";
    if (!accessToken) return;

    const loadLanguage = async () => {
      const response = await fetch(`${apiBase}/settings/me`, {
        headers: { Authorization: `Bearer ${accessToken}` },
        cache: "no-store",
      });
      if (!response.ok) return;
      const payload = (await response.json()) as SettingsLanguagePayload;
      setLanguage(payload.ui_language ?? DEFAULT_UI_LANGUAGE);
    };

    void loadLanguage();
  }, []);

  return { language, setLanguage };
}
