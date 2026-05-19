/**
 * pages/Admin/Audit.tsx
 * ======================
 * Log de auditoría de reasignaciones de grupo.
 */

import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { adminApi } from "../../api/teacher";
import type { AuditEntry } from "../../api/teacher";

function formatTimestamp(ts: string, lang: string): string {
  if (!ts) return "—";
  const d = new Date(ts.replace(" ", "T"));
  if (isNaN(d.getTime())) return ts.slice(0, 16);
  return d.toLocaleString(lang === "en" ? "en-US" : "es-CO", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function AuditRow({ entry }: { entry: AuditEntry }) {
  const { t, i18n } = useTranslation();
  const noGroup = t("adminAudit.noGroup");
  const oldLabel = entry.old_group_name ?? (entry.old_group_id ? `ID ${entry.old_group_id}` : noGroup);
  const newLabel = entry.new_group_name ?? (entry.new_group_id ? `ID ${entry.new_group_id}` : noGroup);

  return (
    <tr className="hover:bg-slate-700/30 transition-colors">
      <td className="px-4 py-3 text-xs text-slate-500">#{entry.id}</td>
      <td className="px-4 py-3 text-sm text-slate-100">
        {entry.student_username ?? `ID ${entry.student_id}`}
      </td>
      <td className="px-4 py-3 text-sm text-slate-400">{oldLabel}</td>
      <td className="px-4 py-3 text-slate-500">→</td>
      <td className="px-4 py-3 text-sm text-violet-300">{newLabel}</td>
      <td className="px-4 py-3 text-sm text-amber-300">
        {entry.admin_username ?? `ID ${entry.admin_id}`}
      </td>
      <td className="px-4 py-3 text-xs text-slate-500">{formatTimestamp(entry.timestamp, i18n.language)}</td>
    </tr>
  );
}

export function AdminAudit() {
  const { t } = useTranslation();
  const { data, isLoading } = useQuery({
    queryKey: ["admin-audit"],
    queryFn: () => adminApi.audit(200),
    staleTime: 30_000,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-400 animate-pulse">{t("adminAudit.loading")}</p>
      </div>
    );
  }

  const entries = data?.entries ?? [];

  return (
    <div className="max-w-5xl mx-auto py-6 px-4 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-slate-100">{t("adminAudit.title")}</h2>
        <span className="text-xs text-slate-500">
          {t(entries.length === 1 ? "adminAudit.countSingular" : "adminAudit.countPlural", {
            count: entries.length,
          })}
        </span>
      </div>

      <p className="text-xs text-slate-500">{t("adminAudit.intro")}</p>

      <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-xs text-slate-500 border-b border-slate-700">
                <th className="px-4 py-2 text-left">{t("adminAudit.colId")}</th>
                <th className="px-4 py-2 text-left">{t("adminAudit.colStudent")}</th>
                <th className="px-4 py-2 text-left">{t("adminAudit.colOldGroup")}</th>
                <th className="px-4 py-2 text-left"></th>
                <th className="px-4 py-2 text-left">{t("adminAudit.colNewGroup")}</th>
                <th className="px-4 py-2 text-left">{t("adminAudit.colAdmin")}</th>
                <th className="px-4 py-2 text-left">{t("adminAudit.colDate")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {entries.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center text-slate-500 text-sm py-8">
                    {t("adminAudit.empty")}
                  </td>
                </tr>
              ) : (
                entries.map((e) => <AuditRow key={e.id} entry={e} />)
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
