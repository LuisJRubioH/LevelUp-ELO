/**
 * pages/Home.tsx
 * ==============
 * Landing pública (rediseño). Portada del prototipo de diseño
 * (docs/redesign/source/LevelUp-ELO.html + landing.css + landing.js).
 *
 * - Estilos en Home.css, scopeados bajo .lue-home para no filtrar al resto
 *   de la app (Tailwind v4 + paleta slate). Tema claro vía html.light.
 * - La interactividad de landing.js (toggle idioma, nav scrolled, menú móvil,
 *   reveal on scroll, FAQ, demo ELO, mini-bars docente, chat KatIA) está
 *   reimplementada con estado/efectos de React.
 * - i18n local ES/EN persistido en la misma clave "levelup-lang" que usa la
 *   app; los CTAs apuntan a /login (ruta interna) en vez de la URL de Vercel.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { rankColor } from "../components/ELO/rankColors";
import "./Home.css";

const KATIA_GIF = "/katia/correcto_compressed.gif";

type Lang = "es" | "en";
type Bi = { es: string; en: string };

const LS_LANG = "levelup-lang";

const NAV_LINKS: { href: string; t: Bi }[] = [
  { href: "#features", t: { es: "Funciones", en: "Features" } },
  { href: "#engine", t: { es: "Cómo funciona", en: "How it works" } },
  { href: "#katia", t: { es: "KatIA", en: "KatIA" } },
  { href: "#teachers", t: { es: "Docentes", en: "Teachers" } },
  { href: "#about", t: { es: "Nosotros", en: "About" } },
  { href: "#faq", t: { es: "FAQ", en: "FAQ" } },
];

/** English names of the rank labels. The scale itself — labels and thresholds — is the API's
 *  (GET /api/meta/ranks, spec 001); the demo ladder shows its rungs from Plata I to Maestro. */
const RANK_EN: Record<string, string> = {
  Aspirante: "Aspirant", Hierro: "Iron", "Bronce II": "Bronze II", "Bronce I": "Bronze I",
  "Plata II": "Silver II", "Plata I": "Silver I", "Oro II": "Gold II", "Oro I": "Gold I",
  "Platino II": "Platinum II", "Platino I": "Platinum I", "Diamante II": "Diamond II",
  "Diamante I": "Diamond I", Maestro: "Master", "Gran Maestro": "Grandmaster",
  Leyenda: "Legend", "Leyenda Suprema": "Supreme Legend",
};
type Rung = { es: string; en: string; min: number; c: string };
const LADDER_MIN = 1000; // Plata I
const LADDER_MAX = 1800; // Maestro
const START = 1180;

const FAQS: { q: Bi; a: Bi }[] = [
  {
    q: { es: "¿Qué es el ELO y por qué usarlo para matemáticas?", en: "What is ELO and why use it for math?" },
    a: {
      es: "El ELO es el sistema de rating del ajedrez: un número que mide tu nivel. Aquí, cada respuesta actualiza tu ELO y el de la pregunta, así la plataforma siempre te ofrece un reto a tu medida — ni muy fácil, ni imposible.",
      en: "ELO is the chess rating system: a number that measures your level. Here, every answer updates your ELO and the question's, so the platform always offers a challenge that fits you — never too easy, never impossible.",
    },
  },
  {
    q: { es: "¿Quién es KatIA?", en: "Who is KatIA?" },
    a: {
      es: "KatIA es tu tutora con inteligencia artificial. Usa el método socrático: en lugar de darte la respuesta, te hace preguntas para que la descubras tú. También revisa tus procedimientos escritos a mano paso a paso.",
      en: "KatIA is your AI tutor. She uses the socratic method: instead of giving you the answer, she asks questions so you discover it yourself. She also reviews your handwritten work step by step.",
    },
  },
  {
    q: { es: "¿Cómo se calcula mi rango?", en: "How is my rank calculated?" },
    a: {
      es: "Tu rango depende de tu ELO. Hay 16 niveles, de Aspirante a Leyenda Suprema. A medida que aciertas preguntas más difíciles, tu ELO sube y desbloqueas nuevos rangos por materia.",
      en: "Your rank depends on your ELO. There are 16 levels, from Aspirant to Supreme Legend. As you solve harder questions, your ELO rises and you unlock new ranks per subject.",
    },
  },
  {
    q: { es: "¿Qué materias puedo practicar?", en: "Which subjects can I practice?" },
    a: {
      es: "Desde colegio (álgebra, aritmética, geometría, trigonometría) hasta universidad (cálculo, álgebra lineal, ecuaciones diferenciales, probabilidad), además de semilleros y preparación para concursos.",
      en: "From school (algebra, arithmetic, geometry, trigonometry) to university (calculus, linear algebra, differential equations, probability), plus talent programs and contest prep.",
    },
  },
  {
    q: { es: "¿Funciona en el celular?", en: "Does it work on mobile?" },
    a: {
      es: "Sí. Oulad está pensado para usarse desde el navegador en computador o celular, y puedes cambiar entre español e inglés en cualquier momento sin recargar la página.",
      en: "Yes. Oulad is built to be used from the browser on desktop or mobile, and you can switch between Spanish and English at any time without reloading the page.",
    },
  },
  {
    q: { es: "Soy docente, ¿cómo empiezo?", en: "I'm a teacher — how do I start?" },
    a: {
      es: "Solicita acceso docente y tendrás un panel para crear grupos, asignar exámenes con ventana de tiempo, revisar procedimientos y exportar calificaciones en CSV o XLSX.",
      en: "Request teacher access and you'll get a dashboard to create groups, assign timed exams, review student work and export grades to CSV or XLSX.",
    },
  },
  {
    q: { es: "¿Mis datos están seguros?", en: "Is my data safe?" },
    a: {
      es: "Sí. Las contraseñas se protegen con Argon2id, un estándar moderno de cifrado, y los procedimientos se almacenan de forma privada.",
      en: "Yes. Passwords are protected with Argon2id, a modern hashing standard, and your submitted work is stored privately.",
    },
  },
];

