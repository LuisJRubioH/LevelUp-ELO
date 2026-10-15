import { Fragment, useMemo } from "react";
import katex from "katex";
import "katex/dist/katex.min.css";
import "./MathContent.css";

type MathFormulaProps = {
  math: string;
  display?: boolean;
  ariaLabel?: string;
  className?: string;
};

/** Corrige escapes duplicados frecuentes al atravesar JSON, sin alterar saltos LaTeX. */
export function normalizeLatex(source: string): string {
  let value = source.trim();
  if (value.startsWith("$$") && value.endsWith("$$")) value = value.slice(2, -2);
  else if (value.startsWith("$") && value.endsWith("$")) value = value.slice(1, -1);
  else if (
    (value.startsWith("\\(") && value.endsWith("\\)")) ||
    (value.startsWith("\\[") && value.endsWith("\\]"))
  ) {
    value = value.slice(2, -2);
  }

  return value
    .replace(/\\\\(?=[A-Za-z])/g, "\\")
    .replace(/\\(mathbb|mathbf|mathrm)([A-Z0-9])\b/g, "\\$1{$2}")
    .replace(/\\text\{✸\}|✸/g, "\\star")
    .replace(/○/g, "\\bigcirc");
}

/**
 * Un slot de fórmula al que le llega PROSA con `$...$` intercalado (pasa cuando
 * el autor del nodo escribe "$12mx^{2}-12m$ tratado como…" en `cases.division`
 * o en `methods.steps`) caía al fallback y el estudiante veía los delimitadores
 * en crudo. Se delega en MathText, que sí sabe mezclar texto y matemática.
 */
export function MathFormula(props: MathFormulaProps) {
  if (/(?<!\\)\$/.test(normalizeLatex(props.math))) {
    return <MathText text={props.math} className={props.className} />;
  }
  return <Katex {...props} />;
}

function Katex({ math, display = false, ariaLabel, className = "" }: MathFormulaProps) {
  const normalized = normalizeLatex(math);
  const rendered = useMemo(() => {
    try {
      return {
        html: katex.renderToString(normalized, {
          displayMode: display,
          throwOnError: true,
          strict: "warn",
          trust: false,
          output: "htmlAndMathml",
        }),
        failed: false,
      };
    } catch {
      return { html: "", failed: true };
    }
  }, [display, normalized]);

  // Un `aria-label` sobre un <span> pelado lo ignoran casi todos los lectores de
  // pantalla: solo nombran elementos con rol que admita nombre de autor. Con
  // role="img" la etiqueta SUSTITUYE al contenido, que es justo lo que se busca
  // — leer «tres cuartos» en vez de deletrear el MathML de \dfrac{3}{4}.
  // Sin `ariaLabel` no se pone rol: gana el MathML que emite KaTeX.
  const named = ariaLabel ? { role: "img" as const, "aria-label": ariaLabel } : {};

  if (rendered.failed) {
    return (
      <span
        className={`math-fallback ${display ? "math-display" : ""} ${className}`.trim()}
        role="img"
        aria-label={ariaLabel ?? normalized}
        data-math-error="true"
      >
        {normalized}
      </span>
    );
  }

  return (
    <span
      className={`math-rendered ${display ? "math-display" : ""} ${className}`.trim()}
      {...named}
      dangerouslySetInnerHTML={{ __html: rendered.html }}
    />
  );
}

type MathTextProps = {
  text: string;
  className?: string;
};

/** Renderiza texto mixto con $, $$, \(...\) y \[...\] desde una sola implementación. */
export function MathText({ text, className = "" }: MathTextProps) {
  // Un \$ dentro de la expresión es moneda, no el delimitador de cierre.
  const tokens = text.split(
    /(\$\$(?:\\\$|[\s\S])*?\$\$|\\\[[\s\S]+?\\\]|(?<!\\)\$(?:\\\$|[^$\n])+?(?<!\\)\$|\\\([\s\S]+?\\\))/g,
  );
  return (
    <span className={className}>
      {tokens.map((token, index) => {
        let math: string | null = null;
        let display = false;
        if (token.startsWith("$$") && token.endsWith("$$")) {
          math = token.slice(2, -2);
          display = true;
        } else if (token.startsWith("\\[") && token.endsWith("\\]")) {
          math = token.slice(2, -2);
          display = true;
        } else if (token.startsWith("$") && token.endsWith("$")) {
          math = token.slice(1, -1);
        } else if (token.startsWith("\\(") && token.endsWith("\\)")) {
          math = token.slice(2, -2);
        }

        return math === null ? (
          <Fragment key={index}>{token}</Fragment>
        ) : (
          // Katex y no MathFormula: el token ya viene sin delimitadores y
          // delegar de vuelta sería recursión infinita.
          <Katex key={index} math={math} display={display} />
        );
      })}
    </span>
  );
}
