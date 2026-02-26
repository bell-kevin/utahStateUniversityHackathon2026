import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Next + Expo + Convex Template",
  description: "Starter monorepo with Turborepo and Biome",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
