import Link from "next/link";
import { EmptyState, ScreenHeader, SectionCard } from "@/components/ui-kit";
import { DEFAULT_UI_LANGUAGE, translate } from "@/lib/i18n";

export default function SettingsPage() {
  const language = DEFAULT_UI_LANGUAGE;

  return (
    <section className="screen-flow">
      <ScreenHeader title={translate(language, "settingsTitle")} subtitle={translate(language, "settingsSubtitle")} />
      <EmptyState message={translate(language, "settingsHubEmpty")} />
      <div className="two-col">
        <SectionCard title={translate(language, "userSettings")}>
          <Link className="app-button app-button--primary" href="/settings/user">{translate(language, "openUserSettings")}</Link>
        </SectionCard>
        <SectionCard title={translate(language, "appSettings")}>
          <Link className="app-button app-button--primary" href="/settings/app">{translate(language, "openAppSettings")}</Link>
        </SectionCard>
      </div>
    </section>
  );
}
