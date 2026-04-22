import { useEffect, useState } from "react";
import { api, API } from "@/lib/api";
import {
  Download,
  FileText,
  Sheet,
  DatabaseZap,
  Loader2,
  BookOpen,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { toast } from "sonner";

const ADMIN_TOKEN = process.env.REACT_APP_ADMIN_TOKEN;
const ADMIN_HEADERS = { headers: { "X-Admin-Token": ADMIN_TOKEN } };

/**
 * Teacher toolbar:
 *  - Export CSV / PDF (direct download)
 *  - Open-education datasets manager (UCI / OULAD / Kaggle xAPI)
 */
export function TeacherActions({ onImportDone }) {
  const [importOpen, setImportOpen] = useState(false);
  const [datasets, setDatasets] = useState([]);
  const [selectedKey, setSelectedKey] = useState(null);
  const [busyKey, setBusyKey] = useState(null); // `${action}:${key}`

  const refresh = async () => {
    try {
      const { data } = await api.get("/admin/datasets", ADMIN_HEADERS);
      setDatasets(data);
      if (!selectedKey && data.length) setSelectedKey(data[0].key);
    } catch {
      toast.error("Dataset catalog unavailable");
    }
  };

  useEffect(() => {
    if (importOpen) refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [importOpen]);

  const download = (format) => {
    window.open(`${API}/teacher/export/${format}`, "_blank", "noopener,noreferrer");
  };

  const runImport = async (key) => {
    setBusyKey(`import:${key}`);
    try {
      const { data } = await api.post(`/admin/datasets/${key}/import`, {}, ADMIN_HEADERS);
      toast.success(
        `${data.dataset}: +${data.imported_students} students, +${data.imported_attempts} attempts`,
      );
      await refresh();
      onImportDone?.();
    } catch {
      toast.error("Import failed");
    } finally {
      setBusyKey(null);
    }
  };

  const runReset = async (key) => {
    setBusyKey(`reset:${key}`);
    try {
      const { data } = await api.post(`/admin/datasets/${key}/reset`, {}, ADMIN_HEADERS);
      toast.success(`Removed ${data.deleted_students} students from ${key.toUpperCase()}`);
      await refresh();
      onImportDone?.();
    } catch {
      toast.error("Reset failed");
    } finally {
      setBusyKey(null);
    }
  };

  const runResetAll = async () => {
    setBusyKey("reset-all");
    try {
      const { data } = await api.post("/admin/datasets/reset-all", {}, ADMIN_HEADERS);
      toast.success(`Removed ${data.deleted_students} imported students (all datasets)`);
      await refresh();
      onImportDone?.();
    } catch {
      toast.error("Reset-all failed");
    } finally {
      setBusyKey(null);
    }
  };

  const selected = datasets.find((d) => d.key === selectedKey);

  return (
    <>
      <div className="flex flex-wrap items-center gap-2" data-testid="teacher-actions">
        <Button
          variant="outline"
          data-testid="export-csv-btn"
          onClick={() => download("csv")}
          className="bg-transparent border-white/10 text-white hover:bg-white/5 rounded-xl"
        >
          <Sheet className="h-4 w-4 mr-1.5" /> Export CSV
        </Button>
        <Button
          variant="outline"
          data-testid="export-pdf-btn"
          onClick={() => download("pdf")}
          className="bg-transparent border-white/10 text-white hover:bg-white/5 rounded-xl"
        >
          <FileText className="h-4 w-4 mr-1.5" /> Export PDF
        </Button>
        <Button
          data-testid="import-dataset-btn"
          onClick={() => setImportOpen(true)}
          className="bg-[#38BDF8]/15 border border-[#38BDF8]/30 text-[#38BDF8] hover:bg-[#38BDF8]/25 rounded-xl"
        >
          <DatabaseZap className="h-4 w-4 mr-1.5" /> Open datasets
        </Button>
      </div>

      <Dialog open={importOpen} onOpenChange={setImportOpen}>
        <DialogContent
          data-testid="import-dialog"
          className="bg-[#12121A] border border-white/[0.08] text-white sm:max-w-2xl"
        >
          <DialogHeader>
            <DialogTitle className="font-display text-xl flex items-center gap-2">
              <DatabaseZap className="h-5 w-5 text-[#38BDF8]" />
              Open-education datasets
            </DialogTitle>
            <DialogDescription className="text-zinc-400">
              Plug in real-world learning-analytics datasets. Each import
              becomes additional students + quiz attempts in your class, tagged
              so you can remove them independently.
            </DialogDescription>
          </DialogHeader>

          {/* Dataset tabs */}
          <div className="flex flex-wrap gap-2 border-b border-white/[0.06] pb-3">
            {datasets.map((d) => (
              <button
                key={d.key}
                data-testid={`dataset-tab-${d.key}`}
                onClick={() => setSelectedKey(d.key)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors flex items-center gap-1.5 ${
                  d.key === selectedKey
                    ? "bg-[#38BDF8]/15 border border-[#38BDF8]/30 text-[#38BDF8]"
                    : "bg-white/[0.03] border border-white/[0.06] text-zinc-400 hover:text-white"
                }`}
              >
                <BookOpen className="h-3 w-3" />
                {d.key.toUpperCase()}
                <span className="font-mono text-[10px] text-zinc-500 ml-1">
                  {d.already_imported}/{d.available_records}
                </span>
              </button>
            ))}
          </div>

          {/* Selected dataset card */}
          {selected ? (
            <div
              className="space-y-3 text-sm"
              data-testid={`dataset-panel-${selected.key}`}
            >
              <div className="rounded-xl bg-[#0E0E14] border border-white/[0.06] p-4 space-y-2">
                <div className="text-[10px] tracking-[0.18em] uppercase text-zinc-500 font-semibold">
                  Dataset
                </div>
                <div className="font-medium text-white">{selected.name}</div>
                <div className="text-xs text-zinc-500 leading-relaxed">
                  {selected.source}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-xl bg-[#0E0E14] border border-white/[0.06] p-3">
                  <div className="text-[10px] tracking-wider uppercase text-zinc-500 font-semibold">
                    Available
                  </div>
                  <div className="font-mono text-lg text-white">
                    {selected.available_records}
                  </div>
                </div>
                <div className="rounded-xl bg-[#0E0E14] border border-white/[0.06] p-3">
                  <div className="text-[10px] tracking-wider uppercase text-zinc-500 font-semibold">
                    Already imported
                  </div>
                  <div className="font-mono text-lg text-white">
                    {selected.already_imported}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-zinc-500 text-xs">Loading...</div>
          )}

          <div className="flex items-center justify-between gap-2 pt-3 border-t border-white/[0.06]">
            <Button
              variant="outline"
              onClick={runResetAll}
              disabled={busyKey !== null}
              data-testid="reset-all-btn"
              className="bg-transparent border-red-500/20 text-red-300 hover:bg-red-500/10 rounded-xl"
            >
              {busyKey === "reset-all" ? (
                <Loader2 className="h-4 w-4 mr-1.5 animate-spin" />
              ) : null}
              Reset all
            </Button>
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => selected && runReset(selected.key)}
                disabled={
                  busyKey !== null || !selected || selected.already_imported === 0
                }
                data-testid={selected ? `reset-dataset-btn-${selected.key}` : "reset-dataset-btn"}
                className="bg-transparent border-white/10 text-white hover:bg-white/5 rounded-xl"
              >
                {busyKey === `reset:${selected?.key}` ? (
                  <Loader2 className="h-4 w-4 mr-1.5 animate-spin" />
                ) : null}
                Remove imported
              </Button>
              <Button
                onClick={() => selected && runImport(selected.key)}
                disabled={busyKey !== null || !selected}
                data-testid={selected ? `confirm-import-btn-${selected.key}` : "confirm-import-btn"}
                className="bg-[#38BDF8] hover:bg-[#0EA5E9] text-white rounded-xl"
              >
                {busyKey === `import:${selected?.key}` ? (
                  <Loader2 className="h-4 w-4 mr-1.5 animate-spin" />
                ) : (
                  <Download className="h-4 w-4 mr-1.5" />
                )}
                Import now
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
