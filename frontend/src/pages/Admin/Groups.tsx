/**
 * pages/Admin/Groups.tsx
 * =======================
 * Vista de administrador: todos los grupos del sistema con opción de eliminar.
 *
 * Spec 009 GI (FR-019 … FR-024): cada grupo muestra su institución y su grado; el admin ve cuántos
 * grupos siguen sin institución, puede mostrar solo esos y edita la institución y el grado de cada
 * uno. Las instituciones ya registradas se ofrecen al escribir (una por clave, del servidor), otro
 * grupo con la misma institución y grado se nombra antes de guardar, y ningún estudiante cambia.
 */

import { useId, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { useTranslation } from "react-i18next";
import { ApiError } from "../../api/client";
import { adminApi } from "../../api/teacher";
import type {
  AdminGroup,
  GroupInstitutionResult,
  SameInstitutionConflict,
} from "../../api/teacher";
import { Button } from "../../components/ui/Button";

const GRADES = [6, 7, 8, 9, 10, 11];

const gradeLabel = (grade: number | null | undefined) => (grade == null ? "—" : `${grade}.º`);

const hasInstitution = (group: AdminGroup) => !!(group.institution ?? "").trim();

function isSameInstitution(err: unknown): SameInstitutionConflict | null {
  if (!(err instanceof ApiError) || err.status !== 409) return null;
  const detail = err.detail as unknown as SameInstitutionConflict | string;
  return typeof detail === "object" && detail?.code === "same_institution_and_grade"
    ? detail
    : null;
}

/** GI: the inline form — the institution with the recorded ones offered, and the grade. */
function InstitutionForm({
  group,
  onSaved,
  onCancel,
}: {
  group: AdminGroup;
  onSaved: (result: GroupInstitutionResult) => void;
  onCancel: () => void;
}) {
  const { t } = useTranslation();
  const ids = useId();
  const [institution, setInstitution] = useState(group.institution?.trim() ?? "");
  const [grade, setGrade] = useState<string>(group.grade == null ? "" : String(group.grade));
  const [conflict, setConflict] = useState<SameInstitutionConflict | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { data: recorded } = useQuery({
    queryKey: ["admin-institutions"],
    queryFn: adminApi.institutions,
    staleTime: 30_000,
  });

  const save = useMutation({
    mutationFn: (confirm_same: boolean) =>
      adminApi.setGroupInstitution(group.id, {
        institution,
        grade: grade === "" ? null : Number(grade),
        confirm_same,
      }),
    onSuccess: (result) => {
      setConflict(null);
      onSaved(result);
    },
    onError: (err) => {
      const same = isSameInstitution(err);
      if (same) {
        setError(null);
        setConflict(same);
        return;
      }
      setConflict(null);
      setError(
        err instanceof ApiError &&
          err.status >= 400 &&
          err.status < 500 &&
          typeof err.detail === "string"
          ? err.detail
          : t("adminGroups.institutionError"),
      );
    },
  });

  const submit = (confirm_same: boolean) => {
    setError(null);
    save.mutate(confirm_same);
  };

  return (
    <motion.form
      initial={{ opacity: 0, y: -6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.18, ease: "easeOut" }}
      onSubmit={(e) => {
        e.preventDefault();
        submit(false);
      }}
      className="flex flex-wrap items-center gap-3 border-l-2 border-[color:var(--color-partial)] pl-3"
    >
      <label className="text-xs text-slate-400" htmlFor={`${ids}-institution`}>
        {t("adminGroups.fieldInstitution")}
      </label>
      <input
        id={`${ids}-institution`}
        list={`${ids}-recorded`}
        value={institution}
        maxLength={240}
        onChange={(e) => {
          setInstitution(e.target.value);
          setConflict(null);
        }}
        className="min-w-[16rem] flex-1 bg-slate-800 border border-slate-600 rounded-lg px-3 py-1.5 text-sm text-slate-200 focus:outline-none focus:border-violet-500"
      />
      <datalist id={`${ids}-recorded`}>
        {(recorded?.institutions ?? []).map((r) => (
          <option key={r.institution} value={r.institution} />
        ))}
      </datalist>
      <label className="text-xs text-slate-400" htmlFor={`${ids}-grade`}>
        {t("adminGroups.fieldGrade")}
      </label>
      <select
        id={`${ids}-grade`}
        value={grade}
        onChange={(e) => {
          setGrade(e.target.value);
          setConflict(null);
        }}
        className="bg-slate-800 border border-slate-600 rounded-lg px-2 py-1.5 text-sm text-slate-200 focus:outline-none focus:border-violet-500"
      >
        <option value="">{t("adminGroups.gradeNone")}</option>
        {GRADES.map((g) => (
          <option key={g} value={String(g)}>
            {gradeLabel(g)}
          </option>
        ))}
      </select>
      <Button size="sm" type="submit" loading={save.isPending && !conflict}>
        {t("adminGroups.save")}
      </Button>
      <Button size="sm" variant="ghost" type="button" onClick={onCancel}>
        {t("adminGroups.cancel")}
      </Button>

      {error && (
        <p role="alert" className="basis-full text-xs text-red-300">
          {error}
        </p>
      )}
      {conflict && (
        <div
          role="alert"
          className="basis-full rounded-lg border border-amber-700/40 bg-amber-900/20 px-3 py-2 text-xs text-amber-200 space-y-2"
        >
          <p>{t("adminGroups.sameInstitution")}</p>
          <ul className="list-disc pl-5">
            {conflict.groups.map((g) => (
              <li key={g.id}>
                {t("adminGroups.sameInstitutionGroup", { name: g.name, teacher: g.teacher ?? "—" })}
              </li>
            ))}
          </ul>
          <Button
            size="sm"
            variant="secondary"
            type="button"
            loading={save.isPending}
            onClick={() => submit(true)}
          >
            {t("adminGroups.saveAnyway")}
          </Button>
        </div>
      )}
    </motion.form>
  );
}

function GroupRow({
  group,
  onDelete,
  deleting,
  editing,
  onEdit,
  onSaved,
  onCancelEdit,
}: {
  group: AdminGroup;
  onDelete: (id: number) => void;
  deleting: boolean;
  editing: boolean;
  onEdit: () => void;
  onSaved: (result: GroupInstitutionResult) => void;
  onCancelEdit: () => void;
}) {
  const { t } = useTranslation();
  const [confirm, setConfirm] = useState(false);

  return (
    <>
      <tr className="hover:bg-slate-700/30 transition-colors">
        <td className="px-4 py-3 text-slate-100 text-sm font-medium">{group.name}</td>
        <td className="px-4 py-3 text-slate-400 text-sm">{group.teacher_name}</td>
        <td className="px-4 py-3 text-center text-slate-300 text-sm">{group.student_count}</td>
        {hasInstitution(group) ? (
          <td className="px-4 py-3 text-slate-200 text-sm">{group.institution}</td>
        ) : (
          // D1: the groups still to fix stand out in the warning token.
          <td
            className="px-4 py-3 text-sm font-semibold text-[color:var(--color-partial)]"
            title={t("adminGroups.noInstitution")}
          >
            —
          </td>
        )}
        <td className="px-4 py-3 text-center text-slate-300 text-sm tabular-nums">
          {gradeLabel(group.grade)}
        </td>
        <td className="px-4 py-3">
          {confirm ? (
            <div className="flex items-center gap-2">
              <span className="text-xs text-red-400">{t("adminGroups.confirmDelete")}</span>
              <Button
                size="sm"
                variant="danger"
                loading={deleting}
                onClick={() => onDelete(group.id)}
              >
                {t("adminGroups.confirmYes")}
              </Button>
              <Button size="sm" variant="ghost" onClick={() => setConfirm(false)}>
                {t("adminGroups.cancel")}
              </Button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Button size="sm" variant="secondary" onClick={onEdit} disabled={editing}>
                {t("adminGroups.editInstitution")}
              </Button>
              <Button size="sm" variant="danger" onClick={() => setConfirm(true)}>
                {t("adminGroups.delete")}
              </Button>
            </div>
          )}
        </td>
      </tr>
      {editing && (
        <tr className="bg-slate-900/40">
          <td colSpan={6} className="px-4 py-3">
            <InstitutionForm group={group} onSaved={onSaved} onCancel={onCancelEdit} />
          </td>
        </tr>
      )}
    </>
  );
}

export function AdminGroups() {
  const { t } = useTranslation();
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [onlyMissing, setOnlyMissing] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: onlyMissing ? ["admin-groups", "without-institution"] : ["admin-groups"],
    queryFn: onlyMissing ? adminApi.groupsWithoutInstitution : adminApi.allGroups,
    staleTime: 30_000,
  });

  const deleteMutation = useMutation({
    mutationFn: (group_id: number) => adminApi.deleteGroup(group_id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-groups"] });
      setDeletingId(null);
    },
    onError: (err) => {
      setDeletingId(null);
      // A refusal (unknown group) comes with its reason; anything else gets the generic text.
      setDeleteError(
        err instanceof ApiError && err.status >= 400 && err.status < 500
          ? err.detail
          : t("adminGroups.deleteError"),
      );
    },
  });

  const handleDelete = (group_id: number) => {
    setDeleteError(null);
    setDeletingId(group_id);
    deleteMutation.mutate(group_id);
  };

  const handleSaved = (result: GroupInstitutionResult) => {
    setEditingId(null);
    setNotice(
      result.unchanged
        ? t("adminGroups.unchanged")
        : result.students_with_other_grade > 0
          ? t("adminGroups.otherGrade", { count: result.students_with_other_grade })
          : t("adminGroups.saved"),
    );
    qc.invalidateQueries({ queryKey: ["admin-groups"] });
    qc.invalidateQueries({ queryKey: ["admin-institutions"] });
    qc.invalidateQueries({ queryKey: ["admin-account-audit"] });
  };

  if (isLoading && !data) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-400 animate-pulse">{t("adminGroups.loading")}</p>
      </div>
    );
  }

  const groups = data?.groups ?? [];
  const missing = data?.without_institution ?? groups.filter((g) => !hasInstitution(g)).length;
  const filtered = groups.filter((g) =>
    g.name.toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <div className="max-w-5xl mx-auto py-6 px-4 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-slate-100">{t("adminGroups.title")}</h2>
        <span className="text-xs text-slate-500">{t("adminGroups.count", { count: groups.length })}</span>
      </div>

      <div className="bg-amber-900/20 border border-amber-700/30 rounded-lg px-4 py-2 text-xs text-amber-300">
        {t("adminGroups.warning")}
      </div>

      {deleteError && (
        <div
          role="alert"
          className="bg-red-900/20 border border-red-700/30 rounded-lg px-4 py-2 text-xs text-red-300"
        >
          {deleteError}
        </div>
      )}

      {notice && (
        <div
          role="status"
          className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-xs text-slate-300"
        >
          {notice}
        </div>
      )}

      <div className="flex flex-wrap items-center gap-4">
        <input
          type="text"
          placeholder={t("adminGroups.searchPlaceholder")}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="bg-slate-800 border border-slate-600 rounded-lg px-3 py-1.5 text-sm text-slate-200 focus:outline-none focus:border-violet-500 placeholder-slate-600"
        />
        <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
          <input
            type="checkbox"
            checked={onlyMissing}
            onChange={(e) => {
              setOnlyMissing(e.target.checked);
              setEditingId(null);
            }}
            className="accent-[color:var(--color-partial)]"
          />
          {t("adminGroups.onlyWithoutInstitution", { count: missing })}
        </label>
      </div>

      <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-xs text-slate-500 border-b border-slate-700">
                <th className="px-4 py-2 text-left">{t("adminGroups.colName")}</th>
                <th className="px-4 py-2 text-left">{t("adminGroups.colTeacher")}</th>
                <th className="px-4 py-2 text-center">{t("adminGroups.colStudents")}</th>
                <th className="px-4 py-2 text-left">{t("adminGroups.colInstitution")}</th>
                <th className="px-4 py-2 text-center">{t("adminGroups.colGrade")}</th>
                <th className="px-4 py-2 text-left">{t("adminGroups.colAction")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center text-slate-500 text-sm py-8">
                    {onlyMissing ? t("adminGroups.emptyWithoutInstitution") : t("adminGroups.empty")}
                  </td>
                </tr>
              ) : (
                filtered.map((g) => (
                  <GroupRow
                    key={g.id}
                    group={g}
                    onDelete={handleDelete}
                    deleting={deletingId === g.id && deleteMutation.isPending}
                    editing={editingId === g.id}
                    onEdit={() => {
                      setNotice(null);
                      setEditingId(g.id);
                    }}
                    onSaved={handleSaved}
                    onCancelEdit={() => setEditingId(null)}
                  />
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
