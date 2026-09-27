import React, { useState } from "react";
import { Info, Target } from "lucide-react";
import { cn } from "@/lib/utils";

interface FusionWeightsPanelProps {
  metadata: {
    effective_weights: Record<string, number>;
    source: string;
    signals_used: string[];
    last_updated?: string | null;
  };
}

export function FusionWeightsPanel({ metadata }: FusionWeightsPanelProps) {
  const [isOpen, setIsOpen] = useState(false);

  if (!metadata) return null;

  return (
    <div className="relative inline-block text-left">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-300 bg-slate-800/50 hover:bg-slate-800 px-2.5 py-1 rounded-md transition-colors border border-slate-700/50"
      >
        <Info className="w-3.5 h-3.5" />
        <span>How was this calculated?</span>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-72 rounded-md shadow-lg bg-slate-800 ring-1 ring-black ring-opacity-5 border border-slate-700 z-10">
          <div className="p-4">
            <h4 className="text-sm font-semibold text-slate-200 mb-2 flex items-center gap-2">
              <Target className="w-4 h-4 text-[var(--color-accent)]" />
              Adaptive Fusion Weights
            </h4>
            <p className="text-xs text-slate-400 mb-3 leading-relaxed">
              Weights are dynamically updated from analysis feedback. 
              <br />
              <span className="text-emerald-400/80">Source: {metadata.source}</span>
              {metadata.last_updated && (
                <>
                  <br />
                  <span className="text-slate-500">Updated: {new Date(metadata.last_updated).toLocaleString()}</span>
                </>
              )}
            </p>
            
            <div className="space-y-2">
              {Object.entries(metadata.effective_weights).map(([signal, weight]) => (
                <div key={signal} className="flex justify-between items-center text-xs">
                  <span className={cn(
                    "capitalize",
                    metadata.signals_used.includes(signal) ? "text-slate-300 font-medium" : "text-slate-500 line-through"
                  )}>
                    {signal}
                  </span>
                  <span className={cn(
                    "font-mono",
                    metadata.signals_used.includes(signal) ? "text-slate-200" : "text-slate-500"
                  )}>
                    {(weight * 100).toFixed(1)}%
                  </span>
                </div>
              ))}
            </div>
            
            <div className="mt-3 pt-3 border-t border-slate-700">
              <div className="flex justify-between text-xs font-semibold text-slate-300">
                <span>Total</span>
                <span className="font-mono">100%</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
