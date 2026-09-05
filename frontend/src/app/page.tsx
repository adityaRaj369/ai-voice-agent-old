"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowRight, Mic2, Search, Users } from "lucide-react";
import { api } from "@/lib/api";
import { TipButton } from "@/components/tip-button";
import { LivePill, Panel } from "@/components/page-shell";

type Status = {
  hunar_configured: boolean;
  hunar_ok: boolean;
  hunar_error?: string | null;
  pdl_configured: boolean;
  apollo_configured: boolean;
  counts: Record<string, number>;
};

const modules = [
  {
    href: "/hiring",
    icon: Mic2,
    step: "01",
    title: "AI Hiring Assistant",
    body: "Create jobs, live Hunar screening agents, and call candidates.",
    tip: "Open hiring module",
  },
  {
    href: "/search",
    icon: Search,
    step: "02",
    title: "People Search & Reachout",
    body: "Search from a JD, then reach out by voice, WhatsApp, or email.",
    tip: "Open people search",
  },
  {
    href: "/attendance",
    icon: Users,
    step: "03",
    title: "Attendance at scale",
    body: "100 sites and 1000 workers with landline PIN and Voice AI.",
    tip: "Open attendance module",
  },
];

export default function HomePage() {
  const [status, setStatus] = useState<Status | null>(null);

  useEffect(() => {
    api.get<Status>("/api/status").then(setStatus).catch(() => setStatus(null));
  }, []);

  return (
    <div className="space-y-8">
      <section className="surface-card relative overflow-hidden p-6 sm:p-10">
        <div className="mb-4 flex flex-wrap gap-2">
          <LivePill live={!!status?.hunar_ok} label={status?.hunar_ok ? "Hunar Voice LIVE" : "Hunar offline"} />
          <LivePill live={!!status?.pdl_configured} label={status?.pdl_configured ? "PDL live" : "PDL optional"} />
          <LivePill live={!!status?.apollo_configured} label={status?.apollo_configured ? "Apollo live" : "Apollo optional"} />
        </div>
        <p className="font-display text-4xl font-semibold tracking-tight text-slate-900 sm:text-5xl">Frontline OS</p>
        <h1 className="mt-3 max-w-2xl text-base text-slate-600 sm:text-lg">
          Hire, reach talent, and mark attendance with Hunar Voice AI — clear workflows for every assignment module.
        </h1>
        <div className="mt-6 flex flex-wrap gap-3">
          <TipButton tip="Go to AI hiring flow" size="lg" nativeButton={false} render={<Link href="/hiring" />}>
            Start hiring <ArrowRight className="size-4" />
          </TipButton>
          <TipButton tip="Read Q3 attendance design" size="lg" variant="outline" nativeButton={false} render={<Link href="/design" />}>
            Read Q3 design
          </TipButton>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {modules.map((m) => (
          <Link key={m.href} href={m.href} title={m.tip} className="surface-card group block p-5 transition hover:border-teal-300 hover:shadow-md">
            <div className="mb-4 flex items-center justify-between">
              <span className="flex size-10 items-center justify-center rounded-xl bg-teal-50 text-teal-700">
                <m.icon className="size-5" />
              </span>
              <span className="font-mono text-xs text-slate-400">{m.step}</span>
            </div>
            <h2 className="font-display text-xl font-semibold text-slate-900 group-hover:text-teal-800">{m.title}</h2>
            <p className="mt-2 text-sm text-slate-500">{m.body}</p>
            <p className="mt-4 text-sm font-medium text-teal-700">Open module →</p>
          </Link>
        ))}
      </section>

      <Panel title="System pulse" description="Live counts from your backend and Hunar connection.">
        {status ? (
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
            {[
              ["Jobs", status.counts.jobs],
              ["Candidates", status.counts.candidates],
              ["Agents", status.counts.agents],
              ["Calls", status.counts.calls],
              ["Campaigns", status.counts.campaigns],
            ].map(([k, v]) => (
              <div key={String(k)} className="rounded-xl border border-border bg-slate-50 px-3 py-3 text-center">
                <div className="font-mono text-xl font-semibold text-teal-700">{v}</div>
                <div className="text-[11px] uppercase tracking-wide text-slate-500">{k}</div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-500">Backend offline — start API on :8001</p>
        )}
        {status?.hunar_error ? <p className="mt-3 text-sm text-red-600">{status.hunar_error}</p> : null}
      </Panel>
    </div>
  );
}
