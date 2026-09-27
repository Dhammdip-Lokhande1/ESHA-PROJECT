"use client";

import React, { useEffect, useState } from "react";
import { fetchRuns, getExportReportUrl, deleteRun } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { History, Download, FileText, ArrowRight, RefreshCcw, Trash2, Shield } from "lucide-react";
import Link from "next/link";

interface RunData {
  id: string;
  file_a_name: string;
  file_b_name: string;
  fusion_score: number;
  transformation_type: string;
  created_at: string;
}

export default function HistoryPage() {
  const { user, isLoading: authLoading } = useAuth();
  const [runs, setRuns] = useState<RunData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [runToDelete, setRunToDelete] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [toastMessage, setToastMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  const showToast = (type: 'success' | 'error', text: string) => {
    setToastMessage({ type, text });
    setTimeout(() => setToastMessage(null), 3000);
  };

  const handleDelete = async () => {
    if (!runToDelete) return;
    setIsDeleting(true);
    try {
      await deleteRun(runToDelete);
      setRuns(runs.filter(r => r.id !== runToDelete));
      showToast('success', 'Investigation deleted successfully.');
    } catch {
      showToast('error', 'Failed to delete investigation.');
    } finally {
      setIsDeleting(false);
      setRunToDelete(null);
    }
  };


  const loadRuns = async () => {
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      const data = await fetchRuns();
      setRuns(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to fetch runs.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!user) return;

    let isMounted = true;
    fetchRuns()
      .then((data) => {
        if (isMounted) setRuns(data);
      })
      .catch((err: unknown) => {
        if (isMounted) setError(err instanceof Error ? err.message : "Failed to fetch runs.");
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });
    return () => {
      isMounted = false;
    };
  }, [user]);

  if (authLoading) {
    return (
      <div className="container mx-auto px-4 py-16 text-center text-slate-400">
        Loading investigation history...
      </div>
    );
  }

  if (!user) {
    return (
      <main className="min-h-[80vh] flex items-center justify-center p-6 bg-slate-950 text-slate-100">
        <div className="max-w-md w-full text-center p-8 bg-slate-900 border border-slate-800 rounded-2xl shadow-xl">
          <Shield className="h-12 w-12 text-blue-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">Authentication Required</h2>
          <p className="text-sm text-slate-400 mb-6">
            Please log in to view your private investigation history.
          </p>
          <Link
            href="/login"
            className="inline-flex items-center justify-center gap-2 px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold rounded-xl transition-all shadow-md"
          >
            Login
          </Link>
        </div>
      </main>
    );
  }

  return (
    <div className="container mx-auto px-4 py-12 max-w-7xl">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
            <History className="w-8 h-8 text-indigo-500" />
            Investigation History
          </h1>
          <p className="text-slate-400">View past pairwise comparisons and export evidence reports.</p>
        </div>
        <button
          onClick={loadRuns}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium rounded-lg transition-colors border border-slate-700"
        >
          <RefreshCcw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {error && (
        <div className="bg-rose-900/30 border border-rose-500/50 text-rose-200 p-4 rounded-lg mb-6">
          {error}
        </div>
      )}

      {toastMessage && (
        <div className={`fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-lg text-sm font-medium z-50 animate-in fade-in slide-in-from-bottom-5 ${toastMessage.type === 'success' ? 'bg-emerald-900/90 text-emerald-100 border border-emerald-500/50' : 'bg-rose-900/90 text-rose-100 border border-rose-500/50'}`}>
          {toastMessage.text}
        </div>
      )}

      {runToDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="bg-[var(--color-panel)] border border-[var(--color-panel-border)] p-6 rounded-xl shadow-2xl max-w-sm w-full mx-4">
            <h3 className="text-xl font-bold text-white mb-2">Delete Investigation?</h3>
            <p className="text-slate-400 text-sm mb-6">
              This will permanently remove this investigation from your history.<br/>
              This action cannot be undone.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setRunToDelete(null)}
                disabled={isDeleting}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium rounded-lg transition-colors border border-slate-700"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={isDeleting}
                className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white font-medium rounded-lg transition-colors border border-rose-500 flex items-center gap-2"
              >
                {isDeleting ? <RefreshCcw className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="bg-[var(--color-panel)] border border-[var(--color-panel-border)] rounded-xl overflow-hidden shadow-md">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-900/50 text-slate-400 uppercase text-xs font-semibold">
              <tr>
                <th className="px-6 py-4">Date</th>
                <th className="px-6 py-4">Files Compared</th>
                <th className="px-6 py-4">Fusion Score</th>
                <th className="px-6 py-4">Transformation</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {loading && runs.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-slate-500">
                    Loading history...
                  </td>
                </tr>
              ) : runs.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-slate-500">
                    No runs found. Start an analysis to see history.
                  </td>
                </tr>
              ) : (
                runs.map((run) => (
                  <tr key={run.id} className="hover:bg-slate-800/80 transition-colors group">
                    <td className="px-6 py-4 whitespace-nowrap text-left">
                      {new Date(run.created_at).toLocaleDateString()}{" "}
                      <span className="text-slate-500 ml-1">
                        {new Date(run.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-medium text-slate-200 text-left">
                      <div className="flex items-center gap-2">
                        {run.file_a_name} <span className="text-slate-500">vs</span> {run.file_b_name}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-left">
                      <div className="flex items-center gap-3">
                        <div className="w-24 h-3 bg-slate-900 rounded-full overflow-hidden border border-slate-700/50">
                          <div 
                            className={`h-full transition-all duration-500 ${run.fusion_score >= 0.8 ? 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.6)]' : run.fusion_score <= 0.5 ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]'}`}
                            style={{ width: `${Math.round(run.fusion_score * 100)}%` }}
                          />
                        </div>
                        <span className={`font-bold w-12 ${run.fusion_score >= 0.8 ? 'text-rose-400' : run.fusion_score <= 0.5 ? 'text-emerald-400' : 'text-amber-400'}`}>
                          {(run.fusion_score * 100).toFixed(1)}%
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-left">
                      <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-slate-700/50 text-slate-300 border border-slate-600">
                        {run.transformation_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right flex justify-end gap-3">
                      <div className="flex bg-slate-900/50 rounded-lg border border-slate-700 overflow-hidden">
                        <a 
                          href={getExportReportUrl(run.id, "html")} 
                          title="Download HTML Report (Print to PDF)"
                          className="px-3 py-1.5 hover:bg-slate-700 transition-colors border-r border-slate-700 flex items-center text-slate-300"
                        >
                          <FileText className="w-4 h-4" />
                        </a>
                        <a 
                          href={getExportReportUrl(run.id, "json")} 
                          title="Download JSON Raw Data"
                          className="px-3 py-1.5 hover:bg-slate-700 transition-colors flex items-center text-slate-300 border-r border-slate-700"
                        >
                          <Download className="w-4 h-4" />
                        </a>
                        <button
                          onClick={() => setRunToDelete(run.id)}
                          title="Delete Investigation"
                          className="px-3 py-1.5 hover:bg-rose-900/50 hover:text-rose-400 transition-colors flex items-center text-slate-400"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                      
                      {run.file_a_name && run.file_b_name && (
                        <Link 
                          href={`/?sub=${encodeURIComponent(run.file_a_name)}&ref=${encodeURIComponent(run.file_b_name)}`}
                          className="px-3 py-1.5 bg-indigo-600/20 text-indigo-400 hover:bg-indigo-600 hover:text-white rounded-lg border border-indigo-500/30 transition-colors flex items-center gap-1 text-sm font-medium"
                        >
                          View <ArrowRight className="w-3 h-3" />
                        </Link>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
