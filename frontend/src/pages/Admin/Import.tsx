/**
 * pages/Admin/Import.tsx
 * ======================
 * Spec 009 I1 — «Importar estudiantes»: the admin uploads the form's export, maps its columns,
 * chooses the batch's last day (and level and grade where not mapped), pairs each institution and
 * grade of the file with a group, reads the preview and confirms (US1-AS1, US1-AS2). Nothing is
 * saved before the confirmation; the file stays in this page's memory and goes again with it, so
 * the server confirms exactly what the admin saw (FR-003).
 */

import { useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { motion } from "framer-motion";
import { adminApi } from "../../api/teacher";
import type {
  AdminGroup,
  ImportBatch,
  ImportChangeField,
  ImportChoices,
  ImportColumns,
  ImportMapping,
  ImportPair,
  ImportPreview,
  ImportRow,
  ImportStatus,
} from "../../api/teacher";
import { ApiError } from "../../api/client";
import { Button } from "../../components/ui/Button";

const FIELD =
  "bg-slate-900 border border-slate-600 rounded-lg px-3 py-1.5 text-sm text-slate-200 focus:outline-none focus:border-violet-500";
const LEVELS = ["colegio", "universidad", "concursos", "semillero"] as const;
const GRADES = [6, 7, 8, 9, 10, 11];
const STATUSES: ImportStatus[] = ["new", "existing", "duplicate", "error"];
const STATUS_TONE: Record<ImportStatus, string> = {
  new: "text-emerald-300 bg-emerald-900/30",
  existing: "text-sky-300 bg-sky-900/30",
  duplicate: "text-slate-300 bg-slate-700/50",
  error: "text-red-300 bg-red-900/30",
};

const pairKey = (institution: string | null, grade: number | null) =>
  `${institution ?? ""}|${grade ?? ""}`;

/** The step rail: where the admin is, numbered like the plan's four steps. */
function Steps({ current }: { current: number }) {
  const { t } = useTranslation();
  const labels = [
    t("adminImport.stepFile"),
    t("adminImport.stepColumns"),
    t("adminImport.stepBatch"),
    t("adminImport.stepPreview"),
  ];
  return (
    <ol className="flex flex-wrap gap-2" aria-label={t("adminImport.title")}>
      {labels.map((label, i) => (
        <li
          key={label}
          aria-current={i + 1 === current ? "step" : undefined}
          className={`flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium ${
            i + 1 === current
              ? "bg-violet-600/30 text-violet-200 ring-1 ring-violet-500/60"
              : i + 1 < current
                ? "bg-slate-700/60 text-slate-300"
                : "bg-slate-800 text-slate-500"
          }`}
        >
          <span className="tabular-nums">{i + 1}</span>
          {label}
        </li>
      ))}
    </ol>
  );
}

function ColumnSelect({
  label,
  value,
  header,
  onChange,
  optional = false,
}: {
  label: string;
  value: string | null | undefined;
  header: string[];
  onChange: (value: string | null) => void;
  optional?: boolean;
}) {
  const { t } = useTranslation();
  return (
    <label className="text-xs text-slate-400 flex flex-col gap-1">
      {label}
      <select
        aria-label={label}
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value || null)}
        className={FIELD}
        required={!optional}
      >
        <option value="">{optional ? t("adminImport.notMapped") : t("adminImport.chooseColumn")}</option>
        {header.map((column) => (
          <option key={column} value={column}>
            {column}
          </option>
        ))}
      </select>
    </label>
  );
}

function groupLabel(groups: AdminGroup[], id: unknown): string {
  const group = groups.find((g) => g.id === id);
  return group ? `${group.name} · ${group.teacher_name}` : String(id ?? "—");
}

function RowChanges({
  row,
  groups,
  checked,
  onToggle,
}: {
  row: ImportRow;
  groups: AdminGroup[];
  checked: ImportChangeField[];
  onToggle: (field: ImportChangeField) => void;
}) {
  const { t } = useTranslation();
  const fields = Object.keys(row.changes) as ImportChangeField[];
  if (fields.length === 0) return <span className="text-slate-500">{t("adminImport.noChanges")}</span>;
  const text = (field: ImportChangeField) => {
    const change = row.changes[field]!;
    const shown = (v: unknown) => (v === null || v === undefined || v === "" ? t("adminImport.none") : String(v));
    if (field === "group_id")
      return t("adminImport.changeGroup", {
        from: change.from == null ? t("adminImport.none") : groupLabel(groups, change.from),
        to: groupLabel(groups, change.to),
      });
    if (field === "access_until")
      return t("adminImport.changeLastDay", { from: shown(change.from), to: shown(change.to) });
    return t("adminImport.changeEmail", { from: shown(change.from), to: shown(change.to) });
  };
  return (
    <div className="flex flex-col gap-1">
      {fields.map((field) => (
        <label key={field} className="flex items-center gap-2 text-xs text-slate-300">
          <input
            type="checkbox"
            checked={checked.includes(field)}
            onChange={() => onToggle(field)}
            className="accent-violet-500"
          />
          {text(field)}
        </label>
      ))}
    </div>
  );
}

