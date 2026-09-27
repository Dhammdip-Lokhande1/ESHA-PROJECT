import React from "react";
import { TransformationBadge } from "./TransformationBadge";

interface ExplanationData {
  transformation_type?: string;
  confidence?: number;
  verdict?: string;
  narrative?: string;
  signals?: string[];
  caveats?: string[];
  rule_matched?: string;
}

interface ExplanationBlockProps {
  explanation: ExplanationData | string | null;
  transformationType: string;
}

export function ExplanationBlock({ explanation, transformationType }: ExplanationBlockProps) {
  if (!explanation) return null;

  // Handle legacy string explanation (just in case)
  if (typeof explanation === "string") {
    const advisoryIndex = explanation.lastIndexOf("Advisory:");
    return (
      <div className="bg-slate-800/40 border border-slate-700/50 rounded-xl p-6 shadow-inner">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 mb-4">
          <h2 className="text-xl font-semibold text-slate-100 flex items-center gap-2">
            Verdict Summary
          </h2>
          <TransformationBadge type={transformationType} />
        </div>
        <div className="prose prose-invert max-w-none">
          {advisoryIndex !== -1 ? (
            <>
              <p className="mb-3 text-slate-300 leading-relaxed text-lg">{explanation.substring(0, advisoryIndex).trim()}</p>
              <div className="bg-amber-900/10 border-l-4 border-amber-500/50 p-3 mt-4 rounded-r-md">
                <p className="text-amber-200/80 text-sm font-medium italic">{explanation.substring(advisoryIndex)}</p>
              </div>
            </>
          ) : (
            <p className="text-slate-300 leading-relaxed text-lg">{explanation}</p>
          )}
        </div>
      </div>
    );
  }

  // Handle new object explanation from M3
  return (
    <div className="bg-slate-800/40 border border-slate-700/50 rounded-xl p-6 shadow-inner space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 border-b border-slate-700/50 pb-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-100 mb-2">
            {explanation.verdict}
          </h2>
          <p className="text-slate-300 text-lg leading-relaxed">{explanation.narrative}</p>
        </div>
        <TransformationBadge type={explanation.transformation_type || transformationType} />
      </div>

      {explanation.signals && explanation.signals.length > 0 && (
        <div className="bg-slate-900/50 rounded-lg p-4">
          <h3 className="text-sm uppercase tracking-wider text-slate-400 font-semibold mb-3">Key Evidence Signals</h3>
          <ul className="list-disc pl-5 space-y-2 text-slate-300">
            {explanation.signals.map((signal, idx) => (
              <li key={idx}>{signal}</li>
            ))}
          </ul>
        </div>
      )}

      {explanation.caveats && explanation.caveats.length > 0 && (
        <div className="bg-amber-900/10 border-l-4 border-amber-500/50 p-4 mt-4 rounded-r-md">
          <h3 className="text-amber-500 font-semibold mb-2">Advisory Notes</h3>
          <ul className="list-disc pl-5 space-y-2 text-amber-200/80 text-sm font-medium italic">
            {explanation.caveats.map((caveat, idx) => (
              <li key={idx}>{caveat}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
