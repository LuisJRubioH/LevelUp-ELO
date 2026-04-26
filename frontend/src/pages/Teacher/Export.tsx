/**
 * pages/Teacher/Export.tsx
 * =========================
 * Descarga de datos de estudiantes en CSV y Excel.
 */

import { useState } from "react";
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
      setError(err instanceof Error ? err.message : "Error al descargar.");
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
      {done && <p className="text-green-400 text-sm">✓ Descarga iniciada</p>}

      <Button
        onClick={handleClick}
        loading={loading}
        variant={done ? "secondary" : "primary"}
        className="w-full"
      >
        {done ? "✓ Descargado" : buttonLabel}
      </Button>
    </div>
  );
}

export function TeacherExport() {
  return (
    <div className="max-w-2xl mx-auto py-6 px-4 space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-100">Exportar Datos</h2>
        <p className="text-slate-400 text-sm mt-1">
          Descarga los datos de tus estudiantes para análisis estadístico externo.
          Los datos incluyen solo los estudiantes de tus grupos.
        </p>
      </div>

      <div className="space-y-4">
        <ExportCard
          icon="📄"
          title="CSV — Intentos de práctica"
          description="Tabla plana con todos los intentos de tus estudiantes: ELO antes/después, tópico, tiempo, acierto, desviación de rating."
          buttonLabel="⬇ Descargar CSV"
          onDownload={teacherApi.downloadCsv}
        />

        <ExportCard
          icon="📊"
          title="Excel — Dataset completo (4 hojas)"
          description="Archivo Excel con cuatro hojas de datos: intentos de práctica, matrículas por curso, procedimientos matemáticos y conversaciones con KatIA."
          sheets={["Intentos", "Matrículas", "Procedimientos", "KatIA"]}
          buttonLabel="⬇ Descargar Excel (.xlsx)"
          onDownload={teacherApi.downloadXlsx}
        />
      </div>

      <div className="bg-slate-800 border border-slate-700 rounded-xl p-4">
        <h4 className="text-sm font-semibold text-slate-300 mb-2">¿Qué incluye cada campo?</h4>
        <ul className="text-xs text-slate-400 space-y-1">
          <li>
            <span className="text-slate-300 font-medium">elo_before / elo_after:</span> ELO del
            estudiante antes y después de responder.
          </li>
          <li>
            <span className="text-slate-300 font-medium">time_taken:</span> Segundos que tardó en
            responder la pregunta.
          </li>
          <li>
            <span className="text-slate-300 font-medium">rating_deviation:</span> Incertidumbre del
            ELO (Glicko). Menor = más confiable.
          </li>
          <li>
            <span className="text-slate-300 font-medium">prob_failure:</span> Probabilidad estimada
            de fallo al momento de responder (1 − P_ZDP).
          </li>
          <li>
            <span className="text-slate-300 font-medium">confidence_score:</span> Confianza estimada
            por el análisis cognitivo de IA (0–1).
          </li>
        </ul>
      </div>
    </div>
  );
}
