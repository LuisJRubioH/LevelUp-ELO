/**
 * pages/Teacher/Exams.tsx — Exámenes (rediseño)
 * =============================================
 * Gestión de plantillas de examen + asignación a grupos. Reskin al diseño
 * del console (.lue-tc); la lógica real (templates, catálogo de ítems,
 * asignaciones con ventana de tiempo) se conserva intacta.
 */

import { useEffect, useMemo, useState } from "react";
import { MathText } from "../../components/Math/MathContent";
import {
  teacherApi,
  type ExamAssignment,
  type ExamResults,
  type ExamTemplate,
  type Group,
  type ItemCatalogEntry,
} from "../../api/teacher";

type Tab = "list" | "form";
interface Course {
  id: string;
  name: string;
  block: string;
}

const accColor = (a: number) => (a >= 80 ? "#34d399" : a >= 60 ? "#fbbf24" : "#f87171");

/* ── drawer de resultados del examen ─────────────────────────────────────── */
function ExamResultsDrawer({ template, onClose }: { template: ExamTemplate; onClose: () => void }) {
  const [data, setData] = useState<ExamResults | null>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  useEffect(() => {
    let alive = true;
    teacherApi
      .examResults(template.id)
      .then((d) => alive && setData(d))
      .catch(() => alive && setErr("No se pudieron cargar los resultados."))
      .finally(() => alive && setLoading(false));
    return () => {
      alive = false;
    };
  }, [template.id]);

  const stripMath = (s: string) => s.replace(/\$\$?/g, "").slice(0, 90);

  return (
    <div className="grp-backdrop" onClick={onClose}>
      <aside className="grp-drawer" onClick={(e) => e.stopPropagation()} role="dialog" aria-label="Resultados del examen">
        <div className="gd-head">
          <div className="gd-htop">
            <span className="gd-ic" style={{ background: "var(--accent)" }}>
              📊
            </span>
            <button className="gd-x" onClick={onClose} aria-label="Cerrar">
              ✕
            </button>
          </div>
          <h2>{template.title}</h2>
          <p className="gd-sub">Análisis de resultados</p>
        </div>

        {loading ? (
          <div className="gd-section">
            <p style={{ color: "var(--mute)", fontSize: 13 }}>Cargando…</p>
          </div>
        ) : err ? (
          <div className="gd-section">
            <p style={{ color: "#f87171", fontSize: 13 }}>{err}</p>
          </div>
        ) : !data || data.n_sessions === 0 ? (
          <div className="gd-section">
            <p style={{ color: "var(--mute)", fontSize: 13.5, lineHeight: 1.5 }}>
              Aún nadie ha presentado este examen. Cuando tus estudiantes lo respondan, aquí verás la pregunta
              más acertada, la más fallada y el tema a reforzar.
            </p>
          </div>
        ) : (
          <>
            <div className="gd-stats">
              <div className="gds">
                <span className="l">Presentaciones</span>
                <b>{data.n_sessions}</b>
              </div>
              <div className="gds">
                <span className="l">Estudiantes</span>
                <b>{data.n_students}</b>
              </div>
              <div className="gds">
                <span className="l">Nota promedio</span>
                <b style={{ color: accColor(data.avg_score) }}>{data.avg_score}%</b>
              </div>
            </div>

            <div className="gd-section">
              <h4>Resumen</h4>
              <div className="ex-res-hl">
                <div className="ex-hl good">
                  <span className="hl-l">Más acertada</span>
                  <span className="hl-v">{data.best_question ? `${data.best_question.accuracy}%` : "—"}</span>
                  {data.best_question && <span className="hl-s">{stripMath(data.best_question.content)}</span>}
                </div>
                <div className="ex-hl bad">
                  <span className="hl-l">Más fallada</span>
                  <span className="hl-v">{data.worst_question ? `${data.worst_question.accuracy}%` : "—"}</span>
                  {data.worst_question && <span className="hl-s">{stripMath(data.worst_question.content)}</span>}
                </div>
                <div className="ex-hl warn">
                  <span className="hl-l">Tema a reforzar</span>
                  <span className="hl-v" style={{ fontSize: 15 }}>
                    {data.reinforce_topic ? data.reinforce_topic.topic : "—"}
                  </span>
                  {data.reinforce_topic && <span className="hl-s">{data.reinforce_topic.accuracy}% de acierto</span>}
                </div>
              </div>
            </div>

            <div className="gd-section">
              <h4>Por pregunta</h4>
              {data.questions.map((q) => (
                <div className="ex-qstat" key={q.item_id}>
                  <div className="q-main">
                    <div className="q-txt">{stripMath(q.content)}</div>
                    <div className="q-meta">
                      {q.topic ?? "—"} · {q.correct}/{q.total} correctas
                    </div>
                  </div>
                  <div className="q-acc">
                    <b style={{ color: accColor(q.accuracy) }}>{q.accuracy}%</b>
                    <div className="q-bar">
                      <i style={{ width: q.accuracy + "%", background: accColor(q.accuracy) }} />
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {data.topics.length > 0 && (
              <div className="gd-section">
                <h4>Por tópico</h4>
                {data.topics.map((tp) => (
                  <div className="mastery-row" key={tp.topic}>
                    <div className="ml">{tp.topic}</div>
                    <div className="mbar">
                      <i style={{ width: tp.accuracy + "%", background: accColor(tp.accuracy) }} />
                    </div>
                    <div className="mv">{tp.accuracy}%</div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </aside>
    </div>
  );
}

export function TeacherExams() {
  const [tab, setTab] = useState<Tab>("list");
  const [courses, setCourses] = useState<Course[]>([]);
  const [filterCourse, setFilterCourse] = useState<string>("");
  const [templates, setTemplates] = useState<ExamTemplate[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [editing, setEditing] = useState<ExamTemplate | null>(null);
  const [formCourseId, setFormCourseId] = useState("");
  const [formTitle, setFormTitle] = useState("");
  const [formTime, setFormTime] = useState(20);
  const [formItemIds, setFormItemIds] = useState<string[]>([]);
  const [catalog, setCatalog] = useState<ItemCatalogEntry[]>([]);
  const [catalogLoading, setCatalogLoading] = useState(false);
  const [filterTopic, setFilterTopic] = useState("");
  const [saving, setSaving] = useState(false);

  const [assigningTo, setAssigningTo] = useState<ExamTemplate | null>(null);
  const [groups, setGroups] = useState<Group[]>([]);
  const [assignments, setAssignments] = useState<ExamAssignment[]>([]);
  const [assignGroupIds, setAssignGroupIds] = useState<number[]>([]);
  const [assignStartsAt, setAssignStartsAt] = useState("");
  const [assignEndsAt, setAssignEndsAt] = useState("");
  const [assignSaving, setAssignSaving] = useState(false);
  const [assignError, setAssignError] = useState("");
  const [resultsFor, setResultsFor] = useState<ExamTemplate | null>(null);

  useEffect(() => {
    teacherApi
      .allCourses()
      .then((cs) => {
        setCourses(cs);
        if (cs.length && !filterCourse) setFilterCourse(cs[0].id);
      })
      .catch(() => setError("No se pudieron cargar los cursos."));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!filterCourse) return;
    setLoading(true);
    setError("");
    teacherApi
      .examTemplates(filterCourse)
      .then(setTemplates)
      .catch(() => setError("No se pudieron cargar los exámenes."))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filterCourse]);

  useEffect(() => {
    if (!formCourseId) {
      setCatalog([]);
      return;
    }
    setCatalogLoading(true);
    teacherApi
      .itemsCatalog(formCourseId)
      .then(setCatalog)
      .catch(() => setError("No se pudo cargar el catálogo de preguntas."))
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
    [catalog, filterTopic]
  );

  const toggleItem = (id: string) =>
    setFormItemIds((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));

  const startCreate = () => {
    setEditing(null);
    setFormCourseId(filterCourse || courses[0]?.id || "");
    setFormTitle("");
    setFormTime(20);
    setFormItemIds([]);
    setFilterTopic("");
    setTab("form");
  };

  const startEdit = (tpl: ExamTemplate) => {
    setEditing(tpl);
    setFormCourseId(tpl.course_id);
    setFormTitle(tpl.title);
    setFormTime(tpl.time_limit_min);
    setFormItemIds(tpl.item_ids);
    setFilterTopic("");
    setTab("form");
  };

  const archive = async (tpl: ExamTemplate) => {
    if (!confirm(`¿Archivar "${tpl.title}"?`)) return;
    try {
      await teacherApi.archiveExamTemplate(tpl.id);
      setTemplates((prev) => prev.filter((x) => x.id !== tpl.id));
    } catch {
      setError("No se pudo archivar el examen.");
    }
  };

  const openAssign = async (tpl: ExamTemplate) => {
    setAssigningTo(tpl);
    setAssignError("");
    setAssignGroupIds([]);
    setAssignStartsAt("");
    setAssignEndsAt("");
    try {
      const [grps, assigns] = await Promise.all([teacherApi.groups(), teacherApi.listAssignments(tpl.id)]);
      setGroups(grps);
      setAssignments(assigns);
    } catch {
      setAssignError("No se pudieron cargar las asignaciones.");
    }
  };

  const closeAssign = () => {
    setAssigningTo(null);
    setAssignments([]);
    setAssignGroupIds([]);
    setAssignStartsAt("");
    setAssignEndsAt("");
    setAssignError("");
  };

  const submitAssignments = async () => {
    if (!assigningTo || assignGroupIds.length === 0) {
      setAssignError("Selecciona al menos un grupo.");
      return;
    }
    setAssignSaving(true);
    setAssignError("");
    try {
      const updated = await teacherApi.createAssignments(assigningTo.id, {
        group_ids: assignGroupIds,
        starts_at: assignStartsAt ? new Date(assignStartsAt).toISOString() : null,
        ends_at: assignEndsAt ? new Date(assignEndsAt).toISOString() : null,
      });
      setAssignments(updated);
      setAssignGroupIds([]);
      setAssignStartsAt("");
      setAssignEndsAt("");
    } catch (e) {
      setAssignError(e instanceof Error ? e.message : "No se pudo guardar la asignación.");
    } finally {
      setAssignSaving(false);
    }
  };

  const removeAssignment = async (assignmentId: number) => {
    if (!assigningTo) return;
    if (!confirm("¿Quitar esta asignación?")) return;
    try {
      await teacherApi.deleteAssignment(assigningTo.id, assignmentId);
      setAssignments((prev) => prev.filter((a) => a.id !== assignmentId));
    } catch {
      setAssignError("No se pudo quitar la asignación.");
    }
  };

  const fmtDT = (iso: string | null) =>
    !iso
      ? "—"
      : new Date(iso).toLocaleString(undefined, {
          year: "numeric",
          month: "short",
          day: "2-digit",
          hour: "2-digit",
          minute: "2-digit",
        });

  const submitForm = async () => {
    if (!formTitle.trim() || !formCourseId || formItemIds.length === 0) {
      setError("Completa título, curso y al menos una pregunta.");
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
      const updated = await teacherApi.examTemplates(filterCourse);
      setTemplates(updated);
      setTab("list");
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudo guardar el examen.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <div className="tc-head">
        <div className="ttl">
          <h1>Exámenes</h1>
          <p>Arma plantillas de examen con preguntas calibradas y asígnalas a tus grupos con ventana de tiempo.</p>
        </div>
      </div>

      <div className="view-tabs">
        <button className={tab === "list" ? "on" : ""} onClick={() => setTab("list")}>
          📋 Mis exámenes
        </button>
        <button className={tab === "form" ? "on" : ""} onClick={startCreate}>
          ＋ {editing ? "Editar examen" : "Crear examen"}
        </button>
      </div>

      {error && <div className="auth-msg error" style={{ marginBottom: 16 }}>{error}</div>}

      {/* ── LISTA ─────────────────────────────────────────────────────────── */}
      {tab === "list" && (
        <>
          <div className="ex-toolbar">
            <label className="gm-field">
              <span>Curso</span>
              <select value={filterCourse} onChange={(e) => setFilterCourse(e.target.value)}>
                {courses.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </label>
            <button className="btn-pri" onClick={startCreate}>
              ＋ Crear examen
            </button>
          </div>

          {loading ? (
            <div className="tc-soon">
              <div className="box">
                <div className="em-ic">⏳</div>
                <h2>Cargando…</h2>
              </div>
            </div>
          ) : templates.length === 0 ? (
            <div className="panel">
              <div className="empty">
                <div className="em-ic">📋</div>
                <p>No hay exámenes en este curso. Crea el primero.</p>
              </div>
            </div>
          ) : (
            <div className="ex-grid">
              {templates.map((tpl) => (
                <div className="ex-card" key={tpl.id}>
                  <h3>{tpl.title}</h3>
                  <div className="ex-meta">
                    <span>
                      {tpl.item_ids.length} {tpl.item_ids.length === 1 ? "pregunta" : "preguntas"}
                    </span>
                    <i />
                    <span>{tpl.time_limit_min} min</span>
                    <i />
                    <span>{String(tpl.created_at).slice(0, 10)}</span>
                  </div>
                  <div className="ex-actions">
                    <button className="ex-act results" onClick={() => setResultsFor(tpl)}>
                      Resultados
                    </button>
                    <button className="ex-act assign" onClick={() => openAssign(tpl)}>
                      Asignar
                    </button>
                    <button className="ex-act edit" onClick={() => startEdit(tpl)}>
                      Editar
                    </button>
                    <button className="ex-act archive" onClick={() => archive(tpl)}>
                      Archivar
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* ── FORMULARIO ────────────────────────────────────────────────────── */}
      {tab === "form" && (
        <div className="ex-form">
          <div className="ex-config">
            <label className="gm-field">
              <span>Curso</span>
              <select value={formCourseId} onChange={(e) => setFormCourseId(e.target.value)} disabled={!!editing}>
                {courses.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
              {editing && <span className="ex-hint">El curso no se puede cambiar al editar.</span>}
            </label>

            <label className="gm-field">
              <span>Título del examen</span>
              <input value={formTitle} onChange={(e) => setFormTitle(e.target.value)} placeholder="Ej. Parcial de Álgebra" />
            </label>

            <label className="gm-field">
              <span>
                Tiempo límite: <b style={{ color: "var(--accent-soft)" }}>{formTime} min</b>
              </span>
              <input
                type="range"
                min={5}
                max={120}
                step={5}
                value={formTime}
                onChange={(e) => setFormTime(Number(e.target.value))}
                style={{ width: "100%", accentColor: "var(--accent)" }}
              />
            </label>

            <div className="ex-selected">
              Preguntas seleccionadas: <b>{formItemIds.length}</b>
              {formItemIds.length === 0 && <span className="warn">Selecciona al menos una pregunta del catálogo.</span>}
            </div>

            <div className="gm-foot">
              <button className="btn-soft" onClick={() => setTab("list")}>
                Cancelar
              </button>
              <button className="btn-pri" onClick={submitForm} disabled={saving}>
                {saving ? "Guardando…" : editing ? "Guardar cambios" : "Crear examen"}
              </button>
            </div>
          </div>

          <div className="ex-catalog">
            <div className="ex-cat-head">
              <h3>Catálogo de preguntas</h3>
              {topics.length > 0 && (
                <select className="sort-sel" value={filterTopic} onChange={(e) => setFilterTopic(e.target.value)}>
                  <option value="">Todos los tópicos</option>
                  {topics.map((tp) => (
                    <option key={tp} value={tp}>
                      {tp}
                    </option>
                  ))}
                </select>
              )}
            </div>
            {catalogLoading ? (
              <p style={{ color: "var(--mute)", fontSize: 13 }}>Cargando…</p>
            ) : filteredCatalog.length === 0 ? (
              <p style={{ color: "var(--mute)", fontSize: 13 }}>Sin preguntas para este curso.</p>
            ) : (
              <div className="ex-cat-list">
                {filteredCatalog.map((it) => {
                  const checked = formItemIds.includes(it.id);
                  const order = checked ? formItemIds.indexOf(it.id) + 1 : null;
                  return (
                    <div
                      key={it.id}
                      className={"ex-item" + (checked ? " on" : "")}
                      onClick={() => toggleItem(it.id)}
                    >
                      <div className="ex-item-top">
                        <span className="ex-item-meta">
                          {it.topic} · dif {Math.round(it.difficulty)}
                        </span>
                        {order && <span className="ex-item-order">#{order}</span>}
                      </div>
                      <p>
                        <MathText text={it.content} />
                      </p>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── MODAL DE ASIGNACIÓN ───────────────────────────────────────────── */}
      {assigningTo && (
        <div className="grp-backdrop center" onClick={closeAssign}>
          <div
            className="grp-modal"
            style={{ width: "min(560px, 100%)" }}
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-label="Asignar examen"
          >
            <div className="gm-head">
              <h3>Asignar examen</h3>
              <button className="gd-x" onClick={closeAssign} aria-label="Cerrar">
                ✕
              </button>
            </div>
            <p className="gm-sub">{assigningTo.title}</p>

            {assignError && <p className="gm-err">{assignError}</p>}

            <div style={{ marginBottom: 18 }}>
              <span className="xp-lbl">Asignaciones actuales</span>
              {assignments.length === 0 ? (
                <p style={{ color: "var(--mute)", fontSize: 12.5 }}>Aún no está asignado a ningún grupo.</p>
              ) : (
                <div className="ex-assign-list">
                  {assignments.map((a) => (
                    <div className="ex-assign-row" key={a.id}>
                      <div>
                        <div className="ar-b">👥 {a.group_name}</div>
                        <div className="ar-when">
                          {fmtDT(a.starts_at)} · hasta {fmtDT(a.ends_at)}
                        </div>
                      </div>
                      <button className="ar-x" onClick={() => removeAssignment(a.id)} aria-label="Quitar">
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <span className="xp-lbl">Nueva asignación</span>
            <label className="gm-field">
              <span>Grupos</span>
              {groups.length === 0 ? (
                <p style={{ color: "var(--mute)", fontSize: 12.5 }}>No tienes grupos disponibles.</p>
              ) : (
                <div className="ex-grp-list">
                  {groups.map((g) => (
                    <label key={g.group_id} className="ex-grp-opt">
                      <input
                        type="checkbox"
                        checked={assignGroupIds.includes(g.group_id)}
                        onChange={() =>
                          setAssignGroupIds((prev) =>
                            prev.includes(g.group_id)
                              ? prev.filter((id) => id !== g.group_id)
                              : [...prev, g.group_id]
                          )
                        }
                      />
                      <span>{g.name}</span>
                      <span className="cnt">{g.student_count} est.</span>
                    </label>
                  ))}
                </div>
              )}
            </label>

            <div className="ex-dt-grid">
              <label className="gm-field">
                <span>Inicio</span>
                <input type="datetime-local" value={assignStartsAt} onChange={(e) => setAssignStartsAt(e.target.value)} />
                <span className="ex-hint">Vacío = disponible ya.</span>
              </label>
              <label className="gm-field">
                <span>Fin</span>
                <input type="datetime-local" value={assignEndsAt} onChange={(e) => setAssignEndsAt(e.target.value)} />
                <span className="ex-hint">Vacío = sin cierre.</span>
              </label>
            </div>

            <div className="gm-foot">
              <button className="btn-soft" onClick={closeAssign}>
                Cerrar
              </button>
              <button className="btn-pri" onClick={submitAssignments} disabled={assignSaving || assignGroupIds.length === 0}>
                {assignSaving ? "Guardando…" : "Guardar asignación"}
              </button>
            </div>
          </div>
        </div>
      )}

      {resultsFor && (
        <ExamResultsDrawer template={resultsFor} onClose={() => setResultsFor(null)} />
      )}
    </>
  );
}
