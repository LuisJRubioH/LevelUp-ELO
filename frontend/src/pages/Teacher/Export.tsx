/**
 * pages/Teacher/Export.tsx — Exportar datos (rediseño)
 * ====================================================
 * Portado al diseño del console (selector de formato + descarga real).
 * Acciones reales: teacherApi.downloadCsv() / downloadXlsx().
 * (El preview/filtros/columnas/recents del prototipo eran mock; se omiten.)
 */

import { useState } from "react";
import { teacherApi } from "../../api/teacher";

type Fmt = "csv" | "xlsx";

const SHEETS = ["Intentos", "Matrículas", "Procedimientos", "KatIA"];

const FIELDS: { k: string; d: string }[] = [
  { k: "elo_before / elo_after", d: "ELO del estudiante antes y después de cada intento." },
  { k: "time_taken", d: "Segundos que tardó en responder." },
  { k: "rating_deviation", d: "Incertidumbre del ELO (RD) en ese momento." },
  { k: "prob_failure", d: "Probabilidad estimada de fallo de la pregunta." },
  { k: "confidence_score", d: "Confianza declarada por el estudiante." },
];

export function TeacherExport() {
  const [fmt, setFmt] = useState<Fmt>("csv");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [toast, setToast] = useState(false);

  const handleExport = async () => {
    setError("");
    setLoading(true);
    try {
      if (fmt === "csv") await teacherApi.downloadCsv();
      else await teacherApi.downloadXlsx();
      setToast(true);
      setTimeout(() => setToast(false), 3200);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "No se pudo descargar el archivo.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="tc-head">
        <div className="ttl">
          <h1>Exportar datos</h1>
          <p>Descarga la actividad de tus estudiantes para tu registro o análisis externo.</p>
        </div>
      </div>

      <div className="xp-card">
        <span className="xp-lbl">Formato</span>
        <div className="xp-formats">
          <button className={"xp-fmt" + (fmt === "csv" ? " on" : "")} onClick={() => setFmt("csv")}>
            <span className="xpf-ic">📄</span>
            <b>CSV</b>
            <span className="xpf-note">Tabla única de intentos. Ideal para hojas de cálculo.</span>
          </button>
          <button className={"xp-fmt" + (fmt === "xlsx" ? " on" : "")} onClick={() => setFmt("xlsx")}>
            <span className="xpf-ic">📊</span>
            <b>Excel (XLSX)</b>
            <span className="xpf-note">Libro completo con varias hojas de datos.</span>
          </button>
        </div>

        {fmt === "xlsx" && (
          <div className="xp-sheets">
            {SHEETS.map((s) => (
              <span key={s} className="xp-sheet">
                {s}
              </span>
            ))}
          </div>
        )}

        {error && <p className="xp-err">{error}</p>}

        <div className="xp-export-bar">
          <div className="xp-export-info">
            <b>{fmt === "csv" ? "levelup_intentos.csv" : "levelup_datos_completos.xlsx"}</b>
            <span>{fmt === "csv" ? "Un archivo CSV con todos los intentos." : "Un archivo Excel con 4 hojas de datos."}</span>
          </div>
          <button className="btn-pri xp-export-btn" onClick={handleExport} disabled={loading}>
            {loading ? "Generando…" : "⬇ Descargar"}
          </button>
        </div>
      </div>

      <div className="xp-card">
        <h4>Qué incluye el detalle</h4>
        <div className="xp-sub">Algunas columnas clave de cada intento exportado.</div>
        <ul className="xp-fields">
          {FIELDS.map((f) => (
            <li key={f.k}>
              <b>{f.k}</b> — {f.d}
            </li>
          ))}
        </ul>
      </div>

      {toast && (
        <div className="xp-toast">
          <span className="xpt-ic">✓</span>
          <div>
            <b>Descarga iniciada</b>
            <span>Revisa tu carpeta de descargas.</span>
          </div>
        </div>
      )}
    </>
  );
}
