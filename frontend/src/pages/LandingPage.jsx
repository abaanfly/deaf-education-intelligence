import { useNavigate } from "react-router-dom";
import {
  GraduationCap,
  Sparkles,
  Users,
  BrainCircuit,
  Eye,
  ShieldCheck,
  ArrowRight,
} from "lucide-react";

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#08080C] text-zinc-100 relative overflow-hidden">
      {/* gradient backdrop */}
      <div
        className="absolute inset-0 pointer-events-none opacity-60"
        style={{
          backgroundImage:
            "radial-gradient(50% 40% at 18% 20%, rgba(255,122,89,0.30), transparent 60%), radial-gradient(45% 40% at 88% 78%, rgba(56,189,248,0.28), transparent 60%), radial-gradient(30% 25% at 50% 100%, rgba(129,140,248,0.18), transparent 60%)",
        }}
        aria-hidden
      />
      {/* grid pattern */}
      <div
        className="absolute inset-0 opacity-[0.04] pointer-events-none"
        style={{
          backgroundImage:
            "linear-gradient(rgba(255,255,255,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.5) 1px, transparent 1px)",
          backgroundSize: "44px 44px",
        }}
        aria-hidden
      />

      <div className="relative">
        {/* Nav */}
        <nav className="flex items-center justify-between px-6 lg:px-12 py-6">
          <div className="flex items-center gap-2.5">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-[#FF7A59] to-[#38BDF8] flex items-center justify-center shadow-lg shadow-[#FF7A59]/20">
              <GraduationCap className="h-5 w-5 text-white" strokeWidth={2.2} />
            </div>
            <div>
              <div className="font-display text-lg font-semibold leading-none">DEIS</div>
              <div className="text-[10px] tracking-[0.22em] uppercase text-zinc-500 mt-0.5">
                Intelligence
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/[0.04] border border-white/[0.06] text-xs text-zinc-400">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Live AI engine
            </div>
          </div>
        </nav>

        {/* Hero */}
        <div className="px-6 lg:px-12 pt-10 pb-8 max-w-6xl mx-auto">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/[0.04] border border-white/[0.06] text-[11px] tracking-wider uppercase text-zinc-400 font-semibold mb-7 anim-fade-up">
            <Sparkles className="h-3 w-3 text-[#FF7A59]" />
            Accessibility × Intelligence
          </div>
          <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl font-semibold tracking-tight leading-[1.05] max-w-4xl anim-fade-up">
            Turning accessibility into{" "}
            <span className="bg-gradient-to-r from-[#FF7A59] via-[#F472B6] to-[#38BDF8] bg-clip-text text-transparent">
              actionable intelligence
            </span>{" "}
            for Deaf learners.
          </h1>
          <p className="mt-6 text-base sm:text-lg text-zinc-400 leading-relaxed max-w-2xl anim-fade-up">
            DEIS is the first AI-powered learning intelligence system designed for Deaf
            and Hard-of-Hearing students. Track learning behavior, detect weak topics
            early, and recommend visual-first paths — for every student.
          </p>

          {/* Feature pills */}
          <div className="mt-8 flex flex-wrap gap-2 anim-fade-up">
            {[
              { icon: BrainCircuit, label: "AI Performance Prediction" },
              { icon: Eye, label: "Weak Topic Detection" },
              { icon: ShieldCheck, label: "Visual-First Recommendations" },
            ].map(({ icon: Icon, label }) => (
              <div
                key={label}
                className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/[0.03] border border-white/[0.07] text-xs text-zinc-300"
              >
                <Icon className="h-3.5 w-3.5 text-[#38BDF8]" />
                {label}
              </div>
            ))}
          </div>
        </div>

        {/* Role cards */}
        <div className="px-6 lg:px-12 pb-20 max-w-6xl mx-auto">
          <div className="text-[10px] tracking-[0.22em] uppercase text-zinc-500 font-semibold mb-4 flex items-center gap-2">
            <span className="h-px w-8 bg-white/10" />
            Enter the demo as
          </div>
          <div className="grid md:grid-cols-2 gap-5">
            <RoleCard
              testid="enter-as-student-btn"
              onClick={() => navigate("/student/stu_001")}
              icon={GraduationCap}
              title="Student"
              description="Your personalized dashboard with AI tutor, visual recommendations, and progress insights."
              badges={["AI Tutor", "Progress", "Visual-first"]}
              accent="#FF7A59"
              glow="255,122,89"
            />
            <RoleCard
              testid="enter-as-teacher-btn"
              onClick={() => navigate("/teacher")}
              icon={Users}
              title="Teacher"
              description="Class intelligence console with at-risk alerts, topic heatmap, and student drill-down."
              badges={["Class insights", "Risk alerts", "Heatmap"]}
              accent="#38BDF8"
              glow="56,189,248"
            />
          </div>

          {/* Footer quote */}
          <div className="mt-14 pt-8 border-t border-white/[0.05] text-sm text-zinc-500 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div>
              <span className="text-zinc-300 font-medium">Vision.</span> Build the
              world's first AI-powered education intelligence system for Deaf learners.
            </div>
            <div className="text-[11px] tracking-wider uppercase">
              Demo environment · Seeded data
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function RoleCard({ icon: Icon, title, description, badges, onClick, accent, glow, testid }) {
  return (
    <button
      onClick={onClick}
      data-testid={testid}
      className="group relative text-left rounded-3xl p-8 lg:p-10 bg-[#0C0C12] border border-white/[0.06] hover:border-white/[0.14] transition-all overflow-hidden"
      style={{
        boxShadow: `inset 0 1px 0 0 rgba(255,255,255,0.04)`,
      }}
    >
      {/* halo */}
      <div
        className="absolute -top-16 -right-16 h-56 w-56 rounded-full opacity-40 group-hover:opacity-70 transition-opacity blur-3xl pointer-events-none"
        style={{ background: `rgba(${glow}, 0.35)` }}
      />
      <div className="relative">
        <div
          className="h-12 w-12 rounded-2xl flex items-center justify-center mb-6"
          style={{
            background: `rgba(${glow}, 0.14)`,
            border: `1px solid rgba(${glow}, 0.25)`,
            color: accent,
          }}
        >
          <Icon className="h-5 w-5" />
        </div>
        <div className="font-display text-2xl font-semibold text-white mb-2">
          {title}
        </div>
        <p className="text-sm text-zinc-400 leading-relaxed mb-6 max-w-md">
          {description}
        </p>
        <div className="flex flex-wrap gap-1.5 mb-7">
          {badges.map((b) => (
            <span
              key={b}
              className="text-[10px] tracking-wider uppercase font-semibold text-zinc-400 px-2 py-1 rounded-md bg-white/[0.04] border border-white/[0.05]"
            >
              {b}
            </span>
          ))}
        </div>
        <div
          className="inline-flex items-center gap-2 text-sm font-medium group-hover:gap-3 transition-all"
          style={{ color: accent }}
        >
          Enter workspace <ArrowRight className="h-4 w-4" />
        </div>
      </div>
    </button>
  );
}
