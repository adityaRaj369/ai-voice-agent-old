"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { PhoneCall, RefreshCw } from "lucide-react";
import { api, type Agent, type Candidate, type Job, type VoiceCall } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { TipButton } from "@/components/tip-button";
import { Field, LivePill, PageHeader, Panel } from "@/components/page-shell";

const ACTIVE_CALL = new Set(["NOT_STARTED", "SCHEDULED", "INITIATED", "RINGING", "IN_PROGRESS"]);

function callStatusLabel(status: string) {
  const map: Record<string, string> = {
    NOT_STARTED: "Queued — waiting to dial",
    SCHEDULED: "Scheduled — will dial soon",
    INITIATED: "Dialing candidate…",
    RINGING: "Ringing — waiting for answer",
    IN_PROGRESS: "On call — conversation live",
    COMPLETED: "Completed",
    NOT_CONNECTED: "Not connected",
    CANCELLED: "Cancelled",
    FAILED: "Failed",
  };
  return map[status] || status;
}

function candidateStatusLabel(status: string) {
  const map: Record<string, string> = {
    new: "New",
    calling: "Calling…",
    on_call: "On call",
    contacted: "Contacted",
    engaged: "Engaged / interested",
    not_interested: "Not interested",
    no_answer: "No answer",
    sourced: "Sourced",
  };
  return map[status] || status;
}

