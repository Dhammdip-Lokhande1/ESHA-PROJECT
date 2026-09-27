"use client";

import React, { useState, useMemo } from "react";
import { compareBatch } from "@/lib/api";
import { Upload, AlertCircle, RefreshCcw, SlidersHorizontal, ArrowRight } from "lucide-react";
import Link from "next/link";

interface BatchResult {
  run_id: string;
  file_a: string;
  file_b: string;
  fusion_score: number;
  transformation_type: string;
}

export default function BatchPage() {
  const [files, setFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<BatchResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [threshold, setThreshold] = useState<number>(0.75);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selected = Array.from(e.target.files);
      if (selected.length > 20) {
        setError("Maximum 20 files allowed at once.");
        setFiles(selected.slice(0, 20));
      } else {
        setError(null);
        setFiles(selected);
      }
    }
  };

  const handleProcess = async () => {
    if (files.length < 2) {
      setError("Please select at least 2 files to compare.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await compareBatch(files);
      setResults(data.matrix);
    } catch (err: unknown) {
      const detail = err && typeof err === "object" && "response" in err 
        ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail 
        : null;
      setError(detail || "An error occurred during batch processing.");
    } finally {
      setLoading(false);
    }
  };

  // Derive unique filenames from results for the matrix
  const fileNames = useMemo(() => {
    if (results.length === 0) return [];
    const names = new Set<string>();
    results.forEach((r) => {
      names.add(r.file_a);
      names.add(r.file_b);
    });
    return Array.from(names).sort();
  }, [results]);

  // Fast lookup for score given two filenames
  const scoreLookup = useMemo(() => {
    const map = new Map<string, BatchResult>();
    results.forEach((r) => {
      map.set(`${r.file_a}|${r.file_b}`, r);
      map.set(`${r.file_b}|${r.file_a}`, r);
    });
    return map;
  }, [results]);

  // Safe to Warning color mapping
  const getColor = (score: number) => {
    if (score < threshold) return "bg-emerald-950/40 text-emerald-500/70 border-emerald-900/50";
    
    // Scale intensity based on how much it exceeds threshold
    const intensity = (score - threshold) / (1 - threshold);
    
    if (intensity > 0.8) return "bg-rose-600 text-white font-bold border-rose-500 shadow-[0_0_10px_rgba(225,29,72,0.6)]";
    if (intensity > 0.5) return "bg-rose-500/80 text-white font-semibold border-rose-500/70 shadow-[0_0_8px_rgba(225,29,72,0.4)]";
    if (intensity > 0.2) return "bg-amber-600/80 text-white font-medium border-amber-500/50";
    return "bg-amber-500/40 text-amber-200 border-amber-500/30";
  };

  return (
    <div className="container mx-auto px-4 py-12 max-w-7xl">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Batch Analysis</h1>
          <p className="text-slate-400">Run O(n²) pairwise comparisons on a class set (Max 20 files).</p>
        </div>
      </div>

      {error && (
        <div className="bg-rose-900/30 border border-rose-500/50 text-rose-200 p-4 rounded-lg mb-6 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
          <p className="text-sm">{error}</p>
        </div>
      )}

      {results.length === 0 && !loading && (
        <div className="bg-[var(--color-panel)] border border-[var(--color-panel-border)] rounded-xl p-12 mb-8 text-center shadow-md">
          <Upload className="w-12 h-12 text-slate-500 mx-auto mb-6" />
          <h3 className="text-xl font-bold text-slate-100 mb-2">Upload Submissions</h3>
          <p className="text-slate-400 text-sm mb-8 max-w-md mx-auto">
            Select multiple Python files to compare. The system will automatically compare every file against every other file.
          </p>
          
          <div className="flex flex-col items-center gap-4">
            <input 
              type="file" 
              multiple 
              accept=".py" 
              onChange={handleFileChange}
              className="block w-full max-w-sm text-sm text-slate-400
                file:mr-4 file:py-2 file:px-4
                file:rounded-full file:border-0
                file:text-sm file:font-semibold
                file:bg-indigo-600 file:text-white
                hover:file:bg-indigo-500 file:cursor-pointer"
            />
            {files.length > 0 && (
              <p className="text-sm text-indigo-400 font-medium">
                {files.length} {files.length === 1 ? 'file' : 'files'} selected ({(files.length * (files.length - 1) / 2)} comparisons)
              </p>
            )}
            
            <button
              onClick={handleProcess}
              disabled={files.length < 2}
              className="mt-4 px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors flex items-center gap-2"
            >
              Start Batch Process
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {loading && (
        <div className="bg-[var(--color-panel)] border border-[var(--color-panel-border)] rounded-xl p-16 text-center flex flex-col items-center justify-center shadow-md">
          <div className="relative w-16 h-16 mb-8">
            <div className="absolute inset-0 border-4 border-indigo-500/20 rounded-full animate-pulse"></div>
            <div className="absolute inset-0 border-4 border-t-indigo-500 border-r-transparent border-b-transparent border-l-transparent rounded-full animate-spin"></div>
          </div>
          <h3 className="text-xl font-bold text-slate-100 mb-3">Processing Batch Analysis</h3>
          <p className="text-slate-400 text-sm max-w-md mx-auto leading-relaxed">
            Running {files.length * (files.length - 1) / 2} multi-dimensional pairwise comparisons. This involves lexical, structural, and semantic model execution.
          </p>
        </div>
      )}

      {results.length > 0 && !loading && (
        <div className="space-y-6">
          {/* Current Batch Session Analytics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 bg-[var(--color-panel)] border border-[var(--color-panel-border)] rounded-xl p-6 shadow-md">
            <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800">
              <div className="text-xs font-semibold text-slate-400 mb-1">Files Uploaded</div>
              <div className="text-2xl font-bold text-white">{fileNames.length}</div>
            </div>
            <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800">
              <div className="text-xs font-semibold text-slate-400 mb-1">Pairwise Comparisons</div>
              <div className="text-2xl font-bold text-indigo-400">{results.length}</div>
            </div>
            <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800">
              <div className="text-xs font-semibold text-slate-400 mb-1">High Similarity Cases</div>
              <div className="text-2xl font-bold text-rose-400">
                {results.filter(r => r.fusion_score >= threshold).length}
              </div>
            </div>
            <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800">
              <div className="text-xs font-semibold text-slate-400 mb-1">Batch Average Score</div>
              <div className="text-2xl font-bold text-emerald-400">
                {results.length > 0 ? `${((results.reduce((acc, r) => acc + r.fusion_score, 0) / results.length) * 100).toFixed(1)}%` : "0%"}
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-4 bg-[var(--color-panel)] border border-[var(--color-panel-border)] rounded-xl p-6 shadow-md">
            <div className="flex items-center gap-4 flex-1">
              <div className="p-3 bg-indigo-900/50 rounded-lg text-indigo-400">
                <SlidersHorizontal className="w-5 h-5" />
              </div>
              <div className="flex-1 max-w-md">
                <div className="flex justify-between mb-1">
                  <label className="text-sm font-medium text-slate-300">Flag Threshold</label>
                  <span className="text-sm font-bold text-indigo-400">{(threshold * 100).toFixed(0)}%</span>
                </div>
                <input 
                  type="range" 
                  min="0.1" 
                  max="1.0" 
                  step="0.05"
                  value={threshold}
                  onChange={(e) => setThreshold(parseFloat(e.target.value))}
                  className="w-full accent-indigo-500 cursor-pointer"
                  aria-label={`Flag threshold ${(threshold * 100).toFixed(0)} percent`}
                />
              </div>
            </div>
            
            <button
              onClick={() => { setResults([]); setFiles([]); }}
              className="px-4 py-2 border border-slate-600 hover:bg-slate-700 text-slate-300 font-medium rounded-lg transition-colors flex items-center gap-2"
            >
              <RefreshCcw className="w-4 h-4" />
              New Batch
            </button>
          </div>

          <div className="bg-[var(--color-panel)] border border-[var(--color-panel-border)] rounded-xl shadow-md overflow-hidden flex flex-col">
            <div className="p-6 border-b border-[var(--color-panel-border)]">
              <h2 className="text-xl font-bold text-slate-100">Similarity Matrix Heatmap</h2>
              <p className="text-xs text-slate-400 mt-1">
                Click any highlighted cell to view the full evidence comparison.
              </p>
            </div>
            
            <div className="p-6 overflow-x-auto">
              <div className="inline-grid gap-1" style={{ gridTemplateColumns: `auto repeat(${fileNames.length}, minmax(40px, 1fr))` }}>
                {/* Header Row */}
                <div className="bg-transparent" />
                {fileNames.map(f => (
                  <div key={`header-col-${f}`} className="text-[10px] font-medium text-slate-400 -rotate-45 origin-bottom-left whitespace-nowrap mb-2 px-1">
                    {f.length > 15 ? f.substring(0, 12) + "..." : f}
                  </div>
                ))}

                {/* Data Rows */}
                {fileNames.map(rowFile => (
                  <React.Fragment key={`row-${rowFile}`}>
                    {/* Row Header */}
                    <div className="text-[10px] font-medium text-slate-400 text-right pr-4 self-center whitespace-nowrap">
                      {rowFile.length > 15 ? rowFile.substring(0, 12) + "..." : rowFile}
                    </div>
                    
                    {/* Cells */}
                    {fileNames.map(colFile => {
                      if (rowFile === colFile) {
                        return <div key={`${rowFile}-${colFile}`} className="w-10 h-10 bg-slate-900 rounded flex items-center justify-center text-[10px] text-slate-700">-</div>;
                      }
                      
                      const result = scoreLookup.get(`${rowFile}|${colFile}`);
                      if (!result) {
                        return <div key={`${rowFile}-${colFile}`} className="w-10 h-10 bg-slate-900/50 rounded flex items-center justify-center text-[10px] text-slate-700">N/A</div>;
                      }

                      const score = result.fusion_score;
                      const cellClass = getColor(score);
                      
                      return (
                        <Link 
                          href={`/?sub=${encodeURIComponent(result.file_a)}&ref=${encodeURIComponent(result.file_b)}`}
                          key={`${rowFile}-${colFile}`} 
                          title={`${rowFile} vs ${colFile} (${(score * 100).toFixed(1)}%) - ${result.transformation_type}`}
                          className={`w-10 h-10 rounded border transition-all duration-200 flex items-center justify-center cursor-pointer hover:ring-2 hover:ring-white/50 hover:scale-110 hover:z-20 z-10 ${cellClass}`}
                          aria-label={`Similarity ${(score * 100).toFixed(0)} percent`}
                        >
                          {(score * 100).toFixed(0)}
                        </Link>
                      );
                    })}
                  </React.Fragment>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
