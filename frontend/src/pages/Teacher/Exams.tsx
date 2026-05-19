/**
 * pages/Teacher/Exams.tsx
 * ========================
 * Gestión de plantillas de examen manuales — Sprint C.
 * Tabs:
 *   - Mis exámenes: lista de templates activos + acciones editar/archivar
 *   - Crear/Editar: selector de items por curso con preview
 * El docente arma una lista de preguntas; el orden se preserva tal cual.
 */

import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import katex from "katex";
import "katex/dist/katex.min.css";
import { teacherApi, type ExamTemplate, type ItemCatalogEntry } from "../../api/teacher";

type Tab = "list" | "form";

interface Course {
  id: string;
  name: string;
  block: string;
}

function RenderMath({ text }: { text: string }) {
  const parts = text.split(/(\$\$[^$]+\$\$|\$[^$\n]+\$)/g);
  if (parts.length === 1) return <>{text}</>;
  return (
    <>
      {parts.map((p, i) => {
        let math: string | null = null;
        let display = false;
        if (p.startsWith("$$") && p.endsWith("$$") && p.length >= 4) {
          math = p.slice(2, -2);
          display = true;
        } else if (p.startsWith("$") && p.endsWith("$") && p.length >= 2) {
          math = p.slice(1, -1);
        }
        if (math !== null) {
          try {
            const html = katex.renderToString(math, {
              displayMode: display,
              throwOnError: false,
              errorColor: "#ef4444",
            });
            return (
              <span
                key={i}
                className={display ? "block my-1" : "inline-block align-middle"}
                dangerouslySetInnerHTML={{ __html: html }}
              />
            );
          } catch {
            return <span key={i}>{p}</span>;
          }
        }
        return <span key={i}>{p}</span>;
      })}
    </>
  );
}

