/**
 * pages/Admin/Reports.tsx
 * ========================
 * Reportes de problemas técnicos enviados por estudiantes.
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { adminApi } from "../../api/teacher";
import type { ProblemReport } from "../../api/teacher";
import { Button } from "../../components/ui/Button";

function ReportCard({ report }: { report: ProblemReport }) {
  const { t } = useTranslation();
  const qc = useQueryClient();

  const resolveMutation = useMutation({
    mutationFn: () => adminApi.resolveReport(report.id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-reports"] }),
  });

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl p-4 space-y-3">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs text-slate-500">#{report.id}</span>
            <span className="text-xs text-slate-400">·</span>
            <span className="text-xs font-medium text-slate-300">
              {report.username ?? t("adminReports.unknownUser", { id: report.user_id })}
            </span>
            <span className="text-xs text-slate-500">·</span>
            <span className="text-xs text-slate-500">
              {report.created_at ? report.created_at.slice(0, 10) : "—"}
            </span>
          </div>
          <p className="text-sm text-slate-200">{report.description}</p>
        </div>
        <span
          className={`text-xs px-2 py-0.5 rounded-full shrink-0 ${
            report.status === "pending"
              ? "bg-amber-900/40 text-amber-400"
              : "bg-green-900/40 text-green-400"
          }`}
        >
          {report.status === "pending"
            ? t("adminReports.statusPending")
            : t("adminReports.statusResolved")}
        </span>
      </div>

      {report.status === "pending" && (
        <Button
          size="sm"
          variant="secondary"
          loading={resolveMutation.isPending}
          onClick={() => resolveMutation.mutate()}
          className="w-full"
        >
          {t("adminReports.resolve")}
        </Button>
      )}
    </div>
  );
}

export function AdminReports() {
  const { t } = useTranslation();
  const { data, isLoading } = useQuery({
    queryKey: ["admin-reports"],
    queryFn: adminApi.reports,
    refetchInterval: 60_000,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-400 animate-pulse">{t("adminReports.loading")}</p>
      </div>
    );
  }

  const reports = data?.reports ?? [];

  return (
    <div className="max-w-2xl mx-auto py-6 px-4 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-slate-100">{t("adminReports.title")}</h2>
        {reports.length > 0 && (
          <span className="text-xs bg-amber-700 text-slate-100 px-2.5 py-1 rounded-full font-medium">
            {t(reports.length === 1 ? "adminReports.pending" : "adminReports.pendingPlural", {
              count: reports.length,
            })}
          </span>
        )}
      </div>

      {reports.length === 0 ? (
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-12 text-center">
          <div className="text-3xl mb-3">✅</div>
          <p className="text-slate-300 font-medium">{t("adminReports.emptyTitle")}</p>
          <p className="text-slate-600 text-sm mt-1">{t("adminReports.emptyHint")}</p>
        </div>
      ) : (
        <div className="space-y-3">
          {reports.map((r) => (
            <ReportCard key={r.id} report={r} />
          ))}
        </div>
      )}
    </div>
  );
}
