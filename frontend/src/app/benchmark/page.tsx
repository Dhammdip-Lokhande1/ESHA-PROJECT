"use client";

import React, { useEffect, useState } from "react";
import { fetchResearchBenchmark } from "@/lib/api";
import { Database, CheckCircle2, Award, Info, Layers, BarChart3 } from "lucide-react";

interface CategoryItem {
  name: string;
  count: number;
  description: string;
}

interface BenchmarkData {
  dataset_name: string;
  total_pairs: number;
  program_families: number;
  categories: CategoryItem[];
  evaluation_methodology: string;
  results: {
    adaptive_fusion_f1: number;
    equal_weights_f1: number;
    lexical_only_f1: number;
    structural_only_f1: number;
    semantic_only_f1: number;
    auc_roc: number;
  };
}

export default function BenchmarkPage() {
  const [data, setData] = useState<BenchmarkData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchResearchBenchmark()
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center p-6 text-slate-400">
        Loading research benchmark data...
      </div>
    );
  }

  if (!data) {
    return <div className="p-12 text-center text-rose-400">Failed to load benchmark evaluation metrics.</div>;
  }

  return (
    <div className="container mx-auto px-4 py-12 max-w-7xl">
      {/* Header Banner */}
      <div className="mb-10 pb-6 border-b border-slate-800">
        <div className="flex items-center gap-3 mb-2">
          <Database className="w-8 h-8 text-blue-400" />
          <h1 className="text-3xl font-bold text-white">Research Benchmark Evaluation</h1>
        </div>
        <p className="text-sm text-slate-400 max-w-3xl leading-relaxed">
          Offline evaluation results on the <span className="text-slate-200 font-semibold">{data.dataset_name}</span>. Evaluation uses {data.evaluation_methodology} to guarantee zero data leakage between program families.
        </p>
        <div className="mt-4 flex items-center gap-2 text-xs text-amber-400 bg-amber-500/10 border border-amber-500/20 px-3.5 py-2 rounded-xl w-fit">
          <Info className="w-4 h-4 shrink-0" />
          <span>Offline Research Data: Benchmark statistics are strictly decoupled from live user analysis runs and production dashboards.</span>
        </div>
      </div>

      {/* Benchmark Metric Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
        <MetricCard title="Total Code Pairs" value={data.total_pairs} sub="30 Program Families" icon={<Layers className="w-5 h-5 text-indigo-400" />} />
        <MetricCard title="Adaptive Fusion F1" value={`${(data.results.adaptive_fusion_f1 * 100).toFixed(1)}%`} sub="Target Baseline Metric" icon={<Award className="w-5 h-5 text-emerald-400" />} />
        <MetricCard title="Equal-Weights F1" value={`${(data.results.equal_weights_f1 * 100).toFixed(1)}%`} sub="Fixed 0.25 weights" icon={<BarChart3 className="w-5 h-5 text-amber-400" />} />
        <MetricCard title="AUC-ROC Score" value={data.results.auc_roc.toFixed(3)} sub="Classification ROC Area" icon={<CheckCircle2 className="w-5 h-5 text-purple-400" />} />
      </div>

      {/* Ablation Comparison Table & Category Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
        {/* Component Performance Breakdown */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl">
          <h2 className="text-xl font-bold text-white mb-6">Component Ablation Results</h2>
          <div className="space-y-4">
            <AblationBar label="Adaptive Fusion (M4.5)" score={data.results.adaptive_fusion_f1} highlight />
            <AblationBar label="Equal-Weights Fusion" score={data.results.equal_weights_f1} />
            <AblationBar label="Semantic Similarity Only (UniXcoder)" score={data.results.semantic_only_f1} />
            <AblationBar label="Structural Similarity Only (ZSS AST)" score={data.results.structural_only_f1} />
            <AblationBar label="Lexical Similarity Only (Token Jaccard)" score={data.results.lexical_only_f1} />
          </div>
        </div>

        {/* Dataset Category Breakdown */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl">
          <h2 className="text-xl font-bold text-white mb-6">Dataset Category Breakdown</h2>
          <div className="divide-y divide-slate-800">
            {data.categories.map((cat) => (
              <div key={cat.name} className="py-3.5 flex items-center justify-between">
                <div>
                  <div className="font-mono text-sm text-slate-200 font-semibold">{cat.name}</div>
                  <div className="text-xs text-slate-400">{cat.description}</div>
                </div>
                <div className="font-mono font-bold text-xs bg-slate-800 text-slate-300 px-3 py-1 rounded-lg">
                  {cat.count} pairs
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ title, value, sub, icon }: { title: string; value: string | number; sub: string; icon: React.ReactNode }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-lg">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold text-slate-400">{title}</span>
        {icon}
      </div>
      <div className="text-3xl font-extrabold text-white mb-1">{value}</div>
      <div className="text-[11px] text-slate-500">{sub}</div>
    </div>
  );
}

function AblationBar({ label, score, highlight }: { label: string; score: number; highlight?: boolean }) {
  const pct = (score * 100).toFixed(1);
  return (
    <div>
      <div className="flex justify-between text-xs mb-1 font-semibold">
        <span className={highlight ? "text-emerald-400 font-bold" : "text-slate-300"}>{label}</span>
        <span className={highlight ? "text-emerald-400 font-mono font-bold" : "text-slate-400 font-mono"}>{pct}% F1</span>
      </div>
      <div className="h-2.5 bg-slate-800 rounded-full overflow-hidden">
        <div 
          className={`h-full rounded-full transition-all duration-500 ${highlight ? "bg-emerald-500 shadow-md shadow-emerald-500/30" : "bg-blue-600"}`} 
          style={{ width: `${pct}%` }} 
        />
      </div>
    </div>
  );
}
