import React from "react";
import { cn } from "@/lib/utils";
import { Copy, Edit3, Settings, Bot, SearchCode, HelpCircle } from "lucide-react";

interface TransformationBadgeProps {
  type: string;
}

export function TransformationBadge({ type }: TransformationBadgeProps) {
  // Normalize the type string
  const normalized = type.toLowerCase().replace(/ /g, "_");

  const config: Record<string, { label: string; icon: React.ElementType; styles: string }> = {
    exact_copy: {
      label: "Exact Copy",
      icon: Copy,
      styles: "bg-rose-500/20 text-rose-300 border-rose-500/30",
    },
    variable_renaming: {
      label: "Variable Renaming",
      icon: Edit3,
      styles: "bg-amber-500/20 text-amber-300 border-amber-500/30",
    },
    structural_refactoring: {
      label: "Structural Refactoring",
      icon: Settings,
      styles: "bg-amber-500/20 text-amber-300 border-amber-500/30",
    },
    likely_ai_rewrite: {
      label: "Likely AI Rewrite",
      icon: Bot,
      styles: "bg-fuchsia-500/20 text-fuchsia-300 border-fuchsia-500/30",
    },
    partial_match: {
      label: "Partial Match",
      icon: SearchCode,
      styles: "bg-indigo-500/20 text-indigo-300 border-indigo-500/30",
    },
    unrelated: {
      label: "Unrelated",
      icon: HelpCircle,
      styles: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
    },
  };

  const badge = config[normalized] || {
    label: type,
    icon: HelpCircle,
    styles: "bg-slate-700 text-slate-300 border-slate-600",
  };

  const Icon = badge.icon;

  return (
    <div
      className={cn(
        "inline-flex items-center gap-2 px-3 py-1.5 rounded-full border text-sm font-medium tracking-wide shadow-sm",
        badge.styles
      )}
    >
      <Icon className="w-4 h-4" />
      {badge.label}
    </div>
  );
}
