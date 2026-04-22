import { useEffect, useState, useCallback } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "@/lib/api";
import { AppShell } from "@/components/AppShell";
import { StatCard } from "@/components/StatCard";
import { PerformanceChart } from "@/components/PerformanceChart";
import { WeakTopicsPanel } from "@/components/WeakTopicsPanel";
import { AIRecommendations } from "@/components/AIRecommendations";
import { AITutorChat } from "@/components/AITutorChat";
import {
  Gauge,
  ShieldAlert,
  TrendingUp,
  Clock3,
  BookOpenCheck,
  PlayCircle,
  ChevronRight,
} from "lucide-react";
import { toast } from "sonner";

export default function StudentDashboard() {
  const { studentId } = useParams();
  const navigate = useNavigate();

  const [student, setStudent] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [recs, setRecs] = useState([]);
  const [recsLoading, setRecsLoading] = useState(false);
  const [quizzes, setQuizzes] = useState([]);
  const [prediction, setPrediction] = useState(null);

  const loadRecs = useCallback(async () => {
    setRecsLoading(true);
    try {
      const { data } = await api.post(`/students/${studentId}/recommendations`, {
        refresh: true,
      });
      setRecs(data.recommendations || []);
    } catch {
      toast.error("Failed to load AI recommendations");
    } finally {
      setRecsLoading(false);
    }
  }, [studentId]);

  useEffect(() => {
    (async () => {
      try {
        const [s, p, q, pr] = await Promise.all([
          api.get(`/students/${studentId}`),
          api.get(`/students/${studentId}/performance`),
          api.get(`/quizzes`),
          api.post(`/students/${studentId}/predict`),
        ]);
        setStudent(s.data);
        setPerformance(p.data);
        setQuizzes(q.data);
        setPrediction(pr.data);
      } catch {
        toast.error("Failed to load dashboard");
      }
    })();
    loadRecs();
  }, [studentId, loadRecs]);

  if (!student) {
    return (
      <div className="min-h-screen bg-[#08080C] flex items-center justify-center text-zinc-500">
        Loading dashboard...
      </div>
    );
  }

  const riskColor =
    student.risk === "HIGH" ? "red" : student.risk === "MEDIUM" ? "amber" : "emerald";

  return (
    <AppShell
      role="student"
      studentId={studentId}
      subtitle={`Welcome back, ${student.name.split(" ")[0]}`}
    >
      {/* Greeting hero */}
      <div className="mb-8 flex items-center gap-4">
        <img
          src={student.avatar}
          alt=""
          className="h-14 w-14 rounded-full object-cover ring-2 ring-white/10"
        />
        <div>
          <div className="text-xs tracking-wider uppercase text-zinc-500">
            {student.grade} · Personalized for visual learners
          </div>
          <div className="font-display text-2xl lg:text-3xl font-semibold text-white mt-0.5">
            Let's bridge your weak topics today.
          </div>
        </div>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          testid="stat-overall-score"
          icon={Gauge}
          label="Overall Score"
          value={`${student.avg_score}%`}
          sub={`${student.total_attempts} attempts`}
          accent="sky"
        />
        <StatCard
          testid="stat-risk"
          icon={ShieldAlert}
          label="Risk Level"
          value={student.risk}
          sub={
            prediction
              ? `${prediction.fail_probability_pct}% fail chance`
              : "Calculating..."
          }
          accent={riskColor}
        />
        <StatCard
          testid="stat-progress"
          icon={TrendingUp}
          label="Weekly Progress"
          value={`${student.weekly_progress >= 0 ? "+" : ""}${student.weekly_progress}`}
          sub="vs first week"
          accent={student.weekly_progress >= 0 ? "emerald" : "red"}
        />
        <StatCard
          testid="stat-time"
          icon={Clock3}
          label="Time Invested"
          value={`${Math.round(student.time_spent_min / 60)}h`}
          sub={`${student.time_spent_min} minutes total`}
          accent="orange"
        />
      </div>

      {/* Main grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left column */}
        <div className="lg:col-span-8 space-y-6">
          <section
            className="rounded-2xl border border-white/[0.07] bg-[#12121A] p-6 lg:p-8 card-inner-glow"
            data-testid="performance-card"
          >
            <div className="flex items-start justify-between mb-5">
              <div>
                <div className="text-[10px] tracking-[0.18em] uppercase text-zinc-500 font-semibold mb-1">
                  Performance Timeline
                </div>
                <h2 className="font-display text-xl text-white">
                  How your scores are trending
                </h2>
              </div>
              {prediction && (
                <div className="text-right text-xs">
                  <div className="text-zinc-500">AI Prediction</div>
                  <div className="font-mono text-white">
                    {prediction.pass_probability_pct}% pass next
                  </div>
                </div>
              )}
            </div>
            <PerformanceChart data={performance?.timeline || []} />
          </section>

          <AIRecommendations
            items={recs}
            loading={recsLoading}
            onRefresh={loadRecs}
          />

          {/* Practice quizzes */}
          <section
            className="rounded-2xl border border-white/[0.07] bg-[#12121A] p-6 lg:p-8 card-inner-glow"
            data-testid="practice-quizzes"
          >
            <div className="flex items-center gap-2 mb-1">
              <BookOpenCheck className="h-4 w-4 text-[#38BDF8]" />
              <h3 className="font-display text-base font-medium text-white">
                Practice Quizzes
              </h3>
            </div>
            <p className="text-xs text-zinc-500 mb-5">
              Short sets (5 questions). Your scores flow back into your predictions.
            </p>
            <div className="grid sm:grid-cols-2 gap-3">
              {quizzes.map((q) => (
                <button
                  key={q.id}
                  onClick={() => navigate(`/student/${studentId}/quiz/${q.id}`)}
                  data-testid={`start-quiz-${q.id}`}
                  className="group text-left p-4 rounded-xl bg-[#0E0E14] border border-white/[0.05] hover:border-[#FF7A59]/30 hover:bg-[#11111A] transition-all"
                >
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-lg bg-[#FF7A59]/10 border border-[#FF7A59]/20 flex items-center justify-center">
                      <PlayCircle className="h-4 w-4 text-[#FF7A59]" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="text-sm font-medium text-white truncate">
                        {q.title}
                      </div>
                      <div className="text-[11px] text-zinc-500 mt-0.5">
                        {q.subject} · {q.difficulty} · {q.question_count} Qs
                      </div>
                    </div>
                    <ChevronRight className="h-4 w-4 text-zinc-600 group-hover:text-[#FF7A59] transition-colors" />
                  </div>
                </button>
              ))}
            </div>
          </section>
        </div>

        {/* Right column */}
        <div className="lg:col-span-4 space-y-6">
          <WeakTopicsPanel weakTopics={student.weak_topics} />
          <AITutorChat studentId={studentId} />
        </div>
      </div>
    </AppShell>
  );
}
