"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { api, type VoiceCall } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { TipButton } from "@/components/tip-button";
import { PageHeader, Panel } from "@/components/page-shell";

type Dashboard = {
  pipeline: Record<string, number>;
  recent_calls: VoiceCall[];
  structured_answers: Array<{
    call_id: number;
    purpose: string;
    person: string;
    status: string;
    answers: Record<string, unknown>;
    recording_url?: string;
  }>;
};

export default function DashboardPage() {
  const [data, setData] = useState<Dashboard | null>(null);

  async function load() {
    try {
      setData(await api.get<Dashboard>("/api/dashboard"));
    } catch (e) {
      toast.error(String((e as Error).message));
    }
  }

  useEffect(() => {
    load();
    const t = setInterval(load, 15000);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader
        kicker="Conversation intelligence"
        title="Answers Dashboard"
        description="Structured responses from Hunar Voice calls. Auto-refreshes every 15 seconds."
        action={
          <TipButton tip="Reload dashboard data now" variant="outline" onClick={load}>
            Refresh now
          </TipButton>
        }
      />

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-6">
        {data
          ? Object.entries(data.pipeline).map(([k, v]) => (
              <div key={k} className="surface-card px-3 py-3 text-center">
                <div className="font-mono text-xl font-semibold text-teal-700">{v}</div>
                <div className="truncate text-[11px] uppercase tracking-wide text-slate-500">{k}</div>
              </div>
            ))
          : null}
      </div>

      <Panel title="Structured call answers" description="Filled after a completed Hunar call + refresh.">
        <div className="space-y-3">
          {data?.structured_answers.map((row) => (
            <div key={row.call_id} className="rounded-xl border border-border bg-slate-50 p-3 sm:p-4">
              <div className="flex flex-wrap items-center gap-2">
                <p className="font-medium text-slate-900">{row.person}</p>
                <Badge>{row.purpose}</Badge>
                <Badge variant="outline">{row.status}</Badge>
              </div>
              <pre className="mt-3 overflow-auto rounded-lg border border-border bg-white p-3 font-mono text-xs text-slate-700">
                {JSON.stringify(row.answers, null, 2)}
              </pre>
              {row.recording_url ? (
                <a
                  className="mt-2 inline-block text-sm text-teal-700 underline"
                  href={row.recording_url}
                  target="_blank"
                  rel="noreferrer"
                  title="Open call recording"
                >
                  Listen to recording
                </a>
              ) : null}
            </div>
          ))}
          {!data?.structured_answers.length ? (
            <p className="text-sm text-slate-500">No answers yet — finish a screening call, then refresh.</p>
          ) : null}
        </div>
      </Panel>

      <Panel title="Recent calls">
        <div className="divide-y divide-border">
          {data?.recent_calls.map((c) => (
            <div key={c.id} className="flex flex-wrap items-center justify-between gap-2 py-2.5 text-sm">
              <span className="text-slate-700">
                <span className="font-mono text-slate-400">#{c.id}</span> {c.callee_name} · {c.purpose}
              </span>
              <Badge variant="outline">{c.status}</Badge>
            </div>
          ))}
        </div>
      </Panel>
    </div>
  );
}
