import React, { useState } from "react";
import { Check, X, Loader2 } from "lucide-react";
import { submitFeedback } from "@/lib/api";
import { cn } from "@/lib/utils";

interface FeedbackButtonsProps {
  runId: string | null;
}

export function FeedbackButtons({ runId }: FeedbackButtonsProps) {
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [selected, setSelected] = useState<"confirmed" | "false_positive" | null>(null);

  const handleFeedback = async (verdict: "confirmed" | "false_positive") => {
    if (!runId) return;
    
    setStatus("loading");
    setSelected(verdict);
    
    try {
      await submitFeedback(runId, verdict);
      setStatus("success");
      // Reset after a few seconds
      setTimeout(() => {
        setStatus("idle");
        setSelected(null);
      }, 3000);
    } catch (err) {
      console.error("Feedback error", err);
      setStatus("error");
      setTimeout(() => setStatus("idle"), 3000);
    }
  };

  const isConfirmed = selected === "confirmed";
  const isFP = selected === "false_positive";

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow-sm">
      <div className="flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <h3 className="text-sm font-semibold text-slate-200">Analysis Verdict</h3>
          <p className="text-xs text-slate-400 mt-1">
            Your feedback helps recalibrate future comparisons.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {status === "success" && (
            <span className="text-xs font-medium text-emerald-400 animate-pulse mr-2">
              Feedback saved!
            </span>
          )}
          {status === "error" && (
            <span className="text-xs font-medium text-rose-400 mr-2">
              Failed to save
            </span>
          )}

          <button
            onClick={() => handleFeedback("confirmed")}
            disabled={!runId || status === "loading"}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors border",
              isConfirmed
                ? "bg-emerald-500 text-white border-emerald-600 shadow-md"
                : "bg-slate-700 text-slate-300 border-slate-600 hover:bg-slate-600",
              !runId && "opacity-50 cursor-not-allowed"
            )}
          >
            {status === "loading" && isConfirmed ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Check className="w-4 h-4" />
            )}
            Confirm Match
          </button>

          <button
            onClick={() => handleFeedback("false_positive")}
            disabled={!runId || status === "loading"}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors border",
              isFP
                ? "bg-rose-500 text-white border-rose-600 shadow-md"
                : "bg-slate-700 text-slate-300 border-slate-600 hover:bg-slate-600",
              !runId && "opacity-50 cursor-not-allowed"
            )}
          >
            {status === "loading" && isFP ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <X className="w-4 h-4" />
            )}
            Mark False Positive
          </button>
        </div>
      </div>
    </div>
  );
}
