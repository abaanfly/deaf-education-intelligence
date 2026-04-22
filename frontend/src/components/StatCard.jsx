export function StatCard({ icon: Icon, label, value, sub, accent = "orange", testid }) {
  const accents = {
    orange: "text-[#FF7A59] bg-[#FF7A59]/10 border-[#FF7A59]/20",
    sky: "text-[#38BDF8] bg-[#38BDF8]/10 border-[#38BDF8]/20",
    emerald: "text-emerald-400 bg-emerald-400/10 border-emerald-400/20",
    red: "text-red-400 bg-red-500/10 border-red-500/20",
    amber: "text-amber-400 bg-amber-500/10 border-amber-500/20",
    violet: "text-indigo-300 bg-indigo-500/10 border-indigo-500/20",
  };
  return (
    <div
      data-testid={testid}
      className="group relative rounded-2xl bg-[#12121A] border border-white/[0.07] p-6 card-inner-glow hover:bg-[#161620] transition-colors"
    >
      <div className="flex items-center gap-3 mb-4">
        <div
          className={`h-9 w-9 rounded-lg border flex items-center justify-center ${accents[accent]}`}
        >
          {Icon ? <Icon className="h-4 w-4" /> : null}
        </div>
        <div className="text-[10px] tracking-[0.18em] uppercase text-zinc-500 font-semibold">
          {label}
        </div>
      </div>
      <div className="font-mono text-3xl lg:text-4xl font-light tracking-tighter text-white">
        {value}
      </div>
      {sub && <div className="mt-2 text-xs text-zinc-500">{sub}</div>}
    </div>
  );
}
