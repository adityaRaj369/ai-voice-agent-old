"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { api, type Site, type Worker } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { TipButton } from "@/components/tip-button";
import { Field, LivePill, PageHeader, Panel } from "@/components/page-shell";

type Summary = {
  sites: number;
  workers: number;
  marked_today: number;
  present_today: number;
  missing_today: number;
  by_method: Record<string, number>;
};

type SiteDetail = Site & {
  workers: Worker[];
  recent_events: Array<{
    id: number;
    method: string;
    status: string;
    notes: string;
    worker?: Worker | null;
  }>;
};

export default function AttendancePage() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [sites, setSites] = useState<Site[]>([]);
  const [selected, setSelected] = useState<SiteDetail | null>(null);
  const [code, setCode] = useState("");
  const [pin, setPin] = useState("");
  const [busy, setBusy] = useState(false);

  async function load() {
    const [s, list] = await Promise.all([
      api.get<Summary>("/api/attendance/summary"),
      api.get<Site[]>("/api/attendance/sites"),
    ]);
    setSummary(s);
    setSites(list);
  }

  useEffect(() => {
    load().catch((e) => toast.error(String(e.message || e)));
  }, []);

  async function openSite(id: number) {
    try {
      setSelected(await api.get<SiteDetail>(`/api/attendance/sites/${id}`));
    } catch (e) {
      toast.error(String((e as Error).message));
    }
  }

  async function markLandline() {
    setBusy(true);
    try {
      await api.post("/api/attendance/mark", {
        employee_code: code,
        spoken_pin: pin,
        method: "landline_ivr",
        status: "present",
      });
      toast.success("Attendance marked");
      setCode("");
      setPin("");
      await load();
      if (selected) await openSite(selected.id);
    } catch (e) {
      toast.error(String((e as Error).message));
    } finally {
      setBusy(false);
    }
  }

  async function ensureAttendanceAgent() {
    const agents = await api.get<Array<{ id: number; kind: string }>>("/api/agents");
    const existing = agents.find((a) => a.kind === "attendance");
    if (existing) return existing;
    return api.post<{ id: number }>("/api/agents", {
      kind: "attendance",
      language: "HINDI",
      voice_persona: "MIRA",
    });
  }

  async function voiceCheckin(worker: Worker) {
    setBusy(true);
    try {
      const agent = await ensureAttendanceAgent();
      await api.post("/api/attendance/voice-checkin", {
        worker_id: worker.id,
        agent_id: agent.id,
      });
      toast.success(`Live Voice AI check-in for ${worker.name}`);
      await load();
    } catch (e) {
      toast.error(String((e as Error).message));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        kicker="Module 03 · No smartphones"
        title="Attendance without apps"
        description="Prototype for 100 locations and 1000 workers using landline PIN and Hunar Voice check-in."
        action={<LivePill live={(summary?.sites || 0) === 100} label="100 sites ready" />}
      />

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {[
          ["Sites", summary?.sites],
          ["Workers", summary?.workers],
          ["Present today", summary?.present_today],
          ["Missing today", summary?.missing_today],
        ].map(([label, value]) => (
          <div key={String(label)} className="surface-card p-4">
            <p className="text-[11px] uppercase tracking-wide text-slate-500">{label}</p>
            <p className="font-display mt-1 text-3xl font-semibold text-teal-700">{value ?? "—"}</p>
          </div>
        ))}
      </div>

      <div className="grid gap-5 lg:grid-cols-2 lg:items-start">
        <Panel title="Landline / IVR mark" description="Try E0001 with PIN 1000.">
          <div className="form-grid">
            <div className="form-grid-2">
              <Field label="Employee code">
                <Input className="h-10" value={code} onChange={(e) => setCode(e.target.value)} placeholder="E0001" />
              </Field>
              <Field label="Spoken PIN">
                <Input className="h-10" value={pin} onChange={(e) => setPin(e.target.value)} placeholder="1000" />
              </Field>
            </div>
            <TipButton tip="Mark this worker present for today" disabled={busy} onClick={markLandline}>
              Mark present
            </TipButton>
          </div>
        </Panel>

        <Panel title="Methods today" description="How attendance was recorded.">
          <div className="flex flex-wrap gap-2">
            {summary && Object.keys(summary.by_method).length ? (
              Object.entries(summary.by_method).map(([k, v]) => (
                <Badge key={k} variant="outline">
                  {k}: {v}
                </Badge>
              ))
            ) : (
              <p className="text-sm text-slate-500">No marks yet today.</p>
            )}
          </div>
        </Panel>
      </div>

      <Panel title="100 locations" description="Click a site to open workers.">
        <div className="max-h-80 overflow-auto rounded-xl border border-border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Code</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>City</TableHead>
                <TableHead>Present</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sites.map((s) => (
                <TableRow
                  key={s.id}
                  className="cursor-pointer hover:bg-teal-50"
                  title={`Open ${s.name}`}
                  onClick={() => openSite(s.id)}
                >
                  <TableCell className="font-mono text-teal-700">{s.code}</TableCell>
                  <TableCell>{s.name}</TableCell>
                  <TableCell>{s.city}</TableCell>
                  <TableCell>
                    {s.present ?? 0}/{s.headcount ?? 0}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </Panel>

      {selected ? (
        <Panel
          title={`${selected.code} · ${selected.name}`}
          description={`Landline ${selected.landline} · Supervisor ${selected.supervisor_name}`}
        >
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Code</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Shift</TableHead>
                  <TableHead>PIN</TableHead>
                  <TableHead className="text-right">Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {selected.workers.map((w) => (
                  <TableRow key={w.id}>
                    <TableCell className="font-mono">{w.employee_code}</TableCell>
                    <TableCell>{w.name}</TableCell>
                    <TableCell>{w.shift}</TableCell>
                    <TableCell className="font-mono">{w.spoken_pin}</TableCell>
                    <TableCell className="text-right">
                      <TipButton tip="Start Hunar voice attendance check-in" size="sm" disabled={busy} onClick={() => voiceCheckin(w)}>
                        Voice check-in
                      </TipButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          <div className="mt-4">
            <h3 className="mb-2 text-sm font-semibold text-slate-800">Recent events</h3>
            {selected.recent_events.length ? (
              selected.recent_events.map((e) => (
                <div key={e.id} className="border-b border-border py-1.5 text-sm text-slate-700">
                  {e.worker?.name} · {e.method} · <Badge variant="outline">{e.status}</Badge>
                </div>
              ))
            ) : (
              <p className="text-sm text-slate-500">No events yet for this site.</p>
            )}
          </div>
        </Panel>
      ) : null}
    </div>
  );
}
