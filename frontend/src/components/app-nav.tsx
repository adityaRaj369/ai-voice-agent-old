"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Menu, Radio, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { TipButton } from "@/components/tip-button";

const links = [
  { href: "/", label: "Overview", tip: "Home and system status" },
  { href: "/hiring", label: "AI Hiring", tip: "Screen candidates with Voice AI" },
  { href: "/search", label: "Search", tip: "Find people and launch reachout" },
  { href: "/dashboard", label: "Answers", tip: "View call answers and pipeline" },
  { href: "/attendance", label: "Attendance", tip: "Track site attendance" },
  { href: "/design", label: "Q3 Design", tip: "Read the no-smartphone design" },
];

export function AppNav() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-white/90 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-3 px-4 py-3 sm:px-6">
        <Link href="/" className="flex min-w-0 items-center gap-2.5" title="Go to overview">
          <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-teal-700 text-white shadow-sm">
            <Radio className="size-4" />
          </span>
          <span className="min-w-0">
            <span className="font-display block truncate text-lg font-semibold text-slate-900 sm:text-xl">
              Frontline OS
            </span>
            <span className="hidden text-[11px] text-slate-500 sm:block">Hunar Voice hiring platform</span>
          </span>
        </Link>

        <nav className="hidden items-center gap-1 lg:flex">
          {links.map((link) => {
            const active = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                title={link.tip}
                className={cn(
                  "rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  active ? "bg-teal-700 text-white" : "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
                )}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>

        <TipButton tip="Open or close menu" variant="outline" size="icon" className="lg:hidden" onClick={() => setOpen((v) => !v)}>
          {open ? <X className="size-4" /> : <Menu className="size-4" />}
        </TipButton>
      </div>

      {open ? (
        <nav className="border-t border-border bg-white px-4 py-3 lg:hidden">
          <div className="mx-auto flex max-w-6xl flex-col gap-1">
            {links.map((link) => {
              const active = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  title={link.tip}
                  onClick={() => setOpen(false)}
                  className={cn(
                    "rounded-lg px-3 py-2.5 text-sm font-medium",
                    active ? "bg-teal-50 text-teal-800" : "text-slate-600 hover:bg-slate-50",
                  )}
                >
                  {link.label}
                </Link>
              );
            })}
          </div>
        </nav>
      ) : null}
    </header>
  );
}
