"""
Genera dos PDFs auto-contenidos:
  - guia_docente.pdf     — qué puede hacer un docente en LevelUp-ELO
  - guia_estudiante.pdf  — qué puede hacer un estudiante en LevelUp-ELO

Estilo: paleta V2 (#6C63FF acento, fondo blanco para impresión).
Cada documento sirve como manual de uso completo.

Uso:
    python scripts/generate_user_guides.py
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

# Registrar Segoe UI (TrueType, soporta UTF-8 completo: →, −, ±, etc.)
_FONT_DIR = Path("C:/Windows/Fonts")
pdfmetrics.registerFont(TTFont("Body", str(_FONT_DIR / "segoeui.ttf")))
pdfmetrics.registerFont(TTFont("Body-Bold", str(_FONT_DIR / "segoeuib.ttf")))
pdfmetrics.registerFont(TTFont("Body-Italic", str(_FONT_DIR / "segoeuii.ttf")))
pdfmetrics.registerFont(TTFont("Mono", str(_FONT_DIR / "consola.ttf")))
pdfmetrics.registerFontFamily(
    "Body",
    normal="Body",
    bold="Body-Bold",
    italic="Body-Italic",
    boldItalic="Body-Bold",
)

# ── Paleta ───────────────────────────────────────────────────────────────────
ACCENT = colors.HexColor("#6C63FF")
ACCENT_DARK = colors.HexColor("#4F46E5")
ACCENT_LIGHT = colors.HexColor("#E8E6FF")
TEXT = colors.HexColor("#0F172A")
TEXT2 = colors.HexColor("#475569")
SUCCESS = colors.HexColor("#16A34A")
WARNING = colors.HexColor("#D97706")
DANGER = colors.HexColor("#DC2626")
SURFACE = colors.HexColor("#F8FAFC")
BORDER = colors.HexColor("#E2E8F0")


# ── Estilos de párrafo ────────────────────────────────────────────────────────
def make_styles():
    base = getSampleStyleSheet()
    base["Normal"].fontName = "Body"
    base["Normal"].fontSize = 10.5
    base["Normal"].leading = 15
    base["Normal"].textColor = TEXT
    base["Normal"].alignment = TA_JUSTIFY
    base["Normal"].spaceAfter = 6

    base.add(
        ParagraphStyle(
            name="H1",
            fontName="Body-Bold",
            fontSize=22,
            leading=26,
            textColor=ACCENT_DARK,
            spaceAfter=10,
            spaceBefore=14,
        )
    )
    base.add(
        ParagraphStyle(
            name="H2",
            fontName="Body-Bold",
            fontSize=14,
            leading=18,
            textColor=TEXT,
            spaceAfter=6,
            spaceBefore=14,
            borderPadding=4,
            leftIndent=0,
        )
    )
    base.add(
        ParagraphStyle(
            name="H3",
            fontName="Body-Bold",
            fontSize=11.5,
            leading=15,
            textColor=ACCENT_DARK,
            spaceAfter=4,
            spaceBefore=10,
        )
    )
    base.add(
        ParagraphStyle(
            name="Lead",
            fontName="Body",
            fontSize=12,
            leading=17,
            textColor=TEXT2,
            spaceAfter=10,
            alignment=TA_LEFT,
        )
    )
    base.add(
        ParagraphStyle(
            name="MyBullet",
            fontName="Body",
            fontSize=10.5,
            leading=15,
            textColor=TEXT,
            leftIndent=18,
            bulletIndent=6,
            spaceAfter=3,
            alignment=TA_LEFT,
        )
    )
    base.add(
        ParagraphStyle(
            name="Mono",
            fontName="Mono",
            fontSize=9.5,
            leading=13,
            textColor=TEXT,
            backColor=SURFACE,
            borderPadding=6,
            spaceAfter=8,
        )
    )
    base.add(
        ParagraphStyle(
            name="CalloutText",
            fontName="Body",
            fontSize=10.5,
            leading=15,
            textColor=TEXT,
            alignment=TA_LEFT,
            leftIndent=0,
            spaceAfter=4,
        )
    )
    return base


STYLES = make_styles()


# ── Páginas: header morado + footer con número ────────────────────────────────
class GuidePageTemplate(PageTemplate):
    def __init__(self, doc_title, document_kind):
        self.doc_title = doc_title
        self.kind = document_kind  # "docente" o "estudiante"
        margin_x = 2.0 * cm
        margin_top = 3.0 * cm
        margin_bot = 2.0 * cm
        w, h = LETTER
        frame = Frame(
            margin_x,
            margin_bot,
            w - 2 * margin_x,
            h - margin_top - margin_bot,
            id="body",
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )
        super().__init__(id="GuideTemplate", frames=[frame], onPage=self.draw_header_footer)

    def draw_header_footer(self, c: canvas.Canvas, doc):
        w, h = LETTER
        # Header band
        c.setFillColor(ACCENT)
        c.rect(0, h - 1.7 * cm, w, 1.7 * cm, fill=1, stroke=0)
        # Title left
        c.setFillColor(colors.white)
        c.setFont("Body-Bold", 13)
        c.drawString(2 * cm, h - 1.05 * cm, "LevelUp-ELO")
        # Subtitle right
        c.setFont("Body", 10)
        c.drawRightString(w - 2 * cm, h - 1.05 * cm, self.doc_title)
        # Decorative thin line
        c.setStrokeColor(ACCENT_DARK)
        c.setLineWidth(2)
        c.line(0, h - 1.7 * cm - 2, w, h - 1.7 * cm - 2)
        # Footer
        c.setFillColor(TEXT2)
        c.setFont("Body", 8.5)
        c.drawString(2 * cm, 1.0 * cm, f"Guía {self.kind} · Plataforma de práctica adaptativa")
        c.drawRightString(w - 2 * cm, 1.0 * cm, f"Página {doc.page}")


def build_pdf(filename: str, title: str, kind: str, story: list):
    doc = BaseDocTemplate(
        filename,
        pagesize=LETTER,
        title=title,
        author="LevelUp-ELO",
        creator="LevelUp-ELO",
    )
    doc.addPageTemplates([GuidePageTemplate(title, kind)])
    doc.build(story)
    print(f"OK -> {filename}  ({Path(filename).stat().st_size // 1024} KB)")


# ── Helpers de contenido ──────────────────────────────────────────────────────
def h1(text):
    return Paragraph(text, STYLES["H1"])


def h2(text):
    return Paragraph(text, STYLES["H2"])


def h3(text):
    return Paragraph(text, STYLES["H3"])


def p(text):
    return Paragraph(text, STYLES["Normal"])


def lead(text):
    return Paragraph(text, STYLES["Lead"])


def bullet(text):
    return Paragraph(f"• {text}", STYLES["MyBullet"])


def numbered(items):
    return [Paragraph(f"<b>{i}.</b>  {t}", STYLES["MyBullet"]) for i, t in enumerate(items, 1)]


def mono(text):
    return Paragraph(f"<font face='Mono'>{text}</font>", STYLES["Mono"])


def spacer(h=8):
    return Spacer(1, h)


def callout(title_text, body_text, accent=ACCENT):
    """Caja con borde lateral del color accent, título en negrita, cuerpo."""
    data = [
        [Paragraph(f"<b>{title_text}</b>", STYLES["CalloutText"])],
        [Paragraph(body_text, STYLES["CalloutText"])],
    ]
    t = Table(data, colWidths=[15.5 * cm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
                ("LINEBEFORE", (0, 0), (0, -1), 3, accent),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return t


def info_table(rows, col_widths=None):
    """Tabla de 2 columnas con borde sutil."""
    if col_widths is None:
        col_widths = [5.5 * cm, 10 * cm]
    data = []
    for label, value in rows:
        data.append(
            [
                Paragraph(f"<b>{label}</b>", STYLES["CalloutText"]),
                Paragraph(value, STYLES["CalloutText"]),
            ]
        )
    t = Table(data, colWidths=col_widths)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return t


# ── Contenido: Guía Docente ───────────────────────────────────────────────────
def docente_story():
    s = []

    # Portada
    s.append(spacer(40))
    s.append(Paragraph("Guía del Docente", STYLES["H1"]))
    s.append(Paragraph("Cómo usar LevelUp-ELO para acompañar a tus estudiantes", STYLES["Lead"]))
    s.append(spacer(10))
    s.append(
        p(
            "LevelUp-ELO es una plataforma de práctica matemática adaptativa que ajusta la "
            "dificultad de cada pregunta según el desempeño del estudiante, usando un sistema ELO "
            "vectorial por tópico. Como docente, tienes acceso a un panel completo para crear grupos, "
            "monitorear el progreso, revisar procedimientos y crear exámenes manuales."
        )
    )
    s.append(spacer(10))
    s.append(
        callout(
            "Acceso",
            "URL: <b>luislevelupelo.vercel.app</b> · Inicia sesión con tu usuario y contraseña. "
            "Si te registras como docente por primera vez, tu cuenta queda <b>pendiente de aprobación</b> "
            "por el administrador antes de poder ingresar.",
        )
    )

    # 1. Panel principal
    s.append(h2("1. Panel principal (Dashboard)"))
    s.append(
        p(
            "Al iniciar sesión llegas al Dashboard. En la parte superior verás cuatro tarjetas con "
            "indicadores rápidos:"
        )
    )
    s.append(bullet("<b>Active groups</b> — número total de grupos que has creado."))
    s.append(bullet("<b>Students</b> — estudiantes activos repartidos entre tus grupos."))
    s.append(bullet("<b>Average ELO</b> — promedio de ELO global de todos tus estudiantes."))
    s.append(bullet("<b>Average accuracy</b> — % de respuestas correctas global de tus grupos."))
    s.append(spacer(6))
    s.append(p("Debajo verás tres pestañas:"))
    s.append(
        bullet(
            "<b>Students</b> — tabla con tus estudiantes, ELO, intentos, accuracy y última actividad. Puedes filtrar por grupo, nivel y buscar por nombre."
        )
    )
    s.append(bullet("<b>Ranking</b> — ordenamiento por ELO global o por curso."))
    s.append(
        bullet(
            "<b>Metrics</b> — tiempo promedio, tasa de abandono, distribución horaria de intentos, gráfico de actividad diaria y desglose por tópico."
        )
    )
    s.append(spacer(6))
    s.append(
        callout(
            "Detalle de un estudiante",
            "Haz clic en cualquier fila de la tabla <i>Students</i> para abrir su ficha completa: "
            "historial de intentos, gráfico de ELO por curso, conversaciones con KatIA, procedimientos enviados "
            "y la posibilidad de pedir un análisis con IA (requiere API key).",
        )
    )

    # 2. Gestión de grupos
    s.append(h2("2. Gestión de grupos"))
    s.append(
        p(
            "Los grupos son la unidad básica para organizar a tus estudiantes. Ve a <b>Groups</b> en el sidebar."
        )
    )
    s.append(h3("Crear un grupo nuevo"))
    s.extend(
        numbered(
            [
                "Click en <b>+ New group</b>.",
                "Elige el curso (Álgebra Básica, Cálculo Diferencial, etc.).",
                "Asigna un nombre descriptivo: por ejemplo, “11A-2026” o “Semillero Olimpiadas 10°”.",
                "Click en <b>Create</b>.",
            ]
        )
    )
    s.append(h3("Que tus estudiantes entren al grupo"))
    s.append(p("Hay dos vías:"))
    s.append(
        bullet(
            "<b>Vía A (recomendada): código de invitación</b> — genera un código de 6 caracteres con el botón <i>Invite code</i>. Compártelo en clase. Cuando un estudiante lo ingrese en su pantalla de <i>Courses</i> → <i>Access code</i>, queda inscrito al curso y al grupo automáticamente."
        )
    )
    s.append(
        bullet(
            "<b>Vía B: asignación manual</b> — el administrador puede mover estudiantes entre grupos. Útil si un estudiante ya estaba inscrito sin grupo."
        )
    )
    s.append(spacer(4))
    s.append(
        callout(
            "Sobre los grupos inter-nivel",
            "Un código de invitación permite que estudiantes de cualquier nivel educativo (colegio, universidad, semillero) "
            "se unan a tu grupo, aunque el sistema normalmente filtre cursos por nivel.",
            accent=WARNING,
        )
    )

    # 3. Procedimientos
    s.append(h2("3. Revisión de procedimientos"))
    s.append(
        p(
            "Cuando un estudiante sube una foto de su procedimiento (en una pregunta de práctica o "
            "como ejercicio suelto), llega a tu bandeja en <b>Procedures</b>."
        )
    )
    s.append(h3("Qué ves de cada procedimiento"))
    s.append(bullet("Nombre del estudiante y la pregunta original."))
    s.append(bullet("Imagen del procedimiento (puedes ampliar haciendo clic)."))
    s.append(
        bullet(
            "<b>Sugerencia de IA</b>: si tu configuración tiene una clave de Groq con Llama 4 Scout, la IA propone un puntaje 0–100 y un análisis de pasos, errores y saltos lógicos."
        )
    )
    s.append(bullet("Estado: pendiente, revisado por IA, o calificado por ti."))
    s.append(h3("Cómo calificar"))
    s.extend(
        numbered(
            [
                "Asigna un puntaje 0–100 (la sugerencia de IA es solo orientativa, NO afecta el ELO).",
                "Escribe un comentario para el estudiante.",
                "Opcionalmente, sube una foto de retroalimentación (correcciones, anotaciones).",
                "Click en <b>Submit grade</b>.",
            ]
        )
    )
    s.append(
        callout(
            "Impacto en el ELO",
            "El puntaje del docente se traduce en un ajuste de ELO: "
            "<font face='Mono'>ELO_delta = (score - 50) * 0.2</font>. "
            "Eso significa hasta &#177;10 puntos por procedimiento. La IA <b>nunca</b> ajusta ELO por sí sola.",
        )
    )

    # 4. Exámenes manuales
    s.append(h2("4. Crear exámenes manuales"))
    s.append(
        p(
            "Además del examen estándar generado por el sistema, puedes armar exámenes "
            "específicos seleccionando preguntas del banco. Ve a <b>Exams</b> en el sidebar."
        )
    )
    s.append(h3("Paso 1: crear la plantilla"))
    s.extend(
        numbered(
            [
                "Click en <b>+ Create exam</b>.",
                "Selecciona el curso al que pertenecerá el examen.",
                "Dale un título reconocible: ej. “Parcial 1 — Áreas y perímetros”.",
                "Ajusta el tiempo límite (5 a 180 minutos).",
                "En el catálogo de la derecha, haz clic en cada pregunta para añadirla. El orden se preserva.",
                "Click en <b>Create exam</b> al final.",
            ]
        )
    )
    s.append(h3("Paso 2: asignar a grupos y programar (opcional)"))
    s.append(
        p(
            "Una vez creada la plantilla, verás un botón verde <b>Assign</b> junto a Edit/Archive. "
            "Si la dejas sin asignar, será visible a todos los estudiantes inscritos en el curso. "
            "Si la asignas:"
        )
    )
    s.extend(
        numbered(
            [
                "Click en <b>Assign</b> → abre un modal.",
                "Marca uno o varios grupos.",
                "Opcionalmente define <b>From</b> (apertura) y <b>Until</b> (cierre). Vacío = sin restricción.",
                "Click en <b>Assign</b> dentro del modal.",
            ]
        )
    )
    s.append(
        callout(
            "Notificación al estudiante",
            "Los estudiantes asignados verán un <b>punto rojo con el conteo</b> sobre el ítem “Exam” de su sidebar, "
            "y un contador en el tab “From teacher”. No reciben correo ni notificación push — anúncialo en clase.",
        )
    )
    s.append(h3("Editar o archivar"))
    s.append(
        bullet(
            "<b>Edit</b> — cambia título, tiempo o lista de preguntas. El curso no se puede cambiar."
        )
    )
    s.append(
        bullet("<b>Archive</b> — oculta la plantilla a los estudiantes y a ti mismo (soft delete).")
    )

    s.append(PageBreak())

    # 5. Análisis de estudiantes
    s.append(h2("5. Análisis individual del estudiante"))
    s.append(
        p("Desde la tabla del Dashboard, haciendo clic en una fila, accedes a la ficha completa:")
    )
    s.append(
        bullet("<b>ELO history</b> — gráfico de los últimos 20 intentos con su ELO progresivo.")
    )
    s.append(
        bullet(
            "<b>KatIA history</b> — todas las conversaciones del estudiante con la tutora socrática."
        )
    )
    s.append(bullet("<b>Ranking en grupo</b> — posición del estudiante dentro de su grupo."))
    s.append(
        bullet(
            "<b>Análisis con IA</b> — botón que envía sus datos a una IA (Groq/Claude/OpenAI según tu config) para obtener un resumen pedagógico. Requiere API key en tu sidebar."
        )
    )

    # 6. Exportar reportes
    s.append(h2("6. Descargar reportes"))
    s.append(p("Ve a <b>Export data</b> en el sidebar. Tienes dos formatos:"))
    s.append(h3("CSV (intentos)"))
    s.append(
        p(
            "Un único archivo <font face='Mono'>levelup_intentos.csv</font> con una fila por cada intento de cada estudiante. Útil para análisis rápido en Excel/Sheets."
        )
    )
    s.append(h3("XLSX (datos completos)"))
    s.append(p("Un libro <font face='Mono'>levelup_datos_completos.xlsx</font> con 4 hojas:"))
    s.append(bullet("<b>Attempts</b> — un intento por fila, con todos los metadatos."))
    s.append(bullet("<b>Enrollments</b> — qué estudiantes están en qué cursos."))
    s.append(bullet("<b>Procedures</b> — procedimientos enviados y calificados."))
    s.append(bullet("<b>KatIA</b> — interacciones con la tutora."))
    s.append(spacer(4))
    s.append(h3("Qué significa cada columna importante"))
    s.append(
        info_table(
            [
                ("elo_before / elo_after", "ELO del tópico antes y después del intento."),
                ("time_taken", "Tiempo en segundos que tomó responder."),
                ("rating_deviation (RD)", "Incertidumbre del ELO (350=máxima, 30=mínima)."),
                ("prob_failure", "Probabilidad estimada de fallar antes del intento (0–1)."),
                ("confidence_score", "Auto-evaluación del estudiante (0–100) si la dio."),
                ("error_type", "Tipo de error si falló: distributivo, signo, fracción, etc."),
            ]
        )
    )

    # 7. Métricas globales
    s.append(h2("7. Métricas globales (Dashboard → Metrics)"))
    s.append(bullet("<b>Total attempts</b> — total de intentos de todos tus grupos."))
    s.append(bullet("<b>Avg time per attempt</b> — tiempo promedio para responder."))
    s.append(
        bullet("<b>Abandonment rate</b> — % de preguntas que el estudiante abrió y no respondió.")
    )
    s.append(
        bullet("<b>Hourly distribution</b> — a qué horas del día tus estudiantes practican más.")
    )
    s.append(
        bullet(
            "<b>Topic breakdown</b> — accuracy, número de intentos y tiempo promedio por tópico."
        )
    )

    # 8. Buenas prácticas
    s.append(h2("8. Buenas prácticas pedagógicas"))
    s.append(
        callout(
            "1. ELO bajo no es mal estudiante",
            "El ELO refleja desempeño en el rango de dificultad probado. Un estudiante con ELO 1200 que solo "
            "ve preguntas de dificultad 1100 puede estar consolidando antes de subir. Mira el <i>ELO history</i> "
            "para ver tendencias, no valores aislados.",
            accent=SUCCESS,
        )
    )
    s.append(spacer(4))
    s.append(
        callout(
            "2. Procedimientos > respuestas",
            "La pregunta de selección múltiple mide el resultado. El procedimiento mide el pensamiento. "
            "Si un estudiante responde correcto pero su procedimiento muestra saltos lógicos, vale la pena calificarlo bajo. "
            "Inversamente, un procedimiento correcto con respuesta marcada mal (error de transcripción) merece bonificación.",
        )
    )
    s.append(spacer(4))
    s.append(
        callout(
            "3. KatIA no reemplaza tu rol",
            "KatIA da pistas socráticas sin revelar la respuesta. No conoce el contexto de tu clase ni los acuerdos pedagógicos. "
            "Usa el historial de KatIA como insumo, no como autoridad.",
            accent=WARNING,
        )
    )

    # 9. Cierre
    s.append(h2("9. Resolución de problemas"))
    s.append(
        bullet(
            "<b>“Un estudiante no aparece en mi grupo”</b> — verifica que se haya inscrito al curso correcto y que el código de invitación esté activo."
        )
    )
    s.append(
        bullet(
            "<b>“La IA no analiza el procedimiento”</b> — necesitas una API key de Groq (preferida) o Anthropic en tu sidebar bajo “API de IA”."
        )
    )
    s.append(
        bullet(
            "<b>“No puedo crear el examen, falla al guardar”</b> — algún <font face='Mono'>item_id</font> seleccionado no existe en el curso. Refresca el catálogo."
        )
    )
    s.append(
        bullet(
            "<b>“Asigné el examen pero el estudiante no lo ve”</b> — confirma que el estudiante esté en uno de los grupos asignados y que la ventana <i>From / Until</i> incluya la fecha actual."
        )
    )

    s.append(spacer(20))
    s.append(
        Paragraph(
            "<i>LevelUp-ELO · Plataforma desarrollada por Luis J. Rubio H. · "
            "Cualquier duda, usa el botón “Report a problem” en tu sidebar.</i>",
            STYLES["CalloutText"],
        )
    )

    return s


# ── Contenido: Guía Estudiante ────────────────────────────────────────────────
def estudiante_story():
    s = []

    s.append(spacer(40))
    s.append(Paragraph("Guía del Estudiante", STYLES["H1"]))
    s.append(Paragraph("Cómo aprender mejor con LevelUp-ELO", STYLES["Lead"]))
    s.append(spacer(10))
    s.append(
        p(
            "LevelUp-ELO es una plataforma para practicar matemáticas que se adapta a tu nivel. "
            "A diferencia de un libro que tiene un orden fijo, aquí cada pregunta se elige para "
            "ti según lo que estás dominando: ni tan fácil que te aburras, ni tan difícil que te frustres."
        )
    )
    s.append(spacer(6))
    s.append(
        callout(
            "Lo más importante",
            "Tu objetivo no es responder rápido ni acumular puntos. Es <b>entender</b>. Si fallas, "
            "es una oportunidad para corregir. Tu ELO subirá y bajará — esa es la señal de que el "
            "sistema está calibrando lo que sabes.",
        )
    )

    # 1. Registro y acceso
    s.append(h2("1. Registro y acceso"))
    s.append(h3("Primera vez"))
    s.extend(
        numbered(
            [
                "Abre <font face='Mono'>luislevelupelo.vercel.app</font> en cualquier navegador.",
                "Click en <b>Regístrate</b>.",
                "Selecciona el rol <b>Estudiante</b> → <i>Siguiente</i>.",
                "Llena: usuario (3–50 chars, único), contraseña (mínimo 6), email opcional, nivel educativo (Colegio/Universidad/Semillero) y grado si es Semillero.",
                "Click en <b>Registrarse</b>. Entras directo — no necesitas aprobación.",
            ]
        )
    )
    s.append(spacer(4))
    s.append(
        callout(
            "Si olvidas tu contraseña",
            "<b>No hay recuperación automática.</b> Si pusiste un email al registrarte, podrás pedir ayuda al docente o al administrador. "
            "Anota tu contraseña en un lugar seguro la primera vez.",
            accent=WARNING,
        )
    )

    # 2. Inscribirse a cursos
    s.append(h2("2. Inscribirte en cursos"))
    s.append(p("Ve a <b>Courses</b> en el sidebar. Tienes tres pestañas:"))
    s.append(bullet("<b>Explore</b> — todos los cursos disponibles para tu nivel educativo."))
    s.append(bullet("<b>My enrollments</b> — los cursos en los que ya estás inscrito."))
    s.append(
        bullet("<b>Access code</b> — para entrar a un curso con un código que te dio tu docente.")
    )
    s.append(spacer(4))
    s.append(h3("Cursos por nivel educativo"))
    s.append(
        info_table(
            [
                ("Colegio", "Aritmética Básica, Álgebra Básica, Geometría, Trigonometría."),
                (
                    "Universidad",
                    "Cálculo Diferencial, Cálculo Integral, Cálculo Varias Variables, Álgebra Lineal, Ecuaciones Diferenciales, Probabilidad.",
                ),
                (
                    "Semillero (6° a 11°)",
                    "Álgebra, Aritmética, Conteo y Combinatoria, Geometría, Lógica, Probabilidad — adaptados por grado.",
                ),
                ("Concursos", "DIAN, SENA y otros (acceso por código de invitación)."),
            ]
        )
    )

    # 3. Sala de práctica
    s.append(h2("3. Sala de práctica"))
    s.append(
        p(
            "Es el corazón de la plataforma. Click en <b>Practice</b> en el sidebar y elige un curso."
        )
    )
    s.append(h3("Qué pasa cuando respondes"))
    s.extend(
        numbered(
            [
                "El sistema te muestra una pregunta cuya dificultad estima que te dará <b>40–75%</b> de probabilidad de éxito (zona de desarrollo próximo).",
                "Elige una de las opciones múltiples y haz clic en <b>Submit</b>.",
                "Verás de inmediato si acertaste, cuánto ELO ganaste/perdiste, y un mensaje de KatIA según tu desempeño.",
                "Pasa a la siguiente pregunta. Tu siguiente desafío se elige en función del nuevo ELO.",
            ]
        )
    )
    s.append(h3("Pedirle ayuda a KatIA antes de responder"))
    s.append(
        p(
            "Si no entiendes la pregunta, haz clic en <b>Ask KatIA</b>. KatIA te dará una "
            "<b>pista socrática</b> — una pregunta que te hace pensar, no la respuesta directa. "
            "Las conversaciones con KatIA quedan registradas para tu docente."
        )
    )
    s.append(spacer(4))
    s.append(
        callout(
            "Sobre el ELO y los niveles",
            "Tu ELO inicial es 1000. Hay 16 niveles, desde <b>Aspirante</b> (0–399) hasta <b>Leyenda Suprema</b> (2500+). "
            "Sube tu nivel respondiendo preguntas difíciles correctamente. El ELO se mide por tópico, no como número único — "
            "puedes ser fuerte en Trigonometría y estar empezando en Probabilidad.",
        )
    )

    # 4. Procedimientos
    s.append(h2("4. Subir procedimientos escritos a mano"))
    s.append(p("Hay dos lugares para subir procedimientos:"))
    s.append(h3("Opción A: vinculado a la pregunta (recomendado)"))
    s.extend(
        numbered(
            [
                "Durante la práctica, debajo de la pregunta verás <b>Subir procedimiento manuscrito</b>.",
                "Toma una foto clara de tu trabajo en papel.",
                "Súbela. La IA te dará feedback inmediato (si tu docente lo habilitó).",
                "Tu docente lo recibirá en su bandeja para calificarlo manualmente.",
            ]
        )
    )
    s.append(h3("Opción B: ejercicio suelto (Open Procedure)"))
    s.append(
        p(
            "Para ejercicios abiertos o desarrollos largos no asociados a una pregunta del banco. "
            "Ve a <b>Open Proc.</b> en el sidebar, sube tu foto, agrega contexto si quieres, y se enviará a tu docente."
        )
    )
    s.append(spacer(4))
    s.append(
        callout(
            "Calidad de la foto",
            "Buena iluminación, sin sombras, perpendicular a la hoja. Si la imagen es ilegible, "
            "ni la IA ni el docente podrán calificarte bien.",
        )
    )

    # 5. Estadísticas
    s.append(h2("5. Tus estadísticas (Statistics)"))
    s.append(p("Ve a <b>Statistics</b> en el sidebar. Encontrarás:"))
    s.append(
        bullet(
            "<b>ELO global</b> — promedio de tus ELO por tópico, con tu nivel actual y siguiente."
        )
    )
    s.append(bullet("<b>Racha</b> — días consecutivos practicando."))
    s.append(bullet("<b>Total de intentos</b> — cuántas preguntas has respondido."))
    s.append(
        bullet(
            "<b>Radar por tópico</b> — gráfico circular que muestra tus fortalezas y debilidades."
        )
    )
    s.append(bullet("<b>Heatmap de actividad</b> — calendario con los días que practicaste."))
    s.append(bullet("<b>Ranking grupal</b> — tu posición dentro de tu grupo."))
    s.append(
        bullet(
            "<b>Logros</b> — medallas que desbloqueas por hitos (primera correcta, 10 seguidas correctas, etc.)."
        )
    )
    s.append(
        bullet("<b>Historial de exámenes</b> — todos los exámenes que has tomado con su puntaje.")
    )

    # 6. Examen
    s.append(h2("6. Modo examen"))
    s.append(p("Ve a <b>Exam</b> en el sidebar. Tienes dos tipos:"))
    s.append(h3("Standard (auto)"))
    s.append(
        p(
            "Examen generado automáticamente con una curva de dificultad 30/40/30 (fácil/medio/difícil). "
            "Tú eliges cuántas preguntas (5–30) y cuánto tiempo (5–60 min). El examen <b>no afecta tu ELO</b> — "
            "es solo una evaluación de tu nivel actual."
        )
    )
    s.append(h3("From teacher"))
    s.append(
        p(
            "Examen creado por tu docente. Si hay alguno disponible para ti, verás un <b>punto rojo</b> "
            "sobre el ítem “Exam” en tu sidebar. El número indica cuántos exámenes tienes pendientes. "
            "Las preguntas, el tiempo y el orden los define tu docente."
        )
    )
    s.append(spacer(4))
    s.append(
        callout(
            "Reglas del examen",
            "No hay pistas, no hay KatIA, no hay feedback inmediato. Verás el resultado completo al final. "
            "Si te quedas sin tiempo, las preguntas no respondidas cuentan como incorrectas.",
            accent=DANGER,
        )
    )

    # 7. KatIA
    s.append(h2("7. KatIA — tu tutora socrática"))
    s.append(
        p(
            "KatIA es una IA con personalidad de tutora gata cyborg. Su trabajo es <b>hacerte pensar</b>, no darte la respuesta. "
            "Ella sigue el método socrático: te hace preguntas que te ayudan a descubrir el camino por tu cuenta."
        )
    )
    s.append(h3("Cómo invocarla"))
    s.append(bullet("Durante una pregunta de práctica → botón <b>Ask KatIA</b>."))
    s.append(
        bullet("Le puedes hablar en español, escribir tus dudas, mostrarle dónde te atascaste.")
    )
    s.append(spacer(4))
    s.append(
        callout(
            "Lo que KatIA NO hará",
            "<b>No te dirá la opción correcta.</b> Si insistes, te repetirá la pregunta socrática de otra forma. "
            "Tu docente verá tus conversaciones con ella, así que aprovecha el espacio para pensar en voz alta, "
            "no para tratar de “engañarla”.",
        )
    )

    # 8. Retroalimentación
    s.append(h2("8. Retroalimentación de tu docente"))
    s.append(p("Ve a <b>Feedback</b> en el sidebar. Verás:"))
    s.append(bullet("Todos tus procedimientos enviados."))
    s.append(
        bullet(
            "Su estado: <i>pendiente</i> (esperando docente), <i>revisado por IA</i> (con feedback automático), <i>calificado</i> (puntaje final del docente)."
        )
    )
    s.append(
        bullet(
            "La imagen original, la sugerencia de la IA, el comentario del docente y la imagen de retroalimentación si tu docente la subió."
        )
    )
    s.append(bullet("Mensaje motivador de KatIA según el puntaje."))

    # 9. Reportar
    s.append(h2("9. Reportar un problema"))
    s.append(
        p(
            "Si encuentras una pregunta con error, una imagen rota, o cualquier bug, usa el botón "
            "<b>Report a problem</b> en tu sidebar. Describe el problema con detalle (mínimo 10 caracteres). "
            "El reporte llegará directo al administrador."
        )
    )

    # 10. Configuración
    s.append(h2("10. Configuración personal"))
    s.append(
        bullet(
            "<b>API de IA</b> — si tienes una API key propia (Groq, Claude, OpenAI), la puedes poner en el panel para que tus interacciones con KatIA sean ilimitadas. Si no, se usa la clave del sistema."
        )
    )
    s.append(bullet("<b>Tema</b> — claro u oscuro, según prefieras."))
    s.append(bullet("<b>Idioma</b> — Español o English. El selector está al final del sidebar."))
    s.append(
        bullet(
            "<b>Email</b> — si no lo pusiste al registrarte, puedes agregarlo desde el botón naranja del sidebar."
        )
    )

    # 11. Consejos
    s.append(h2("11. Consejos para sacar más provecho"))
    s.append(
        callout(
            "1. Constancia > intensidad",
            "Practicar 15 minutos cada día funciona mejor que 3 horas un sábado. Tu racha lo refleja.",
            accent=SUCCESS,
        )
    )
    s.append(spacer(4))
    s.append(
        callout(
            "2. Falla a propósito",
            "Si solo respondes preguntas fáciles, tu ELO subirá poco. Acepta fallar el 30% de las veces — es donde más aprendes.",
        )
    )
    s.append(spacer(4))
    s.append(
        callout(
            "3. Sube tu procedimiento aunque acertaste",
            "Acertar la opción correcta no significa que el procedimiento esté bien. Si subes tu trabajo, tu docente puede corregirte un error de método que la pregunta de selección múltiple oculta.",
        )
    )
    s.append(spacer(4))
    s.append(
        callout(
            "4. Habla con KatIA",
            "No la uses solo como “buscador de pistas”. Cuéntale qué intentaste, qué no entendiste. Mientras más te explayes, mejor te ayuda.",
        )
    )

    s.append(spacer(20))
    s.append(
        Paragraph(
            "<i>LevelUp-ELO · Plataforma desarrollada por Luis J. Rubio H. · "
            "¡Suerte y disfruta el camino!</i>",
            STYLES["CalloutText"],
        )
    )

    return s


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    out_dir = Path(__file__).parent.parent
    build_pdf(
        str(out_dir / "guia_docente.pdf"),
        title="Guía del Docente",
        kind="docente",
        story=docente_story(),
    )
    build_pdf(
        str(out_dir / "guia_estudiante.pdf"),
        title="Guía del Estudiante",
        kind="estudiante",
        story=estudiante_story(),
    )


if __name__ == "__main__":
    main()
