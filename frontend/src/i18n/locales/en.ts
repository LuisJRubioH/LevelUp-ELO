import type { TranslationKeys } from "./es";

const en: TranslationKeys = {
  // ── Navigation ───────────────────────────────────────────────────────────────
  nav: {
    practice: "Practice",
    stats: "Statistics",
    courses: "Courses",
    exam: "Exam",
    procedure: "Open Proc.",
    feedback: "Feedback",
    dashboard: "Dashboard",
    groups: "Groups",
    procedures: "Procedures",
    exams: "Exams",
    export: "Export data",
    users: "Users",
    reports: "Reports",
    audit: "Audit",
  },

  // ── Login ────────────────────────────────────────────────────────────────────
  login: {
    title: "Sign in",
    usernameLabel: "Username or email",
    usernamePlaceholder: "username or email@example.com",
    passwordLabel: "Password",
    submit: "Sign in",
    noAccount: "No account?",
    register: "Sign up",
    backToLogin: "← Back to sign in",
    error: {
      invalid: "Invalid credentials.",
    },
    registerStep1: {
      title: "Create account",
      subtitle: "What is your role?",
      student: "I'm a student",
      teacher: "I'm a teacher",
      next: "Next →",
    },
    registerStep2: {
      title: "Account details",
      usernameLabel: "Username",
      usernamePlaceholder: "username123",
      passwordLabel: "Password",
      emailLabel: "Email",
      emailPlaceholder: "email@example.com",
      emailOptional: "optional",
      levelLabel: "Education level",
      levels: {
        colegio: "High school",
        universidad: "University",
        semillero: "Semillero",
      },
      gradeLabel: "Grade",
      submit: "Sign up",
      teacherNote: "Your account requires administrator approval.",
    },
  },

  // ── Layout / Sidebar ─────────────────────────────────────────────────────────
  layout: {
    aiConfig: "AI API",
    provider: "Provider",
    model: "Model",
    modelAuto: "Auto (recommended)",
    apiKey: "API Key",
    keyConfigured: "✓ Key configured",
    addEmail: "Add your email to keep access",
    changeEmail: "Change",
    saveEmail: "Save",
    cancel: "Cancel",
    emailPlaceholder: "email@example.com",
    emailError: "Enter a valid email.",
    session: "session",
    logout: "Sign out →",
    logoutMobile: "Exit →",
    grade: "Grade",
    notifications: "notifications",
    moreThan99: "more than 99",
    moreThan9: "more than 9",
  },

  // ── Practice ─────────────────────────────────────────────────────────────────
  practice: {
    title: "Practice Room",
    subtitle: "Select a course to start.",
    loadingCourses: "Loading courses...",
    noCourses: "You are not enrolled in any course yet.",
    browseCourses: "→ Browse course catalog",
    changeCourse: "← Change course",
    loadingQuestion: "Loading question...",
    sendAnswer: "Submit answer",
    sending: "Submitting answer...",
    nextQuestion: "Next question →",
    ifCorrect: "If correct:",
    ifWrong: "If wrong:",
    noMoreQuestions: "You've completed all available questions for today! Come back tomorrow 🎉",
    errorLoading: "Could not load question. Are you connected?",
    retry: "Retry",
    connectionError: "Could not submit answer (connection error).",
    katiaHelp: "🐱 Need help? Ask KatIA",
    hideChat: "Hide KatIA chat",
    question: "Question",
    topicEloLabel: "ELO in this topic",
    topicEloNote: "The global ELO in the header averages every topic; this only shows this topic's ELO.",
  },

  // ── Statistics ────────────────────────────────────────────────────────────────
  stats: {
    title: "My Statistics",
    globalElo: "Global ELO",
    attempts: "Attempts",
    streak: "Streak",
    days: "days",
    rank: "Rank",
    topicElo: "ELO by topic",
    recentActivity: "Recent activity",
    achievements: "Achievements",
    weeklyRanking: "Weekly ranking",
    loading: "Loading statistics...",
    error: "Could not load statistics.",
    errorHint: "The server may be starting up. Try reloading the page.",
    noAchievements: "Complete exercises to unlock achievements.",
    noRanking: "No ranking data yet for your group.",
  },

  // ── Courses ───────────────────────────────────────────────────────────────────
  courses: {
    title: "Explore courses",
    enrolled: "My enrollments",
    enroll: "Enroll",
    unenroll: "Unenroll",
    loading: "Loading courses...",
    noEnrolled: "You are not in any course yet.",
    enrollByCode: "Join with code",
    codePlaceholder: "Invitation code",
    join: "Join",
  },

  // ── Theme ─────────────────────────────────────────────────────────────────────
  theme: {
    light: "Light mode",
    dark: "Dark mode",
  },

  // ── Language ──────────────────────────────────────────────────────────────────
  lang: {
    toggle: "ES",
    current: "EN",
  },

  // ── General errors ────────────────────────────────────────────────────────────
  error: {
    generic: "Something went wrong.",
    reload: "Reload page",
    goHome: "Go home",
  },
};

export default en;
