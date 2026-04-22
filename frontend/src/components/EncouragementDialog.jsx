import { useState } from "react";
import { api } from "@/lib/api";
import { Heart, Send, Sparkles, Copy, Check } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

/**
 * Modal that asks Claude to draft a personalized encouragement message
 * for an at-risk student, letting the teacher tweak or send it.
 */
export function EncouragementDialog({ open, onOpenChange, student }) {
  const [note, setNote] = useState("");
  const [generating, setGenerating] = useState(false);
  const [message, setMessage] = useState("");
  const [sent, setSent] = useState(false);
  const [copied, setCopied] = useState(false);

  const reset = () => {
    setNote("");
    setMessage("");
    setSent(false);
    setCopied(false);
  };

  const generate = async () => {
    if (!student) return;
    setGenerating(true);
    setSent(false);
    try {
      const { data } = await api.post(`/students/${student.id}/encouragement`, {
        note: note.trim() || null,
      });
      setMessage(data.message);
      setSent(true);
      toast.success("Encouragement drafted & logged");
    } catch {
      toast.error("Could not generate message");
    } finally {
      setGenerating(false);
    }
  };

  const copyToClipboard = async () => {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(message);
      } else {
        // Fallback for iframes/insecure contexts: execCommand
        const ta = document.createElement("textarea");
        ta.value = message;
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        document.body.removeChild(ta);
      }
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast.error("Copy failed");
    }
  };

  return (
    <Dialog
      open={open}
      onOpenChange={(o) => {
        if (!o) reset();
        onOpenChange(o);
      }}
    >
      <DialogContent
        data-testid="encouragement-dialog"
        className="bg-[#12121A] border border-white/[0.08] text-white sm:max-w-lg"
      >
        <DialogHeader>
          <DialogTitle className="font-display text-xl flex items-center gap-2">
            <Heart className="h-5 w-5 text-[#FF7A59]" />
            Encourage {student?.name?.split(" ")[0]}
          </DialogTitle>
          <DialogDescription className="text-zinc-400">
            Claude will draft a short, warm message tailored to their progress.
            You can add a nudge below.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 mt-2">
          <div>
            <label className="text-[10px] tracking-[0.18em] uppercase text-zinc-500 font-semibold mb-2 block">
              Optional note to guide the AI
            </label>
            <textarea
              data-testid="encouragement-note"
              value={note}
              onChange={(e) => setNote(e.target.value)}
              rows={2}
              placeholder="e.g. celebrate improvement in Algebra this week"
              className="w-full bg-[#0E0E14] border border-white/[0.08] rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:border-[#FF7A59]/50 focus:ring-1 focus:ring-[#FF7A59]/40 resize-none"
            />
          </div>

          {message ? (
            <div
              data-testid="encouragement-message"
              className="rounded-xl bg-[#0E0E14] border border-[#FF7A59]/25 p-4"
            >
              <div className="flex items-start gap-2 mb-2 text-[10px] tracking-wider uppercase text-[#FF7A59] font-semibold">
                <Sparkles className="h-3 w-3 mt-0.5" />
                AI-drafted message
              </div>
              <div className="text-sm text-zinc-100 leading-relaxed whitespace-pre-wrap">
                {message}
              </div>
              <button
                onClick={copyToClipboard}
                data-testid="encouragement-copy-btn"
                className="mt-3 inline-flex items-center gap-1.5 text-xs text-zinc-400 hover:text-white transition-colors"
              >
                {copied ? (
                  <>
                    <Check className="h-3.5 w-3.5 text-emerald-400" /> Copied!
                  </>
                ) : (
                  <>
                    <Copy className="h-3.5 w-3.5" /> Copy message
                  </>
                )}
              </button>
            </div>
          ) : null}

          <div className="flex items-center justify-end gap-2 pt-2">
            <Button
              variant="outline"
              data-testid="encouragement-cancel-btn"
              onClick={() => onOpenChange(false)}
              className="bg-transparent border-white/10 text-white hover:bg-white/5 rounded-xl"
            >
              Close
            </Button>
            <Button
              data-testid="encouragement-generate-btn"
              disabled={generating}
              onClick={generate}
              className="bg-[#FF7A59] hover:bg-[#F97316] text-white rounded-xl"
            >
              <Send className="h-4 w-4 mr-1.5" />
              {sent ? "Regenerate" : generating ? "Drafting..." : "Generate"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
