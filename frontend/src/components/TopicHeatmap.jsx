import { Flame } from "lucide-react";

function cellColor(score) {
  if (score == null) return "bg-white/[0.03] text-zinc-600";
  if (score >= 80) return "bg-emerald-500/20 text-emerald-200 border-emerald-500/20";
  if (score >= 65) return "bg-sky-500/15 text-sky-200 border-sky-500/20";
  if (score >= 50) return "bg-amber-500/20 text-amber-200 border-amber-500/25";
  return "bg-red-500/25 text-red-100 border-red-500/30";
}

export function TopicHeatmap({ subjects, rows }) {
  return (
    <div
      className="rounded-2xl border border-white/[0.07] bg-[#12121A] p-6 card-inner-glow"
      data-testid="topic-heatmap"
    >
      <div className="flex items-center gap-2 mb-1">
        <Flame className="h-4 w-4 text-[#FF7A59]" />
        <h3 className="font-display text-base font-medium text-white">
          Topic Difficulty Heatmap
        </h3>
      </div>
      <p className="text-xs text-zinc-500 mb-5">
        Darker red = class is struggling. Green = mastered.
      </p>

      <div className="overflow-x-auto">
        <table className="w-full text-sm border-separate border-spacing-1">
          <thead>
            <tr>
              <th className="text-left text-[10px] tracking-wider uppercase text-zinc-500 font-semibold px-2 py-2 w-40">
                Student
              </th>
              {subjects.map((s) => (
                <th
                  key={s}
                  className="text-center text-[10px] tracking-wider uppercase text-zinc-500 font-semibold px-2 py-2"
                >
                  {s}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.student_id}>
                <td className="text-sm text-zinc-200 px-2 py-1.5 truncate">{r.name}</td>
                {subjects.map((s) => {
                  const v = r.scores[s];
                  return (
                    <td key={s} className="px-0.5 py-0.5">
                      <div
                        className={`font-mono text-xs text-center py-2 rounded-md border ${cellColor(
                          v
                        )}`}
                      >
                        {v != null ? Math.round(v) : "—"}
                      </div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
