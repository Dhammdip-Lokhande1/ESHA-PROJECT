"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth";
import { fetchAnalyticsSummary, triggerFusionRetrain } from "@/lib/api";
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  PieChart, Pie, Cell, LineChart, Line, Legend
} from "recharts";
import { Activity, AlertTriangle, FileCode, LineChart as LucideLineChart, ClipboardX, RefreshCw, ShieldAlert } from "lucide-react";

interface CalibrationRecord {
  verdict: string;
  score: number;
}

interface TransformationBreakdownItem {
  name: string;
  value: number;
}

interface AnalyticsSummaryData {
  total_runs: number;
  flagged_count: number;
  avg_fusion_score: number;
  score_distribution: Array<{ bucket: string; count: number }>;
  transformation_breakdown: TransformationBreakdownItem[];
  weight_drift_history: Array<{ date: string; lexical: number; structural: number; semantic: number; behavioral: number }>;
  calibration_data: CalibrationRecord[];
}

export default function AnalyticsPage() {
  const { user, isLoading: authLoading } = useAuth();
  const [data, setData] = useState<AnalyticsSummaryData | null>(null);
  const [fetching, setFetching] = useState(true);
  const [retraining, setRetraining] = useState(false);
  const [retrainMsg, setRetrainMsg] = useState<string | null>(null);

  const loadData = () => {
    setFetching(true);
    fetchAnalyticsSummary()
      .then(setData)
      .catch(console.error)
      .finally(() => setFetching(false));
  };

  useEffect(() => {
    if (user) {
      fetchAnalyticsSummary()
        .then(setData)
        .catch(console.error)
        .finally(() => setFetching(false));
    }
  }, [user]);

  const isAuthorized = !!user;

  if (authLoading || (isAuthorized && fetching && !data)) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center p-6 text-slate-400">
        Loading analytics...
      </div>
    );
  }

  // Access Guard
  if (!user) {
    return (
      <div className="min-h-[75vh] flex items-center justify-center p-6 max-w-md mx-auto text-center">
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl">
          <ShieldAlert className="w-12 h-12 text-rose-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">Access Restricted</h2>
          <p className="text-sm text-slate-400 leading-relaxed">
            This dashboard contains aggregate statistics, user feedback calibration, and adaptive model retraining controls. Please log in to access this page.
          </p>
        </div>
      </div>
    );
  }

  if (!data) {
    return <div className="p-12 text-center text-rose-400">Failed to load analytics.</div>;
  }

  const COLORS = ['#818cf8', '#34d399', '#fbbf24', '#f87171', '#a78bfa'];
  const HISTOGRAM_COLOR = "#818cf8";

  const calibrationSummary = {
    "Confirmed Match (High Score)": data.calibration_data.filter((d) => d.verdict === "confirmed" && d.score >= 0.7).length,
    "Confirmed Match (Low Score)": data.calibration_data.filter((d) => d.verdict === "confirmed" && d.score < 0.7).length,
    "False Positive (High Score)": data.calibration_data.filter((d) => d.verdict === "false_positive" && d.score >= 0.7).length,
    "False Positive (Low Score)": data.calibration_data.filter((d) => d.verdict === "false_positive" && d.score < 0.7).length,
  };

  const handleRetrain = async () => {
    setRetraining(true);
    setRetrainMsg(null);
    try {
      const res = await triggerFusionRetrain();
      setRetrainMsg(`Retraining Complete! Updated weights: ${JSON.stringify(res.new_weights)}`);
      loadData();
    } catch (err: unknown) {
      if (typeof err === "object" && err !== null && "response" in err) {
        const axiosErr = err as { response?: { data?: { detail?: string } } };
        setRetrainMsg(axiosErr.response?.data?.detail || "Retraining failed.");
      } else {
        setRetrainMsg("Retraining error.");
      }
    } finally {
      setRetraining(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-12 max-w-7xl">
      {/* Header & Retrain Action */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold text-white">Analytics & Calibration</h1>
            <span className="text-xs font-mono font-bold uppercase px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              {user.role} Access
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Submission aggregates, human verdict calibration, and adaptive fusion model weights.
          </p>
        </div>
        {user?.role === "admin" && (
          <div className="flex items-center gap-3">
            <button
              onClick={handleRetrain}
              disabled={retraining}
              className="flex items-center gap-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-xl shadow-lg transition-all disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${retraining ? "animate-spin" : ""}`} />
              {retraining ? "Retraining Weights..." : "Trigger Model Retraining"}
            </button>
          </div>
        )}
      </div>

      {retrainMsg && (
        <div className="mb-8 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm">
          {retrainMsg}
        </div>
      )}

      {/* 1. Summary Stat Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <StatCard 
          title="Total Submissions" 
          value={data.total_runs} 
          icon={<FileCode className="w-5 h-5" />} 
          color="text-indigo-400"
        />
        <StatCard 
          title="Flagged Runs (Score > 0.8)" 
          value={data.flagged_count} 
          icon={<AlertTriangle className="w-5 h-5" />}
          color="text-amber-400" 
        />
        <StatCard 
          title="Average Score" 
          value={`${(data.avg_fusion_score * 100).toFixed(1)}%`} 
          icon={<Activity className="w-5 h-5" />}
          color="text-emerald-400"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
        {/* 2. Score Distribution */}
        <div className="bg-[var(--color-panel)] border border-[var(--color-panel-border)] rounded-xl p-6 shadow-md">
          <h2 className="text-xl font-bold text-slate-100 mb-6">Score Distribution</h2>
          <div className="h-64 bg-slate-900/50 rounded-lg p-3 border border-slate-800/50">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.score_distribution} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="bucket" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
                <Tooltip 
                  cursor={{ fill: '#334155' }} 
                  contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc' }}
                />
                <Bar dataKey="count" fill={HISTOGRAM_COLOR} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 3. Transformation Breakdown */}
        <div className="bg-[var(--color-panel)] border border-[var(--color-panel-border)] rounded-xl p-6 shadow-md">
          <h2 className="text-xl font-bold text-slate-100 mb-6">Transformation Breakdown</h2>
          <div className="h-64 bg-slate-900/50 rounded-lg p-3 border border-slate-800/50">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.transformation_breakdown}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={75}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {data.transformation_breakdown.map((entry, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc' }}
                  formatter={(value: unknown, name: unknown) => [`${value} runs`, String(name)]}
                />
                <Legend
                  formatter={(value: string) => <span style={{ color: '#94a3b8', fontSize: 12 }}>{value}</span>}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
        {/* 4. Fusion Weight Drift */}
        <div className="bg-[var(--color-panel)] border border-[var(--color-panel-border)] rounded-xl p-6 shadow-md">
          <h2 className="text-xl font-bold text-slate-100 mb-1">Fusion Weight Drift</h2>
          <p className="text-xs text-slate-400 mb-6">Historical adaptation of signal weights based on feedback.</p>
          <div className="h-64 bg-slate-900/50 rounded-lg p-3 border border-slate-800/50">
            {data.weight_drift_history.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data.weight_drift_history} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                  <XAxis
                    dataKey="date"
                    tick={{ fill: '#94a3b8', fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                    tickFormatter={(val: string) => val ? new Date(val).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : ''}
                  />
                  <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} domain={[0, 1]} />
                  <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc' }} />
                  <Legend />
                  <Line type="monotone" dataKey="lexical" stroke="#3b82f6" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="structural" stroke="#10b981" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="semantic" stroke="#f59e0b" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="behavioral" stroke="#ef4444" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex flex-col h-full items-center justify-center text-center p-6 border-2 border-dashed border-slate-700/50 rounded-xl bg-slate-900/20">
                <LucideLineChart className="w-8 h-8 text-slate-500 mb-3" />
                <h3 className="text-sm font-medium text-slate-300">No Retraining History</h3>
                <p className="text-xs text-slate-500 mt-1 max-w-[200px]">Model weights have not been adaptively retrained yet.</p>
              </div>
            )}
          </div>
        </div>

        {/* 5. Feedback Calibration */}
        <div className="bg-[var(--color-panel)] border border-[var(--color-panel-border)] rounded-xl p-6 shadow-md">
          <h2 className="text-xl font-bold text-slate-100 mb-1">Analysis Feedback Calibration</h2>
          <p className="text-xs text-slate-400 mb-6">Alignment of automated scores against user verdicts.</p>
          <div className="h-64 flex items-center justify-center bg-slate-900/50 rounded-lg p-3 border border-slate-800/50">
            {data.calibration_data.length > 0 ? (
              <div className="grid grid-cols-2 gap-4 w-full">
                <div className="p-4 bg-emerald-900/20 border border-emerald-900/50 rounded-lg text-center">
                  <div className="text-xs text-emerald-400/70 mb-1">True Positives</div>
                  <div className="text-3xl font-light text-emerald-400">{calibrationSummary["Confirmed Match (High Score)"]}</div>
                  <div className="text-[10px] text-slate-500 mt-1">Confirmed &gt; 70%</div>
                </div>
                <div className="p-4 bg-amber-900/20 border border-amber-900/50 rounded-lg text-center">
                  <div className="text-xs text-amber-400/70 mb-1">False Positives</div>
                  <div className="text-3xl font-light text-amber-400">{calibrationSummary["False Positive (High Score)"]}</div>
                  <div className="text-[10px] text-slate-500 mt-1">Rejected &gt; 70%</div>
                </div>
                <div className="p-4 bg-rose-900/20 border border-rose-900/50 rounded-lg text-center">
                  <div className="text-xs text-rose-400/70 mb-1">False Negatives</div>
                  <div className="text-3xl font-light text-rose-400">{calibrationSummary["Confirmed Match (Low Score)"]}</div>
                  <div className="text-[10px] text-slate-500 mt-1">Confirmed &lt; 70%</div>
                </div>
                <div className="p-4 bg-slate-700/20 border border-slate-700/50 rounded-lg text-center">
                  <div className="text-xs text-slate-400/70 mb-1">True Negatives</div>
                  <div className="text-3xl font-light text-slate-400">{calibrationSummary["False Positive (Low Score)"]}</div>
                  <div className="text-[10px] text-slate-500 mt-1">Rejected &lt; 70%</div>
                </div>
              </div>
            ) : (
              <div className="flex flex-col h-full items-center justify-center text-center p-6 border-2 border-dashed border-slate-700/50 rounded-xl bg-slate-900/20 w-full">
                <ClipboardX className="w-8 h-8 text-slate-500 mb-3" />
                <h3 className="text-sm font-medium text-slate-300">No Feedback Recorded</h3>
                <p className="text-xs text-slate-500 mt-1 max-w-[250px]">No verdicts submitted on analysis runs yet.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon, color }: { title: string, value: string | number, icon: React.ReactNode, color: string }) {
  return (
    <div className="bg-[var(--color-panel)] border border-[var(--color-panel-border)] rounded-xl p-6 shadow-md flex items-center justify-between">
      <div>
        <h3 className="text-sm font-medium text-slate-400 mb-1">{title}</h3>
        <p className="text-3xl font-semibold text-slate-100">{value}</p>
      </div>
      <div className={`p-3 bg-slate-900/50 rounded-lg ${color}`}>
        {icon}
      </div>
    </div>
  );
}
