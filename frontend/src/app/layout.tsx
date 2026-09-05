import type { Metadata } from "next";
import { DM_Sans, Fraunces, JetBrains_Mono } from "next/font/google";
import { Toaster } from "@/components/ui/sonner";
import { AppNav } from "@/components/app-nav";
import "./globals.css";

const display = Fraunces({
  variable: "--font-display",
  subsets: ["latin"],
  weight: ["500", "600", "700"],
});

const sans = DM_Sans({
  variable: "--font-sans",
  subsets: ["latin"],
});

const mono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Frontline OS · Hunar Assignment",
  description: "AI hiring, people reachout, and attendance at scale with Hunar Voice AI",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${display.variable} ${sans.variable} ${mono.variable} h-full`}>
      <body className="flex min-h-full flex-col bg-background text-foreground">
        <AppNav />
        <main className="relative mx-auto w-full max-w-6xl flex-1 px-4 py-6 sm:px-6 sm:py-8">{children}</main>
        <footer className="border-t border-border bg-white py-4 text-center text-xs text-slate-500">
          Frontline OS · Hunar.ai assignment · API key stays server-side
        </footer>
        <Toaster theme="light" />
      </body>
    </html>
  );
}