export function AdminImport() {
  const { t } = useTranslation();
  const [file, setFile] = useState<File | null>(null);
  const [columns, setColumns] = useState<ImportColumns | null>(null);
  const [mapping, setMapping] = useState<ImportMapping>({ identification: "", name: [] });
  const [batch, setBatch] = useState<ImportBatch>({ level: "semillero", grade: null, access_until: "" });
  const [chosen, setChosen] = useState<Record<string, number | null>>({});
  const [preview, setPreview] = useState<ImportPreview | null>(null);
  const [confirmed, setConfirmed] = useState<Record<number, ImportChangeField[]>>({});
  const [filter, setFilter] = useState<ImportStatus | "all">("all");
  const [importId, setImportId] = useState<string | null>(null);
  const [error, setError] = useState("");

  const { data: groupsData } = useQuery({ queryKey: ["admin-groups"], queryFn: adminApi.allGroups });
  const groups = groupsData?.groups ?? [];

  const record = useQuery({
    queryKey: ["admin-import", importId],
    queryFn: () => adminApi.getImport(importId!),
    enabled: importId !== null,
    refetchInterval: (query) => (query.state.data?.state === "running" ? 1500 : false),
  });

  const readColumns = useMutation({
    mutationFn: (chosenFile: File) => adminApi.importColumns(chosenFile),
    onSuccess: (res) => {
      setColumns(res);
      setMapping({
        identification: res.suggested.identification ?? "",
        name: res.suggested.name ?? [],
        level: res.suggested.level ?? null,
        grade: res.suggested.grade ?? null,
        institution: res.suggested.institution ?? null,
        recovery_email: res.suggested.recovery_email ?? null,
      });
      setPreview(null);
      setError("");
    },
    onError: (err: Error) => setError(err.message),
  });

  const choices = (pairs: ImportPair[] | null): ImportChoices => ({
    file: file!,
    mapping: { ...mapping, name: mapping.name.filter(Boolean) },
    batch: {
      level: mapping.level ? null : batch.level,
      grade: mapping.grade || batch.level !== "semillero" ? null : batch.grade,
      access_until: batch.access_until || null,
    },
    pairing: (pairs ?? [])
      .map((p) => ({
        institution: p.institution,
        grade: p.grade,
        group_id: chosen[pairKey(p.institution, p.grade)] ?? p.group_id,
      }))
      .filter((p): p is { institution: string | null; grade: number | null; group_id: number } => p.group_id != null),
  });

  const runPreview = useMutation({
    mutationFn: (pairs: ImportPair[] | null) => adminApi.importPreview(choices(pairs)),
    onSuccess: (res) => {
      setPreview(res);
      setConfirmed({});
      setError("");
    },
    onError: (err: Error) => setError(err.message),
  });

  const confirm = useMutation({
    mutationFn: () =>
      adminApi.importConfirm(
        choices(preview!.pairs),
        preview!.digest,
        Object.entries(confirmed)
          .filter(([, fields]) => fields.length > 0)
          .map(([row, fields]) => ({ row: Number(row), changes: fields }))
      ),
    onSuccess: (res) => setImportId(res.import_id),
    onError: (err: Error) => {
      setError(err.message);
      // FR-003: a preview that changed since the admin saw it must be generated again.
      if (err instanceof ApiError && err.status === 409) setPreview(null);
    },
  });

  const rows = useMemo(
    () => (preview?.rows ?? []).filter((r) => filter === "all" || r.status === filter),
    [preview, filter]
  );

  const step = importId ? 4 : preview ? 4 : columns ? (mapping.identification && mapping.name[0] ? 3 : 2) : 1;
  const done = record.data ? Object.values(record.data.counts).reduce((a, b) => a + b, 0) : 0;

  const startOver = () => {
    setFile(null);
    setColumns(null);
    setPreview(null);
    setImportId(null);
    setChosen({});
    setConfirmed({});
    setError("");
  };

  const invalidate = () => setPreview(null);

  return (
    <div className="max-w-6xl mx-auto py-6 px-4 space-y-6">
      <header className="space-y-2">
        <h2 className="text-xl font-bold text-slate-100">{t("adminImport.title")}</h2>
        <p className="text-sm text-slate-400 max-w-3xl">{t("adminImport.intro")}</p>
        <Steps current={step} />
      </header>

      {error ? (
        <p role="alert" className="text-sm text-red-300 bg-red-900/20 border border-red-800/50 rounded-lg px-3 py-2">
          {error}
        </p>
      ) : null}

      {importId ? (
        <section
          aria-label={t("adminImport.stepPreview")}
          className="bg-slate-800 border border-slate-700 rounded-xl p-5 space-y-4"
        >
          {record.data?.state === "running" || !record.data ? (
            <p role="status" className="text-sm text-slate-300 animate-pulse">
              {t("adminImport.running", { done, total: record.data?.total_rows ?? preview?.rows.length ?? 0 })}
            </p>
          ) : record.data.state === "interrupted" ? (
            <p role="status" className="text-sm text-amber-300">
              {t("adminImport.interrupted")}
            </p>
          ) : (
            <p role="status" className="text-sm font-semibold text-emerald-300">
              {t("adminImport.finished")}
            </p>
          )}
          {record.data ? (
            <dl className="grid grid-cols-3 sm:grid-cols-6 gap-3" data-testid="import-result">
              {(["created", "updated", "unchanged", "skipped", "duplicate", "error"] as const).map((key) => (
                <motion.div
                  key={key}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="bg-slate-900/60 rounded-lg px-3 py-2"
                >
                  <dt className="text-[11px] uppercase tracking-wide text-slate-500">
                    {t(`adminImport.result${key[0].toUpperCase()}${key.slice(1)}`)}
                  </dt>
                  <dd className="text-lg font-semibold tabular-nums text-slate-100">{record.data!.counts[key]}</dd>
                </motion.div>
              ))}
            </dl>
          ) : null}
          {record.data && record.data.state !== "running" ? (
            <Button size="sm" variant="secondary" onClick={startOver}>
              {t("adminImport.startOver")}
            </Button>
          ) : null}
        </section>
      ) : (
        <>
          <section className="bg-slate-800 border border-slate-700 rounded-xl p-4 space-y-3">
            <label className="text-xs text-slate-400 flex flex-col gap-1 max-w-md">
              {t("adminImport.chooseFile")}
              <input
                type="file"
                accept=".xlsx,.csv"
                onChange={(e) => {
                  const chosenFile = e.target.files?.[0] ?? null;
                  setFile(chosenFile);
                  setColumns(null);
                  setPreview(null);
                  if (chosenFile) readColumns.mutate(chosenFile);
                }}
                className="text-sm text-slate-300 file:mr-3 file:rounded-lg file:border-0 file:bg-violet-600 file:px-3 file:py-1.5 file:text-white"
              />
            </label>
            {readColumns.isPending ? <p className="text-xs text-slate-400">{t("adminImport.reading")}</p> : null}
          </section>

          {columns ? (
            <section
              aria-label={t("adminImport.stepColumns")}
              className="bg-slate-800 border border-slate-700 rounded-xl p-4 space-y-4"
            >
              <p className="text-xs text-slate-500">{t("adminImport.rowsInFile", { count: columns.rows })}</p>
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                <ColumnSelect
                  label={t("adminImport.mapIdentification")}
                  value={mapping.identification}
                  header={columns.header}
                  onChange={(v) => {
                    setMapping((m) => ({ ...m, identification: v ?? "" }));
                    invalidate();
                  }}
                />
                <ColumnSelect
                  label={t("adminImport.mapNameFirst")}
                  value={mapping.name[0]}
                  header={columns.header}
                  onChange={(v) => {
                    setMapping((m) => ({ ...m, name: [v ?? "", m.name[1] ?? ""].filter(Boolean) }));
                    invalidate();
                  }}
                />
                <ColumnSelect
                  optional
                  label={t("adminImport.mapNameSecond")}
                  value={mapping.name[1]}
                  header={columns.header}
                  onChange={(v) => {
                    setMapping((m) => ({ ...m, name: [m.name[0] ?? "", v ?? ""].filter(Boolean) }));
                    invalidate();
                  }}
                />
                <ColumnSelect
                  optional
                  label={t("adminImport.mapGrade")}
                  value={mapping.grade}
                  header={columns.header}
                  onChange={(v) => {
                    setMapping((m) => ({ ...m, grade: v }));
                    invalidate();
                  }}
                />
                <ColumnSelect
                  optional
                  label={t("adminImport.mapLevel")}
                  value={mapping.level}
                  header={columns.header}
                  onChange={(v) => {
                    setMapping((m) => ({ ...m, level: v }));
                    invalidate();
                  }}
                />
                <ColumnSelect
                  optional
                  label={t("adminImport.mapInstitution")}
                  value={mapping.institution}
                  header={columns.header}
                  onChange={(v) => {
                    setMapping((m) => ({ ...m, institution: v }));
                    invalidate();
                  }}
                />
                <ColumnSelect
                  optional
                  label={t("adminImport.mapEmail")}
                  value={mapping.recovery_email}
                  header={columns.header}
                  onChange={(v) => {
                    setMapping((m) => ({ ...m, recovery_email: v }));
                    invalidate();
                  }}
                />
              </div>
              <details className="text-xs text-slate-400">
                <summary className="cursor-pointer">{t("adminImport.examplesTitle")}</summary>
                <div className="overflow-x-auto mt-2">
                  <table className="text-[11px] text-slate-300">
                    <thead>
                      <tr>
                        {columns.header.map((c) => (
                          <th key={c} className="px-2 py-1 text-left text-slate-500 whitespace-nowrap">
                            {c}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {columns.examples.map((cells, i) => (
                        <tr key={i}>
                          {cells.map((cell, j) => (
                            <td key={j} className="px-2 py-1 whitespace-nowrap">
                              {cell}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </details>
            </section>
          ) : null}

          {columns && mapping.identification && mapping.name[0] ? (
            <section
              aria-label={t("adminImport.stepBatch")}
              className="bg-slate-800 border border-slate-700 rounded-xl p-4 space-y-4"
            >
              <div className="grid gap-3 sm:grid-cols-3">
                {!mapping.level ? (
                  <label className="text-xs text-slate-400 flex flex-col gap-1">
                    {t("adminImport.batchLevel")}
                    <select
                      aria-label={t("adminImport.batchLevel")}
                      value={batch.level ?? ""}
                      onChange={(e) => {
                        setBatch((b) => ({ ...b, level: e.target.value }));
                        invalidate();
                      }}
                      className={FIELD}
                    >
                      {LEVELS.map((level) => (
                        <option key={level} value={level}>
                          {level}
                        </option>
                      ))}
                    </select>
                  </label>
                ) : null}
                {!mapping.grade && batch.level === "semillero" ? (
                  <label className="text-xs text-slate-400 flex flex-col gap-1">
                    {t("adminImport.batchGrade")}
                    <select
                      aria-label={t("adminImport.batchGrade")}
                      value={batch.grade ?? ""}
                      onChange={(e) => {
                        setBatch((b) => ({ ...b, grade: e.target.value ? Number(e.target.value) : null }));
                        invalidate();
                      }}
                      className={FIELD}
                    >
                      <option value="">—</option>
                      {GRADES.map((g) => (
                        <option key={g} value={g}>
                          {g}.º
                        </option>
                      ))}
                    </select>
                  </label>
                ) : null}
                <label className="text-xs text-slate-400 flex flex-col gap-1">
                  {t("adminImport.batchLastDay")}
                  <input
                    aria-label={t("adminImport.batchLastDay")}
                    type="date"
                    value={batch.access_until ?? ""}
                    onChange={(e) => {
                      setBatch((b) => ({ ...b, access_until: e.target.value }));
                      invalidate();
                    }}
                    className={FIELD}
                  />
                </label>
              </div>
              <Button size="sm" loading={runPreview.isPending} onClick={() => runPreview.mutate(null)}>
                {preview ? t("adminImport.refreshPreview") : t("adminImport.showPreview")}
              </Button>
            </section>
          ) : null}

          {preview ? (
            <section
              aria-label={t("adminImport.stepPreview")}
              className="bg-slate-800 border border-slate-700 rounded-xl p-4 space-y-4"
            >
              <div className="space-y-2">
                <h3 className="text-sm font-semibold text-slate-200">{t("adminImport.pairsTitle")}</h3>
                <p className="text-xs text-slate-500">{t("adminImport.pairsHint")}</p>
                <div className="grid gap-2 sm:grid-cols-2">
                  {preview.pairs.map((pair) => {
                    const key = pairKey(pair.institution, pair.grade);
                    const value = chosen[key] ?? pair.group_id ?? "";
                    return (
                      <label key={key} className="text-xs text-slate-300 flex flex-col gap-1">
                        <span>
                          {pair.institution ?? t("adminImport.noInstitution")} ·{" "}
                          {pair.grade != null ? t("adminImport.gradeShort", { grade: pair.grade }) : "—"}
                          {pair.suggested_group_id != null && pair.suggested_group_id === value ? (
                            <span className="ml-2 text-[10px] uppercase text-violet-300">{t("adminImport.suggested")}</span>
                          ) : null}
                        </span>
                        <select
                          value={value}
                          onChange={(e) => {
                            const groupId = e.target.value ? Number(e.target.value) : null;
                            const nextChosen = { ...chosen, [key]: groupId };
                            setChosen(nextChosen);
                            runPreview.mutate(
                              preview.pairs.map((p) =>
                                pairKey(p.institution, p.grade) === key ? { ...p, group_id: groupId } : p
                              )
                            );
                          }}
                          className={FIELD}
                        >
                          <option value="">{t("adminImport.noGroup")}</option>
                          {groups.map((g) => (
                            <option key={g.id} value={g.id}>
                              {g.name} · {g.teacher_name}
                            </option>
                          ))}
                        </select>
                      </label>
                    );
                  })}
                </div>
              </div>

              <div className="flex flex-wrap gap-2" role="group" aria-label={t("adminImport.colStatus")}>
                <button
                  type="button"
                  onClick={() => setFilter("all")}
                  aria-pressed={filter === "all"}
                  className={`text-xs px-3 py-1 rounded-full ${filter === "all" ? "bg-violet-600/40 text-violet-100" : "bg-slate-700 text-slate-300"}`}
                >
                  {t("adminImport.filterAll")} · {preview.rows.length}
                </button>
                {STATUSES.map((status) => (
                  <button
                    key={status}
                    type="button"
                    onClick={() => setFilter(status)}
                    aria-pressed={filter === status}
                    data-testid={`count-${status}`}
                    className={`text-xs px-3 py-1 rounded-full ${filter === status ? "ring-1 ring-violet-400 " : ""}${STATUS_TONE[status]}`}
                  >
                    {t(`adminImport.count${status[0].toUpperCase()}${status.slice(1)}`)} · {preview.counts[status]}
                  </button>
                ))}
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-xs text-slate-500 border-b border-slate-700">
                      <th className="px-3 py-2 text-left">{t("adminImport.colRow")}</th>
                      <th className="px-3 py-2 text-left">{t("adminImport.colStatus")}</th>
                      <th className="px-3 py-2 text-left">{t("adminImport.colIdentification")}</th>
                      <th className="px-3 py-2 text-left">{t("adminImport.colName")}</th>
                      <th className="px-3 py-2 text-left">{t("adminImport.colGroup")}</th>
                      <th className="px-3 py-2 text-left">{t("adminImport.colReasons")}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-700/50">
                    {rows.map((row) => (
                      <tr key={row.row} data-testid={`import-row-${row.row}`}>
                        <td className="px-3 py-2 tabular-nums text-slate-400">{row.row}</td>
                        <td className="px-3 py-2">
                          <span className={`text-xs px-2 py-0.5 rounded-full ${STATUS_TONE[row.status]}`}>
                            {t(`adminImport.status${row.status[0].toUpperCase()}${row.status.slice(1)}`)}
                          </span>
                        </td>
                        <td className="px-3 py-2 font-mono text-xs text-slate-300">{row.identification ?? "—"}</td>
                        <td className="px-3 py-2 text-slate-200">{row.display_name ?? "—"}</td>
                        <td className="px-3 py-2 text-slate-400">
                          {row.group_id != null ? groupLabel(groups, row.group_id) : "—"}
                        </td>
                        <td className="px-3 py-2 text-xs">
                          {row.status === "existing" ? (
                            <RowChanges
                              row={row}
                              groups={groups}
                              checked={confirmed[row.row] ?? []}
                              onToggle={(field) =>
                                setConfirmed((c) => {
                                  const current = c[row.row] ?? [];
                                  return {
                                    ...c,
                                    [row.row]: current.includes(field)
                                      ? current.filter((f) => f !== field)
                                      : [...current, field],
                                  };
                                })
                              }
                            />
                          ) : (
                            <ul className="text-red-300 space-y-0.5">
                              {row.reasons.map((reason) => (
                                <li key={reason}>{t(`adminImport.reasons.${reason}`, { defaultValue: reason })}</li>
                              ))}
                            </ul>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="flex items-center gap-3 flex-wrap">
                <Button loading={confirm.isPending} onClick={() => confirm.mutate()}>
                  {t("adminImport.confirm")}
                </Button>
                <span className="text-xs text-slate-500">{t("adminImport.confirmHint")}</span>
              </div>
            </section>
          ) : null}
        </>
      )}
    </div>
  );
}
