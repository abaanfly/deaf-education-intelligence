import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import { AppShell } from "@/components/AppShell";
import { StatCard } from "@/components/StatCard";
import { RiskAlerts } from "@/components/RiskAlerts";
import { TopicHeatmap } from "@/components/TopicHeatmap";
import { StudentTable } from "@/components/StudentTable";
import { TeacherActions } from "@/components/TeacherActions";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import { Users, ShieldAlert, BookOpen, Zap } from "lucide-react";
import { toast } from "sonner";

export default function TeacherDashboard() {
  const [overview, setOverview] = useState(null);
  const [heatmap, setHeatmap] = useState(null);
  const [atRisk, setAtRisk] = useState([]);
  const [students, setStudents] = useState([]);

  const loadAll = useCallback(async () => {
    try {
      const [o, h, r, s] = await Promise.all([
        api.get("/teacher/class-overview"),
        api.get("/teacher/heatmap"),
        api.get("/teacher/at-risk"),
        api.get("/students"),
      ]);
      setOverview(o.data);
      setHeatmap(h.data);
      setAtRisk(r.data);
      setStudents(s.data);
    } catch {
      toast.error("Failed to load teacher console");
    }
  }, []);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  if (!overview || !heatmap) {
    return (
      <div className="min-h-screen bg-[#08080C] flex items-center justify-center text-zinc-500">
        Loading console...
      </div>
    );
  }

  const subjectChart = Object.entries(overview.subject_avg).map(([k, v]) => ({
    subject: k,
    avg: v,
  }));

  return (
    <AppShell role="teacher" subtitle="Class Intelligence Overview">
      {/* Toolbar */}
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div className="text-[10px] tracking-[0.22em] uppercase text-zinc-500 font-semibold">
          Snapshot · {overview.total_students} students tracked
        </div>
        <TeacherActions onImportDone={loadAll} />
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          testid="kpi-students"
          icon={Users}
          label="Students"
          value={overview.total_students}
          sub={`${overview.topics_covered} subjects tracked`}
          accent="sky"
        />
        <StatCard
          testid="kpi-class-avg"
          icon={BookOpen}
          label="Class Average"
          value={`${overview.class_avg}%`}
          sub="All attempts, all topics"
          accent="emerald"
        />
        <StatCard
          testid="kpi-at-risk"
          icon={ShieldAlert}
          label="At Risk"
          value={overview.at_risk_count}
          sub="Require early intervention"
          accent="red"
        />
        <StatCard
          testid="kpi-engagement"
          icon={Zap}
          label="Engagement"
          value={`${Math.round(overview.total_engagement_min / 60)}h`}
          sub="Total class learning time"
          accent="orange"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-8">
        {/* Subject avg chart */}
        <div className="lg:col-span-8 rounded-2xl border border-white/[0.07] bg-[#12121A] p-6 lg:p-8 card-inner-glow">
          <div className="text-[10px] tracking-[0.18em] uppercase text-zinc-500 font-semibold mb-1">
            Subject Performance
          </div>
          <h2 className="font-display text-xl text-white mb-5">
            How the class performs across topics
          </h2>
          <div className="h-72 w-full" data-testid="subject-chart">
            <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={0}>
              <BarChart data={subjectChart} margin={{ top: 10, right: 8, left: -12, bottom: 0 }}>
                <defs>
                  <linearGradient id="barFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#FF7A59" stopOpacity={0.9} />
                    <stop offset="100%" stopColor="#FF7A59" stopOpacity={0.25} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="rgba(255,255,255,0.05)" vertical={false} />
                <XAxis
                  dataKey="subject"
                  stroke="#71717A"
                  fontSize={11}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  stroke="#71717A"
                  fontSize={11}
                  tickLine={false}
                  axisLine={false}
                  domain={[0, 100]}
                />
                <Tooltip
                  cursor={{ fill: "rgba(255,255,255,0.04)" }}
                  contentStyle={{
                    background: "#12121A",
                    border: "1px solid rgba(255,255,255,0.08)",
                    borderRadius: 12,
                    color: "#fff",
                  }}
                />
                <Bar dataKey="avg" fill="#FF7A59" radius={[8, 8, 0, 0]} isAnimationActive={false} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Risk alerts */}
        <div className="lg:col-span-4">
          <RiskAlerts students={atRisk} />
        </div>
      </div>

      {/* Heatmap */}
      <div className="mb-8">
        <TopicHeatmap subjects={heatmap.subjects} rows={heatmap.rows} />
      </div>

      {/* Roster */}
      <StudentTable students={students} />
    </AppShell>
  );
}
