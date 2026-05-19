/**
 * pages/Teacher/Export.tsx
 * =========================
 * Descarga de datos de estudiantes en CSV y Excel.
 */

import { useState } from "react";
import { useTranslation } from "react-i18next";
import { teacherApi } from "../../api/teacher";
import { Button } from "../../components/ui/Button";

interface ExportCardProps {
  icon: string;
  title: string;
  description: string;
  sheets?: string[];
  buttonLabel: string;
  onDownload: () => Promise<void>;
}

function ExportCard({ icon, title, description, sheets, buttonLabel, onDownload }: ExportCardProps) {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);

  const handleClick = async () => {
    setLoading(true);
    setError("");
    setDone(false);
    try {
      await onDownload();
      setDone(true);
      setTimeout(() => setDone(false), 3000);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : t("teacherExport.downloadError"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 space-y-4">
      <div className="flex items-start gap-4">
        <div className="text-3xl">{icon}</div>
        <div className="flex-1">
          <h3 className="font-semibold text-slate-100 text-base">{title}</h3>
          <p className="text-slate-400 text-sm mt-1">{description}</p>
          {sheets && (
            <div className="flex flex-wrap gap-1.5 mt-3">
              {sheets.map((s) => (
                <span
                  key={s}
                  className="text-xs bg-slate-700 text-slate-300 px-2 py-0.5 rounded"
                >
                  {s}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      {error && <p className="text-red-400 text-sm">{error}</p>}
      {done && <p className="text-green-400 text-sm">{t("teacherExport.downloadStarted")}</p>}

      <Button
        onClick={handleClick}
        loading={loading}
        variant={done ? "secondary" : "primary"}
        className="w-full"
      >
        {done ? t("teacherExport.downloaded") : buttonLabel}
      </Button>
    </div>
  );
}

export function TeacherExport() {
  const { t } = useTranslation();
  return (
    <div className="max-w-2xl mx-auto py-6 px-4 space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-100">{t("teacherExport.title")}</h2>
        <p className="text-slate-400 text-sm mt-1">{t("teacherExport.intro")}</p>
      </div>

      <div className="space-y-4">
        <ExportCard
          icon="📄"
          title={t("teacherExport.csvTitle")}
          description={t("teacherExport.csvDesc")}
          buttonLabel={t("teacherExport.csvButton")}
          onDownload={teacherApi.downloadCsv}
        />

        <ExportCard
          icon="📊"
          title={t("teacherExport.xlsxTitle")}
          description={t("teacherExport.xlsxDesc")}
          sheets={[
            t("teacherExport.sheetAttempts"),
            t("teacherExport.sheetEnrollments"),
            t("teacherExport.sheetProcedures"),
            t("teacherExport.sheetKatia"),
          ]}
          buttonLabel={t("teacherExport.xlsxButton")}
          onDownload={teacherApi.downloadXlsx}
        />
      </div>

      <div className="bg-slate-800 border border-slate-700 rounded-xl p-4">
        <h4 className="text-sm font-semibold text-slate-300 mb-2">{t("teacherExport.fieldsTitle")}</h4>
        <ul className="text-xs text-slate-400 space-y-1">
          <li>
            <span className="text-slate-300 font-medium">elo_before / elo_after:</span>{" "}
            {t("teacherExport.fieldEloBeforeAfter")}
          </li>
          <li>
            <span className="text-slate-300 font-medium">time_taken:</span>{" "}
            {t("teacherExport.fieldTimeTaken")}
          </li>
          <li>
            <span className="text-slate-300 font-medium">rating_deviation:</span>{" "}
            {t("teacherExport.fieldRD")}
          </li>
          <li>
            <span className="text-slate-300 font-medium">prob_failure:</span>{" "}
            {t("teacherExport.fieldProbFailure")}
          </li>
          <li>
            <span className="text-slate-300 font-medium">confidence_score:</span>{" "}
            {t("teacherExport.fieldConfidence")}
          </li>
        </ul>
      </div>
    </div>
  );
}
