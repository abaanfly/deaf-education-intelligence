import { useNavigate } from "react-router-dom";
import { ChevronRight } from "lucide-react";

export function StudentTable({ students }) {
  const navigate = useNavigate();
  return (
    <div
      id="roster"
      className="rounded-2xl border border-white/[0.07] bg-[#12121A] card-inner-glow overflow-hidden"
      data-testid="student-table"
    >
      <div className="px-6 py-5 border-b border-white/[0.06]">
        <h3 className="font-display text-base font-medium text-white">Class Roster</h3>
        <p className="text-xs text-zinc-500 mt-0.5">
          Click any student to drill down into their dashboard.
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-white/[0.02]">
            <tr>
              {["Student", "Avg", "Risk", "Trend", "Attempts", ""].map((h) => (
                <th
                  key={h}
                  className="text-left text-[10px] tracking-wider uppercase text-zinc-500 font-semibold px-6 py-3"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {students?.map((s) => (
              <tr
                key={s.id}
                onClick={() => navigate(`/student/${s.id}`)}
                data-testid={`roster-row-${s.id}`}
                className="border-t border-white/[0.04] hover:bg-white/[0.02] cursor-pointer transition-colors"
              >
                <td className="px-6 py-3.5">
                  <div className="flex items-center gap-3">
                    <img
                      src={s.avatar}
                      alt=""
                      className="h-8 w-8 rounded-full object-cover ring-1 ring-white/10"
                    />
                    <div>
                      <div className="text-white font-medium">{s.name}</div>
                      <div className="text-[11px] text-zinc-500">{s.grade}</div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-3.5 font-mono text-white">{s.avg_score}%</td>
                <td className="px-6 py-3.5">
                  <span
                    className={`inline-block text-[10px] tracking-wider font-bold px-2 py-0.5 rounded-full ${
                      s.risk === "HIGH"
                        ? "bg-red-500/10 text-red-400 border border-red-500/20"
                        : s.risk === "MEDIUM"
                          ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                          : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                    }`}
                  >
                    {s.risk}
                  </span>
                </td>
                <td
                  className={`px-6 py-3.5 font-mono text-sm ${
                    s.weekly_progress >= 0 ? "text-emerald-400" : "text-red-400"
                  }`}
                >
                  {s.weekly_progress >= 0 ? "+" : ""}
                  {s.weekly_progress}
                </td>
                <td className="px-6 py-3.5 text-zinc-400">{s.total_attempts}</td>
                <td className="px-6 py-3.5 text-right">
                  <ChevronRight className="h-4 w-4 text-zinc-600 inline" />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
