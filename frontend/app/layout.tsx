import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Kynetic — Knowledge in Motion",
  description: "Turn ambition into capability with an evidence-aware workspace for early-career builders.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
