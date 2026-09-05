"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { api, type Agent, type Candidate, type Job } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { TipButton } from "@/components/tip-button";
import { Field, LivePill, PageHeader, Panel } from "@/components/page-shell";

type SearchResult = {
  parsed: Record<string, unknown>;
  provider_used: string;
  people: Array<{ full_name: string; source: string; score: number }>;
  saved: Candidate[];
};

export default function SearchPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [jobId, setJobId] = useState<number | "">("");
  const [provider, setProvider] = useState("auto");
  const [description, setDescription] = useState("");
  const [result, setResult] = useState<SearchResult | null>(null);
  const [selected, setSelected] = useState<number[]>([]);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [busy, setBusy] = useState(false);
  const [channels, setChannels] = useState({ voice: true, whatsapp: true, email: false });

  async function refresh() {
    const [j, a] = await Promise.all([api.get<Job[]>("/api/jobs"), api.get<Agent[]>("/api/agents")]);
    setJobs(j);
    setAgents(a);
    if (!jobId && j[0]) {
      setJobId(j[0].id);
      setDescription(j[0].description);
    }
  }

  useEffect(() => {
    refresh().catch((e) => toast.error(String(e.message || e)));
  }, []);

  useEffect(() => {
    if (!jobId) return;
    const job = jobs.find((j) => j.id === jobId);
    if (job) setDescription(job.description);
    api.get<Candidate[]>(`/api/candidates?job_id=${jobId}`).then(setCandidates).catch(() => undefined);
  }, [jobId, jobs]);

  async function runSearch() {
    if (!jobId) return toast.error("Select a job");
    setBusy(true);
    try {
      const data = await api.post<SearchResult>("/api/search", {
        job_id: jobId,
        description,
        provider,
        limit: 20,
        save_to_job: true,
      });
      setResult(data);
      setCandidates(data.saved);
      setSelected(data.saved.slice(0, 5).map((c) => c.id));
      toast.success(`Found ${data.people.length} via ${data.provider_used}`);
    } catch (e) {
      toast.error(String((e as Error).message));
    } finally {
      setBusy(false);
    }
  }

  async function ensureOutreachAgent() {
    const existing = agents.find((a) => a.kind === "outreach");
    if (existing) return existing;
    const created = await api.post<Agent>("/api/agents", {
      kind: "outreach",
      language: "ENGLISH",
      voice_persona: "ROY",
    });
    setAgents((prev) => [created, ...prev]);
    return created;
  }

  async function launchOutreach() {
    if (!jobId || !selected.length) return toast.error("Select candidates");
    setBusy(true);
    try {
      const agent = channels.voice ? await ensureOutreachAgent() : null;
      const channelList = Object.entries(channels)
        .filter(([, on]) => on)
        .map(([k]) => k);
      const res = await api.post<{ id: number; calls_placed: number }>("/api/outreach/launch", {
        job_id: jobId,
        candidate_ids: selected,
        agent_id: agent?.id,
        channels: channelList,
      });
      toast.success(`Campaign #${res.id} · ${res.calls_placed} voice calls`);
      await refresh();
    } catch (e) {
      toast.error(String((e as Error).message));
    } finally {
      setBusy(false);
    }
  }

  function toggle(id: number) {
    setSelected((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));
  }

  const providerLive = result?.provider_used === "pdl" || result?.provider_used === "apollo";

  return (
    <div className="space-y-6">
      <PageHeader
        kicker="Module 02 · Search + Reachout"
        title="People Search & Reachout"
        description="Search people from a job description, then launch Voice AI and messaging reachout."
        action={
          <LivePill live={providerLive} label={result ? `Last search: ${result.provider_used}` : "PDL/Apollo keys optional"} />
        }
      />

      <Panel title="Search from job description" description="Auto uses PDL → Apollo → built-in talent index.">
        <div className="form-grid">
          <div className="form-grid-2">
            <Field label="Job">
              <select className="field-control" value={jobId} onChange={(e) => setJobId(Number(e.target.value))}>
                {jobs.map((j) => (
                  <option key={j.id} value={j.id}>
                    {j.title} · {j.location}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Provider">
              <select className="field-control" value={provider} onChange={(e) => setProvider(e.target.value)}>
                <option value="auto">Auto (PDL → Apollo → built-in)</option>
                <option value="pdl">People Data Labs</option>
                <option value="apollo">Apollo.io</option>
                <option value="demo">Built-in talent index</option>
              </select>
            </Field>
          </div>
          <Field label="Job description">
            <Textarea className="min-h-[120px]" rows={5} value={description} onChange={(e) => setDescription(e.target.value)} />
          </Field>
          <TipButton tip="Search people and save matches to this job" disabled={busy} onClick={runSearch}>
            Search & save matches
          </TipButton>
          {result ? (
            <p className="text-sm text-slate-500">
              Provider used: <Badge variant="outline">{result.provider_used}</Badge>
            </p>
          ) : null}
        </div>
      </Panel>

      <Panel title="Matched people" description="Select people, choose channels, then launch.">
        <div className="mb-4 flex flex-col gap-3 rounded-xl border border-border bg-slate-50 p-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex flex-wrap gap-4 text-sm text-slate-700">
            {(["voice", "whatsapp", "email"] as const).map((ch) => (
              <label key={ch} className="flex items-center gap-2 capitalize" title={`Include ${ch} in reachout`}>
                <input
                  type="checkbox"
                  checked={channels[ch]}
                  onChange={(e) => setChannels((prev) => ({ ...prev, [ch]: e.target.checked }))}
                />
                {ch}
              </label>
            ))}
          </div>
          <TipButton tip="Start reachout for selected people" disabled={busy || !selected.length} onClick={launchOutreach}>
            Launch ({selected.length})
          </TipButton>
        </div>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-10" />
                <TableHead>Name</TableHead>
                <TableHead>Headline</TableHead>
                <TableHead>Location</TableHead>
                <TableHead>Score</TableHead>
                <TableHead>Source</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {candidates.map((c) => (
                <TableRow key={c.id}>
                  <TableCell>
                    <input
                      type="checkbox"
                      title={`Select ${c.full_name}`}
                      checked={selected.includes(c.id)}
                      onChange={() => toggle(c.id)}
                    />
                  </TableCell>
                  <TableCell>
                    <div className="font-medium">{c.full_name}</div>
                    <div className="text-xs text-slate-500">{c.phone || c.email}</div>
                  </TableCell>
                  <TableCell>{c.headline}</TableCell>
                  <TableCell>{c.location}</TableCell>
                  <TableCell className="font-mono text-teal-700">{c.score}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{c.source}</Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
        {!candidates.length ? <p className="mt-3 text-sm text-slate-500">Run a search to populate matches.</p> : null}
      </Panel>
    </div>
  );
}
