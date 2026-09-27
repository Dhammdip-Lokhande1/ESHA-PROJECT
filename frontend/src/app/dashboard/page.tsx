"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { fetchMyDashboardSummary } from "@/lib/api";
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  PieChart, Pie, Cell
} from "recharts";
import { Activity, AlertTriangle, FileCode, Lock, ArrowRight, Sparkles } from "lucide-react";

interface TransformationBreakdownItem {
  name: string;
  value: number;
}

interface RecentRunItem {
  id: string;
  file_a_name: string;
  file_b_name: string;
  fusion_score: number;
  transformation_type: string;
  created_at: string;
}

interface MyDashboardSummaryData {
  user_id: string;
  username: string;
  total_runs: number;
  flagged_count: number;
  avg_fusion_score: number;
  score_distribution: Array<{ bucket: string; count: number }>;
  transformation_breakdown: TransformationBreakdownItem[];
  recent_runs: RecentRunItem[];
}

export default function MyDashboardPage() {
  const { user, isLoading: authLoading } = useAuth();
  const [data, setData] = useState<MyDashboardSummaryData | null>(null);
  const [fetching, setFetching] = useState(true);

  useEffect(() => {
    if (!user) return;

    let isMounted = true;
    fetchMyDashboardSummary()
      .then((res) => {
        if (isMounted) setData(res);
      })
      .catch(console.error)
      .finally(() => {
        if (isMounted) setFetching(false);
      });

    return () => {
      isMounted = false;
    };
  }, [user]);

  if (authLoading || (user && fetching && !data)) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center p-6 text-slate-400">
        Loading your personal dashboard...
      </div>
    );
  }

  // 1. Guest Access Control Guard
  if (!user) {
    return (
      <div className="min-h-[75vh] flex items-center justify-center p-6 max-w-xl mx-auto">
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 text-center shadow-2xl backdrop-blur-xl">
          <div className="w-14 h-14 bg-blue-600/10 border border-blue-500/20 rounded-2xl flex items-center justify-center mx-auto mb-6 text-blue-400">
            <Lock className="w-7 h-7" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">Authentication Required</h2>
          <p className="text-sm text-slate-400 mb-8 leading-relaxed">
            The Personal Analysis Dashboard is saved to your account. Login or Sign Up to track your submission history, score distributions, and evidence reports.
          </p>
          <div className="flex items-center justify-center gap-4">
            <Link
              href="/login"
              className="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-semibold rounded-xl border border-slate-700 transition-all"
            >
              Login
            </Link>
            <Link
              href="/register"
              className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold rounded-xl shadow-lg shadow-blue-600/20 transition-all"
            >
              Sign Up
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (!data) {
    return <div className="p-12 text-center text-rose-400">Failed to load dashboard data.</div>;
  }

  const COLORS = ['#818cf8', '#34d399', '#fbbf24', '#f87171', '#a78bfa'];
  const HISTOGRAM_COLOR = "#818cf8";

  return (
    <div className="container mx-auto px-4 py-12 max-w-7xl">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">My Analysis Dashboard</h1>
          <p className="text-sm text-slate-400 mt-1">
            Personal analytics for <span className="text-slate-200 font-semibold">{user.username}</span> — strictly scoped to your analysis submissions.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-xl shadow-lg transition-all"
          >
            <Sparkles className="w-4 h-4" />
            New Comparison
          </Link>
        </div>
      </div>

      {/* 2. Zero-state Check */}
      {data.total_runs === 0 ? (
        <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-12 text-center my-8 shadow-xl">
          <FileCode className="w-12 h-12 text-slate-600 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-slate-200 mb-2">No Analyses Yet</h3>
          <p className="text-sm text-slate-400 max-w-md mx-auto mb-6">
            You haven&apos;t run any code comparisons while logged in. Start a comparison or batch analysis to view your personal similarity stats!
          </p>
          <Link
            href="/"
            className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold rounded-xl shadow-lg transition-all"
          >
            Run First Analysis
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      ) : (
        <>
          {/* Summary Stat Row */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <StatCard 
              title="My Comparisons" 
              value={data.total_runs} 
              icon={<FileCode className="w-5 h-5" />} 
              color="text-indigo-400"
            />
            <StatCard 
              title="My Flagged Cases (Score > 0.8)" 
              value={data.flagged_count} 
              icon={<AlertTriangle className="w-5 h-5" />}
              color="text-amber-400" 
            />
            <StatCard 
              title="My Average Fusion Score" 
              value={`${(data.avg_fusion_score * 100).toFixed(1)}%`} 
              icon={<Activity className="w-5 h-5" />}
              color="text-emerald-400"
            />
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
            {/* Score Distribution */}
            <div className="bg-[var(--color-panel)] border border-[var(--color-panel-border)] rounded-xl p-6 shadow-md">
              <h2 className="text-xl font-bold text-slate-100 mb-6">My Score Distribution</h2>
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

            {/* Transformation Breakdown */}
            <div className="bg-[var(--color-panel)] border border-[var(--color-panel-border)] rounded-xl p-6 shadow-md">
              <h2 className="text-xl font-bold text-slate-100 mb-6">My Transformation Types</h2>
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
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Recent Runs Table */}
          <div className="bg-[var(--color-panel)] border border-[var(--color-panel-border)] rounded-2xl p-6 shadow-xl">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">Recent Analyses</h2>
              <Link href="/history" className="text-xs font-semibold text-blue-400 hover:text-blue-300 transition-colors">
                View Full History &rarr;
              </Link>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-950 text-slate-400 uppercase text-xs tracking-wider border-b border-slate-800">
                  <tr>
                    <th className="py-3 px-4">Files</th>
                    <th className="py-3 px-4">Score</th>
                    <th className="py-3 px-4">Transformation</th>
                    <th className="py-3 px-4">Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50">
                  {data.recent_runs.map((r) => (
                    <tr key={r.id} className="hover:bg-slate-850/50 transition-colors">
                      <td className="py-3.5 px-4 font-mono text-xs text-white">
                        {r.file_a_name} vs {r.file_b_name}
                      </td>
                      <td className="py-3.5 px-4 font-bold">
                        <span className={r.fusion_score >= 0.8 ? "text-red-400" : r.fusion_score >= 0.5 ? "text-amber-400" : "text-emerald-400"}>
                          {(r.fusion_score * 100).toFixed(1)}%
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-xs font-mono text-slate-400">
                        {r.transformation_type || "N/A"}
                      </td>
                      <td className="py-3.5 px-4 text-xs text-slate-500">
                        {r.created_at ? new Date(r.created_at).toLocaleDateString() : ""}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
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
