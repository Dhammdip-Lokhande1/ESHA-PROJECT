import React from "react";
import { cn } from "@/lib/utils";
import { ConfidenceIndicator } from "./ConfidenceIndicator";
import { ChevronDown, ChevronUp } from "lucide-react";

interface ScoreCardProps {
  title: string;
  score: number | null;
  confidence: "high" | "medium" | "low";
  isPrimary?: boolean;
  isExpanded?: boolean;
  onToggleExpand?: () => void;
  children?: React.ReactNode;
}

export function ScoreCard({
  title,
  score,
  confidence,
  isPrimary = false,
  isExpanded = false,
  onToggleExpand,
  children,
}: ScoreCardProps) {
  const isAbsent = score === null || score === undefined;
  const percentage = !isAbsent ? Math.round(score * 100) : null;

  let containerClass = "border-[var(--color-panel-border)] shadow-md";
  if (onToggleExpand) {
    containerClass += " hover:shadow-lg";
  }

  if (score !== null) {
    if (score >= 0.8) {
      containerClass = "border-rose-500/50 shadow-[0_0_15px_rgba(244,63,94,0.1)] bg-rose-950/10";
      if (onToggleExpand) containerClass += " hover:shadow-[0_0_20px_rgba(244,63,94,0.2)]";
    } else if (score <= 0.5) {
      containerClass = "border-emerald-500/30 shadow-md";
      if (onToggleExpand) containerClass += " hover:shadow-[0_0_15px_rgba(16,185,129,0.1)] hover:border-emerald-500/50";
    }
  }

  if (isPrimary) {
    if (score !== null && score >= 0.8) {
      containerClass = "border-rose-500 shadow-[0_0_30px_rgba(244,63,94,0.25)] bg-rose-950/20";
    } else {
      containerClass = "border-[var(--color-accent)] shadow-[0_0_25px_rgba(99,102,241,0.2)] bg-indigo-950/10";
    }
  }

  return (
    <div
      className={cn(
        "rounded-xl border bg-[var(--color-panel)] overflow-hidden transition-all duration-300",
        containerClass
      )}
    >
      <div
        className={cn(
          "p-5 flex items-center justify-between transition-colors duration-200",
          onToggleExpand && "cursor-pointer hover:bg-slate-800/30"
        )}
        onClick={onToggleExpand}
      >
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-3">
            <h3
              className={cn(
                "font-medium",
                isPrimary ? "text-xl text-[var(--color-accent-light)]" : "text-base text-slate-300"
              )}
            >
              {title}
            </h3>
            {!isAbsent && <ConfidenceIndicator level={confidence} />}
          </div>
          {isAbsent ? (
            <span className="text-sm text-slate-500 italic">Not available</span>
          ) : (
            <div className="flex items-baseline gap-1">
              <span
                className={cn(
                  "font-bold tabular-nums tracking-tight",
                  isPrimary ? "text-6xl text-white drop-shadow-md" : "text-3xl text-slate-100"
                )}
              >
                {percentage}
              </span>
              <span className="text-lg text-slate-400">%</span>
            </div>
          )}
        </div>

        {onToggleExpand && (
          <div className="text-slate-500 p-2 rounded-full hover:bg-slate-700/50">
            {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
          </div>
        )}
      </div>

      {isExpanded && children && (
        <div className="border-t border-[var(--color-panel-border)] bg-slate-950/30 p-5 relative">
          <div 
            className={cn(
              "absolute left-0 top-0 bottom-0 w-1",
              score !== null && score >= 0.8 ? "bg-rose-500/50" : 
              score !== null && score <= 0.5 ? "bg-emerald-500/50" : 
              "bg-indigo-500/30"
            )} 
          />
          {children}
        </div>
      )}
    </div>
  );
}
