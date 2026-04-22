import { AlertTriangle, TrendingDown } from "lucide-react";

export function WeakTopicsPanel({ weakTopics }) {
  if (!weakTopics || weakTopics.length === 0) {
    return (
      <div className="rounded-2xl border border-white/[0.07] bg-[#12121A] p-6 card-inner-glow">
        <div className="flex items-center gap-2 text-emerald-400">
          <TrendingDown className="h-4 w-4 rotate-180" />
          <span className="text-sm font-medium">No weak topics — great work!</span>
        </div>
      </div>
    );
  }
  return (
    <div
      className="rounded-2xl border border-white/[0.07] bg-[#12121A] p-6 card-inner-glow"
      data-testid="weak-topics-panel"
    >
      <div className="flex items-center gap-2 mb-1">
        <AlertTriangle className="h-4 w-4 text-[#FF7A59]" />
        <h3 className="font-display text-base font-medium text-white">Weak Topics</h3>
      </div>
      <p className="text-xs text-zinc-500 mb-5">
        Topics where your average is below 70%. Tackle these first.
      </p>

      <div className="space-y-4">
        {weakTopics.map((w) => {
          const color =
            w.severity === "HIGH"
              ? "bg-red-500"
              : w.score < 65
                ? "bg-[#FF7A59]"
                : "bg-amber-400";
          return (
            <div key={w.subject} data-testid={`weak-${w.subject.replace(/\s/g, "-")}`}>
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-sm text-zinc-200">{w.subject}</span>
                <span className="font-mono text-sm text-zinc-400">{w.score}%</span>
              </div>
              <div className="h-1.5 rounded-full bg-white/[0.05] overflow-hidden">
                <div
                  className={`h-full ${color} transition-all duration-700`}
                  style={{ width: `${w.score}%` }}
                />
              </div>
              <div
                className={`mt-1.5 inline-flex items-center gap-1 text-[10px] tracking-wider uppercase font-semibold ${
                  w.severity === "HIGH" ? "text-red-400" : "text-amber-400"
                }`}
              >
                {w.severity} RISK
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
