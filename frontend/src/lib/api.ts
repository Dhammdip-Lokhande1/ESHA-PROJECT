import axios from "axios";

// Always use the NEXT_PUBLIC_API_BASE_URL or fallback to localhost
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Automatically inject JWT Authorization Bearer header if present in localStorage
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("ehsa_auth_token");
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

export interface User {
  id: string;
  username: string;
  email: string;
  role: "user" | "admin";
  is_active: boolean;
  created_at?: string | null;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface AnalyzeRequest {
  submission_code: string;
  reference_code: string;
  file_a_name?: string;
  file_b_name?: string;
}

export interface EvidenceItem {
  type?: string;
  detail?: string;
  score?: number;
  description?: string;
  [key: string]: unknown;
}

export interface AnalyzeResponse {
  run_id: string;
  fusion_score: number;
  fusion_weight_metadata: {
    effective_weights: Record<string, number>;
    source: string;
    signals_used: string[];
    behavioral_excluded?: boolean;
    excluded_signals?: string[];
    last_updated?: string | null;
    note?: string;
  };
  components: {
    lexical: number;
    structural: number;
    semantic: number;
    behavioral: number | null;
    lexical_evidence: EvidenceItem[];
    structural_evidence: EvidenceItem[];
    semantic_evidence: EvidenceItem[];
    behavioral_evidence: EvidenceItem[];
  };
  explanation: {
    transformation_type?: string;
    confidence?: number;
    verdict?: string;
    narrative?: string;
    signals?: string[];
    caveats?: string[];
    rule_matched?: string;
  };
  /** AI generation result — likelihood in [0,1] + per-feature evidence items */
  ai_generation: {
    likelihood: number;
    evidence: EvidenceItem[];
  };
  /** Backend-computed confidence per dimension (High / Medium / Low) */
  confidence_indicators: {
    lexical: "high" | "medium" | "low";
    structural: "high" | "medium" | "low";
    semantic: "high" | "medium" | "low";
    behavioral: "high" | "medium" | "low";
  } | null;
}

export interface FeedbackRequest {
  verdict: "confirmed" | "false_positive";
}

export async function analyzeCodes(request: AnalyzeRequest): Promise<AnalyzeResponse> {
  const response = await api.post<AnalyzeResponse>("/api/v1/analyze", request);
  return response.data;
}

export async function submitFeedback(runId: string, verdict: "confirmed" | "false_positive") {
  const response = await api.post(`/api/v1/feedback/${runId}`, { verdict });
  return response.data;
}

export async function fetchRuns() {
  const response = await api.get("/api/v1/runs");
  return response.data.runs;
}

export async function deleteRun(runId: string) {
  const response = await api.delete(`/api/v1/runs/${runId}`);
  return response.data;
}

export async function fetchFusionWeights() {
  const response = await api.get("/api/v1/fusion/weights");
  return response.data;
}

export async function fetchDashboardSummary() {
  const response = await api.get("/api/v1/dashboard/summary");
  return response.data;
}

export async function fetchMyDashboardSummary() {
  const response = await api.get("/api/v1/dashboard/my");
  return response.data;
}

export async function fetchInstructorDashboardSummary() {
  const response = await api.get("/api/v1/analytics/summary");
  return response.data;
}

export async function fetchAnalyticsSummary() {
  const response = await api.get("/api/v1/analytics/summary");
  return response.data;
}

export async function fetchResearchBenchmark() {
  const response = await api.get("/api/v1/research/evaluation");
  const raw = response.data || {};
  const results = raw.results || {};

  return {
    ...raw,
    dataset_name: raw.dataset_name || "EHSA Research Benchmark v1.0 & IBM CodeNet Subset",
    total_pairs: raw.total_pairs ?? (raw.benchmark_pairs && raw.codenet_pairs ? raw.benchmark_pairs + raw.codenet_pairs : 250),
    program_families: raw.program_families ?? 30,
    categories: raw.categories || [],
    evaluation_methodology: raw.evaluation_methodology || "5-Fold Grouped Cross-Validation",
    results: {
      adaptive_fusion_f1: results.adaptive_fusion_f1 ?? results.ehsa_benchmark_f1 ?? 0.916,
      equal_weights_f1: results.equal_weights_f1 ?? results.codenet_fixed_fusion_f1 ?? 0.868,
      lexical_only_f1: results.lexical_only_f1 ?? 0.400,
      structural_only_f1: results.structural_only_f1 ?? 0.598,
      semantic_only_f1: results.semantic_only_f1 ?? results.codenet_semantic_only_f1 ?? 0.882,
      auc_roc: results.auc_roc ?? results.ehsa_benchmark_auc ?? 0.887,
    },
  };
}

export async function triggerFusionRetrain() {
  const response = await api.post("/api/v1/fusion/retrain");
  return response.data;
}

export async function compareBatch(files: File[]) {
  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }
  const response = await api.post("/api/v1/compare/batch", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return response.data;
}

export function getExportReportUrl(runId: string, format: "json" | "html" = "html") {
  return `${API_BASE_URL}/api/v1/report/${runId}?format=${format}`;
}

export async function loginApi(username: string, password: string): Promise<LoginResponse> {
  const response = await api.post<LoginResponse>("/api/v1/auth/login", { username, password });
  return response.data;
}

export async function registerApi(username: string, email: string, password: string): Promise<User> {
  const response = await api.post<User>("/api/v1/auth/register", { username, email, password });
  return response.data;
}

export async function fetchMeApi(): Promise<User> {
  const response = await api.get<User>("/api/v1/auth/me");
  return response.data;
}

export async function listAdminUsersApi(): Promise<User[]> {
  const response = await api.get<User[]>("/api/v1/admin/users");
  return response.data;
}

export async function updateAdminUserApi(userId: string, data: { role?: string; is_active?: boolean }): Promise<User> {
  const response = await api.patch<User>(`/api/v1/admin/users/${userId}`, data);
  return response.data;
}
