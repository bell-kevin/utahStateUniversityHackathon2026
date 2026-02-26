import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Smart Asset Intelligence",
  description:
    "NFC-first asset operations with AI inspection scoring for hackathon prototyping.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