export function TeacherExams() {
  const { t } = useTranslation();
  const [tab, setTab] = useState<Tab>("list");
  const [courses, setCourses] = useState<Course[]>([]);
  const [filterCourse, setFilterCourse] = useState<string>("");
  const [templates, setTemplates] = useState<ExamTemplate[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Estado del formulario (crear/editar)
  const [editing, setEditing] = useState<ExamTemplate | null>(null);
  const [formCourseId, setFormCourseId] = useState("");
  const [formTitle, setFormTitle] = useState("");
  const [formTime, setFormTime] = useState(20);
  const [formItemIds, setFormItemIds] = useState<string[]>([]);
  const [catalog, setCatalog] = useState<ItemCatalogEntry[]>([]);
  const [catalogLoading, setCatalogLoading] = useState(false);
  const [filterTopic, setFilterTopic] = useState("");
  const [saving, setSaving] = useState(false);

  // ── Cargar cursos al montar ───────────────────────────────────────────────
  useEffect(() => {
    teacherApi
      .allCourses()
      .then((cs) => {
        setCourses(cs);
        if (cs.length && !filterCourse) setFilterCourse(cs[0].id);
      })
      .catch(() => setError(t("teacherExams.errorLoadCourses")));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ── Cargar templates cuando cambia el filtro de curso ─────────────────────
  useEffect(() => {
    if (!filterCourse) return;
    setLoading(true);
    setError("");
    teacherApi
      .examTemplates(filterCourse)
      .then(setTemplates)
      .catch(() => setError(t("teacherExams.errorLoadTemplates")))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filterCourse]);

  // ── Cargar catálogo de items cuando se cambia el curso del formulario ─────
  useEffect(() => {
    if (!formCourseId) {
      setCatalog([]);
      return;
    }
    setCatalogLoading(true);
    teacherApi
      .itemsCatalog(formCourseId)
      .then(setCatalog)
      .catch(() => setError(t("teacherExams.errorLoadCatalog")))
      .finally(() => setCatalogLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [formCourseId]);

  const topics = useMemo(() => {
    const s = new Set<string>();
    catalog.forEach((it) => s.add(it.topic));
    return Array.from(s).sort();
  }, [catalog]);

  const filteredCatalog = useMemo(
    () => (filterTopic ? catalog.filter((it) => it.topic === filterTopic) : catalog),
    [catalog, filterTopic],
  );

  const toggleItem = (id: string) => {
    setFormItemIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    );
  };

  const startCreate = () => {
    setEditing(null);
    setFormCourseId(filterCourse || (courses[0]?.id ?? ""));
    setFormTitle("");
    setFormTime(20);
    setFormItemIds([]);
    setFilterTopic("");
    setTab("form");
  };

  const startEdit = (t: ExamTemplate) => {
    setEditing(t);
    setFormCourseId(t.course_id);
    setFormTitle(t.title);
    setFormTime(t.time_limit_min);
    setFormItemIds(t.item_ids);
    setFilterTopic("");
    setTab("form");
  };

  const archive = async (tpl: ExamTemplate) => {
    if (!confirm(t("teacherExams.confirmArchive", { title: tpl.title }))) return;
    try {
      await teacherApi.archiveExamTemplate(tpl.id);
      setTemplates((prev) => prev.filter((x) => x.id !== tpl.id));
    } catch {
      setError(t("teacherExams.errorArchive"));
    }
  };

  const submitForm = async () => {
    if (!formTitle.trim() || !formCourseId || formItemIds.length === 0) {
      setError(t("teacherExams.errorRequired"));
      return;
    }
    setSaving(true);
    setError("");
    try {
      if (editing) {
        await teacherApi.updateExamTemplate(editing.id, {
          title: formTitle,
          time_limit_min: formTime,
          item_ids: formItemIds,
        });
      } else {
        await teacherApi.createExamTemplate({
          course_id: formCourseId,
          title: formTitle,
          time_limit_min: formTime,
          item_ids: formItemIds,
        });
      }
      // recargar lista
      const updated = await teacherApi.examTemplates(filterCourse);
      setTemplates(updated);
      setTab("list");
    } catch (e) {
      setError(e instanceof Error ? e.message : t("teacherExams.errorSave"));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold text-slate-100 mb-1">{t("teacherExams.title")}</h1>
      <p className="text-sm text-slate-400 mb-5">{t("teacherExams.intro")}</p>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-slate-700 mb-5">
        <button
          onClick={() => setTab("list")}
          className={[
            "px-4 py-2 text-sm font-medium transition-colors border-b-2",
            tab === "list"
              ? "border-violet-500 text-violet-300"
              : "border-transparent text-slate-400 hover:text-slate-200",
          ].join(" ")}
        >
          {t("teacherExams.tabList")}
        </button>
        <button
          onClick={startCreate}
          className={[
            "px-4 py-2 text-sm font-medium transition-colors border-b-2",
            tab === "form"
              ? "border-violet-500 text-violet-300"
              : "border-transparent text-slate-400 hover:text-slate-200",
          ].join(" ")}
        >
          {editing ? t("teacherExams.tabEdit") : t("teacherExams.tabCreate")}
        </button>
      </div>

      {error && (
        <div className="mb-4 text-sm text-red-400 bg-red-900/20 border border-red-800/40 rounded px-3 py-2">
          {error}
        </div>
      )}

      {/* ── LISTA ─────────────────────────────────────────────────────────── */}
      {tab === "list" && (
        <div>
          <div className="flex items-end gap-3 mb-4">
            <div className="flex-1 max-w-xs">
              <label className="block text-xs text-slate-400 mb-1">{t("teacherExams.course")}</label>
              <select
                value={filterCourse}
                onChange={(e) => setFilterCourse(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200"
              >
                {courses.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>
            <button
              onClick={startCreate}
              className="bg-violet-600 hover:bg-violet-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
            >
              {t("teacherExams.createButton")}
            </button>
          </div>

          {loading ? (
            <p className="text-sm text-slate-500">{t("teacherExams.loading")}</p>
          ) : templates.length === 0 ? (
            <div className="text-center py-12 border border-dashed border-slate-700 rounded-xl">
              <p className="text-sm text-slate-400 mb-2">{t("teacherExams.empty")}</p>
              <button
                onClick={startCreate}
                className="text-violet-400 hover:text-violet-300 text-sm font-medium"
              >
                {t("teacherExams.createFirst")}
              </button>
            </div>
          ) : (
            <div className="space-y-2">
              {templates.map((tpl) => (
                <div
                  key={tpl.id}
                  className="bg-slate-800 border border-slate-700 rounded-xl p-4 flex items-start gap-4"
                >
                  <div className="flex-1 min-w-0">
                    <h3 className="text-base font-medium text-slate-100 mb-1">{tpl.title}</h3>
                    <p className="text-xs text-slate-500">
                      {t(
                        tpl.item_ids.length === 1
                          ? "teacherExams.questionCount"
                          : "teacherExams.questionCountPlural",
                        {
                          count: tpl.item_ids.length,
                          time: tpl.time_limit_min,
                          date: tpl.created_at,
                        },
                      )}
                    </p>
                  </div>
                  <button
                    onClick={() => startEdit(tpl)}
                    className="text-xs text-violet-400 hover:text-violet-300 px-2 py-1"
                  >
                    {t("teacherExams.edit")}
                  </button>
                  <button
                    onClick={() => archive(tpl)}
                    className="text-xs text-red-400 hover:text-red-300 px-2 py-1"
                  >
                    {t("teacherExams.archive")}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── FORMULARIO ────────────────────────────────────────────────────── */}
      {tab === "form" && (
        <div className="grid md:grid-cols-2 gap-5">
          <div className="space-y-4">
            <div>
              <label className="block text-xs text-slate-400 mb-1">{t("teacherExams.course")}</label>
              <select
                value={formCourseId}
                onChange={(e) => setFormCourseId(e.target.value)}
                disabled={!!editing}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 disabled:opacity-60"
              >
                {courses.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
              {editing && (
                <p className="text-[10px] text-slate-500 mt-1">
                  {t("teacherExams.courseCannotChange")}
                </p>
              )}
            </div>

            <div>
              <label className="block text-xs text-slate-400 mb-1">{t("teacherExams.examTitle")}</label>
              <input
                type="text"
                value={formTitle}
                onChange={(e) => setFormTitle(e.target.value)}
                placeholder={t("teacherExams.examTitlePlaceholder")}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200"
              />
            </div>

            <div>
              <label className="block text-xs text-slate-400 mb-1">
                {t("teacherExams.timeLimit")}:{" "}
                <span className="text-violet-400 font-semibold">{formTime} min</span>
              </label>
              <input
                type="range"
                min={5}
                max={120}
                step={5}
                value={formTime}
                onChange={(e) => setFormTime(Number(e.target.value))}
                className="w-full accent-violet-500"
              />
            </div>

            <div className="bg-slate-800/60 border border-slate-700 rounded-xl px-4 py-3 text-sm">
              <p className="text-slate-300 mb-1">
                {t("teacherExams.selectedQuestions")}{" "}
                <span className="font-semibold text-violet-300">{formItemIds.length}</span>
              </p>
              {formItemIds.length === 0 && (
                <p className="text-xs text-amber-400">{t("teacherExams.needAtLeastOne")}</p>
              )}
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => setTab("list")}
                className="flex-1 bg-slate-700 hover:bg-slate-600 text-slate-200 text-sm py-2 rounded-lg transition-colors"
              >
                {t("teacherExams.cancel")}
              </button>
              <button
                onClick={submitForm}
                disabled={saving}
                className="flex-1 bg-violet-600 hover:bg-violet-700 disabled:opacity-50 text-white text-sm font-medium py-2 rounded-lg transition-colors"
              >
                {saving
                  ? t("teacherExams.saving")
                  : editing
                    ? t("teacherExams.saveChanges")
                    : t("teacherExams.tabCreate")}
              </button>
            </div>
          </div>

          {/* Catálogo */}
          <div className="bg-slate-800/40 border border-slate-700 rounded-xl p-3 max-h-[600px] overflow-y-auto">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-slate-200">{t("teacherExams.catalogTitle")}</h3>
              {topics.length > 0 && (
                <select
                  value={filterTopic}
                  onChange={(e) => setFilterTopic(e.target.value)}
                  className="text-xs bg-slate-800 border border-slate-700 rounded px-2 py-1 text-slate-300"
                >
                  <option value="">{t("teacherExams.allTopics")}</option>
                  {topics.map((tp) => (
                    <option key={tp} value={tp}>
                      {tp}
                    </option>
                  ))}
                </select>
              )}
            </div>

            {catalogLoading ? (
              <p className="text-xs text-slate-500 p-2">{t("teacherExams.loading")}</p>
            ) : filteredCatalog.length === 0 ? (
              <p className="text-xs text-slate-500 p-2">{t("teacherExams.catalogEmpty")}</p>
            ) : (
              <ul className="space-y-1.5">
                {filteredCatalog.map((it) => {
                  const checked = formItemIds.includes(it.id);
                  const order = checked ? formItemIds.indexOf(it.id) + 1 : null;
                  return (
                    <li
                      key={it.id}
                      onClick={() => toggleItem(it.id)}
                      className={[
                        "px-3 py-2 rounded-lg cursor-pointer transition-colors border",
                        checked
                          ? "bg-violet-900/30 border-violet-500/60"
                          : "bg-slate-900/40 border-slate-700 hover:bg-slate-800",
                      ].join(" ")}
                    >
                      <div className="flex items-center justify-between gap-2 mb-1">
                        <span className="text-[10px] uppercase tracking-wide text-slate-500">
                          {it.topic} · {t("teacherExams.difficultyShort")} {Math.round(it.difficulty)}
                        </span>
                        {order && (
                          <span className="text-xs font-mono text-violet-400">#{order}</span>
                        )}
                      </div>
                      <p className="text-xs text-slate-300 line-clamp-3 leading-snug">
                        <RenderMath text={it.content} />
                      </p>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
