import React from "react";
import { cn } from "@/lib/utils";
import { ShieldCheck, ShieldAlert, Shield } from "lucide-react";

interface ConfidenceIndicatorProps {
  level: "high" | "medium" | "low";
}

export function ConfidenceIndicator({ level }: ConfidenceIndicatorProps) {
  const config = {
    high: {
      icon: ShieldCheck,
      color: "text-emerald-400",
      bg: "bg-emerald-400/10",
      label: "High Confidence",
    },
    medium: {
      icon: Shield,
      color: "text-amber-400",
      bg: "bg-amber-400/10",
      label: "Medium Confidence",
    },
    low: {
      icon: ShieldAlert,
      color: "text-rose-400",
      bg: "bg-rose-400/10",
      label: "Low Confidence",
    },
  };

  const { icon: Icon, color, bg, label } = config[level];

  return (
    <div
      className={cn(
        "inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium border border-transparent",
        bg,
        color
      )}
      title={label}
    >
      <Icon className="w-3.5 h-3.5" />
      <span>{label.split(" ")[0]}</span>
    </div>
  );
}