export default function HiringPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [calls, setCalls] = useState<VoiceCall[]>([]);
  const [title, setTitle] = useState("Warehouse Associate");
  const [company, setCompany] = useState("Northline Logistics");
  const [location, setLocation] = useState("Bengaluru");
  const [description, setDescription] = useState(
    "We are hiring Warehouse Associates in Bengaluru. Hindi + English, inventory experience, night shifts OK. 1+ years preferred.",
  );
  const [candName, setCandName] = useState("");
  const [candPhone, setCandPhone] = useState("");
  const [jobId, setJobId] = useState<number | "">("");
  const [agentId, setAgentId] = useState<number | "">("");
  const [busy, setBusy] = useState(false);
  const [activeBanner, setActiveBanner] = useState<string | null>(null);
  const [liveSyncing, setLiveSyncing] = useState(false);

  const loadLists = useCallback(async () => {
    const [j, a, c, callsRes] = await Promise.all([
      api.get<Job[]>("/api/jobs"),
      api.get<Agent[]>("/api/agents"),
      api.get<Candidate[]>("/api/candidates"),
      api.get<VoiceCall[]>("/api/calls?purpose=screening"),
    ]);
    setJobs(j);
    setAgents(a.filter((x) => x.kind === "screening" || x.kind === "custom"));
    setCandidates(c);
    setCalls(callsRes);
    if (!jobId && j[0]) setJobId(j[0].id);
    if (!agentId) {
      const screening = a.find((x) => x.kind === "screening");
      if (screening) setAgentId(screening.id);
    }
    return callsRes;
  }, [agentId, jobId]);

  const syncLive = useCallback(async () => {
    setLiveSyncing(true);
    try {
      await api.post("/api/calls/sync-open?purpose=screening");
      const callsRes = await loadLists();
      const open = callsRes.find((c) => ACTIVE_CALL.has(c.status));
      if (open) {
        setActiveBanner(
          `Call placed to ${open.callee_name}. Status: ${callStatusLabel(open.status)}. Please wait for the candidate to accept.`,
        );
      } else {
        setActiveBanner(null);
      }
    } catch {
      // keep silent during background poll
    } finally {
      setLiveSyncing(false);
    }
  }, [loadLists]);

  useEffect(() => {
    loadLists().catch((e) => toast.error(String(e.message || e)));
  }, []);

  useEffect(() => {
    const hasOpen = calls.some((c) => ACTIVE_CALL.has(c.status));
    if (!hasOpen) return;
    const t = setInterval(() => {
      syncLive().catch(() => undefined);
    }, 4000);
    return () => clearInterval(t);
  }, [calls, syncLive]);

  const latestActive = useMemo(() => calls.find((c) => ACTIVE_CALL.has(c.status)), [calls]);

  async function createJob() {
    setBusy(true);
    try {
      await api.post("/api/jobs", { title, company, location, description });
      toast.success("Job saved");
      await loadLists();
    } catch (e) {
      toast.error(String((e as Error).message));
    } finally {
      setBusy(false);
    }
  }

  async function createAgent() {
    setBusy(true);
    try {
      await api.post("/api/agents", { kind: "screening", language: "ENGLISH", voice_persona: "NEHA" });
      toast.success("Live Hunar screening agent created");
      await loadLists();
    } catch (e) {
      toast.error(String((e as Error).message));
    } finally {
      setBusy(false);
    }
  }

  async function addCandidate() {
    if (!candName || !candPhone) return toast.error("Name and phone required");
    setBusy(true);
    try {
      await api.post("/api/candidates", {
        full_name: candName,
        phone: candPhone.startsWith("+") ? candPhone : `+91${candPhone}`,
        job_id: jobId || null,
        source: "manual",
        status: "new",
      });
      toast.success("Candidate added");
      setCandName("");
      setCandPhone("");
      await loadLists();
    } catch (e) {
      toast.error(String((e as Error).message));
    } finally {
      setBusy(false);
    }
  }

  async function screenCandidate(c: Candidate) {
    if (!agentId) return toast.error("Create / select a screening agent first");
    setBusy(true);
    try {
      const call = await api.post<VoiceCall>("/api/calls", {
        agent_id: agentId,
        callee_name: c.full_name,
        mobile_number: c.phone,
        candidate_id: c.id,
        job_id: c.job_id || jobId || null,
        purpose: "screening",
      });
      setActiveBanner(
        `Call placed to ${c.full_name} (${c.phone}). Please wait while the candidate’s phone rings and they accept.`,
      );
      toast.success("Call placed — waiting for candidate to answer");
      await loadLists();
      // kick immediate live sync
      setTimeout(() => syncLive().catch(() => undefined), 1500);
      void call;
    } catch (e) {
      toast.error(String((e as Error).message));
    } finally {
      setBusy(false);
    }
  }

  async function refreshCall(id: number) {
    try {
      await api.post(`/api/calls/${id}/refresh`);
      await loadLists();
      toast.success("Status updated from Hunar");
    } catch (e) {
      toast.error(String((e as Error).message));
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        kicker="Module 01 · Live Hunar Voice"
        title="AI Hiring Assistant"
        description="Create a job, create a real Hunar screening agent, call a candidate, then watch live status."
        action={
          <div className="flex flex-wrap items-center gap-2">
            <LivePill live={!!latestActive || liveSyncing} label={latestActive ? "Live call in progress" : "Idle"} />
            <TipButton tip="Pull latest statuses from Hunar now" variant="outline" size="sm" onClick={() => syncLive()}>
              <RefreshCw className={`size-3.5 ${liveSyncing ? "animate-spin" : ""}`} /> Sync live
            </TipButton>
          </div>
        }
      />

      {(activeBanner || latestActive) && (
        <div className="flex gap-3 rounded-2xl border border-teal-200 bg-teal-50 px-4 py-3 text-sm text-teal-900">
          <PhoneCall className="mt-0.5 size-5 shrink-0 text-teal-700" />
          <div>
            <p className="font-semibold">Call placed — please wait</p>
            <p className="mt-0.5 text-teal-800">
              {activeBanner ||
                `Calling ${latestActive?.callee_name}. ${callStatusLabel(latestActive?.status || "")}. Ask the candidate to accept the call.`}
            </p>
            {latestActive ? (
              <p className="mt-1 font-mono text-xs text-teal-700">
                Live status: {latestActive.status} · auto-updates every 4s
              </p>
            ) : null}
          </div>
        </div>
      )}

      <div className="grid gap-5 lg:grid-cols-2 lg:items-start">
        <Panel title="Create job" description="Saved locally. JD is parsed for skills and location.">
          <div className="form-grid">
            <Field label="Job title">
              <Input className="h-10" value={title} onChange={(e) => setTitle(e.target.value)} />
            </Field>
            <div className="form-grid-2">
              <Field label="Company">
                <Input className="h-10" value={company} onChange={(e) => setCompany(e.target.value)} />
              </Field>
              <Field label="Location">
                <Input className="h-10" value={location} onChange={(e) => setLocation(e.target.value)} />
              </Field>
            </div>
            <Field label="Job description">
              <Textarea className="min-h-[120px]" rows={5} value={description} onChange={(e) => setDescription(e.target.value)} />
            </Field>
            <TipButton tip="Save this job to the database" disabled={busy} onClick={createJob}>
              Save job
            </TipButton>
          </div>
        </Panel>

        <Panel title="Agent + candidate" description="Creates a real agent on Hunar. Use your own phone to test.">
          <div className="form-grid">
            <TipButton tip="Create a live screening agent on Hunar" disabled={busy} onClick={createAgent}>
              Create screening agent on Hunar
            </TipButton>
            <div className="flex flex-wrap gap-2">
              {agents.map((a) => (
                <button
                  key={a.id}
                  type="button"
                  title={`Select agent ${a.name}`}
                  onClick={() => setAgentId(a.id)}
                  className={`rounded-full border px-3 py-1 text-xs font-medium ${
                    agentId === a.id ? "border-teal-700 bg-teal-700 text-white" : "border-border bg-white text-slate-600"
                  }`}
                >
                  #{a.id} {a.name}
                </button>
              ))}
            </div>
            <Field label="Job for candidate">
              <select className="field-control" value={jobId} onChange={(e) => setJobId(e.target.value ? Number(e.target.value) : "")}>
                <option value="">None</option>
                {jobs.map((j) => (
                  <option key={j.id} value={j.id}>
                    {j.title} · {j.location}
                  </option>
                ))}
              </select>
            </Field>
            <div className="form-grid-2">
              <Field label="Candidate name">
                <Input className="h-10" value={candName} onChange={(e) => setCandName(e.target.value)} placeholder="Your name" />
              </Field>
              <Field label="Mobile (+91…)">
                <Input className="h-10" value={candPhone} onChange={(e) => setCandPhone(e.target.value)} placeholder="+9198XXXXXXXX" />
              </Field>
            </div>
            <TipButton tip="Add candidate to this job" disabled={busy} variant="secondary" onClick={addCandidate}>
              Add candidate
            </TipButton>
          </div>
        </Panel>
      </div>

      <Panel title="Candidates" description="Status updates live while a call is ringing or in progress.">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Phone</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {candidates.map((c) => (
                <TableRow key={c.id}>
                  <TableCell className="font-medium">{c.full_name}</TableCell>
                  <TableCell className="font-mono text-xs sm:text-sm">{c.phone}</TableCell>
                  <TableCell>
                    <Badge variant={c.status === "calling" || c.status === "on_call" ? "default" : "outline"}>
                      {candidateStatusLabel(c.status)}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <TipButton tip="Call this candidate with Voice AI" size="sm" disabled={busy || !c.phone} onClick={() => screenCandidate(c)}>
                      Screen with Voice AI
                    </TipButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </Panel>

      <Panel title="Screening calls" description="Live Hunar statuses: queued → ringing → on call → completed.">
        <div className="space-y-3">
          {calls.map((call) => (
            <div
              key={call.id}
              className={`rounded-xl border p-3 sm:p-4 ${
                ACTIVE_CALL.has(call.status) ? "border-teal-300 bg-teal-50" : "border-border bg-slate-50"
              }`}
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <p className="font-medium text-slate-900">
                    {call.callee_name}{" "}
                    <Badge variant={ACTIVE_CALL.has(call.status) ? "default" : "outline"}>{call.status}</Badge>
                  </p>
                  <p className="mt-1 text-sm text-slate-600">{callStatusLabel(call.status)}</p>
                  <p className="font-mono text-xs text-slate-500">{call.mobile_number}</p>
                </div>
                <TipButton tip="Fetch latest call result from Hunar" size="sm" variant="outline" onClick={() => refreshCall(call.id)}>
                  <RefreshCw className="size-3.5" /> Refresh
                </TipButton>
              </div>
              {ACTIVE_CALL.has(call.status) ? (
                <p className="mt-2 text-sm font-medium text-teal-800">
                  Waiting for candidate to accept the call…
                </p>
              ) : null}
              {call.result && Object.keys(call.result).length > 0 ? (
                <pre className="mt-3 overflow-auto rounded-lg border border-border bg-white p-3 font-mono text-xs text-slate-700">
                  {JSON.stringify(call.result, null, 2)}
                </pre>
              ) : null}
            </div>
          ))}
          {!calls.length ? <p className="text-sm text-slate-500">No screening calls yet.</p> : null}
        </div>
      </Panel>
    </div>
  );
}
