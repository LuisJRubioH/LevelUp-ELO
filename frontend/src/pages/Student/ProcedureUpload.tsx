/**
 * pages/Student/ProcedureUpload.tsx
 * ===================================
 * Página para que el estudiante suba un procedimiento matemático manuscrito.
 * El docente lo revisa y califica; el score afecta el ELO del estudiante.
 */

import { useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { KatIAAvatar } from "../../components/KatIA/KatIAAvatar";
import { Button } from "../../components/ui/Button";
import { studentApi } from "../../api/student";
import { apiClient } from "../../api/client";

const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp", "application/pdf"];
const MAX_SIZE_MB = 10;

export function ProcedureUpload() {
  const fileRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [selectedItem, setSelectedItem] = useState<string>("");
  const [uploading, setUploading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Cursos matriculados para seleccionar a qué ítem corresponde el procedimiento
  const { data: courses } = useQuery({
    queryKey: ["student-courses"],
    queryFn: () => studentApi.courses(),
  });

  const enrolled = (courses ?? []).filter((c) => c.enrolled);

  const handleFile = (f: File) => {
    setError(null);
    setSuccess(false);
    if (!ALLOWED_TYPES.includes(f.type)) {
      setError(`Tipo no soportado: ${f.type}. Usa JPEG, PNG, WebP o PDF.`);
      return;
    }
    if (f.size > MAX_SIZE_MB * 1024 * 1024) {
      setError(`El archivo supera el límite de ${MAX_SIZE_MB} MB.`);
      return;
    }
    setFile(f);
    if (f.type.startsWith("image/")) {
      const url = URL.createObjectURL(f);
      setPreview(url);
    } else {
      setPreview(null);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  };

  const handleSubmit = async () => {
    if (!file || !selectedItem) return;
    setUploading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("item_id", selectedItem);
      formData.append("item_content", "");
      formData.append("file", file);

      await apiClient.postForm("/api/student/procedure", formData);
      setSuccess(true);
      setFile(null);
      setPreview(null);
      setSelectedItem("");
    } catch (e) {
      setError("Error al subir el procedimiento. Intenta de nuevo.");
      console.error(e);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto py-8 px-4 space-y-6">
      <h2 className="text-xl font-bold text-white">Enviar procedimiento</h2>
      <p className="text-sm text-slate-400">
        Sube la foto de tu procedimiento manuscrito. Tu docente lo revisará y asignará un puntaje.
      </p>

      {/* Éxito */}
      {success && (
        <div className="space-y-3">
          <KatIAAvatar
            state="correct"
            message="¡Recibido! Tu docente revisará tu procedimiento pronto. Sigue practicando 🐱"
            size="md"
          />
          <Button variant="secondary" onClick={() => setSuccess(false)} className="w-full">
            Enviar otro
          </Button>
        </div>
      )}

      {!success && (
        <>
          {/* Selector de curso (como referencia para el item_id) */}
          <div>
            <label className="block text-xs text-slate-400 mb-1.5">
              Identificador del ejercicio <span className="text-red-400">*</span>
            </label>
            <input
              type="text"
              value={selectedItem}
              onChange={(e) => setSelectedItem(e.target.value)}
              placeholder="ej: cd_14, alg_07 (ID del ítem)"
              className="w-full bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-violet-500"
            />
            {enrolled.length > 0 && (
              <p className="text-xs text-slate-600 mt-1">
                Cursos matriculados: {enrolled.map((c) => c.name).join(", ")}
              </p>
            )}
          </div>

          {/* Dropzone */}
          <div
            className={[
              "border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all",
              file
                ? "border-violet-500 bg-violet-900/10"
                : "border-slate-600 hover:border-slate-500 bg-slate-800/50",
            ].join(" ")}
            onClick={() => fileRef.current?.click()}
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
          >
            {preview ? (
              <img
                src={preview}
                alt="Previsualización"
                className="max-h-48 mx-auto rounded-lg object-contain"
              />
            ) : (
              <div className="space-y-2">
                <div className="text-4xl">📷</div>
                <p className="text-slate-400 text-sm">
                  Arrastra tu imagen aquí o{" "}
                  <span className="text-violet-400 underline">haz clic para seleccionar</span>
                </p>
                <p className="text-xs text-slate-600">JPEG, PNG, WebP o PDF · Máx. {MAX_SIZE_MB} MB</p>
              </div>
            )}
            <input
              ref={fileRef}
              type="file"
              accept={ALLOWED_TYPES.join(",")}
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) handleFile(f);
              }}
            />
          </div>

          {file && (
            <div className="flex items-center gap-3 bg-slate-800 rounded-xl px-4 py-2 border border-slate-700">
              <span className="text-slate-300 text-sm flex-1 truncate">{file.name}</span>
              <span className="text-xs text-slate-500">{(file.size / 1024).toFixed(0)} KB</span>
              <button
                onClick={() => { setFile(null); setPreview(null); }}
                className="text-slate-500 hover:text-red-400 text-xs"
              >
                ✕
              </button>
            </div>
          )}

          {error && (
            <div className="rounded-xl p-3 border border-red-600 bg-red-900/20">
              <p className="text-sm text-red-300">{error}</p>
            </div>
          )}

          <Button
            onClick={handleSubmit}
            disabled={!file || !selectedItem || uploading}
            size="lg"
            className="w-full"
          >
            {uploading ? "Subiendo…" : "📤 Enviar procedimiento"}
          </Button>

          <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700 space-y-1">
            <p className="text-xs text-slate-400 font-medium">¿Cómo funciona?</p>
            <ul className="text-xs text-slate-500 space-y-0.5 list-disc list-inside">
              <li>Sube la foto de tu hoja de procedimientos.</li>
              <li>Tu docente la revisa y asigna un puntaje (0–100).</li>
              <li>El puntaje afecta tu ELO: score 50 = neutro, score 100 = +10 ELO.</li>
              <li>Puedes reenviar si te equivocas — solo cuenta el último envío.</li>
            </ul>
          </div>
        </>
      )}
    </div>
  );
}
