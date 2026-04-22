import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "@/lib/api";
import { AppShell } from "@/components/AppShell";
import { Button } from "@/components/ui/button";
import { CheckCircle2, ArrowLeft, Trophy } from "lucide-react";
import { toast } from "sonner";

export default function QuizPage() {
  const { studentId, quizId } = useParams();
  const navigate = useNavigate();
  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [startedAt] = useState(Date.now());

  useEffect(() => {
    (async () => {
      try {
        const { data } = await api.get(`/quizzes/${quizId}`);
        setQuiz(data);
      } catch {
        toast.error("Failed to load quiz");
      }
    })();
  }, [quizId]);

  const onSubmit = async () => {
    if (Object.keys(answers).length < (quiz?.questions.length || 0)) {
      toast.warning("Please answer every question");
      return;
    }
    setSubmitting(true);
    try {
      const timeMin = Math.max(1, Math.round((Date.now() - startedAt) / 60000));
      const ordered = quiz.questions.map((_, i) => answers[i]);
      const { data } = await api.post(`/quizzes/${quizId}/attempt`, {
        student_id: studentId,
        answers: ordered,
        time_spent_min: timeMin,
      });
      setResult(data);
      toast.success(`Scored ${data.score}%`);
    } catch {
      toast.error("Submission failed");
    } finally {
      setSubmitting(false);
    }
  };

  if (!quiz) {
    return (
      <div className="min-h-screen bg-[#08080C] flex items-center justify-center text-zinc-500">
        Loading quiz...
      </div>
    );
  }

  return (
    <AppShell role="student" studentId={studentId} subtitle={quiz.title}>
      <button
        onClick={() => navigate(`/student/${studentId}`)}
        data-testid="back-to-dashboard-btn"
        className="mb-6 inline-flex items-center gap-2 text-sm text-zinc-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="h-4 w-4" /> Back to dashboard
      </button>

      {result ? (
        <div
          data-testid="quiz-result"
          className="rounded-3xl border border-white/[0.07] bg-[#12121A] p-10 lg:p-14 text-center card-inner-glow"
        >
          <div className="inline-flex items-center justify-center h-16 w-16 rounded-2xl bg-[#FF7A59]/15 border border-[#FF7A59]/30 mb-6">
            <Trophy className="h-7 w-7 text-[#FF7A59]" />
          </div>
          <div className="text-[11px] tracking-[0.22em] uppercase text-zinc-500 font-semibold mb-2">
            Quiz complete
          </div>
          <h2 className="font-display text-5xl font-light text-white mb-2">
            {result.score}
            <span className="text-3xl text-zinc-500">%</span>
          </h2>
          <p className="text-sm text-zinc-400 max-w-md mx-auto mb-8">
            You got <span className="text-white font-medium">{result.correct} of{" "}
            {result.total}</span> correct. Your prediction model has been updated.
          </p>
          <div className="flex items-center justify-center gap-3">
            <Button
              data-testid="go-dashboard-btn"
              onClick={() => navigate(`/student/${studentId}`)}
              className="bg-[#FF7A59] hover:bg-[#F97316] text-white rounded-xl px-6"
            >
              Back to dashboard
            </Button>
            <Button
              variant="outline"
              data-testid="retry-quiz-btn"
              onClick={() => {
                setAnswers({});
                setResult(null);
              }}
              className="bg-transparent border-white/10 text-white hover:bg-white/5 rounded-xl px-6"
            >
              Retry quiz
            </Button>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="rounded-2xl border border-white/[0.07] bg-[#12121A] p-6 card-inner-glow flex items-center justify-between">
            <div>
              <div className="text-[10px] tracking-[0.18em] uppercase text-zinc-500 font-semibold mb-1">
                {quiz.subject} · {quiz.difficulty}
              </div>
              <div className="font-display text-xl text-white">{quiz.title}</div>
            </div>
            <div className="text-right text-xs text-zinc-500">
              <div className="font-mono text-sm text-white">
                {Object.keys(answers).length} / {quiz.questions.length}
              </div>
              answered
            </div>
          </div>

          {quiz.questions.map((q, idx) => (
            <div
              key={idx}
              data-testid={`question-${idx}`}
              className="rounded-2xl border border-white/[0.07] bg-[#12121A] p-6 card-inner-glow"
            >
              <div className="flex items-start gap-3 mb-5">
                <div className="shrink-0 h-7 w-7 rounded-lg bg-white/[0.04] border border-white/[0.06] flex items-center justify-center text-xs font-mono text-zinc-400">
                  {idx + 1}
                </div>
                <div className="font-display text-lg text-white">{q.q}</div>
              </div>
              <div className="grid sm:grid-cols-2 gap-2">
                {q.options.map((opt, oi) => {
                  const chosen = answers[idx] === oi;
                  return (
                    <button
                      key={oi}
                      onClick={() => setAnswers({ ...answers, [idx]: oi })}
                      data-testid={`q-${idx}-option-${oi}`}
                      className={`text-left px-4 py-3 rounded-xl border text-sm transition-all ${
                        chosen
                          ? "bg-[#FF7A59]/10 border-[#FF7A59]/40 text-white"
                          : "bg-[#0E0E14] border-white/[0.05] text-zinc-300 hover:border-white/[0.15]"
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs text-zinc-500">
                          {String.fromCharCode(65 + oi)}
                        </span>
                        <span>{opt}</span>
                        {chosen && (
                          <CheckCircle2 className="ml-auto h-4 w-4 text-[#FF7A59]" />
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          ))}

          <div className="flex justify-center pt-2 pb-24">
            <Button
              onClick={onSubmit}
              disabled={submitting}
              data-testid="submit-quiz-btn"
              className="bg-[#FF7A59] hover:bg-[#F97316] text-white rounded-xl px-10 py-6 text-base font-medium w-full sm:w-auto"
            >
              {submitting ? "Submitting..." : "Submit quiz"}
            </Button>
          </div>
        </div>
      )}
    </AppShell>
  );
}
