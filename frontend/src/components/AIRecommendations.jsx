import { Video, BookMarked, PenSquare, Image as ImageIcon, Sparkles, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

const TYPE_META = {
  video: { icon: Video, color: "text-rose-300 bg-rose-500/10 border-rose-500/20" },
  visual: { icon: ImageIcon, color: "text-sky-300 bg-sky-500/10 border-sky-500/20" },
  practice: { icon: PenSquare, color: "text-emerald-300 bg-emerald-500/10 border-emerald-500/20" },
  reading: { icon: BookMarked, color: "text-amber-300 bg-amber-500/10 border-amber-500/20" },
};

export function AIRecommendations({ items, loading, onRefresh }) {
  return (
    <div
      className="rounded-2xl border border-white/[0.07] bg-[#12121A] p-6 card-inner-glow"
      data-testid="ai-recommendations"
    >
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-[#FF7A59]" />
          <h3 className="font-display text-base font-medium text-white">
            AI Recommendations
          </h3>
        </div>
        <Button
          size="sm"
          variant="ghost"
          data-testid="refresh-recommendations-btn"
          onClick={onRefresh}
          disabled={loading}
          className="text-zinc-400 hover:text-white"
        >
          <RefreshCw className={`h-3.5 w-3.5 mr-1 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {loading && (!items || items.length === 0) ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 rounded-xl bg-white/[0.03] animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="space-y-3">
          {items?.map((r, idx) => {
            const meta = TYPE_META[r.type] || TYPE_META.visual;
            const Icon = meta.icon;
            return (
              <div
                key={idx}
                data-testid={`recommendation-${idx}`}
                className="group flex gap-4 p-4 rounded-xl bg-[#0E0E14] border border-white/[0.05] hover:border-white/[0.12] hover:bg-[#11111A] transition-all cursor-pointer"
              >
                <div
                  className={`shrink-0 h-10 w-10 rounded-lg border flex items-center justify-center ${meta.color}`}
                >
                  <Icon className="h-4 w-4" />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className="font-medium text-sm text-white truncate">
                      {r.title}
                    </span>
                    {r.duration_min ? (
                      <span className="shrink-0 text-[10px] text-zinc-500 font-mono">
                        {r.duration_min} min
                      </span>
                    ) : null}
                  </div>
                  <div className="text-xs text-zinc-500 line-clamp-2">{r.reason}</div>
                  {r.subject && (
                    <div className="mt-1.5 inline-block text-[10px] tracking-wider uppercase text-zinc-600 font-semibold">
                      {r.subject}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
