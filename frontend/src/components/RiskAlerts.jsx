import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ShieldAlert, ChevronRight, Heart } from "lucide-react";
import { EncouragementDialog } from "@/components/EncouragementDialog";

export function RiskAlerts({ students }) {
  const navigate = useNavigate();
  const [selected, setSelected] = useState(null);
  const [open, setOpen] = useState(false);

  return (
    <div
      className="rounded-2xl border border-white/[0.07] bg-[#12121A] p-6 card-inner-glow"
      data-testid="risk-alerts"
    >
      <div className="flex items-center gap-2 mb-1">
        <ShieldAlert className="h-4 w-4 text-red-400" />
        <h3 className="font-display text-base font-medium text-white">At-Risk Students</h3>
      </div>
      <p className="text-xs text-zinc-500 mb-5">
        Students predicted to struggle. Prioritize early outreach.
      </p>

      {students?.length === 0 && (
        <div className="text-sm text-emerald-400/80">All students are on track.</div>
      )}

      <div className="space-y-2">
        {students?.map((s) => (
          <div
            key={s.id}
            data-testid={`risk-student-${s.id}`}
            className="w-full flex items-center gap-3 p-3 rounded-xl bg-[#0E0E14] border border-white/[0.05] hover:border-white/[0.12] hover:bg-[#11111A] transition-all"
          >
            <button
              onClick={() => navigate(`/student/${s.id}`)}
              className="flex items-center gap-3 min-w-0 flex-1 text-left"
              data-testid={`risk-student-drill-${s.id}`}
            >
              <img
                src={s.avatar}
                alt=""
                className="h-9 w-9 rounded-full object-cover ring-1 ring-white/10"
              />
              <div className="min-w-0 flex-1">
                <div className="text-sm font-medium text-white truncate">{s.name}</div>
                <div className="text-[11px] text-zinc-500">{s.grade}</div>
              </div>
              <div className="text-right">
                <div className="font-mono text-sm text-white">{s.avg_score}%</div>
                <div
                  className={`text-[10px] font-bold tracking-wider ${
                    s.risk === "HIGH" ? "text-red-400" : "text-amber-400"
                  }`}
                >
                  {s.risk}
                </div>
              </div>
              <ChevronRight className="h-4 w-4 text-zinc-600" />
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                setSelected(s);
                setOpen(true);
              }}
              data-testid={`encourage-btn-${s.id}`}
              aria-label={`Send encouragement to ${s.name}`}
              className="shrink-0 h-8 w-8 rounded-lg bg-[#FF7A59]/10 border border-[#FF7A59]/25 text-[#FF7A59] hover:bg-[#FF7A59]/20 transition-colors flex items-center justify-center"
            >
              <Heart className="h-3.5 w-3.5" />
            </button>
          </div>
        ))}
      </div>

      <EncouragementDialog open={open} onOpenChange={setOpen} student={selected} />
    </div>
  );
}
