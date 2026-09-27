"use client";

import React, { useState } from "react";
import { UploadZone } from "@/components/UploadZone";
import { analyzeCodes, AnalyzeResponse, getExportReportUrl } from "@/lib/api";
import { ScoreCard } from "@/components/ScoreCard";
import { EvidencePanel } from "@/components/EvidencePanel";
import { ExplanationBlock } from "@/components/ExplanationBlock";
import { FeedbackButtons } from "@/components/FeedbackButtons";
import { FusionWeightsPanel } from "@/components/FusionWeightsPanel";
import { DiffEditor } from "@monaco-editor/react";
import { ArrowLeft, Download, FileText } from "lucide-react";

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Store submitted code locally so DiffEditor can render them.
  // The API response does NOT echo the submitted code back.
  const [submittedCode, setSubmittedCode] = useState<string>("");
  const [referenceCode, setReferenceCode] = useState<string>("");

  const [expandedCards, setExpandedCards] = useState<Record<string, boolean>>({});

  const handleAnalyze = async (sub: string, ref: string, subName?: string, refName?: string) => {
    setLoading(true);
    setError(null);
    // Capture code for DiffEditor before the async request
    setSubmittedCode(sub);
    setReferenceCode(ref);
    try {
      const res = await analyzeCodes({
        submission_code: sub,
        reference_code: ref,
        file_a_name: subName || "Submission.py",
        file_b_name: refName || "Reference.py",
      });
      setResult(res);
    } catch (err: unknown) {
      console.error(err);
      const detail = err && typeof err === "object" && "response" in err 
        ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail 
        : null;
      setError(detail || "Failed to analyze code");
    } finally {
      setLoading(false);
    }
  };

  const toggleExpand = (card: string) => {
    setExpandedCards(prev => ({ ...prev, [card]: !prev[card] }));
  };

  return (
    <div className="container mx-auto px-4 py-12 max-w-7xl">
      
      {!result ? (
        <div className="max-w-3xl mx-auto text-center space-y-12">
          <div className="space-y-4">
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-white">
              Investigate Code Similarity
            </h1>
            <p className="text-lg text-slate-400 max-w-2xl mx-auto">
              Drop two Python files or select a quick demo preset below to run a deep multi-dimensional analysis spanning lexical, structural, semantic, and behavioral evidence.
            </p>
          </div>
          {loading ? (
            <div className="bg-[var(--color-panel)] border border-[var(--color-panel-border)] rounded-xl p-16 text-center flex flex-col items-center justify-center shadow-lg animate-in fade-in zoom-in duration-500">
              <div className="relative w-20 h-20 mb-8">
                <div className="absolute inset-0 border-4 border-blue-500/20 rounded-full animate-pulse"></div>
                <div className="absolute inset-0 border-4 border-t-blue-500 border-r-transparent border-b-transparent border-l-transparent rounded-full animate-spin"></div>
              </div>
              <h3 className="text-2xl font-bold text-slate-100 mb-3">Analyzing Similarity...</h3>
              <p className="text-slate-400 text-sm max-w-md mx-auto leading-relaxed">
                Extracting syntactic features, running structural tree comparisons, generating UniXcoder embeddings, and executing behavioral traces.
              </p>
            </div>
          ) : (
            <UploadZone onFilesSelected={handleAnalyze} disabled={loading} />
          )}
          
          {error && !loading && (
            <div className="p-4 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-md">
              {error}
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-700">
          
          {/* Header Action */}
          <div className="flex flex-wrap justify-between items-center gap-4 bg-slate-900/60 p-4 border border-slate-800 rounded-xl backdrop-blur-md">
            <button 
              onClick={() => setResult(null)} 
              className="text-sm font-semibold text-slate-300 hover:text-white transition-colors flex items-center gap-2"
            >
              <ArrowLeft className="w-4 h-4" /> Start New Comparison
            </button>
            
            <div className="flex items-center gap-4">
              <div className="text-xs text-slate-500 font-mono hidden sm:block">Run ID: {result.run_id}</div>
              
              <div className="flex gap-2">
                <a
                  href={getExportReportUrl(result.run_id, "html")}
                  target="_blank"
                  rel="noreferrer"
                  className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg border border-slate-700 transition-all flex items-center gap-1.5"
                >
                  <FileText className="w-3.5 h-3.5 text-blue-400" /> Export HTML
                </a>
                <a
                  href={getExportReportUrl(result.run_id, "json")}
                  download
                  className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg border border-slate-700 transition-all flex items-center gap-1.5"
                >
                  <Download className="w-3.5 h-3.5 text-emerald-400" /> Export JSON
                </a>
              </div>
            </div>
          </div>

          {/* Verdict Summary */}
          <ExplanationBlock 
            explanation={result.explanation} 
            transformationType={result.explanation?.transformation_type || "Unknown"} 
          />

          {/* Score Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
            
            {/* Fusion Score - Primary */}
            <div className="md:col-span-4 flex flex-col gap-4">
              <ScoreCard
                title="Overall Fusion Score"
                score={result.fusion_score}
                confidence="high"
                isPrimary
              />
              <FusionWeightsPanel metadata={result.fusion_weight_metadata} />
              <FeedbackButtons runId={result.run_id} />
              
              <div className="mt-4">
                 <ScoreCard
                  title="AI Generation Likelihood"
                  score={result.ai_generation?.likelihood ?? null}
                  confidence={result.ai_generation?.likelihood >= 0.8 ? "high" : "medium"}
                  isExpanded={expandedCards["ai"]}
                  onToggleExpand={() => toggleExpand("ai")}
                >
                  <EvidencePanel type="ai" evidence={result.ai_generation?.evidence ?? []} />
                </ScoreCard>
              </div>
            </div>

            {/* Component Scores */}
            <div className="md:col-span-8 flex flex-col gap-4">
              <ScoreCard
                title="Lexical Similarity"
                score={result.components.lexical}
                confidence={result.confidence_indicators?.lexical ?? "medium"}
                isExpanded={expandedCards["lexical"]}
                onToggleExpand={() => toggleExpand("lexical")}
              >
                <EvidencePanel type="lexical" evidence={result.components.lexical_evidence} />
              </ScoreCard>
              
              <ScoreCard
                title="Structural Similarity"
                score={result.components.structural}
                confidence={result.confidence_indicators?.structural ?? "medium"}
                isExpanded={expandedCards["structural"]}
                onToggleExpand={() => toggleExpand("structural")}
              >
                <EvidencePanel type="structural" evidence={result.components.structural_evidence} />
              </ScoreCard>

              <ScoreCard
                title="Semantic Similarity"
                score={result.components.semantic}
                confidence={result.confidence_indicators?.semantic ?? "medium"}
                isExpanded={expandedCards["semantic"]}
                onToggleExpand={() => toggleExpand("semantic")}
              >
                <EvidencePanel type="semantic" evidence={result.components.semantic_evidence} />
              </ScoreCard>

              <ScoreCard
                title="Behavioral Similarity"
                score={result.components.behavioral}
                confidence={result.confidence_indicators?.behavioral ?? "low"}
                isExpanded={expandedCards["behavioral"]}
                onToggleExpand={() => toggleExpand("behavioral")}
              >
                <EvidencePanel type="behavioral" evidence={result.components.behavioral_evidence} />
              </ScoreCard>
            </div>
            
          </div>

          {/* Monaco Diff Editor — uses locally stored code, not API echo */}
          <div className="mt-12 space-y-4">
            <h3 className="text-xl font-semibold text-slate-200">Code Diff</h3>
            <div className="h-[600px] border border-slate-700 rounded-xl overflow-hidden shadow-xl bg-[#1e1e1e]">
              <DiffEditor
                language="python"
                original={referenceCode}
                modified={submittedCode}
                theme="vs-dark"
                options={{
                  readOnly: true,
                  renderSideBySide: true,
                  minimap: { enabled: false },
                  scrollBeyondLastLine: false,
                  wordWrap: "on"
                }}
              />
            </div>
          </div>

        </div>
      )}
    </div>
  );
}
