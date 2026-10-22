/* ============================================================
   LevelUp-ELO — Landing interactions
   i18n ES/EN · nav · reveal · FAQ · ELO climb demo · KatIA chat
   ============================================================ */
(function () {
  "use strict";

  /* ---------------- i18n ---------------- */
  const LS_LANG = "lvlup-lang";
  let lang = localStorage.getItem(LS_LANG) || "es";

  function applyLang(l) {
    lang = l;
    document.querySelectorAll("[data-es]").forEach((el) => {
      const v = el.getAttribute("data-" + l);
      if (v !== null) el.textContent = v;
    });
    document.querySelectorAll("[data-es-html]").forEach((el) => {
      const v = el.getAttribute("data-" + l + "-html");
      if (v !== null) el.innerHTML = v;
    });
    document.querySelectorAll(".lang button").forEach((b) =>
      b.classList.toggle("on", b.dataset.l === l)
    );
    document.documentElement.lang = l;
    localStorage.setItem(LS_LANG, l);
    // dynamic blocks that need re-rendering
    renderChat();
    updateDemoLabels();
  }

  document.querySelectorAll(".lang button").forEach((b) =>
    b.addEventListener("click", () => applyLang(b.dataset.l))
  );

  /* ---------------- nav ---------------- */
  const nav = document.getElementById("nav");
  const onScroll = () => nav.classList.toggle("scrolled", window.scrollY > 8);
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  const burger = document.getElementById("burger");
  const mobileMenu = document.getElementById("mobileMenu");
  burger.addEventListener("click", () => mobileMenu.classList.toggle("open"));
  mobileMenu.querySelectorAll("a").forEach((a) =>
    a.addEventListener("click", () => mobileMenu.classList.remove("open"))
  );

  /* ---------------- reveal on scroll ---------------- */
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          e.target.classList.add("in");
          io.unobserve(e.target);
          if (e.target.id === "eloDemo") startHeroXp();
          if (e.target.classList.contains("teach")) animateMiniBars();
        }
      });
    },
    { threshold: 0.15 }
  );
  document.querySelectorAll(".reveal").forEach((el) => io.observe(el));

  /* hero XP bar fill */
  function startHeroXp() {
    const xp = document.getElementById("heroXp");
    if (xp) xp.style.width = "72%";
  }
  setTimeout(startHeroXp, 600);

  /* ---------------- FAQ ---------------- */
  const FAQS = [
    {
      q: { es: "¿Qué es el ELO y por qué usarlo para matemáticas?", en: "What is ELO and why use it for math?" },
      a: { es: "El ELO es el sistema de rating del ajedrez: un número que mide tu nivel. Aquí, cada respuesta actualiza tu ELO y el de la pregunta, así la plataforma siempre te ofrece un reto a tu medida — ni muy fácil, ni imposible.", en: "ELO is the chess rating system: a number that measures your level. Here, every answer updates your ELO and the question's, so the platform always offers a challenge that fits you — never too easy, never impossible." },
    },
    {
      q: { es: "¿Quién es KatIA?", en: "Who is KatIA?" },
      a: { es: "KatIA es tu tutora con inteligencia artificial. Usa el método socrático: en lugar de darte la respuesta, te hace preguntas para que la descubras tú. También revisa tus procedimientos escritos a mano paso a paso.", en: "KatIA is your AI tutor. She uses the socratic method: instead of giving you the answer, she asks questions so you discover it yourself. She also reviews your handwritten work step by step." },
    },
    {
      q: { es: "¿Cómo se calcula mi rango?", en: "How is my rank calculated?" },
      a: { es: "Tu rango depende de tu ELO. Hay 16 niveles, de Aspirante a Leyenda Suprema. A medida que aciertas preguntas más difíciles, tu ELO sube y desbloqueas nuevos rangos por materia.", en: "Your rank depends on your ELO. There are 16 levels, from Aspirant to Supreme Legend. As you solve harder questions, your ELO rises and you unlock new ranks per subject." },
    },
    {
      q: { es: "¿Qué materias puedo practicar?", en: "Which subjects can I practice?" },
      a: { es: "Desde colegio (álgebra, aritmética, geometría, trigonometría) hasta universidad (cálculo, álgebra lineal, ecuaciones diferenciales, probabilidad), además de semilleros y preparación para concursos.", en: "From school (algebra, arithmetic, geometry, trigonometry) to university (calculus, linear algebra, differential equations, probability), plus talent programs and contest prep." },
    },
    {
      q: { es: "¿Funciona en el celular?", en: "Does it work on mobile?" },
      a: { es: "Sí. LevelUp-ELO está pensado para usarse desde el navegador en computador o celular, y puedes cambiar entre español e inglés en cualquier momento sin recargar la página.", en: "Yes. LevelUp-ELO is built to be used from the browser on desktop or mobile, and you can switch between Spanish and English at any time without reloading the page." },
    },
    {
      q: { es: "Soy docente, ¿cómo empiezo?", en: "I'm a teacher — how do I start?" },
      a: { es: "Solicita acceso docente y tendrás un panel para crear grupos, asignar exámenes con ventana de tiempo, revisar procedimientos y exportar calificaciones en CSV o XLSX.", en: "Request teacher access and you'll get a dashboard to create groups, assign timed exams, review student work and export grades to CSV or XLSX." },
    },
    {
      q: { es: "¿Mis datos están seguros?", en: "Is my data safe?" },
      a: { es: "Sí. Las contraseñas se protegen con Argon2id, un estándar moderno de cifrado, y los procedimientos se almacenan de forma privada.", en: "Yes. Passwords are protected with Argon2id, a modern hashing standard, and your submitted work is stored privately." },
    },
  ];

  const faqList = document.getElementById("faq-list");
  FAQS.forEach((item) => {
    const qa = document.createElement("div");
    qa.className = "qa";
    qa.innerHTML =
      '<button class="qa-q"><span data-es="" data-en=""></span><span class="ic"></span></button>' +
      '<div class="qa-a"><p data-es="" data-en=""></p></div>';
    const qSpan = qa.querySelector(".qa-q span:first-child");
    const aP = qa.querySelector(".qa-a p");
    qSpan.setAttribute("data-es", item.q.es); qSpan.setAttribute("data-en", item.q.en);
    aP.setAttribute("data-es", item.a.es); aP.setAttribute("data-en", item.a.en);
    const btn = qa.querySelector(".qa-q");
    const ans = qa.querySelector(".qa-a");
    btn.addEventListener("click", () => {
      const open = qa.classList.toggle("open");
      ans.style.maxHeight = open ? ans.scrollHeight + "px" : "0";
    });
    faqList.appendChild(qa);
  });

  /* ---------------- ELO climb demo ---------------- */
  const RANKS = [
    { es: "Plata I", en: "Silver I", min: 1000, c: "#cbd5e1" },
    { es: "Oro II", en: "Gold II", min: 1120, c: "#fbbf24" },
    { es: "Oro I", en: "Gold I", min: 1180, c: "#fcd34d" },
    { es: "Platino II", en: "Platinum II", min: 1300, c: "#2dd4bf" },
    { es: "Platino I", en: "Platinum I", min: 1420, c: "#5eead4" },
    { es: "Diamante II", en: "Diamond II", min: 1560, c: "#22d3ee" },
    { es: "Diamante I", en: "Diamond I", min: 1700, c: "#67e8f9" },
    { es: "Maestro", en: "Master", min: 1850, c: "#c084fc" },
  ];
  const START = 1180;
  let elo = START;

  const $elo = document.getElementById("demoElo");
  const $bar = document.getElementById("demoBar");
  const $rankName = document.getElementById("demoRankName");
  const $low = document.getElementById("demoRankLow");
  const $high = document.getElementById("demoRankHigh");
  const $delta = document.getElementById("demoDelta");
  const ladder = document.getElementById("ladder");

  // build ladder (top = highest)
  RANKS.slice().reverse().forEach((r) => {
    const row = document.createElement("div");
    row.className = "rung";
    row.style.setProperty("--rc", r.c);
    row.dataset.min = r.min;
    row.innerHTML =
      '<span class="ri">▲</span><span class="rn" data-es="' + r.es + '" data-en="' + r.en + '">' + r.es + '</span><span class="rv">ELO ' + r.min + "+</span>";
    ladder.appendChild(row);
  });

  function rankIndex(e) {
    let idx = 0;
    for (let i = 0; i < RANKS.length; i++) if (e >= RANKS[i].min) idx = i;
    return idx;
  }
  function fmt(n) { return Math.round(n).toLocaleString("es-CO"); }

  function updateDemoLabels() {
    const i = rankIndex(elo);
    const r = RANKS[i];
    const next = RANKS[Math.min(i + 1, RANKS.length - 1)];
    $rankName.textContent = lang === "es" ? r.es : r.en;
    $rankName.style.color = r.c;
    $low.textContent = lang === "es" ? r.es : r.en;
    $high.textContent = lang === "es" ? next.es : next.en;
  }

  function renderDemo(animate) {
    const i = rankIndex(elo);
    const r = RANKS[i];
    const next = RANKS[Math.min(i + 1, RANKS.length - 1)];
    const span = Math.max(1, next.min - r.min);
    const pct = i >= RANKS.length - 1 ? 100 : Math.min(100, ((elo - r.min) / span) * 100);
    $bar.style.width = pct + "%";
    $bar.style.background = "linear-gradient(90deg," + r.c + "," + next.c + ")";
    $elo.textContent = fmt(elo);
    updateDemoLabels();
    // ladder states
    ladder.querySelectorAll(".rung").forEach((row) => {
      const min = +row.dataset.min;
      row.classList.toggle("reached", elo >= min);
      row.classList.toggle("current", min === r.min);
    });
  }

  function countTo(target) {
    const from = parseInt($elo.textContent.replace(/\D/g, ""), 10) || START;
    const dur = 600, t0 = performance.now();
    function step(t) {
      const k = Math.min(1, (t - t0) / dur);
      const val = from + (target - from) * (1 - Math.pow(1 - k, 3));
      $elo.textContent = fmt(val);
      if (k < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  document.getElementById("demoAnswer").addEventListener("click", () => {
    if (elo >= RANKS[RANKS.length - 1].min) return;
    const prevIdx = rankIndex(elo);
    const gain = 18 + Math.floor(Math.random() * 17);
    elo = Math.min(RANKS[RANKS.length - 1].min, elo + gain);
    countTo(elo);
    $delta.textContent = "+" + gain;
    $delta.classList.add("show");
    setTimeout(() => $delta.classList.remove("show"), 1400);
    renderDemo(true);
    const newIdx = rankIndex(elo);
    if (newIdx > prevIdx) {
      const cur = ladder.querySelector(".rung.current");
      if (cur) { cur.animate(
        [{ transform: "translateX(6px) scale(1)" }, { transform: "translateX(6px) scale(1.04)" }, { transform: "translateX(6px) scale(1)" }],
        { duration: 500 }); }
    }
  });
  document.getElementById("demoReset").addEventListener("click", () => {
    elo = START; countTo(START); renderDemo(true);
  });
  renderDemo(false);

  /* ---------------- teacher mini bars ---------------- */
  const BAR_H = [62, 84, 48, 72, 92];
  function buildMiniBars() {
    const wrap = document.getElementById("miniBars");
    if (!wrap || wrap.childElementCount) return;
    BAR_H.forEach(() => {
      const b = document.createElement("div");
      b.className = "mb"; b.style.height = "0%";
      wrap.appendChild(b);
    });
  }
  function animateMiniBars() {
    const bars = document.querySelectorAll("#miniBars .mb");
    bars.forEach((b, i) => setTimeout(() => (b.style.height = BAR_H[i] + "%"), i * 90));
  }
  buildMiniBars();

  /* ---------------- KatIA chat ---------------- */
  const CHAT = {
    greeting: { es: "¡Hola! Soy KatIA 🐱 ¿En qué te trabas hoy?", en: "Hi! I'm KatIA 🐱 What are you stuck on today?" },
    prompts: [
      {
        q: { es: "No sé resolver x² − 5x + 6 = 0", en: "I can't solve x² − 5x + 6 = 0" },
        a: { es: "Antes de la fórmula… ¿qué <b>dos números</b> multiplicados dan 6 y sumados dan 5? 🤔", en: "Before the formula… what <b>two numbers</b> multiply to 6 and add up to 5? 🤔" },
      },
      {
        q: { es: "¿Cuál es la derivada de x³?", en: "What's the derivative of x³?" },
        a: { es: "Piensa en la regla de la potencia. ¿Qué le pasa al <b>exponente</b> cuando derivas xⁿ? 💡", en: "Think of the power rule. What happens to the <b>exponent</b> when you differentiate xⁿ? 💡" },
      },
      {
        q: { es: "Me equivoqué otra vez 😞", en: "I got it wrong again 😞" },
        a: { es: "Equivocarse es parte de subir de ELO. ¿Me muestras tu procedimiento y lo revisamos paso a paso? 💪", en: "Mistakes are part of climbing ELO. Show me your steps and we'll review them together? 💪" },
      },
    ],
  };

  const chatBody = document.getElementById("chatBody");
  const chatPrompts = document.getElementById("chatPrompts");

  function addMsg(who, html) {
    const m = document.createElement("div");
    m.className = "msg " + who;
    m.innerHTML = html;
    chatBody.appendChild(m);
    chatBody.scrollTop = chatBody.scrollHeight;
    return m;
  }
  function showTyping() {
    const t = document.createElement("div");
    t.className = "msg bot";
    t.innerHTML = '<span class="typing"><i></i><i></i><i></i></span>';
    chatBody.appendChild(t);
    chatBody.scrollTop = chatBody.scrollHeight;
    return t;
  }

  function renderChat() {
    if (!chatBody) return;
    chatBody.innerHTML = "";
    chatPrompts.innerHTML = "";
    addMsg("bot", CHAT.greeting[lang]);
    CHAT.prompts.forEach((p, i) => {
      const chip = document.createElement("button");
      chip.className = "chip-prompt";
      chip.textContent = p.q[lang];
      chip.addEventListener("click", () => {
        chip.disabled = true;
        addMsg("user", p.q[lang]);
        const typing = showTyping();
        setTimeout(() => {
          typing.remove();
          addMsg("bot", p.a[lang]);
        }, 950);
      });
      chatPrompts.appendChild(chip);
    });
  }

  /* ---------------- init ---------------- */
  applyLang(lang);
})();
