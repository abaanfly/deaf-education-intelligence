import { Link, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  Users,
  GraduationCap,
  BookOpenCheck,
  Sparkles,
  LogOut,
} from "lucide-react";

/**
 * Shared dark app shell with left navigation rail + top bar.
 * `role` = "student" | "teacher"
 */
export function AppShell({ role, children, subtitle, studentId }) {
  const location = useLocation();

  const studentNav = [
    { to: `/student/${studentId}`, icon: LayoutDashboard, label: "Dashboard" },
    { to: `/student/${studentId}#tutor`, icon: Sparkles, label: "AI Tutor" },
  ];
  const teacherNav = [
    { to: "/teacher", icon: LayoutDashboard, label: "Overview" },
    { to: "/teacher#roster", icon: Users, label: "Students" },
  ];
  const nav = role === "teacher" ? teacherNav : studentNav;

  return (
    <div className="min-h-screen bg-[#08080C] text-zinc-100 relative overflow-x-hidden">
      {/* soft gradient background */}
      <div
        className="fixed inset-0 pointer-events-none opacity-30"
        style={{
          backgroundImage:
            "radial-gradient(60% 40% at 20% 10%, rgba(255,122,89,0.25), transparent 60%), radial-gradient(45% 35% at 85% 90%, rgba(56,189,248,0.22), transparent 60%)",
        }}
        aria-hidden
      />

      <div className="relative flex">
        {/* Sidebar */}
        <aside
          data-testid="app-sidebar"
          className="hidden md:flex flex-col w-60 border-r border-white/5 bg-[#0A0A10]/60 backdrop-blur-xl sticky top-0 h-screen"
        >
          <Link
            to="/"
            className="flex items-center gap-2 px-6 pt-6 pb-8"
            data-testid="brand-link"
          >
            <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-[#FF7A59] to-[#38BDF8] flex items-center justify-center">
              <GraduationCap className="h-5 w-5 text-white" strokeWidth={2.2} />
            </div>
            <div className="leading-tight">
              <div className="font-display text-lg font-semibold">DEIS</div>
              <div className="text-[10px] tracking-[0.2em] uppercase text-zinc-500">
                Intelligence
              </div>
            </div>
          </Link>

          <nav className="flex-1 px-3 space-y-1">
            {nav.map((item) => {
              const Icon = item.icon;
              const active = location.pathname + location.hash === item.to;
              return (
                <Link
                  key={item.label}
                  to={item.to}
                  data-testid={`nav-${item.label.toLowerCase().replace(/\s/g, "-")}`}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                    active
                      ? "bg-white/[0.06] text-white"
                      : "text-zinc-400 hover:text-white hover:bg-white/[0.04]"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </Link>
              );
            })}
          </nav>

          <div className="px-3 pb-6">
            <Link
              to="/"
              data-testid="exit-demo-btn"
              className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-zinc-500 hover:text-white hover:bg-white/[0.04] transition-colors"
            >
              <LogOut className="h-4 w-4" />
              Exit Demo
            </Link>
          </div>
        </aside>

        {/* Main */}
        <main className="flex-1 min-w-0">
          <header className="sticky top-0 z-20 border-b border-white/5 bg-[#08080C]/70 backdrop-blur-xl">
            <div className="px-6 lg:px-10 py-4 flex items-center justify-between">
              <div>
                <div className="text-[10px] tracking-[0.22em] uppercase text-zinc-500 flex items-center gap-2">
                  {role === "teacher" ? (
                    <Users className="h-3 w-3" />
                  ) : (
                    <BookOpenCheck className="h-3 w-3" />
                  )}
                  {role === "teacher" ? "Teacher Console" : "Student Workspace"}
                </div>
                <h1
                  className="font-display text-xl font-semibold tracking-tight"
                  data-testid="page-title"
                >
                  {subtitle}
                </h1>
              </div>
              <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                AI engine live
              </div>
            </div>
          </header>

          <div className="px-6 lg:px-10 py-8">{children}</div>
        </main>
      </div>
    </div>
  );
}
