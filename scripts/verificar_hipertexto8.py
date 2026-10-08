"""Verifica la transcripción de los ejercicios de Hipertexto Matemáticas 8.

El PDF es un escaneo sin capa de texto útil, así que cada ejercicio se transcribe
a mano leyendo la página. Este script es el guardarraíl contra ese riesgo: vuelve
a calcular con sympy toda expresión transcrita y compara con la respuesta
registrada. Un dígito mal leído casi siempre rompe la igualdad.

    python scripts/verificar_hipertexto8.py           # verifica todo
    python scripts/verificar_hipertexto8.py --pagina 12

Tipos verificables:
  numerico    -> `expr` debe evaluar exactamente a `respuesta`
  comparacion -> el signo entre `izquierda` y `derecha` debe ser `respuesta`
  ecuacion    -> las soluciones de `ecuacion` deben ser `soluciones`
  orden       -> `respuesta` debe ser `valores` ordenado de mayor a menor
  intervalo   -> cada decimal propuesto debe caer estrictamente entre `limites`
  racionalidad-> sympy decide si `valor` es racional o irracional
  mismo_valor -> si todos los `valores` son el mismo número ('si'/'no')
  simbolico   -> `expr` y `respuesta` deben ser algebraicamente equivalentes

`abierta` (justificar, representar en la recta, redactar) no es verificable
automáticamente: se cuenta aparte y nunca se convierte en práctica autocalificada.

Dos campos distintos para los problemas del libro, y no son intercambiables:

  erratum   -> error del libro CONFIRMADO y ya corregido en `expr`/`respuesta`.
               El ítem queda listo para usar; el campo solo deja constancia.
  verificar -> duda MÍA que alguien debe resolver antes de reutilizar el ítem:
               una lectura ambigua, un enunciado que admite dos versiones con
               respuestas distintas, una respuesta que no es única.

Solo `verificar` se imprime como REVISAR al final. Por eso, si se responde
contra la lectura literal sin corregir nada, va en `verificar`: en `erratum`
quedaría invisible.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sympy import (
    Eq,
    cancel,
    expand,
    powdenest,
    powsimp,
    simplify,
    solve,
    symbols,
    sympify,
)

ROOT = Path(__file__).resolve().parents[1]
FUENTE = ROOT / "items" / "source" / "hipertexto8"

# El manifiesto del OCR marcó estas páginas como "con ejercicios", pero al mirarlas
# a alto DPI resultaron ser infografía pura, sin ninguna actividad que transcribir.
# Se cuentan como hechas para que el informe de progreso no las pida siempre.
SIN_EJERCICIOS = frozenset(
    {
        94,
        95,  # "Matemáticas + Tecnología: la hoja de cálculo", solo rótulos
    }
)

TIPOS_VERIFICABLES = {
    "numerico",
    "comparacion",
    "ecuacion",
    "orden",
    "intervalo",
    "racionalidad",
    "mismo_valor",
    "simbolico",
}


def _valor(expresion: str):
    return sympify(expresion, rational=True)


def verificar(item: dict) -> str | None:
    """Devuelve un mensaje de error, o None si el ítem cuadra."""
    tipo = item["tipo"]
    try:
        if tipo == "numerico":
            obtenido = _valor(item["expr"])
            esperado = _valor(item["respuesta"])
            if obtenido != esperado:
                return f"expr={item['expr']} da {obtenido}, pero respuesta dice {esperado}"

        elif tipo == "comparacion":
            izq, der = _valor(item["izquierda"]), _valor(item["derecha"])
            signo = "=" if izq == der else (">" if izq > der else "<")
            if signo != item["respuesta"]:
                return (
                    f"{item['izquierda']} ({izq}) vs {item['derecha']} ({der}) "
                    f"da '{signo}', pero respuesta dice '{item['respuesta']}'"
                )
            # Los ítems de "¿es verdadera esta igualdad?" declaran además su veredicto.
            if "veredicto" in item:
                esperado = "V" if signo == "=" else "F"
                if item["veredicto"] != esperado:
                    return f"el signo real es '{signo}', luego el veredicto es {esperado}"

        elif tipo == "simbolico":
            # Igualdad algebraica: no basta comparar estructuras, hay que simplificar.
            diferencia = simplify(_valor(item["expr"]) - _valor(item["respuesta"]))
            if diferencia != 0:
                # Con exponentes literales (a**x * a**(x+1)) simplify se queda corto:
                # powsimp es quien aplica a^m·a^n = a^(m+n). force=True porque aquí las
                # bases son letras del ejercicio, no números que puedan ser 0 o negativos.
                diferencia = powsimp(expand(diferencia), force=True)
            if diferencia != 0:
                # En cocientes notables la diferencia queda como fracción y sobrevive
                # algún (x**2)**n que powsimp no toca: cancel junta la fracción y
                # powdenest es quien aplana (x**2)**n -> x**(2*n).
                diferencia = powsimp(powdenest(cancel(diferencia), force=True), force=True)
            if diferencia != 0:
                return (
                    f"expr={item['expr']} y respuesta={item['respuesta']} "
                    f"no son equivalentes; su diferencia simplifica a {diferencia}"
                )

        elif tipo == "mismo_valor":
            valores = [_valor(v) for v in item["valores"]]
            iguales = len(set(valores)) == 1
            real = "si" if iguales else "no"
            if real != item["respuesta"]:
                distintos = sorted({str(v) for v in valores})
                return f"los valores son {distintos}: la respuesta correcta es '{real}'"

        elif tipo == "racionalidad":
            valor = _valor(item["valor"])
            es_racional = valor.is_rational
            if es_racional is None:
                return f"sympy no decide si {item['valor']} es racional; clasificar a mano"
            real = "racional" if es_racional else "irracional"
            if real != item["respuesta"]:
                return f"{item['valor']} = {valor} es {real}, no {item['respuesta']}"

        elif tipo == "intervalo":
            a, b = sorted(_valor(v) for v in item["limites"])
            fuera = [v for v in item["respuesta"] if not a < _valor(v) < b]
            if fuera:
                return f"{fuera} no está(n) estrictamente entre {a} y {b}"
            if len(item["respuesta"]) != len(set(item["respuesta"])):
                return "los decimales propuestos están repetidos"

        elif tipo == "orden":
            valores = [_valor(v) for v in item["valores"]]
            declarado = [_valor(v) for v in item["respuesta"]]
            if sorted(valores, reverse=True) != declarado:
                esperado = [str(v) for v in sorted(valores, reverse=True)]
                return f"el orden de mayor a menor es {esperado}, no {item['respuesta']}"
            if len(declarado) != len(valores):
                return "la respuesta no tiene la misma cantidad de números que el enunciado"

        elif tipo == "ecuacion":
            incognita = symbols(item.get("incognita", "n"))
            izq, der = item["ecuacion"].split("=")
            obtenidas = solve(Eq(_valor(izq), _valor(der)), incognita)
            esperadas = [_valor(s) for s in item["soluciones"]]
            if len(obtenidas) != len(esperadas):
                return f"ecuacion {item['ecuacion']} da {obtenidas}, se esperaba {esperadas}"
            # sympy devuelve la solución en la forma que se le antoje (a menudo
            # factorizada), así que no sirve comparar strings: hay que emparejar
            # cada esperada con una obtenida que simplifique a la misma cosa.
            libres = list(obtenidas)
            for esperada in esperadas:
                pareja = next((o for o in libres if simplify(o - esperada) == 0), None)
                if pareja is None:
                    return (
                        f"ecuacion {item['ecuacion']} da {obtenidas}, "
                        f"y ninguna equivale a {esperada}"
                    )
                libres.remove(pareja)

    except Exception as exc:  # transcripción que ni siquiera parsea
        return f"no se pudo evaluar ({type(exc).__name__}: {exc})"
    return None


def progreso() -> int:
    """Avance de la transcripción, derivado de los datos: nada que mantener a mano.

    Las páginas con ejercicios salen del manifiesto que dejó el primer pase de OCR;
    las transcritas, de los propios fragmentos JSON.
    """
    import csv
    import itertools

    manifiesto = ROOT / "output" / "latex" / "listas_ejercicios_matematicas_8" / "manifest.csv"
    filas = [
        f
        for f in csv.DictReader(manifiesto.open(encoding="utf-8-sig"))
        if f["libro"] == "hipertexto_matematicas_8"
    ]
    hechas = {
        item["pagina_pdf"]
        for archivo in FUENTE.glob("*.json")
        for item in json.loads(archivo.read_text(encoding="utf-8"))
    } | SIN_EJERCICIOS

    total = len(filas)
    for unidad, grupo in itertools.groupby(filas, key=lambda f: (f["unidad"], f["titulo_unidad"])):
        paginas = [int(f["pagina_pdf"]) for f in grupo]
        listas = [p for p in paginas if p in hechas]
        marca = "OK " if len(listas) == len(paginas) else "   "
        pendientes = [str(p) for p in paginas if p not in hechas]
        print(
            f"{marca}U{unidad[0]:>2} {unidad[1][:34]:34s} {len(listas):>2}/{len(paginas):<2}"
            + (f"  faltan: {', '.join(pendientes)}" if pendientes else "")
        )
    print(f"\n{len(hechas)}/{total} páginas con ejercicios transcritas")
    return 0


def main() -> int:
    # Los enunciados llevan símbolos matemáticos; la consola de Windows es cp1252.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser()
    parser.add_argument("--pagina", type=int, help="verificar solo una página del PDF")
    parser.add_argument(
        "--progreso",
        action="store_true",
        help="qué páginas con ejercicios ya están transcritas y cuáles faltan",
    )
    args = parser.parse_args()

    if args.progreso:
        return progreso()

    items: list[dict] = []
    for archivo in sorted(FUENTE.glob("*.json")):
        items.extend(json.loads(archivo.read_text(encoding="utf-8")))
    if args.pagina:
        items = [i for i in items if i["pagina_pdf"] == args.pagina]
    if not items:
        print(f"Sin ítems en {FUENTE.relative_to(ROOT)}")
        return 1

    fallos: list[str] = []
    verificados = revisar_manual = 0
    for item in items:
        if item["tipo"] in TIPOS_VERIFICABLES:
            error = verificar(item)
            if error:
                fallos.append(f"{item['id']}: {error}")
            else:
                verificados += 1
        else:
            revisar_manual += 1

    for f in fallos:
        print(f"FALLA  {f}")
    pendientes = [i["id"] for i in items if i.get("verificar")]
    for ident in pendientes:
        print(f"REVISAR  {ident}: {next(i for i in items if i['id'] == ident)['verificar']}")

    print(
        f"\n{len(items)} ejercicios · {verificados} recalculados OK · "
        f"{revisar_manual} abiertos (sin verificación automática) · {len(fallos)} fallas"
    )
    return 1 if fallos else 0


if __name__ == "__main__":
    raise SystemExit(main())
