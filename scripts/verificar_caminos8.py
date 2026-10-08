"""Valida la extracción de Los Caminos del Saber Matemáticas 8.

Reutiliza los cálculos simbólicos del verificador de Hipertexto 8 y añade los
tipos propios que aparezcan en este libro. También informa el progreso usando
``items/source/caminos8/_manifiesto.json``.

    python scripts/verificar_caminos8.py
    python scripts/verificar_caminos8.py --pagina 8
    python scripts/verificar_caminos8.py --progreso
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

from sympy import (
    And,
    Eq,
    cancel,
    div,
    expand,
    gcd_list,
    lcm_list,
    simplify,
    solve,
    symbols,
    sympify,
    together,
)

from verificar_hipertexto8 import (
    TIPOS_VERIFICABLES as TIPOS_BASE,
    verificar as verificar_base,
)

ROOT = Path(__file__).resolve().parents[1]
FUENTE = ROOT / "items" / "source" / "caminos8"
MANIFIESTO = FUENTE / "_manifiesto.json"

TIPOS_VERIFICABLES = TIPOS_BASE | {
    "clasificacion_conjuntos",
    "cuadro_magico_aditivo",
    "conjunto_extension",
    "cuadro_magico_multiplicativo",
    "conjunto_natural",
    "decimal_a_fraccion",
    "despeje",
    "division_polinomios",
    "ecuacion_real",
    "inecuacion_lineal",
    "mcd_polinomios",
    "mcm_polinomios",
    "orden_asociado",
    "residuos_simultaneos",
    "secuencia_aritmetica",
    "secuencia_geometrica",
    "valores_numericos",
}
REQUERIDOS = {
    "id",
    "tipo",
    "enunciado",
    "respuesta",
    "conjunto",
    "seccion",
    "unidad",
    "pagina_pdf",
    "referencia",
    "apto_para",
    "dificultad",
}


def verificar(item: dict) -> str | None:
    if item["tipo"] == "simbolico" and "veredicto" in item and "afirmacion" in item:
        error = verificar_base(item)
        if error:
            return error
        expresion = sympify(item["expr"], rational=True)
        afirmacion = sympify(item["afirmacion"], rational=True)
        diferencia = simplify(cancel(together(expresion - afirmacion)))
        veredicto = "V" if diferencia == 0 else "F"
        if item["veredicto"] != veredicto:
            return f"la igualdad propuesta da {veredicto}, no {item['veredicto']}"
        return None

    if item["tipo"] == "ecuacion_real":
        nombre = item.get("incognita", "x")
        incognita = symbols(nombre, real=True)
        locales = {nombre: incognita}
        izq, der = item["ecuacion"].split("=")
        obtenidas = solve(
            Eq(
                sympify(izq, locals=locales, rational=True),
                sympify(der, locals=locales, rational=True),
            ),
            incognita,
        )
        esperadas = [sympify(solucion, rational=True) for solucion in item["soluciones"]]
        if len(obtenidas) != len(esperadas):
            return f"ecuacion real {item['ecuacion']} da {obtenidas}, se esperaba {esperadas}"
        libres = list(obtenidas)
        for esperada in esperadas:
            pareja = next((valor for valor in libres if simplify(valor - esperada) == 0), None)
            if pareja is None:
                return (
                    f"ecuacion real {item['ecuacion']} da {obtenidas}, "
                    f"y ninguna solución equivale a {esperada}"
                )
            libres.remove(pareja)
        return None

    if item["tipo"] == "despeje":
        nombre = item.get("incognita", "x")
        incognita = symbols(nombre)
        izq, der = item["ecuacion"].split("=")
        obtenidas = solve(
            Eq(sympify(izq, rational=True), sympify(der, rational=True)),
            incognita,
        )
        esperada = sympify(item["solucion"], rational=True)
        if not any(simplify(cancel(together(obtenida - esperada))) == 0 for obtenida in obtenidas):
            return (
                f"al despejar {nombre} en {item['ecuacion']} se obtiene {obtenidas}, "
                f"no {esperada}"
            )
        return None

    if item["tipo"] in {"mcd_polinomios", "mcm_polinomios"}:
        expresiones = item.get("expresiones")
        if not isinstance(expresiones, list) or not expresiones:
            return f"{item['tipo']} requiere una lista no vacía en `expresiones`"
        valores = [sympify(expresion, rational=True) for expresion in expresiones]
        obtenido = gcd_list(valores) if item["tipo"] == "mcd_polinomios" else lcm_list(valores)
        esperado = sympify(item["respuesta"], rational=True)
        diferencia = expand(obtenido - esperado)
        # En Z[x], un mcd o mcm queda determinado salvo una unidad ±1.
        if diferencia != 0 and expand(obtenido + esperado) == 0:
            diferencia = 0
        if diferencia != 0:
            operacion = "mcd" if item["tipo"] == "mcd_polinomios" else "mcm"
            return f"el {operacion} calculado es {obtenido}, no {esperado}"
        if "veredicto" in item:
            afirmacion = sympify(item["afirmacion"], rational=True)
            veredicto = "V" if expand(obtenido - afirmacion) == 0 else "F"
            if item["veredicto"] != veredicto:
                return f"la afirmación sobre el divisor da {veredicto}, no {item['veredicto']}"
        return None

    if item["tipo"] == "division_polinomios":
        variable = symbols(item.get("variable", "x"))
        dividendo = sympify(item["dividendo"], rational=True)
        divisor = sympify(item["divisor"], rational=True)
        cociente = sympify(item["cociente"], rational=True)
        residuo = sympify(item.get("residuo", "0"), rational=True)
        if divisor == 0:
            return "el divisor no puede ser cero"
        cociente_real, residuo_real = div(dividendo, divisor, variable)
        if expand(cociente - cociente_real) != 0:
            return f"el cociente correcto es {cociente_real}, no {cociente}"
        if expand(residuo - residuo_real) != 0:
            return f"el residuo correcto es {residuo_real}, no {residuo}"
        return None

    if item["tipo"] == "cuadro_magico_aditivo":
        matriz = item["respuesta"]
        if (
            not isinstance(matriz, list)
            or not matriz
            or any(not isinstance(fila, list) or len(fila) != len(matriz) for fila in matriz)
        ):
            return "la respuesta debe ser una matriz cuadrada no vacía"
        valores = [[sympify(valor) for valor in fila] for fila in matriz]
        suma = sympify(item["suma_magica"])
        orden = len(valores)
        sumas = [
            *(sum(fila) for fila in valores),
            *(sum(valores[i][j] for i in range(orden)) for j in range(orden)),
            sum(valores[i][i] for i in range(orden)),
            sum(valores[i][orden - 1 - i] for i in range(orden)),
        ]
        if any(valor != suma for valor in sumas):
            return f"las sumas obtenidas son {sumas}, no todas {suma}"
        for posicion, valor in item.get("dados", {}).items():
            fila, columna = (int(indice) for indice in posicion.split(","))
            if valores[fila][columna] != sympify(valor):
                return f"la casilla dada {posicion} debe conservar el valor {valor}"
        return None

    if item["tipo"] == "valores_numericos":
        expresiones = item.get("exprs")
        respuestas = item.get("respuesta_valores")
        if not isinstance(expresiones, dict) or not isinstance(respuestas, dict):
            return "valores_numericos requiere `exprs` y `respuesta_valores` como objetos"
        if set(expresiones) != set(respuestas):
            return "`exprs` y `respuesta_valores` deben tener exactamente las mismas claves"
        for etiqueta, expresion in expresiones.items():
            obtenido = sympify(expresion, rational=True)
            esperado = sympify(respuestas[etiqueta], rational=True)
            diferencia = simplify(cancel(together(obtenido - esperado)))
            if diferencia != 0:
                return (
                    f"{etiqueta}: {expresion} no equivale a {esperado}; "
                    f"la diferencia se expande a {diferencia}"
                )
        return None

    if item["tipo"] == "conjunto_extension":
        minimo, maximo = (int(sympify(valor)) for valor in item["limites"])
        filtro = item["filtro"]

        def cumple(n: int) -> bool:
            if filtro == "todos":
                return True
            if filtro == "divisor_de":
                return n != 0 and int(sympify(item["objetivo"])) % n == 0
            if filtro == "impar":
                return n % 2 != 0
            if filtro == "par":
                return n % 2 == 0
            if filtro == "cuadratica_mas_constante_le":
                constante = int(sympify(item["constante"]))
                limite = int(sympify(item["limite"]))
                return n * n + constante <= limite
            if filtro == "multiplo_de_alguno":
                divisores = [int(sympify(valor)) for valor in item["divisores"]]
                return any(n % divisor == 0 for divisor in divisores)
            if filtro == "valor_absoluto_le":
                return abs(n) <= int(sympify(item["limite"]))
            raise ValueError(f"filtro de conjunto no reconocido: {filtro}")

        esperado = [n for n in range(minimo, maximo + 1) if cumple(n)]
        respuesta = [int(sympify(valor)) for valor in item["respuesta"]]
        if respuesta != esperado:
            return f"la extensión correcta es {esperado}, no {respuesta}"
        return None

    if item["tipo"] == "residuos_simultaneos":
        minimo, maximo = (int(sympify(valor)) for valor in item["limites"])
        divisores = [int(sympify(valor)) for valor in item["divisores"]]
        residuo = int(sympify(item["residuo"]))
        esperado = [
            n
            for n in range(minimo + 1, maximo)
            if all(n % divisor == residuo for divisor in divisores)
        ]
        respuesta = [int(sympify(valor)) for valor in item["respuesta"]]
        if respuesta != esperado:
            return f"los números que cumplen los residuos son {esperado}, no {respuesta}"
        return None

    if item["tipo"] == "clasificacion_conjuntos":
        esperadas = {"N": [], "Z": [], "Q": [], "I": []}
        for expresion in item["valores"]:
            valor = sympify(expresion)
            if valor.is_integer:
                categoria = "N" if valor >= 0 else "Z"
            elif valor.is_rational:
                categoria = "Q"
            elif valor.is_rational is False:
                categoria = "I"
            else:
                return f"no se pudo clasificar {expresion}"
            esperadas[categoria].append(str(valor))

        declaradas = {
            categoria: sorted(str(sympify(valor)) for valor in item["respuesta"][categoria])
            for categoria in esperadas
        }
        esperadas = {categoria: sorted(valores) for categoria, valores in esperadas.items()}
        if declaradas != esperadas:
            return f"la clasificación correcta es {esperadas}, no {declaradas}"
        return None

    if item["tipo"] == "inecuacion_lineal":
        coeficiente = sympify(item["coeficiente"])
        independiente = sympify(item["termino_independiente"])
        derecha = sympify(item["derecha"])
        if coeficiente == 0:
            return "inecuacion_lineal requiere un coeficiente distinto de cero"

        signo = item["signo"]
        if signo not in {">", "<", ">=", "<="}:
            return f"signo de desigualdad no reconocido: {signo}"
        cota = (derecha - independiente) / coeficiente
        signo_esperado = signo
        if coeficiente < 0:
            signo_esperado = {">": "<", "<": ">", ">=": "<=", "<=": ">="}[signo]

        cota_declarada = sympify(item["cota"])
        if cota_declarada != cota:
            return f"la cota correcta es {cota}, no {cota_declarada}"
        if item["signo_solucion"] != signo_esperado:
            return (
                f"al despejar, el signo debe ser {signo_esperado}, " f"no {item['signo_solucion']}"
            )
        return None

    if item["tipo"] == "cuadro_magico_multiplicativo":
        matriz = item["respuesta"]
        if (
            not isinstance(matriz, list)
            or len(matriz) != 3
            or any(not isinstance(fila, list) or len(fila) != 3 for fila in matriz)
        ):
            return "la respuesta debe ser una matriz de 3 por 3"
        valores = [[sympify(valor) for valor in fila] for fila in matriz]
        producto = sympify(item["producto_magico"])
        productos = [
            *(fila[0] * fila[1] * fila[2] for fila in valores),
            *(valores[0][j] * valores[1][j] * valores[2][j] for j in range(3)),
            valores[0][0] * valores[1][1] * valores[2][2],
            valores[0][2] * valores[1][1] * valores[2][0],
        ]
        if any(valor != producto for valor in productos):
            return f"los productos obtenidos son {productos}, no todos {producto}"
        for posicion, valor in item.get("dados", {}).items():
            fila, columna = (int(indice) for indice in posicion.split(","))
            if valores[fila][columna] != sympify(valor):
                return f"la casilla dada {posicion} debe conservar el valor {valor}"
        return None

    if item["tipo"] == "racionalidad" and "veredicto" in item:
        error = verificar_base(item)
        if error:
            return error
        afirmacion = item.get("afirmacion", "irracional")
        if afirmacion not in {"racional", "irracional"}:
            return f"afirmación de racionalidad no reconocida: {afirmacion}"
        esperado = "V" if item["respuesta"] == afirmacion else "F"
        if item["veredicto"] != esperado:
            return (
                f"el número es {item['respuesta']} y la afirmación dice {afirmacion}; "
                f"el veredicto debe ser {esperado}"
            )
        return None

    if item["tipo"] == "decimal_a_fraccion":
        patron = re.fullmatch(r"([+-]?)(\d+)\.(\d*)(?:\((\d+)\))?", item["decimal"])
        if patron is None:
            return "`decimal` debe usar punto y, si es periódico, paréntesis: -1.(4)"
        signo, entera, no_periodica, periodo = patron.groups()
        if periodo:
            completo = int(entera + no_periodica + periodo)
            prefijo = int(entera + no_periodica) if no_periodica else int(entera)
            numerador = completo - prefijo
            denominador = 10 ** len(no_periodica) * (10 ** len(periodo) - 1)
        else:
            numerador = int(entera + no_periodica)
            denominador = 10 ** len(no_periodica)
        obtenido = sympify(numerador) / denominador
        if signo == "-":
            obtenido = -obtenido
        esperado = sympify(item["respuesta"])
        if obtenido != esperado:
            return f"{item['decimal']} equivale a {obtenido}, no a {esperado}"
        return None

    if item["tipo"] == "secuencia_aritmetica":
        dados = [sympify(valor) for valor in item.get("dados", [])]
        respuesta = [sympify(valor) for valor in item.get("respuesta", [])]
        if len(dados) < 2 or not respuesta:
            return "secuencia_aritmetica requiere al menos dos datos y una respuesta"
        diferencia = dados[1] - dados[0]
        if any(b - a != diferencia for a, b in zip(dados, dados[1:])):
            return f"los términos dados no tienen diferencia constante: {dados}"
        esperados = [dados[-1] + diferencia * paso for paso in range(1, len(respuesta) + 1)]
        if respuesta != esperados:
            return f"con diferencia {diferencia}, siguen {esperados}, no {respuesta}"
        return None

    if item["tipo"] == "secuencia_geometrica":
        inicio = sympify(item["inicio"], rational=True)
        razon = sympify(item["razon"], rational=True)
        cantidad = int(item["cantidad"])
        respuesta = [sympify(valor, rational=True) for valor in item["respuesta"]]
        if cantidad <= 0:
            return "secuencia_geometrica requiere una cantidad positiva"
        esperada = [inicio * razon**indice for indice in range(cantidad)]
        if respuesta != esperada:
            return f"con inicio {inicio} y razon {razon}, se esperaba {esperada}"
        return None

    if item["tipo"] == "conjunto_natural":
        n = symbols("n", integer=True, nonnegative=True)
        condicion = sympify(item["condicion"], locals={"n": n, "And": And, "Eq": Eq})
        primero = int(sympify(item["primer_natural"]))
        ultimo_bruto = item.get("ultimo_natural")
        ultimo = None if ultimo_bruto is None else int(sympify(ultimo_bruto))
        if primero < 0 or (ultimo is not None and ultimo < primero):
            return "las cotas declaradas no forman un subconjunto válido de N"

        horizonte = max(200, (ultimo or primero) + 50)
        for valor in range(horizonte + 1):
            pertenece = bool(condicion.subs(n, valor))
            esperado = valor >= primero and (ultimo is None or valor <= ultimo)
            if pertenece != esperado:
                return (
                    f"la condición y las cotas discrepan en n={valor}: "
                    f"condición={pertenece}, cotas={esperado}"
                )
        return None

    if item["tipo"] != "orden_asociado":
        return verificar_base(item)

    datos = item.get("datos")
    respuesta = item.get("respuesta")
    if not isinstance(datos, dict) or not isinstance(respuesta, list):
        return "orden_asociado requiere `datos` (objeto) y `respuesta` (lista)"
    if set(datos) != set(respuesta) or len(datos) != len(respuesta):
        return "la respuesta no contiene exactamente todas las etiquetas de `datos`"

    reverso = item.get("direccion", "mayor_a_menor") == "mayor_a_menor"
    esperado = sorted(datos, key=lambda etiqueta: sympify(datos[etiqueta]), reverse=reverso)
    if respuesta != esperado:
        return f"el orden correcto es {esperado}, no {respuesta}"
    return None


def cargar_items() -> list[dict]:
    items: list[dict] = []
    for archivo in sorted(FUENTE.glob("*.json")):
        if archivo.name.startswith("_"):
            continue
        contenido = json.loads(archivo.read_text(encoding="utf-8"))
        if not isinstance(contenido, list):
            raise ValueError(f"{archivo.name} no contiene una lista JSON")
        items.extend(contenido)
    return items


def progreso() -> int:
    manifiesto = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
    paginas = manifiesto["paginas"]
    items = cargar_items()
    hechas = {item["pagina_pdf"] for item in items}

    for unidad in manifiesto["unidades"]:
        numero = unidad["unidad"]
        titulo = unidad["titulo"]
        previstas = [p["pagina"] for p in paginas if p["unidad"] == numero]
        listas = [p for p in previstas if p in hechas]
        pendientes = [str(p) for p in previstas if p not in hechas]
        marca = "OK " if len(listas) == len(previstas) else "   "
        detalle = f"  faltan: {', '.join(pendientes)}" if pendientes else ""
        print(
            f"{marca}U{numero:>2} {titulo[:34]:34s} {len(listas):>2}/{len(previstas):<2}{detalle}"
        )

    fuera = sorted(hechas - {p["pagina"] for p in paginas})
    if fuera:
        print(f"\nADVERTENCIA: páginas transcritas fuera del manifiesto: {fuera}")
    print(
        f"\n{len(hechas & {p['pagina'] for p in paginas})}/{len(paginas)} páginas con ejercicios transcritas"
    )
    return 0


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser()
    parser.add_argument("--pagina", type=int, help="verificar solo una página del PDF")
    parser.add_argument("--progreso", action="store_true")
    args = parser.parse_args()

    if args.progreso:
        return progreso()

    try:
        items = cargar_items()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FALLA  no se pudieron cargar los datos: {exc}")
        return 1
    if args.pagina is not None:
        items = [item for item in items if item.get("pagina_pdf") == args.pagina]
    if not items:
        print(f"Sin ítems en {FUENTE.relative_to(ROOT)}")
        return 1

    fallos: list[str] = []
    verificados = abiertos = 0
    for item in items:
        faltantes = sorted(REQUERIDOS - set(item))
        if faltantes:
            fallos.append(f"{item.get('id', '<sin id>')}: faltan campos {faltantes}")
            continue
        if item["tipo"] in TIPOS_VERIFICABLES:
            try:
                error = verificar(item)
            except Exception as exc:
                error = f"no se pudo evaluar ({type(exc).__name__}: {exc})"
            if error:
                fallos.append(f"{item['id']}: {error}")
            else:
                verificados += 1
        else:
            abiertos += 1

    ids = [item.get("id") for item in items if item.get("id")]
    duplicados = sorted(ident for ident, cantidad in Counter(ids).items() if cantidad > 1)
    for ident in duplicados:
        fallos.append(f"identificador duplicado: {ident}")

    for fallo in fallos:
        print(f"FALLA  {fallo}")
    for item in items:
        if item.get("verificar"):
            print(f"REVISAR  {item['id']}: {item['verificar']}")

    errata = sum("erratum" in item for item in items)
    revisar = sum("verificar" in item for item in items)
    print(
        f"\n{len(items)} ejercicios · {verificados} recalculados OK · "
        f"{abiertos} abiertos (sin verificación automática) · {len(fallos)} fallas"
    )
    print(f"Metadatos: {errata} errata · {revisar} verificar · {len(duplicados)} IDs duplicados")
    return 1 if fallos else 0


if __name__ == "__main__":
    raise SystemExit(main())