const CHAT_GREETING: Bi = {
  es: "¡Hola! Soy KatIA 🐱 ¿En qué te trabas hoy?",
  en: "Hi! I'm KatIA 🐱 What are you stuck on today?",
};
const CHAT_PROMPTS: { q: Bi; a: Bi }[] = [
  {
    q: { es: "No sé resolver x² − 5x + 6 = 0", en: "I can't solve x² − 5x + 6 = 0" },
    a: {
      es: "Antes de la fórmula… ¿qué <b>dos números</b> multiplicados dan 6 y sumados dan 5? 🤔",
      en: "Before the formula… what <b>two numbers</b> multiply to 6 and add up to 5? 🤔",
    },
  },
  {
    q: { es: "¿Cuál es la derivada de x³?", en: "What's the derivative of x³?" },
    a: {
      es: "Piensa en la regla de la potencia. ¿Qué le pasa al <b>exponente</b> cuando derivas xⁿ? 💡",
      en: "Think of the power rule. What happens to the <b>exponent</b> when you differentiate xⁿ? 💡",
    },
  },
  {
    q: { es: "Me equivoqué otra vez 😞", en: "I got it wrong again 😞" },
    a: {
      es: "Equivocarse es parte de subir de ELO. ¿Me muestras tu procedimiento y lo revisamos paso a paso? 💪",
      en: "Mistakes are part of climbing ELO. Show me your steps and we'll review them together? 💪",
    },
  },
];

const BAR_H = [62, 84, 48, 72, 92];

function fmt(n: number): string {
  return Math.round(n).toLocaleString("es-CO");
}

type ChatMsg = { who: "user" | "bot"; html: string };

