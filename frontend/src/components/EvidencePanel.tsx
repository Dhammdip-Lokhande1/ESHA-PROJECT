import React from "react";
import { Info, GitMerge, Fingerprint } from "lucide-react";

interface EvidenceItem {
  type?: string;
  matched_count?: number;
  total_unique_submission_ngrams?: number;
  top_matches?: Array<{ ngram: string; count: number }>;
  distance?: number;
  total_nodes_max?: number;
  details?: Array<{ node_type: string; matched_count: number }>;
  note?: string;
  value?: unknown;
  input?: string;
  output_a?: string;
  output_b?: string;
  matched?: boolean;
  feature?: string;
  interpretation?: string;
  [key: string]: unknown;
}

interface EvidencePanelProps {
  type: "lexical" | "structural" | "semantic" | "behavioral" | "ai";
  evidence: EvidenceItem[];
}

export function EvidencePanel({ type, evidence }: EvidencePanelProps) {
  if (!evidence || evidence.length === 0) {
    return <div className="text-sm text-slate-500 italic">No evidence available.</div>;
  }

  return (
    <div className="space-y-4">
      {type === "lexical" && <LexicalEvidence evidence={evidence} />}
      {type === "structural" && <StructuralEvidence evidence={evidence} />}
      {type === "semantic" && <SemanticEvidence evidence={evidence} />}
      {type === "behavioral" && <BehavioralEvidence evidence={evidence} />}
      {type === "ai" && <AiEvidence evidence={evidence} />}
    </div>
  );
}

function LexicalEvidence({ evidence }: { evidence: EvidenceItem[] }) {
  // Try to find the top matched n-grams summary
  const summary = evidence.find((e) => e.type === "matched_ngrams_summary");
  
  if (summary) {
    return (
      <div className="space-y-3">
        <div className="flex items-center gap-2 text-sm text-slate-300 bg-slate-900/50 border border-slate-800 p-3 rounded-md">
          <Fingerprint className="w-4 h-4 text-slate-400" />
          <span>
            Matched <strong>{summary.matched_count}</strong> of {summary.total_unique_submission_ngrams} unique n-grams in the submission.
          </span>
        </div>
        {summary.top_matches && summary.top_matches.length > 0 && (
          <div>
            <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Top Matched N-Grams</h4>
            <div className="flex flex-wrap gap-2">
              {summary.top_matches.slice(0, 10).map((m, i) => (
                <span key={i} className="px-2 py-1 bg-slate-900/50 border border-slate-700/50 rounded text-xs font-mono text-slate-300">
                  {m.ngram} <span className="text-slate-500 ml-1">x{m.count}</span>
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }
  
  return <GenericEvidenceList evidence={evidence} />;
}

function StructuralEvidence({ evidence }: { evidence: EvidenceItem[] }) {
  const summary = evidence.find((e) => e.type === "zss_distance_summary");
  const subtreeDetail = evidence.find((e) => e.type === "matched_subtrees");

  return (
    <div className="space-y-4">
      {summary && (
        <div className="flex items-center gap-2 text-sm text-slate-300 bg-slate-900/50 border border-slate-800 p-3 rounded-md">
          <GitMerge className="w-4 h-4 text-slate-400" />
          <span>
            Tree Edit Distance: <strong>{summary.distance}</strong> operations across {summary.total_nodes_max} max nodes.
          </span>
        </div>
      )}
      
      {subtreeDetail && subtreeDetail.details && subtreeDetail.details.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Matched AST Subtrees</h4>
          <div className="space-y-2">
            {subtreeDetail.details.map((m, i) => (
              <div key={i} className="flex items-center justify-between bg-slate-900/50 border border-slate-800 p-2 rounded text-sm hover:bg-slate-800/50 transition-colors">
                <span className="font-mono text-slate-300">{m.node_type}</span>
                <span className="text-xs text-slate-400">{m.matched_count} occurrences</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {!summary && !subtreeDetail && <GenericEvidenceList evidence={evidence} />}
    </div>
  );
}

function SemanticEvidence({ evidence }: { evidence: EvidenceItem[] }) {
  return (
    <div className="space-y-3">
      {evidence.map((item, i) => (
        <div key={i} className="flex gap-3 text-sm p-3 bg-slate-900/50 rounded-md border border-slate-800 hover:bg-slate-800/30 transition-colors">
          <Info className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
          <div>
            <div className="text-slate-200 font-medium capitalize">{(item.type || "").replace(/_/g, " ")}</div>
            <div className="text-slate-400 mt-1">{item.note}</div>
            {item.value !== undefined && (
              <div className="mt-2 font-mono text-xs text-slate-300">Value: {String(item.value)}</div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

function BehavioralEvidence({ evidence }: { evidence: EvidenceItem[] }) {
  // Determine if this is a "not available" note
  const isMissing = evidence.length === 1 && evidence[0].note && !evidence[0].input;
  
  if (isMissing) {
    return (
      <div className="flex gap-3 text-sm p-3 bg-amber-900/20 rounded-md border border-amber-900/50">
        <Info className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
        <div className="text-amber-200/80">{evidence[0].note}</div>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm text-left text-slate-300">
        <thead className="text-xs text-slate-500 uppercase bg-slate-800/50">
          <tr>
            <th className="px-4 py-2 rounded-tl-md">Input</th>
            <th className="px-4 py-2">Submission Out</th>
            <th className="px-4 py-2">Reference Out</th>
            <th className="px-4 py-2 text-center rounded-tr-md">Match</th>
          </tr>
        </thead>
        <tbody>
          {evidence.map((test, i) => (
            <tr key={i} className="border-b border-slate-800 hover:bg-slate-800/30">
              <td className="px-4 py-2 font-mono text-xs max-w-[150px] truncate" title={test.input}>{test.input}</td>
              <td className="px-4 py-2 font-mono text-xs text-slate-400 max-w-[150px] truncate" title={test.output_a}>{test.output_a}</td>
              <td className="px-4 py-2 font-mono text-xs text-slate-400 max-w-[150px] truncate" title={test.output_b}>{test.output_b}</td>
              <td className="px-4 py-2 text-center">
                {test.matched ? (
                  <span className="inline-block w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></span>
                ) : (
                  <span className="inline-block w-2 h-2 rounded-full bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.5)]"></span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function AiEvidence({ evidence }: { evidence: EvidenceItem[] }) {
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {evidence.map((item, i) => (
        <div key={i} className="bg-slate-900/50 p-3 rounded-md border border-slate-800 hover:bg-slate-800/30 transition-colors">
          <div className="flex justify-between items-start mb-1">
            <span className="text-xs font-mono text-slate-400 truncate max-w-[70%]">{item.feature}</span>
            <span className="text-sm font-medium text-slate-200">{String(item.value ?? "")}</span>
          </div>
          <p className="text-xs text-slate-500 leading-snug">{item.interpretation}</p>
        </div>
      ))}
    </div>
  );
}

function GenericEvidenceList({ evidence }: { evidence: EvidenceItem[] }) {
  return (
    <ul className="space-y-2">
      {evidence.map((e, i) => (
        <li key={i} className="text-sm text-slate-400 p-2 bg-slate-900/50 border border-slate-800 rounded">
          <pre className="text-xs font-mono overflow-x-auto">
            {JSON.stringify(e, null, 2)}
          </pre>
        </li>
      ))}
    </ul>
  );
}
