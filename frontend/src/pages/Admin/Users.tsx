/**
 * pages/Admin/Users.tsx
 * ======================
 * Panel de administración de usuarios: aprobar docentes, activar/desactivar cuentas; crear
 * estudiantes y docentes, y fijar el último día de acceso (spec 004 E2, E3). Spec 009 I1: la
 * identificación vinculada de cada estudiante, vincularla o quitar un vínculo hecho por error, y
 * crear un grupo para un docente con su institución y grado.
 */

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { adminApi } from "../../api/teacher";
import type { AdminUser, CreateStudentBody, TemporaryPassword } from "../../api/teacher";
import { Button } from "../../components/ui/Button";

function RoleBadge({ role }: { role: string }) {
  const colors: Record<string, string> = {
    student: "bg-blue-900/50 text-blue-300",
    teacher: "bg-violet-900/50 text-violet-300",
    admin: "bg-yellow-900/50 text-yellow-300",
  };
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${colors[role] ?? "bg-slate-700 text-slate-300"}`}>
      {role}
    </span>
  );
}

function PendingTeachersSection() {
  const { t } = useTranslation();
  const qc = useQueryClient();

  const { data } = useQuery({
    queryKey: ["pending-teachers"],
    queryFn: adminApi.pendingTeachers,
    refetchInterval: 30_000,
  });

  const approveMutation = useMutation({
    mutationFn: ({ user_id, action }: { user_id: number; action: "approve" | "reject" }) =>
      adminApi.approveTeacher(user_id, action),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["pending-teachers"] });
      qc.invalidateQueries({ queryKey: ["admin-users"] });
    },
  });

  const teachers = data?.teachers ?? [];
  if (teachers.length === 0) return null;

  const getUserId = (u: AdminUser) => (u.user_id ?? u.id ?? 0) as number;

  return (
    <div className="bg-amber-900/20 border border-amber-700/40 rounded-xl p-4 space-y-3">
      <div className="flex items-center gap-2">
        <span className="text-amber-400">🔔</span>
        <h3 className="text-sm font-semibold text-amber-300">
          {t("adminUsers.pendingTeachersTitle", { count: teachers.length })}
        </h3>
      </div>
      <div className="space-y-2">
        {teachers.map((tch) => {
          const uid = getUserId(tch);
          return (
            <div
              key={uid}
              className="flex items-center justify-between bg-slate-800 rounded-lg px-3 py-2 border border-slate-700"
            >
              <div>
                <span className="text-slate-100 font-medium text-sm">{tch.username}</span>
                <span className="text-xs text-slate-500 ml-2">{t("adminUsers.teacherRoleLabel")}</span>
              </div>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="secondary"
                  loading={approveMutation.isPending}
                  onClick={() => approveMutation.mutate({ user_id: uid, action: "approve" })}
                >
                  {t("adminUsers.approve")}
                </Button>
                <Button
                  size="sm"
                  variant="danger"
                  loading={approveMutation.isPending}
                  onClick={() => approveMutation.mutate({ user_id: uid, action: "reject" })}
                >
                  {t("adminUsers.reject")}
                </Button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/** Spec 004 FR-029, FR-031: the temporary password, shown once; never stored by the page. */
function TemporaryPasswordNotice({
  issued,
  onClose,
}: {
  issued: TemporaryPassword & { username: string };
  onClose: () => void;
}) {
  const { t } = useTranslation();
  return (
    <div
      role="status"
      data-testid="temporary-password"
      className="bg-teal-900/20 border border-teal-600/40 rounded-xl p-4 space-y-2"
    >
      <div className="flex items-start justify-between gap-3">
        <h3 className="text-sm font-semibold text-teal-300">
          {t("adminUsers.temporaryTitle", { username: issued.username })}
        </h3>
        <button onClick={onClose} className="text-xs text-slate-400 hover:text-slate-200">
          {t("adminUsers.close")}
        </button>
      </div>
      <code className="block font-mono text-lg tracking-wider text-slate-100 select-all">
        {issued.temporary_password}
      </code>
      <p className="text-xs text-slate-400">{t("adminUsers.temporaryHint")}</p>
    </div>
  );
}

function CreateTeacherSection({ onIssued }: { onIssued: (p: TemporaryPassword & { username: string }) => void }) {
  const { t } = useTranslation();
  const qc = useQueryClient();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const create = useMutation({
    mutationFn: () =>
      adminApi.createTeacher({ username: username.trim(), email: email.trim() || undefined }),
    onSuccess: (res) => {
      onIssued({ ...res, username: res.username ?? username.trim() });
      setUsername("");
      setEmail("");
      qc.invalidateQueries({ queryKey: ["admin-users"] });
    },
  });
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        create.mutate();
      }}
      className="bg-slate-800 border border-slate-700 rounded-xl p-4 space-y-3"
      aria-label={t("adminUsers.createTeacherTitle")}
    >
      <div>
        <h3 className="text-sm font-semibold text-slate-200">{t("adminUsers.createTeacherTitle")}</h3>
        <p className="text-xs text-slate-500">{t("adminUsers.createTeacherHint")}</p>
      </div>
      <div className="flex gap-3 flex-wrap">
        <input
          required
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder={t("adminUsers.createTeacherUsername")}
          aria-label={t("adminUsers.createTeacherUsername")}
          className="bg-slate-900 border border-slate-600 rounded-lg px-3 py-1.5 text-sm text-slate-200 focus:outline-none focus:border-violet-500"
        />
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder={t("adminUsers.createTeacherEmail")}
          aria-label={t("adminUsers.createTeacherEmail")}
          className="bg-slate-900 border border-slate-600 rounded-lg px-3 py-1.5 text-sm text-slate-200 focus:outline-none focus:border-violet-500"
        />
        <Button size="sm" type="submit" loading={create.isPending}>
          {t("adminUsers.createTeacherSubmit")}
        </Button>
      </div>
      {create.isError && (
        <p role="alert" className="text-xs text-red-400">
          {(create.error as Error).message}
        </p>
      )}
    </form>
  );
}

const LEVELS = [
  ["colegio", "adminUsers.levelColegio"],
  ["universidad", "adminUsers.levelUniversidad"],
  ["concursos", "adminUsers.levelConcursos"],
  ["semillero", "adminUsers.levelSemillero"],
] as const;
const SEMILLERO_GRADES = ["6", "7", "8", "9", "10", "11"];

const FIELD =
  "bg-slate-900 border border-slate-600 rounded-lg px-3 py-1.5 text-sm text-slate-200 focus:outline-none focus:border-violet-500";

/** «2026-12-31» → «31/12/2026»: the day as given, never shifted by the browser's time zone. */
function shownDay(day: string): string {
  const [y, m, d] = day.split("-");
  return d && m && y ? `${d}/${m}/${y}` : day;
}

/** Spec 004 FR-040 (N13, N15): own username, display name, an existing group, level and grade,
 * optional last day; the temporary password is shown once. */
function CreateStudentSection({ onIssued }: { onIssued: (p: TemporaryPassword & { username: string }) => void }) {
  const { t } = useTranslation();
  const qc = useQueryClient();
  const { data: groupsData } = useQuery({ queryKey: ["admin-groups"], queryFn: adminApi.allGroups });
  const empty = { username: "", display_name: "", group_id: "", education_level: "", grade: "9", access_until: "" };
  const [form, setForm] = useState(empty);
  const set = (key: keyof typeof empty) => (e: { target: { value: string } }) =>
    setForm((f) => ({ ...f, [key]: e.target.value }));
  const semillero = form.education_level === "semillero";
  const create = useMutation({
    mutationFn: () => {
      const body: CreateStudentBody = {
        username: form.username.trim(),
        display_name: form.display_name,
        group_id: Number(form.group_id),
        education_level: form.education_level,
        grade: semillero ? form.grade : null,
        access_until: form.access_until || null,
      };
      return adminApi.createStudent(body);
    },
    onSuccess: (res) => {
      onIssued({ ...res, username: res.username ?? form.username.trim() });
      setForm(empty);
      qc.invalidateQueries({ queryKey: ["admin-users"] });
      qc.invalidateQueries({ queryKey: ["admin-groups"] });
    },
  });
  const groups = groupsData?.groups ?? [];
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        create.mutate();
      }}
      className="bg-slate-800 border border-slate-700 rounded-xl p-4 space-y-3"
      aria-label={t("adminUsers.createStudentTitle")}
    >
      <div>
        <h3 className="text-sm font-semibold text-slate-200">{t("adminUsers.createStudentTitle")}</h3>
        <p className="text-xs text-slate-500">{t("adminUsers.createStudentHint")}</p>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <input
          required
          value={form.username}
          onChange={set("username")}
          placeholder={t("adminUsers.createStudentUsername")}
          aria-label={t("adminUsers.createStudentUsername")}
          autoComplete="off"
          className={FIELD}
        />
        <input
          required
          value={form.display_name}
          onChange={set("display_name")}
          maxLength={80}
          placeholder={t("adminUsers.createStudentName")}
          aria-label={t("adminUsers.createStudentName")}
          autoComplete="off"
          className={FIELD}
        />
        <select
          required
          value={form.group_id}
          onChange={set("group_id")}
          aria-label={t("adminUsers.createStudentGroup")}
          className={FIELD}
        >
          <option value="">{t("adminUsers.createStudentChooseGroup")}</option>
          {groups.map((g) => (
            <option key={g.id} value={g.id}>
              {g.teacher_name ? `${g.name} · ${g.teacher_name}` : g.name}
            </option>
          ))}
        </select>
        <select
          required
          value={form.education_level}
          onChange={set("education_level")}
          aria-label={t("adminUsers.createStudentLevel")}
          className={FIELD}
        >
          <option value="">{t("adminUsers.createStudentChooseLevel")}</option>
          {LEVELS.map(([value, label]) => (
            <option key={value} value={value}>
              {t(label)}
            </option>
          ))}
        </select>
        {semillero ? (
          <select
            required
            value={form.grade}
            onChange={set("grade")}
            aria-label={t("adminUsers.createStudentGrade")}
            className={FIELD}
          >
            {SEMILLERO_GRADES.map((g) => (
              <option key={g} value={g}>
                {g}.º
              </option>
            ))}
          </select>
        ) : (
          <span className={`${FIELD} text-slate-500`} aria-label={t("adminUsers.createStudentGrade")}>
            {t("adminUsers.createStudentGrade")}: {t("adminUsers.gradeNotApplicable")}
          </span>
        )}
        <label className="text-xs text-slate-400 flex flex-col gap-1">
          {t("adminUsers.createStudentLastDay")}
          <input type="date" value={form.access_until} onChange={set("access_until")} className={FIELD} />
        </label>
      </div>
      <div className="flex items-center gap-3">
        <Button size="sm" type="submit" loading={create.isPending}>
          {t("adminUsers.createStudentSubmit")}
        </Button>
        <span className="text-[11px] text-slate-500">{t("adminUsers.lastDayHint")}</span>
      </div>
      {create.isError && (
        <p role="alert" className="text-xs text-red-400">
          {(create.error as Error).message}
        </p>
      )}
    </form>
  );
}

/** Spec 004 FR-046, FR-050: the last day of access, shown and changed by the admin. */
function LastDayCell({ user, uid }: { user: AdminUser; uid: number }) {
  const { t } = useTranslation();
  const qc = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(user.access_until ?? "");
  const save = useMutation({
    mutationFn: (value: string | null) => adminApi.setAccessUntil(uid, value),
    onSuccess: () => {
      setEditing(false);
      qc.invalidateQueries({ queryKey: ["admin-users"] });
    },
  });
  const editable = user.role === "student" || user.role === "teacher";
  if (editing) {
    return (
      <form
        className="flex gap-1 items-center flex-wrap"
        onSubmit={(e) => {
          e.preventDefault();
          save.mutate(draft || null);
        }}
      >
        <input
          type="date"
          aria-label={t("adminUsers.lastDayLabel")}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          className="bg-slate-900 border border-slate-600 rounded px-2 py-0.5 text-xs text-slate-200 focus:outline-none focus:border-violet-500"
        />
        <Button size="sm" type="submit" loading={save.isPending}>
          {t("adminUsers.saveLastDay")}
        </Button>
        <Button size="sm" variant="secondary" type="button" onClick={() => save.mutate(null)}>
          {t("adminUsers.removeLastDay")}
        </Button>
        <Button size="sm" variant="secondary" type="button" onClick={() => setEditing(false)}>
          {t("adminUsers.cancelLastDay")}
        </Button>
        {save.isError ? (
          <span role="alert" className="block w-full text-[11px] text-red-400">
            {(save.error as Error).message}
          </span>
        ) : null}
      </form>
    );
  }
  return (
    <div className="flex items-center gap-2 flex-wrap">
      <span className="text-sm text-slate-400">
        {user.access_until ? shownDay(user.access_until) : t("adminUsers.noLastDay")}
      </span>
      {user.access_expired ? (
        <span className="text-[11px] px-2 py-0.5 rounded-full bg-red-900/40 text-red-400">
          {t("adminUsers.expired")}
        </span>
      ) : null}
      {editable ? (
        <button
          type="button"
          className="text-[11px] text-violet-300 hover:text-violet-200 underline-offset-2 hover:underline"
          onClick={() => {
            setDraft(user.access_until ?? "");
            setEditing(true);
          }}
        >
          {t("adminUsers.changeLastDay")}
        </button>
      ) : null}
    </div>
  );
}

/** Spec 009 FR-007, FR-017: the student's linked identification, which the admin links
 * explicitly or removes when it was linked by mistake; the username never changes. */
function IdentificationControls({ user, uid }: { user: AdminUser; uid: number }) {
  const { t } = useTranslation();
  const qc = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState("");
  const done = () => qc.invalidateQueries({ queryKey: ["admin-users"] });
  const link = useMutation({
    mutationFn: () => adminApi.linkIdentification(uid, draft.trim()),
    onSuccess: () => {
      setEditing(false);
      setDraft("");
      done();
    },
  });
  const unlink = useMutation({ mutationFn: () => adminApi.unlinkIdentification(uid), onSuccess: done });
  const failure = (link.error ?? unlink.error) as Error | null;
  return (
    <div className="mt-1 space-y-1">
      {user.identification ? (
        <span className="flex items-center gap-2 text-[11px] text-slate-400">
          <span className="font-mono">{t("adminUsers.identification", { value: user.identification })}</span>
          <button
            type="button"
            className="text-red-300 hover:text-red-200 underline-offset-2 hover:underline"
            onClick={() => {
              if (window.confirm(t("adminUsers.unlinkConfirm", { username: user.username }))) {
                unlink.mutate();
              }
            }}
          >
            {t("adminUsers.unlinkIdentification")}
          </button>
        </span>
      ) : editing ? (
        <form
          className="flex gap-1 items-center flex-wrap"
          onSubmit={(e) => {
            e.preventDefault();
            link.mutate();
          }}
        >
          <input
            aria-label={t("adminUsers.identificationLabel")}
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            inputMode="numeric"
            maxLength={40}
            required
            className="bg-slate-900 border border-slate-600 rounded px-2 py-0.5 text-xs font-mono text-slate-200 focus:outline-none focus:border-violet-500"
          />
          <Button size="sm" type="submit" loading={link.isPending}>
            {t("adminUsers.saveIdentification")}
          </Button>
          <Button size="sm" variant="secondary" type="button" onClick={() => setEditing(false)}>
            {t("adminUsers.cancelIdentification")}
          </Button>
        </form>
      ) : (
        <button
          type="button"
          className="text-[11px] text-violet-300 hover:text-violet-200 underline-offset-2 hover:underline"
          onClick={() => setEditing(true)}
        >
          {t("adminUsers.linkIdentification")}
        </button>
      )}
      {failure ? (
        <span role="alert" className="block text-[11px] text-red-400">
          {failure.message}
        </span>
      ) : null}
    </div>
  );
}

/** Spec 009 N25, N26 (a): a group the admin creates for a teacher, for an institution and grade —
 * the groups the import pairs each institution and grade of the file with. */
function CreateGroupForTeacher({ uid }: { uid: number }) {
  const { t } = useTranslation();
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const empty = { name: "", course_id: "", institution: "", grade: "" };
  const [form, setForm] = useState(empty);
  const [created, setCreated] = useState<string | null>(null);
  const { data: coursesData } = useQuery({
    queryKey: ["admin-courses"],
    queryFn: adminApi.courses,
    enabled: open,
  });
  const set = (key: keyof typeof empty) => (e: { target: { value: string } }) =>
    setForm((f) => ({ ...f, [key]: e.target.value }));
  const create = useMutation({
    mutationFn: () =>
      adminApi.createGroupForTeacher(uid, {
        name: form.name,
        course_id: form.course_id || null,
        institution: form.institution.trim() || null,
        grade: form.grade ? Number(form.grade) : null,
      }),
    onSuccess: (res) => {
      setCreated(res.name);
      setForm(empty);
      setOpen(false);
      qc.invalidateQueries({ queryKey: ["admin-groups"] });
    },
  });
  if (!open) {
    return (
      <span className="flex items-center gap-2">
        <Button size="sm" variant="secondary" onClick={() => setOpen(true)}>
          {t("adminUsers.createGroup")}
        </Button>
        {created ? (
          <span role="status" className="text-[11px] text-emerald-300">
            {t("adminUsers.groupCreated", { name: created })}
          </span>
        ) : null}
      </span>
    );
  }
  return (
    <form
      aria-label={t("adminUsers.createGroup")}
      className="flex gap-1 items-center flex-wrap"
      onSubmit={(e) => {
        e.preventDefault();
        create.mutate();
      }}
    >
      <input
        aria-label={t("adminUsers.groupName")}
        placeholder={t("adminUsers.groupName")}
        value={form.name}
        onChange={set("name")}
        maxLength={100}
        required
        className="bg-slate-900 border border-slate-600 rounded px-2 py-0.5 text-xs text-slate-200 focus:outline-none focus:border-violet-500"
      />
      <select
        aria-label={t("adminUsers.groupCourse")}
        value={form.course_id}
        onChange={set("course_id")}
        className="bg-slate-900 border border-slate-600 rounded px-2 py-0.5 text-xs text-slate-200"
      >
        <option value="">{t("adminUsers.groupNoCourse")}</option>
        {(coursesData?.courses ?? []).map((c) => (
          <option key={c.id} value={c.id}>
            {c.name}
          </option>
        ))}
      </select>
      <input
        aria-label={t("adminUsers.groupInstitution")}
        placeholder={t("adminUsers.groupInstitution")}
        value={form.institution}
        onChange={set("institution")}
        maxLength={200}
        className="bg-slate-900 border border-slate-600 rounded px-2 py-0.5 text-xs text-slate-200 focus:outline-none focus:border-violet-500"
      />
      <select
        aria-label={t("adminUsers.groupGrade")}
        value={form.grade}
        onChange={set("grade")}
        className="bg-slate-900 border border-slate-600 rounded px-2 py-0.5 text-xs text-slate-200"
      >
        <option value="">{t("adminUsers.groupNoGrade")}</option>
        {SEMILLERO_GRADES.map((g) => (
          <option key={g} value={g}>
            {g}.º
          </option>
        ))}
      </select>
      <Button size="sm" type="submit" loading={create.isPending}>
        {t("adminUsers.saveGroup")}
      </Button>
      <Button size="sm" variant="secondary" type="button" onClick={() => setOpen(false)}>
        {t("adminUsers.cancelGroup")}
      </Button>
      {create.isError ? (
        <span role="alert" className="block w-full text-[11px] text-red-400">
          {(create.error as Error).message}
        </span>
      ) : null}
    </form>
  );
}

function UserRow({
  user,
  onIssued,
}: {
  user: AdminUser;
  onIssued: (p: TemporaryPassword & { username: string }) => void;
}) {
  const { t } = useTranslation();
  const qc = useQueryClient();

  const isActive = !!user.active;
  const uid = (user.user_id ?? user.id ?? 0) as number;

  const toggleMutation = useMutation({
    mutationFn: () => (isActive ? adminApi.deactivate(uid) : adminApi.reactivate(uid)),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-users"] }),
  });
  // Spec 004 FR-025: the admin corrects a student's display name, under the same filter.
  const [editingName, setEditingName] = useState(false);
  const [nameDraft, setNameDraft] = useState(user.display_name ?? "");
  const nameMutation = useMutation({
    mutationFn: () => adminApi.setDisplayName(uid, nameDraft),
    onSuccess: () => {
      setEditingName(false);
      qc.invalidateQueries({ queryKey: ["admin-users"] });
    },
  });
  const resetMutation = useMutation({
    mutationFn: () => adminApi.resetPassword(uid),
    onSuccess: (res) => {
      onIssued({ ...res, username: user.username });
      qc.invalidateQueries({ queryKey: ["admin-users"] });
    },
  });

  return (
    <tr className="hover:bg-slate-700/30 transition-colors">
      <td className="px-4 py-3">
        <span className="text-slate-100 text-sm font-medium">{user.username}</span>
        {user.role === "student" && !editingName ? (
          <span className="block text-xs text-slate-400">
            {user.display_name || t("adminUsers.noDisplayName")}
          </span>
        ) : null}
        {editingName ? (
          <form
            className="mt-1 flex gap-1 items-center"
            onSubmit={(e) => {
              e.preventDefault();
              nameMutation.mutate();
            }}
          >
            <input
              aria-label={t("adminUsers.nameLabel")}
              value={nameDraft}
              onChange={(e) => setNameDraft(e.target.value)}
              maxLength={80}
              required
              className="bg-slate-900 border border-slate-600 rounded px-2 py-0.5 text-xs text-slate-200 focus:outline-none focus:border-violet-500"
            />
            <Button size="sm" type="submit" loading={nameMutation.isPending}>
              {t("adminUsers.saveName")}
            </Button>
            <Button size="sm" variant="secondary" type="button" onClick={() => setEditingName(false)}>
              {t("adminUsers.cancelName")}
            </Button>
          </form>
        ) : null}
        {nameMutation.isError ? (
          <span role="alert" className="block text-[11px] text-red-400">
            {(nameMutation.error as Error).message}
          </span>
        ) : null}
        {user.must_change_password ? (
          <span className="block text-[11px] text-amber-400">{t("adminUsers.mustChange")}</span>
        ) : null}
        {user.role === "student" ? <IdentificationControls user={user} uid={uid} /> : null}
      </td>
      <td className="px-4 py-3">
        <RoleBadge role={user.role} />
      </td>
      <td className="px-4 py-3 text-sm text-slate-400">
        {user.education_level ?? "—"}
      </td>
      <td className="px-4 py-3 text-sm text-slate-400">
        {user.group_name ?? "—"}
      </td>
      <td className="px-4 py-3">
        <LastDayCell user={user} uid={uid} />
      </td>
      <td className="px-4 py-3">
        <span
          className={`text-xs px-2 py-0.5 rounded-full ${
            isActive ? "bg-green-900/40 text-green-400" : "bg-red-900/40 text-red-400"
          }`}
        >
          {isActive ? t("adminUsers.statusActive") : t("adminUsers.statusInactive")}
        </span>
      </td>
      <td className="px-4 py-3">
        <div className="flex gap-2 flex-wrap">
          <Button
            size="sm"
            variant={isActive ? "danger" : "secondary"}
            loading={toggleMutation.isPending}
            onClick={() => toggleMutation.mutate()}
          >
            {isActive ? t("adminUsers.deactivate") : t("adminUsers.activate")}
          </Button>
          {user.role === "student" || user.role === "teacher" ? (
            <Button
              size="sm"
              variant="secondary"
              loading={resetMutation.isPending}
              onClick={() => {
                if (window.confirm(t("adminUsers.resetConfirm", { username: user.username }))) {
                  resetMutation.mutate();
                }
              }}
            >
              {t("adminUsers.resetPassword")}
            </Button>
          ) : null}
          {user.role === "student" && !editingName ? (
            <Button
              size="sm"
              variant="secondary"
              onClick={() => {
                setNameDraft(user.display_name ?? "");
                setEditingName(true);
              }}
            >
              {t("adminUsers.changeName")}
            </Button>
          ) : null}
          {user.role === "teacher" && user.approved && isActive ? <CreateGroupForTeacher uid={uid} /> : null}
        </div>
      </td>
    </tr>
  );
}

export function AdminUsers() {
  const { t } = useTranslation();
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState<string>("all");
  const [issued, setIssued] = useState<(TemporaryPassword & { username: string }) | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["admin-users"],
    queryFn: adminApi.users,
    staleTime: 30_000,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-400 animate-pulse">{t("adminUsers.loading")}</p>
      </div>
    );
  }

  const users = data?.users ?? [];
  const filtered = users.filter((u) => {
    const needle = search.toLowerCase();
    const matchSearch =
      u.username.toLowerCase().includes(needle) ||
      (u.display_name ?? "").toLowerCase().includes(needle) ||
      (u.identification ?? "").includes(needle);
    const matchRole = roleFilter === "all" || u.role === roleFilter;
    return matchSearch && matchRole;
  });

  return (
    <div className="max-w-5xl mx-auto py-6 px-4 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-slate-100">{t("adminUsers.title")}</h2>
        <span className="text-xs text-slate-500">{t("adminUsers.totalUsers", { count: users.length })}</span>
      </div>

      {/* Docentes pendientes */}
      <PendingTeachersSection />

      {/* Spec 004 E2: contraseña temporal recién emitida y alta de docentes */}
      {issued ? <TemporaryPasswordNotice issued={issued} onClose={() => setIssued(null)} /> : null}
      <CreateStudentSection onIssued={setIssued} />
      <CreateTeacherSection onIssued={setIssued} />

      {/* Filtros */}
      <div className="flex gap-3 flex-wrap">
        <input
          type="text"
          placeholder={t("adminUsers.searchPlaceholder")}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="bg-slate-800 border border-slate-600 rounded-lg px-3 py-1.5 text-sm text-slate-200 focus:outline-none focus:border-violet-500 placeholder-slate-600"
        />
        <select
          value={roleFilter}
          onChange={(e) => setRoleFilter(e.target.value)}
          className="bg-slate-800 border border-slate-600 rounded-lg px-3 py-1.5 text-sm text-slate-200 focus:outline-none focus:border-violet-500"
        >
          <option value="all">{t("adminUsers.allRoles")}</option>
          <option value="student">{t("adminUsers.students")}</option>
          <option value="teacher">{t("adminUsers.teachers")}</option>
          <option value="admin">{t("adminUsers.admins")}</option>
        </select>
      </div>

      {/* Tabla */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-xs text-slate-500 border-b border-slate-700">
                <th className="px-4 py-2 text-left">{t("adminUsers.colUser")}</th>
                <th className="px-4 py-2 text-left">{t("adminUsers.colRole")}</th>
                <th className="px-4 py-2 text-left">{t("adminUsers.colLevel")}</th>
                <th className="px-4 py-2 text-left">{t("adminUsers.colGroup")}</th>
                <th className="px-4 py-2 text-left">{t("adminUsers.colLastDay")}</th>
                <th className="px-4 py-2 text-left">{t("adminUsers.colStatus")}</th>
                <th className="px-4 py-2 text-left">{t("adminUsers.colAction")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center text-slate-500 text-sm py-8">
                    {t("adminUsers.noMatches")}
                  </td>
                </tr>
              ) : (
                filtered.map((u, idx) => (
                  <UserRow key={(u.user_id ?? u.id ?? idx) as number} user={u} onIssued={setIssued} />
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