export function Home() {
  const [lang, setLang] = useState<Lang>(
    () => ((localStorage.getItem(LS_LANG) as Lang) || "es")
  );
  const t = useCallback((b: Bi) => (lang === "es" ? b.es : b.en), [lang]);

  const switchLang = (l: Lang) => {
    setLang(l);
    localStorage.setItem(LS_LANG, l);
    document.documentElement.lang = l;
  };

  // ── nav scrolled + menú móvil ──────────────────────────────────────────
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // ── reveal on scroll + hero XP + mini-bars docente ─────────────────────
  const rootRef = useRef<HTMLDivElement>(null);
  const [heroXp, setHeroXp] = useState(false);
  const [miniOn, setMiniOn] = useState(false);
  useEffect(() => {
    const root = rootRef.current;
    if (!root) return;
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add("in");
            io.unobserve(e.target);
            if (e.target.id === "eloDemo") setHeroXp(true);
            if (e.target.classList.contains("teach")) setMiniOn(true);
          }
        });
      },
      { threshold: 0.15 }
    );
    root.querySelectorAll(".reveal").forEach((el) => io.observe(el));
    const timer = window.setTimeout(() => setHeroXp(true), 600);
    return () => {
      io.disconnect();
      window.clearTimeout(timer);
    };
  }, []);

  // ── FAQ ────────────────────────────────────────────────────────────────
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  // ── demo ELO ─────────────────────────────────────────────────────────────
  const [rungs, setRungs] = useState<Rung[]>([]);
  useEffect(() => {
    api
      .get<{ label: string; min: number }[]>("/api/meta/ranks")
      .then((ranks) =>
        setRungs(
          ranks
            .filter((r) => r.min >= LADDER_MIN && r.min <= LADDER_MAX)
            .map((r) => ({ es: r.label, en: RANK_EN[r.label] ?? r.label, min: r.min, c: rankColor(r.label) }))
        )
      )
      .catch(() => setRungs([]));
  }, []);
  const rankIndex = (e: number) => {
    let idx = 0;
    for (let i = 0; i < rungs.length; i++) if (e >= rungs[i].min) idx = i;
    return idx;
  };
  const [elo, setElo] = useState(START);
  const [displayElo, setDisplayElo] = useState(START);
  const [delta, setDelta] = useState<number | null>(null);
  const rafRef = useRef<number | null>(null);
  const deltaTimer = useRef<number | null>(null);

  useEffect(() => {
    // anima displayElo hacia elo
    const from = displayElo;
    const target = elo;
    if (from === target) return;
    const dur = 600;
    const t0 = performance.now();
    const step = (now: number) => {
      const k = Math.min(1, (now - t0) / dur);
      const val = from + (target - from) * (1 - Math.pow(1 - k, 3));
      setDisplayElo(val);
      if (k < 1) rafRef.current = requestAnimationFrame(step);
    };
    rafRef.current = requestAnimationFrame(step);
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [elo]);

  useEffect(
    () => () => {
      if (deltaTimer.current) window.clearTimeout(deltaTimer.current);
    },
    []
  );

  const answerCorrectly = () => {
    const max = rungs.length ? rungs[rungs.length - 1].min : START;
    if (elo >= max) return;
    const gain = 18 + Math.floor(Math.random() * 17);
    setElo((prev) => Math.min(max, prev + gain));
    setDelta(gain);
    if (deltaTimer.current) window.clearTimeout(deltaTimer.current);
    deltaTimer.current = window.setTimeout(() => setDelta(null), 1400);
  };
  const resetDemo = () => {
    setElo(START);
    setDelta(null);
  };

  const placeholder: Rung = { es: "", en: "", min: START, c: "#94a3b8" };
  const curIdx = rankIndex(elo);
  const cur = rungs[curIdx] ?? placeholder;
  const next = rungs[Math.min(curIdx + 1, rungs.length - 1)] ?? placeholder;
  const span = Math.max(1, next.min - cur.min);
  const pct = curIdx >= rungs.length - 1 ? 100 : Math.min(100, ((elo - cur.min) / span) * 100);

  // ── chat KatIA ───────────────────────────────────────────────────────────
  const [chatMsgs, setChatMsgs] = useState<ChatMsg[]>([]);
  const [usedPrompts, setUsedPrompts] = useState<Set<number>>(new Set());
  const [typing, setTyping] = useState(false);
  const chatBodyRef = useRef<HTMLDivElement>(null);
  const chatTimer = useRef<number | null>(null);

  // reinicia el chat al cambiar de idioma (como el landing original)
  useEffect(() => {
    setChatMsgs([{ who: "bot", html: t(CHAT_GREETING) }]);
    setUsedPrompts(new Set());
    setTyping(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lang]);

  useEffect(() => {
    const el = chatBodyRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [chatMsgs, typing]);

  useEffect(
    () => () => {
      if (chatTimer.current) window.clearTimeout(chatTimer.current);
    },
    []
  );

  const sendPrompt = (i: number) => {
    if (usedPrompts.has(i)) return;
    const p = CHAT_PROMPTS[i];
    setUsedPrompts((prev) => new Set(prev).add(i));
    setChatMsgs((prev) => [...prev, { who: "user", html: t(p.q) }]);
    setTyping(true);
    if (chatTimer.current) window.clearTimeout(chatTimer.current);
    chatTimer.current = window.setTimeout(() => {
      setTyping(false);
      setChatMsgs((prev) => [...prev, { who: "bot", html: t(p.a) }]);
    }, 950);
  };

  return (
    <div className="lue-home" ref={rootRef}>
      {/* ===================== NAV ===================== */}
      <header className={`nav${scrolled ? " scrolled" : ""}`}>
        <div className="container nav-inner">
          <a href="#top" aria-label="Oulad">
            <img className="nav-logo nav-logo-dark" src="/oulad-logo-dark.png" alt="Oulad" />
            <img className="nav-logo nav-logo-light" src="/oulad-logo-light.png" alt="Oulad" />
          </a>
          <nav>
            <ul className="nav-links">
              {NAV_LINKS.map((l) => (
                <li key={l.href}>
                  <a href={l.href}>{t(l.t)}</a>
                </li>
              ))}
            </ul>
          </nav>
          <div className="nav-actions">
            <div className="lang" role="group" aria-label="Idioma">
              <button className={lang === "es" ? "on" : ""} onClick={() => switchLang("es")}>
                ES
              </button>
              <button className={lang === "en" ? "on" : ""} onClick={() => switchLang("en")}>
                EN
              </button>
            </div>
            <Link className="nav-login" to="/login">
              {t({ es: "Iniciar sesión", en: "Log in" })}
            </Link>
            <Link className="btn btn-primary" to="/login">
              {t({ es: "Empezar gratis", en: "Start free" })}
            </Link>
            <button
              className="nav-burger"
              aria-label="Menú"
              aria-expanded={menuOpen}
              onClick={() => setMenuOpen((o) => !o)}
            >
              ☰
            </button>
          </div>
        </div>
      </header>
      <nav className={`mobile-menu${menuOpen ? " open" : ""}`}>
        {NAV_LINKS.map((l) => (
          <a key={l.href} href={l.href} onClick={() => setMenuOpen(false)}>
            {t(l.t)}
          </a>
        ))}
        <Link to="/login" onClick={() => setMenuOpen(false)}>
          {t({ es: "Iniciar sesión →", en: "Log in →" })}
        </Link>
      </nav>

      {/* ===================== HERO ===================== */}
      <section className="hero" id="top">
        <div className="hero-bg">
          <span className="glow a" />
          <span className="glow b" />
        </div>
        <div className="container hero-grid">
          <div className="hero-copy">
            <span className="eyebrow">
              <span className="dot" />
              <span>{t({ es: "Aprendizaje adaptativo con ELO", en: "Adaptive learning powered by ELO" })}</span>
            </span>
            <h1 className="hero-h1">
              {lang === "es" ? (
                <>
                  Las matemáticas tienen rango. <span className="em">Sube el tuyo.</span>
                </>
              ) : (
                <>
                  Math has a rank. <span className="em">Climb yours.</span>
                </>
              )}
            </h1>
            <p className="hero-sub">
              {t({
                es: "Oulad mide tu nivel en tiempo real y te sirve siempre el reto perfecto — ni tan fácil que aburra, ni tan difícil que frustre. Con KatIA, tu tutora socrática, guiándote en cada jugada.",
                en: "Oulad measures your level in real time and always serves the perfect challenge — never too easy, never too hard. With KatIA, your socratic tutor, guiding every move.",
              })}
            </p>
            <div className="hero-cta">
              <Link className="btn btn-primary btn-lg" to="/login">
                {t({ es: "Crear mi cuenta", en: "Create my account" })}
              </Link>
              <a className="btn btn-ghost btn-lg" href="#engine">
                {t({ es: "Ver cómo funciona", en: "See how it works" })}
              </a>
            </div>
            <div className="hero-stats">
              <div className="hero-stat">
                <div className="n">
                  <span className="a">+1.900</span>
                </div>
                <div className="l">{t({ es: "preguntas calibradas", en: "calibrated questions" })}</div>
              </div>
              <div className="hero-stat">
                <div className="n">16</div>
                <div className="l">{t({ es: "rangos por escalar", en: "ranks to climb" })}</div>
              </div>
              <div className="hero-stat">
                <div className="n">10+</div>
                <div className="l">{t({ es: "materias", en: "subjects" })}</div>
              </div>
            </div>
          </div>

          <div className="hero-visual">
            <div className="float-chip chip-elo">
              <div className="ico">♛</div>
              <div>
                <div className="ck">ELO</div>
                <div className="cv">1.847</div>
              </div>
            </div>
            <div className="float-chip chip-rank">
              <div className="ico">▲</div>
              <div>
                <div className="ck">{t({ es: "RANGO", en: "RANK" })}</div>
                <div className="cv">Diamante I</div>
              </div>
            </div>
            <div className="charframe">
              <div className="hud">
                <span className="fdot" style={{ background: "#ff5f57" }} />
                <span className="fdot" style={{ background: "#febc2e" }} />
                <span className="fdot" style={{ background: "#28c840" }} />
                <span className="lbl">KATIA.EXE</span>
              </div>
              <img src={KATIA_GIF} alt="KatIA, tutora socrática pixel-art" />
              <div className="nameplate">
                <div className="who">
                  KatIA<small>{t({ es: "Tutora socrática", en: "Socratic tutor" })}</small>
                </div>
                <div className="hpbar">
                  <div className="t">XP 72%</div>
                  <div className="bar">
                    <i style={{ width: heroXp ? "72%" : "0%" }} />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===================== MARQUEE ===================== */}
      <div className="marquee" aria-hidden="true">
        <div className="marquee-track">
          <span>
            ÁLGEBRA · CÁLCULO · GEOMETRÍA · TRIGONOMETRÍA · PROBABILIDAD · ARITMÉTICA · LÓGICA ·
            COMBINATORIA · ÁLGEBRA LINEAL ·{" "}
          </span>
          <span>
            ÁLGEBRA · CÁLCULO · GEOMETRÍA · TRIGONOMETRÍA · PROBABILIDAD · ARITMÉTICA · LÓGICA ·
            COMBINATORIA · ÁLGEBRA LINEAL ·{" "}
          </span>
        </div>
      </div>

      {/* ===================== FEATURES ===================== */}
      <section className="section" id="features">
        <div className="container">
          <div className="section-head reveal">
            <span className="kicker">{t({ es: "Funciones", en: "Features" })}</span>
            <h2 className="section-title">
              {lang === "es" ? (
                <>
                  Todo lo que necesitas para <span className="em">avanzar de verdad.</span>
                </>
              ) : (
                <>
                  Everything you need to <span className="em">truly progress.</span>
                </>
              )}
            </h2>
            <p className="section-sub">
              {t({
                es: "Un motor de rating que se adapta a ti, una tutora con IA que te guía sin darte la respuesta, y una plataforma completa pensada para el aula.",
                en: "A rating engine that adapts to you, an AI tutor that guides you without handing over the answer, and a full platform built for the classroom.",
              })}
            </p>
          </div>
          <div className="feat-grid">
            <div className="card feat t1 reveal">
              <div className="ficon">♟</div>
              <h3>{t({ es: "Motor ELO adaptativo", en: "Adaptive ELO engine" })}</h3>
              <p>
                {t({
                  es: "El mismo rating del ajedrez, por tópico. Cada respuesta recalibra tu nivel y el de la pregunta.",
                  en: "The same rating used in chess, per topic. Every answer recalibrates your level and the question's.",
                })}
              </p>
              <ul>
                <li><span>{t({ es: "ELO vectorial por materia", en: "Vector ELO per subject" })}</span></li>
                <li><span>{t({ es: "Factor K dinámico según tu experiencia", en: "Dynamic K-factor based on your experience" })}</span></li>
                <li><span>{t({ es: "Selección por Zona de Desarrollo Próximo", en: "Zone of Proximal Development selection" })}</span></li>
              </ul>
            </div>
            <div className="card feat t2 reveal">
              <div className="ficon">🐱</div>
              <h3>{t({ es: "KatIA, tutora con IA", en: "KatIA, AI tutor" })}</h3>
              <p>
                {t({
                  es: "Una tutora socrática que te hace la pregunta correcta y revisa tus procedimientos paso a paso.",
                  en: "A socratic tutor that asks you the right question and reviews your handwritten work step by step.",
                })}
              </p>
              <ul>
                <li><span>{t({ es: "Chat socrático que no revela la solución", en: "Socratic chat that never reveals the solution" })}</span></li>
                <li><span>{t({ es: "Revisión de procedimientos manuscritos", en: "Handwritten procedure review" })}</span></li>
                <li><span>{t({ es: "Mensajes según tu racha y tu rango", en: "Messages based on your streak and rank" })}</span></li>
              </ul>
            </div>
            <div className="card feat t3 reveal">
              <div className="ficon">🏆</div>
              <h3>{t({ es: "Progresión gamificada", en: "Gamified progression" })}</h3>
              <p>
                {t({
                  es: "16 rangos por escalar, de Aspirante a Leyenda Suprema. Rachas, logros y ranking del grupo.",
                  en: "16 ranks to climb, from Aspirant to Supreme Legend. Streaks, achievements and group ranking.",
                })}
              </p>
              <ul>
                <li><span>{t({ es: "Insignias de rango por materia", en: "Rank badges per subject" })}</span></li>
                <li><span>{t({ es: "Rachas diarias y logros animados", en: "Daily streaks and animated achievements" })}</span></li>
                <li><span>{t({ es: "Ranking de tu grupo en tiempo real", en: "Real-time group leaderboard" })}</span></li>
              </ul>
            </div>

            <div className="card feat feat-wide t4 reveal">
              <div>
                <div className="ficon">🛡️</div>
                <h3 style={{ marginTop: 15 }}>
                  {t({ es: "Una plataforma completa, segura y bilingüe", en: "A complete, secure, bilingual platform" })}
                </h3>
                <p style={{ marginTop: 10, maxWidth: "46ch" }}>
                  {t({
                    es: "Tres roles, dashboard docente, exámenes asignables y exportación de datos. Funciona en el celular y cambia entre español e inglés sin recargar.",
                    en: "Three roles, a teacher dashboard, assignable exams and data export. Works on mobile and switches between Spanish and English without reloading.",
                  })}
                </p>
              </div>
              <ul style={{ alignSelf: "center" }}>
                <li><span>{t({ es: "Estudiante, docente y administrador", en: "Student, teacher and admin" })}</span></li>
                <li><span>{t({ es: "Contraseñas protegidas con Argon2id", en: "Passwords protected with Argon2id" })}</span></li>
                <li><span>{t({ es: "Mobile-ready y bilingüe ES / EN", en: "Mobile-ready and bilingual ES / EN" })}</span></li>
                <li><span>{t({ es: "Materias de colegio, universidad y concursos", en: "School, university and contest subjects" })}</span></li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* ===================== ELO DEMO ===================== */}
      <section className="section" id="engine" style={{ paddingTop: 0 }}>
        <div className="container">
          <div className="section-head center reveal">
            <span className="kicker" style={{ justifyContent: "center" }}>
              {t({ es: "El motor en acción", en: "The engine in action" })}
            </span>
            <h2 className="section-title">
              {lang === "es" ? (
                <>
                  Responde. Recalibra. <span className="em">Sube de nivel.</span>
                </>
              ) : (
                <>
                  Answer. Recalibrate. <span className="em">Level up.</span>
                </>
              )}
            </h2>
            <p className="section-sub">
              {t({
                es: "Mira cómo tu ELO sube con cada acierto y te acerca al siguiente rango. Así se siente progresar en Oulad.",
                en: "Watch your ELO rise with every correct answer and bring the next rank closer. This is what progress feels like in Oulad.",
              })}
            </p>
          </div>

          <div className="demo-wrap reveal" id="eloDemo">
            <span className="glow a" style={{ top: -120, left: -80 }} />
            <div className="demo-left">
              <div className="pixel" style={{ fontSize: 9, color: "var(--mute)", marginBottom: 14 }}>
                {t({ es: "TU ELO ACTUAL", en: "YOUR CURRENT ELO" })}
              </div>
              <div className="demo-elo">{fmt(displayElo)}</div>
              <div className="demo-rank">
                <span style={{ color: cur.c }}>{t(cur)}</span>
                <span className={`delta${delta !== null ? " show" : ""}`}>
                  {delta !== null ? `+${delta}` : ""}
                </span>
              </div>
              <div className="demo-bar">
                <i style={{ width: `${pct}%`, background: `linear-gradient(90deg, ${cur.c}, ${next.c})` }} />
              </div>
              <div className="demo-meta">
                <span>{t(cur)}</span>
                <span>{t(next)}</span>
              </div>
              <div className="demo-cta">
                <button className="btn btn-primary" onClick={answerCorrectly}>
                  {t({ es: "Responder bien ✓", en: "Answer correctly ✓" })}
                </button>
                <button className="demo-replay" onClick={resetDemo}>
                  {t({ es: "Reiniciar", en: "Reset" })}
                </button>
              </div>
            </div>
            <div className="ladder">
              {rungs.slice()
                .reverse()
                .map((r) => {
                  const reached = elo >= r.min;
                  const isCurrent = r.min === cur.min;
                  return (
                    <div
                      key={r.min}
                      className={`rung${reached ? " reached" : ""}${isCurrent ? " current" : ""}`}
                      style={{ "--rc": r.c } as React.CSSProperties}
                    >
                      <span className="ri">▲</span>
                      <span className="rn">{t(r)}</span>
                      <span className="rv">ELO {r.min}+</span>
                    </div>
                  );
                })}
            </div>
          </div>
        </div>
      </section>

      {/* ===================== KATIA ===================== */}
      <section className="section" id="katia">
        <div className="container">
          <div className="section-head reveal">
            <span className="kicker">{t({ es: "Conoce a KatIA", en: "Meet KatIA" })}</span>
            <h2 className="section-title">
              {lang === "es" ? (
                <>
                  No te da la respuesta. <span className="em">Te enseña a encontrarla.</span>
                </>
              ) : (
                <>
                  She won't give you the answer. <span className="em">She teaches you to find it.</span>
                </>
              )}
            </h2>
          </div>
          <div className="katia-wrap">
            <div className="reveal">
              <div className="katia-art">
                <img src={KATIA_GIF} alt="KatIA escribiendo con pluma sobre un pergamino" />
                <div className="scan" />
              </div>
              <div className="katia-points">
                <div className="kpt">
                  <div className="ki">💬</div>
                  <div>
                    <h4>{t({ es: "Método socrático", en: "Socratic method" })}</h4>
                    <p>
                      {t({
                        es: "Te guía con preguntas hasta que la solución surge de ti. Nunca la regala.",
                        en: "She guides you with questions until the solution comes from you. Never hands it over.",
                      })}
                    </p>
                  </div>
                </div>
                <div className="kpt">
                  <div className="ki">✍️</div>
                  <div>
                    <h4>{t({ es: "Revisa tu procedimiento", en: "Reviews your work" })}</h4>
                    <p>
                      {t({
                        es: "Sube una foto de tu desarrollo a mano y KatIA lo analiza paso a paso.",
                        en: "Upload a photo of your handwritten work and KatIA analyses it step by step.",
                      })}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="chat reveal">
              <div className="chat-top">
                <div className="av">
                  <img src={KATIA_GIF} alt="KatIA" />
                </div>
                <div>
                  <div className="nm">KatIA</div>
                  <div className="st">{t({ es: "en línea", en: "online" })}</div>
                </div>
              </div>
              <div className="chat-body" ref={chatBodyRef}>
                {chatMsgs.map((m, i) => (
                  <div
                    key={i}
                    className={`msg ${m.who}`}
                    dangerouslySetInnerHTML={{ __html: m.html }}
                  />
                ))}
                {typing && (
                  <div className="msg bot">
                    <span className="typing">
                      <i />
                      <i />
                      <i />
                    </span>
                  </div>
                )}
              </div>
              <div className="chat-input">
                {CHAT_PROMPTS.map((p, i) => (
                  <button
                    key={i}
                    className="chip-prompt"
                    disabled={usedPrompts.has(i)}
                    onClick={() => sendPrompt(i)}
                  >
                    {t(p.q)}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===================== TEACHERS ===================== */}
      <section className="section" id="teachers">
        <div className="container">
          <div className="teach reveal">
            <span className="glow b" style={{ top: -100, right: -80, opacity: 0.4 }} />
            <div style={{ position: "relative", zIndex: 1 }}>
              <span className="kicker">{t({ es: "Para docentes", en: "For teachers" })}</span>
              <h2 className="section-title" style={{ fontSize: "clamp(28px,3.6vw,40px)", margin: "16px 0 14px" }}>
                {lang === "es" ? (
                  <>
                    Ve el progreso real de cada estudiante, <span className="em">tópico por tópico.</span>
                  </>
                ) : (
                  <>
                    See each student's real progress, <span className="em">topic by topic.</span>
                  </>
                )}
              </h2>
              <p className="section-sub">
                {t({
                  es: "Un panel pensado para el aula: identifica fortalezas y debilidades, revisa procedimientos y exporta calificaciones en un clic.",
                  en: "A dashboard built for the classroom: spot strengths and weaknesses, review work, and export grades in one click.",
                })}
              </p>
              <div className="teach-list">
                <div className="tfeat">
                  <span className="ti">📈</span>
                  <div>
                    <h4>{t({ es: "ELO temporal por alumno", en: "ELO over time per student" })}</h4>
                    <p>{t({ es: "Evolución y radar por tópico.", en: "Trend and per-topic radar." })}</p>
                  </div>
                </div>
                <div className="tfeat">
                  <span className="ti">🧠</span>
                  <div>
                    <h4>{t({ es: "Análisis pedagógico con IA", en: "AI pedagogical analysis" })}</h4>
                    <p>{t({ es: "Resúmenes y recomendaciones.", en: "Summaries and recommendations." })}</p>
                  </div>
                </div>
                <div className="tfeat">
                  <span className="ti">📝</span>
                  <div>
                    <h4>{t({ es: "Exámenes asignables", en: "Assignable exams" })}</h4>
                    <p>{t({ es: "Por grupo y ventana de tiempo.", en: "By group and time window." })}</p>
                  </div>
                </div>
                <div className="tfeat">
                  <span className="ti">📤</span>
                  <div>
                    <h4>{t({ es: "Exportación CSV / XLSX", en: "CSV / XLSX export" })}</h4>
                    <p>{t({ es: "Calificaciones listas para tu registro.", en: "Grades ready for your records." })}</p>
                  </div>
                </div>
              </div>
              <Link className="btn btn-primary" to="/login">
                {t({ es: "Solicitar acceso docente", en: "Request teacher access" })}
              </Link>
            </div>
            <div className="teach-visual" style={{ position: "relative", zIndex: 1 }}>
              <div className="tv-head">
                <span className="pixel">{t({ es: "ELO POR TÓPICO", en: "ELO BY TOPIC" })}</span>
                <span className="pixel" style={{ color: "var(--accent-2)" }}>
                  9° A
                </span>
              </div>
              <div className="mini-bars">
                {BAR_H.map((h, i) => (
                  <div
                    key={i}
                    className="mb"
                    style={{ height: miniOn ? `${h}%` : "0%", transitionDelay: `${i * 90}ms` }}
                  />
                ))}
              </div>
              <div className="mini-row">
                <span>{t({ es: "Álgebra", en: "Algebra" })}</span>
                <span>{t({ es: "Geometría", en: "Geometry" })}</span>
                <span>{t({ es: "Aritmética", en: "Arithmetic" })}</span>
                <span>{t({ es: "Lógica", en: "Logic" })}</span>
                <span>{t({ es: "Prob.", en: "Prob." })}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===================== ABOUT ===================== */}
      <section className="section" id="about">
        <div className="container about-grid">
          <div className="reveal">
            <span className="kicker">{t({ es: "Nosotros", en: "About us" })}</span>
            <h2 className="section-title" style={{ fontSize: "clamp(28px,3.6vw,42px)", marginTop: 16 }}>
              {lang === "es" ? (
                <>
                  Aprender debería sentirse <span className="em">justo.</span>
                </>
              ) : (
                <>
                  Learning should feel <span className="em">fair.</span>
                </>
              )}
            </h2>
          </div>
          <div className="about-body reveal">
            <p>
              {lang === "es" ? (
                <>
                  Oulad nació de una idea simple: cada estudiante avanza a su propio ritmo, y la
                  dificultad debería ajustarse a la persona — no al revés. Tomamos el{" "}
                  <strong>sistema de rating del ajedrez</strong> y lo aplicamos a la educación matemática.
                </>
              ) : (
                <>
                  Oulad was born from a simple idea: every student moves at their own pace, and
                  difficulty should adapt to the person — not the other way around. We took the{" "}
                  <strong>chess rating system</strong> and applied it to math education.
                </>
              )}
            </p>
            <p>
              {lang === "es" ? (
                <>
                  El resultado: un reto siempre a tu medida, una tutora que respeta tu proceso, y datos que
                  ayudan a docentes a enseñar mejor. Desde el <strong>colegio hasta la universidad</strong>,
                  pasando por semilleros y concursos.
                </>
              ) : (
                <>
                  The result: a challenge always tailored to you, a tutor that respects your process, and
                  data that helps teachers teach better. From <strong>school to university</strong>, including
                  talent programs and contests.
                </>
              )}
            </p>
            <div className="values">
              <div className="card val">
                <span className="vi">🎯</span>
                <div>
                  <h4>{t({ es: "El reto justo", en: "The right challenge" })}</h4>
                  <p>
                    {t({
                      es: "Ni aburrimiento ni frustración: siempre en tu zona de aprendizaje.",
                      en: "No boredom, no frustration: always in your learning zone.",
                    })}
                  </p>
                </div>
              </div>
              <div className="card val">
                <span className="vi">🤝</span>
                <div>
                  <h4>{t({ es: "Guiar, no resolver", en: "Guide, don't solve" })}</h4>
                  <p>
                    {t({
                      es: "KatIA te acompaña para que el aprendizaje sea tuyo de verdad.",
                      en: "KatIA walks beside you so the learning is genuinely yours.",
                    })}
                  </p>
                </div>
              </div>
              <div className="card val">
                <span className="vi">📊</span>
                <div>
                  <h4>{t({ es: "Decisiones con datos", en: "Data-driven decisions" })}</h4>
                  <p>
                    {t({
                      es: "Métricas claras por tópico para estudiantes y docentes.",
                      en: "Clear per-topic metrics for students and teachers.",
                    })}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===================== FAQ ===================== */}
      <section className="section" id="faq">
        <div className="container">
          <div className="section-head center reveal">
            <span className="kicker" style={{ justifyContent: "center" }}>
              {t({ es: "Preguntas frecuentes", en: "FAQ" })}
            </span>
            <h2 className="section-title">{t({ es: "¿Tienes dudas?", en: "Got questions?" })}</h2>
          </div>
          <div className="faq">
            {FAQS.map((item, i) => {
              const open = openFaq === i;
              return (
                <div key={i} className={`qa${open ? " open" : ""}`}>
                  <button className="qa-q" onClick={() => setOpenFaq(open ? null : i)} aria-expanded={open}>
                    <span>{t(item.q)}</span>
                    <span className="ic" />
                  </button>
                  <div className="qa-a" style={{ maxHeight: open ? 600 : 0 }}>
                    <p>{t(item.a)}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ===================== FINAL CTA ===================== */}
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <div className="cta-final reveal">
            <span className="kicker">{t({ es: "Empieza hoy", en: "Start today" })}</span>
            <h2>
              {lang === "es" ? (
                <>
                  ¿Listo para <span className="em">subir de nivel?</span>
                </>
              ) : (
                <>
                  Ready to <span className="em">level up?</span>
                </>
              )}
            </h2>
            <p>
              {t({
                es: "Crea tu cuenta gratis y deja que el motor ELO encuentre tu reto perfecto. KatIA ya te está esperando.",
                en: "Create your free account and let the ELO engine find your perfect challenge. KatIA is already waiting for you.",
              })}
            </p>
            <div className="hero-cta">
              <Link className="btn btn-primary btn-lg" to="/login">
                {t({ es: "Crear mi cuenta", en: "Create my account" })}
              </Link>
              <a className="btn btn-ghost btn-lg" href="#katia">
                {t({ es: "Conocer a KatIA", en: "Meet KatIA" })}
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* ===================== FOOTER ===================== */}
      <footer className="footer">
        <div className="container">
          <div className="foot-grid">
            <div className="foot-brand">
              <img className="nav-logo nav-logo-dark" src="/oulad-logo-dark.png" alt="Oulad" style={{ height: 30 }} />
              <img className="nav-logo nav-logo-light" src="/oulad-logo-light.png" alt="Oulad" style={{ height: 30 }} />
              <p>
                {t({
                  es: "Matemáticas con rango adaptativo. Sube de nivel, una jugada a la vez.",
                  en: "Math with adaptive rank. Level up, one move at a time.",
                })}
              </p>
            </div>
            <div className="foot-col">
              <h5>{t({ es: "Producto", en: "Product" })}</h5>
              <ul>
                <li><a href="#features">{t({ es: "Funciones", en: "Features" })}</a></li>
                <li><a href="#engine">{t({ es: "Cómo funciona", en: "How it works" })}</a></li>
                <li><a href="#katia">KatIA</a></li>
                <li><a href="#teachers">{t({ es: "Para docentes", en: "For teachers" })}</a></li>
              </ul>
            </div>
            <div className="foot-col">
              <h5>{t({ es: "Recursos", en: "Resources" })}</h5>
              <ul>
                <li><a href="#about">{t({ es: "Nosotros", en: "About" })}</a></li>
                <li><a href="#faq">FAQ</a></li>
                <li>
                  <a href="https://github.com/LuisJRubioH/LevelUp-ELO" target="_blank" rel="noopener noreferrer">
                    GitHub
                  </a>
                </li>
              </ul>
            </div>
            <div className="foot-col">
              <h5>{t({ es: "Cuenta", en: "Account" })}</h5>
              <ul>
                <li><Link to="/login">{t({ es: "Iniciar sesión", en: "Log in" })}</Link></li>
                <li><Link to="/login">{t({ es: "Crear cuenta", en: "Sign up" })}</Link></li>
              </ul>
            </div>
          </div>
          <div className="foot-bot">
            <span>© 2026 Oulad</span>
            <span className="pixel" style={{ fontSize: 8 }}>
              {t({ es: "HECHO PARA SUBIR DE NIVEL", en: "MADE TO LEVEL UP" })}
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}
