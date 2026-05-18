const es = {
  // ── Navegación ──────────────────────────────────────────────────────────────
  nav: {
    practice: "Practicar",
    stats: "Estadísticas",
    courses: "Cursos",
    exam: "Examen",
    procedure: "Proc. abierto",
    feedback: "Retroalimentación",
    dashboard: "Dashboard",
    groups: "Grupos",
    procedures: "Procedimientos",
    exams: "Exámenes",
    export: "Exportar datos",
    users: "Usuarios",
    reports: "Reportes",
    audit: "Auditoría",
  },

  // ── Login ────────────────────────────────────────────────────────────────────
  login: {
    title: "Iniciar sesión",
    usernameLabel: "Usuario o correo electrónico",
    usernamePlaceholder: "usuario o correo@ejemplo.com",
    passwordLabel: "Contraseña",
    submit: "Entrar",
    noAccount: "¿Sin cuenta?",
    register: "Registrarse",
    backToLogin: "← Volver al inicio de sesión",
    error: {
      invalid: "Credenciales inválidas.",
    },
    registerStep1: {
      title: "Crear cuenta",
      subtitle: "¿Cuál es tu rol?",
      student: "Soy estudiante",
      teacher: "Soy docente",
      next: "Siguiente →",
    },
    registerStep2: {
      title: "Datos de acceso",
      usernameLabel: "Nombre de usuario",
      usernamePlaceholder: "usuario123",
      passwordLabel: "Contraseña",
      emailLabel: "Correo electrónico",
      emailPlaceholder: "correo@ejemplo.com",
      emailOptional: "opcional",
      levelLabel: "Nivel educativo",
      levels: {
        colegio: "Colegio",
        universidad: "Universidad",
        semillero: "Semillero",
      },
      gradeLabel: "Grado",
      submit: "Registrarse",
      teacherNote: "Tu cuenta requiere aprobación del administrador.",
    },
  },

  // ── Layout / Sidebar ─────────────────────────────────────────────────────────
  layout: {
    aiConfig: "API de IA",
    provider: "Proveedor",
    model: "Modelo",
    modelAuto: "Auto (recomendado)",
    apiKey: "API Key",
    keyConfigured: "✓ Clave configurada",
    addEmail: "Agrega tu correo para no perder acceso",
    changeEmail: "Cambiar",
    saveEmail: "Guardar",
    cancel: "Cancelar",
    emailPlaceholder: "correo@ejemplo.com",
    emailError: "Ingresa un correo válido.",
    session: "sesión",
    logout: "Cerrar sesión →",
    logoutMobile: "Salir →",
    grade: "Grado",
    notifications: "notificaciones",
    moreThan99: "más de 99",
    moreThan9: "más de 9",
  },

  // ── Práctica ─────────────────────────────────────────────────────────────────
  practice: {
    title: "Sala de Práctica",
    subtitle: "Selecciona un curso para empezar.",
    loadingCourses: "Cargando cursos...",
    noCourses: "No estás matriculado en ningún curso aún.",
    browseCourses: "→ Ver catálogo de cursos",
    changeCourse: "← Cambiar curso",
    loadingQuestion: "Cargando pregunta...",
    sendAnswer: "Enviar respuesta",
    sending: "Enviando respuesta...",
    nextQuestion: "Siguiente pregunta →",
    ifCorrect: "Si aciertas:",
    ifWrong: "Si fallas:",
    noMoreQuestions: "¡Has completado todas las preguntas disponibles hoy! Vuelve mañana 🎉",
    errorLoading: "No se pudo cargar la pregunta. ¿Tienes conexión?",
    retry: "Reintentar",
    connectionError: "No se pudo registrar la respuesta (error de conexión).",
    katiaHelp: "🐱 ¿Necesitas ayuda? Pregúntale a KatIA",
    hideChat: "Ocultar chat KatIA",
    question: "Pregunta",
  },

  // ── Estadísticas ──────────────────────────────────────────────────────────────
  stats: {
    title: "Mis Estadísticas",
    globalElo: "ELO Global",
    attempts: "Intentos",
    streak: "Racha",
    days: "días",
    rank: "Rango",
    topicElo: "ELO por tema",
    recentActivity: "Actividad reciente",
    achievements: "Logros",
    weeklyRanking: "Ranking semanal",
    loading: "Cargando estadísticas...",
    error: "No se pudieron cargar las estadísticas.",
    errorHint: "El servidor puede estar iniciando. Intenta recargar la página.",
    noAchievements: "Completa ejercicios para desbloquear logros.",
    noRanking: "Aún no hay datos de ranking para tu grupo.",
  },

  // ── Cursos ───────────────────────────────────────────────────────────────────
  courses: {
    title: "Explorar cursos",
    enrolled: "Mis matrículas",
    enroll: "Matricularse",
    unenroll: "Darse de baja",
    loading: "Cargando cursos...",
    noEnrolled: "Aún no estás en ningún curso.",
    enrollByCode: "Acceder con código",
    codePlaceholder: "Código de invitación",
    join: "Unirse",
  },

  // ── Modo tema ────────────────────────────────────────────────────────────────
  theme: {
    light: "Modo claro",
    dark: "Modo oscuro",
  },

  // ── Idioma ───────────────────────────────────────────────────────────────────
  lang: {
    toggle: "EN",
    current: "ES",
  },

  // ── Errores generales ─────────────────────────────────────────────────────────
  error: {
    generic: "Algo salió mal.",
    reload: "Recargar página",
    goHome: "Ir al inicio",
  },
} as const;

export default es;

type DeepString<T> = { [K in keyof T]: T[K] extends object ? DeepString<T[K]> : string };
export type TranslationKeys = DeepString<typeof es>;
