import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";
import { Send, Bot, User as UserIcon, History } from "lucide-react";

export function AITutorChat({ studentId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const sessionId = `tutor_${studentId}`;
  const scrollRef = useRef(null);

  // Load persisted history on mount / when student changes
  useEffect(() => {
    let cancelled = false;
    setMessages([]);
    setLoadingHistory(true);
    (async () => {
      try {
        const { data } = await api.get(`/ai-tutor/history/${studentId}`);
        if (cancelled) return;
        // Flatten each record into user + assistant messages
        const hist = [];
        data.forEach((m) => {
          if (m.user_message) hist.push({ role: "user", text: m.user_message });
          if (m.assistant_message) hist.push({ role: "assistant", text: m.assistant_message });
        });
        setMessages(hist);
      } catch {
        // noop — start empty
      } finally {
        if (!cancelled) setLoadingHistory(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [studentId]);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  const send = async (e) => {
    e?.preventDefault();
    if (!input.trim() || loading) return;
    const text = input.trim();
    setInput("");
    setMessages((m) => [...m, { role: "user", text }]);
    setLoading(true);
    try {
      const { data } = await api.post("/ai-tutor/chat", {
        student_id: studentId,
        session_id: sessionId,
        message: text,
      });
      setMessages((m) => [...m, { role: "assistant", text: data.reply }]);
    } catch {
      setMessages((m) => [
        ...m,
        { role: "assistant", text: "Sorry, I had trouble reaching the AI. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      id="tutor"
      data-testid="ai-tutor-chat"
      className="rounded-2xl border border-white/[0.07] bg-[#12121A] card-inner-glow flex flex-col h-[520px]"
    >
      <div className="px-6 py-4 border-b border-white/[0.06] flex items-center gap-3">
        <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-[#FF7A59] to-[#38BDF8] flex items-center justify-center">
          <Bot className="h-4 w-4 text-white" />
        </div>
        <div className="flex-1">
          <div className="font-display font-medium text-white text-sm">DEIS Tutor</div>
          <div className="text-[11px] text-zinc-500">Visual-first AI learning coach</div>
        </div>
        {messages.length > 0 && (
          <div
            className="flex items-center gap-1 text-[10px] tracking-wider uppercase text-zinc-500"
            data-testid="tutor-history-indicator"
          >
            <History className="h-3 w-3" />
            {Math.ceil(messages.length / 2)} exchanges
          </div>
        )}
      </div>

      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto px-6 py-5 space-y-4"
        data-testid="tutor-messages"
      >
        {loadingHistory ? (
          <div className="text-center text-zinc-600 text-xs mt-16">
            Loading your chat history...
          </div>
        ) : messages.length === 0 ? (
          <div className="text-center text-zinc-500 text-sm mt-12">
            <Bot className="h-8 w-8 mx-auto mb-3 text-zinc-700" />
            <p className="font-medium text-zinc-300 mb-1">Ask me anything</p>
            <p className="text-xs">
              Try: <em>"Explain fractions with a picture"</em>
            </p>
          </div>
        ) : (
          messages.map((m, i) => (
            <div
              key={i}
              className={`flex gap-3 ${m.role === "user" ? "flex-row-reverse" : ""}`}
            >
              <div
                className={`shrink-0 h-8 w-8 rounded-full flex items-center justify-center ${
                  m.role === "user"
                    ? "bg-[#38BDF8]/15 text-[#38BDF8]"
                    : "bg-[#FF7A59]/15 text-[#FF7A59]"
                }`}
              >
                {m.role === "user" ? <UserIcon className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
              </div>
              <div
                className={`max-w-[80%] text-sm leading-relaxed rounded-2xl px-4 py-2.5 whitespace-pre-wrap ${
                  m.role === "user"
                    ? "bg-[#38BDF8]/10 border border-[#38BDF8]/20 text-sky-100"
                    : "bg-[#0E0E14] border border-white/[0.06] text-zinc-200"
                }`}
              >
                {m.text}
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="flex gap-3">
            <div className="h-8 w-8 rounded-full bg-[#FF7A59]/15 flex items-center justify-center">
              <Bot className="h-4 w-4 text-[#FF7A59]" />
            </div>
            <div className="flex items-center gap-1 bg-[#0E0E14] border border-white/[0.06] rounded-2xl px-4 py-3">
              <span className="h-1.5 w-1.5 rounded-full bg-zinc-500 animate-pulse" />
              <span className="h-1.5 w-1.5 rounded-full bg-zinc-500 animate-pulse [animation-delay:0.15s]" />
              <span className="h-1.5 w-1.5 rounded-full bg-zinc-500 animate-pulse [animation-delay:0.3s]" />
            </div>
          </div>
        )}
      </div>

      <form
        onSubmit={send}
        className="border-t border-white/[0.06] px-4 py-3 flex items-center gap-2"
      >
        <input
          data-testid="tutor-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question..."
          className="flex-1 bg-[#0E0E14] border border-white/[0.08] rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:border-[#FF7A59]/50 focus:ring-1 focus:ring-[#FF7A59]/40"
        />
        <button
          type="submit"
          data-testid="tutor-send-btn"
          disabled={loading || !input.trim()}
          className="h-10 w-10 rounded-xl bg-[#FF7A59] hover:bg-[#F97316] disabled:opacity-40 flex items-center justify-center transition-all active:scale-[0.96]"
        >
          <Send className="h-4 w-4 text-white" />
        </button>
      </form>
    </div>
  );
}
