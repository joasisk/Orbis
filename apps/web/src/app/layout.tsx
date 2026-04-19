import type { Metadata } from "next";
import { Manrope, Plus_Jakarta_Sans } from "next/font/google";

import "./globals.css";
import { AppShell } from "@/components/app-shell";

const manrope = Manrope({
  subsets: ["latin"],
  variable: "--font-manrope",
  weight: ["400", "500", "600", "700"],
});

const plusJakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-plus-jakarta",
  weight: ["500", "600", "700", "800"],
});

export const metadata: Metadata = {
  title: "Orbis",
  description: "ADHD-friendly planning and project management",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${manrope.variable} ${plusJakarta.variable}`}>
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
