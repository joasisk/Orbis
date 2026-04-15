import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Orbis",
  description: "ADHD-friendly planning and project management",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
