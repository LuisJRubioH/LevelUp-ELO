import { readFileSync, readdirSync, statSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import katex from "katex";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..", "..", "items", "bank");

function filesUnder(directory) {
  return readdirSync(directory).flatMap((name) => {
    const path = join(directory, name);
    return statSync(path).isDirectory() ? filesUnder(path) : path.endsWith(".json") ? [path] : [];
  });
}

function normalizeLatex(source) {
  return source
    .trim()
    .replace(/\\\\(?=[A-Za-z])/g, "\\")
    .replace(/\\(mathbb|mathbf|mathrm)([A-Z0-9])\b/g, "\\$1{$2}")
    .replace(/\\text\{✸\}|✸/g, "\\star")
    .replace(/○/g, "\\bigcirc");
}

function formulasIn(text) {
  return [...text.matchAll(/\$\$((?:\\\$|[\s\S])*?)\$\$|(?<!\\)\$((?:\\\$|[^$\n])+?)(?<!\\)\$/g)].map(
    (match) => match[1] ?? match[2],
  );
}

const failures = [];
let checked = 0;
const smokeFormulas = [
  String.raw`\mathbb{N}`,
  String.raw`\\mathbb{R}\\setminus\\mathbb{Q}`,
  String.raw`\mathbbN\subset\mathbbZ\subset\mathbbQ\subset\mathbbR`,
  String.raw`3^{\circ}-5^{\circ}`,
  String.raw`\frac{○}{3}+\text{✸}`,
];

for (const formula of smokeFormulas) {
  checked += 1;
  try {
    katex.renderToString(normalizeLatex(formula), { throwOnError: true, strict: "warn" });
  } catch (error) {
    failures.push(`smoke :: ${formula} :: ${error.message}`);
  }
}

for (const file of filesUnder(root)) {
  const items = JSON.parse(readFileSync(file, "utf8"));
  for (const item of items) {
    const values = [item.content, ...(item.options ?? []), item.correct_option].filter(
      (value) => typeof value === "string",
    );
    for (const value of values) {
      for (const formula of formulasIn(value)) {
        checked += 1;
        try {
          katex.renderToString(normalizeLatex(formula), { throwOnError: true, strict: "warn" });
        } catch (error) {
          failures.push(`${file} :: ${item.id} :: ${formula} :: ${error.message}`);
        }
      }
    }
  }
}

if (failures.length) {
  console.error(`LaTeX inválido: ${failures.length} de ${checked} expresiones.`);
  console.error(failures.join("\n"));
  process.exitCode = 1;
} else {
  console.log(`LaTeX OK: ${checked} expresiones validadas con KaTeX.`);
}
