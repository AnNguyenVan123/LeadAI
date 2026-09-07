import type { Metadata } from "next";
import { IBM_Plex_Sans, IBM_Plex_Sans_Condensed, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";

const plex = IBM_Plex_Sans({ subsets: ["latin", "vietnamese"], weight: ["400", "500", "600"], variable: "--font-plex" });
const cond = IBM_Plex_Sans_Condensed({ subsets: ["latin"], weight: ["500", "600", "700"], variable: "--font-plex-cond" });
const mono = IBM_Plex_Mono({ subsets: ["latin"], weight: ["400", "500"], variable: "--font-plex-mono" });

export const metadata: Metadata = {
  title: "Intent Radar",
  description: "Paste your landing page or product description — get people who are looking for it, along with reasons and suggested replies.",
};

import Sidebar from "@/components/Sidebar";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi" className={`${plex.variable} ${cond.variable} ${mono.variable}`}>
      <body className="min-h-dvh bg-ground flex">
        <Sidebar />
        <div className="flex-1 overflow-auto bg-ground">
          {children}
        </div>
      </body>
    </html>
  );
}
