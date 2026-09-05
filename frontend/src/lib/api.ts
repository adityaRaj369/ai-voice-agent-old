const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  detail: unknown;
  constructor(status: number, detail: unknown) {
    super(typeof detail === "string" ? detail : JSON.stringify(detail));
    this.status = status;
    this.detail = detail;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    cache: "no-store",
  });
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  if (!res.ok) {
    throw new ApiError(res.status, data?.detail || data || res.statusText);
  }
  return data as T;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "POST", body: body ? JSON.stringify(body) : undefined }),
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "PATCH", body: body ? JSON.stringify(body) : undefined }),
};

export type Job = {
  id: number;
  title: string;
  company: string;
  location: string;
  description: string;
  employment_type: string;
  parsed: Record<string, unknown>;
  created_at?: string;
};

export type Candidate = {
  id: number;
  job_id?: number | null;
  full_name: string;
  phone: string;
  email: string;
  headline: string;
  location: string;
  skills: string[];
  source: string;
  profile_url: string;
  status: string;
  score: number;
};

export type Agent = {
  id: number;
  hunar_agent_id: string;
  name: string;
  kind: string;
  language: string;
  voice_persona: string;
  objective: string;
};

export type VoiceCall = {
  id: number;
  hunar_call_id: string;
  purpose: string;
  callee_name: string;
  mobile_number: string;
  status: string;
  result: Record<string, unknown>;
  recording_url: string;
  candidate?: Candidate | null;
  agent?: Agent | null;
  created_at?: string;
};

export type Site = {
  id: number;
  code: string;
  name: string;
  city: string;
  landline: string;
  supervisor_name: string;
  supervisor_phone: string;
  present?: number | null;
  headcount?: number | null;
};

export type Worker = {
  id: number;
  employee_code: string;
  name: string;
  site_id: number;
  shift: string;
  spoken_pin: string;
  rfid: string;
  site?: Site | null;
};
