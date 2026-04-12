"""
Utilidades compartidas del proyecto LevelUp-ELO.
"""

import re


def strip_thinking_tags(text: str) -> str:
    """Elimina etiquetas de pensamiento del texto generado por IA.

    Soporta múltiples formatos usados por distintos modelos:
    - Angular: <think>...</think>, <thought>...</thought>
    - Corchetes: [THINK]...[/THINK], [THOUGHT]...[/THOUGHT]

    Maneja tags completos, incompletos (sin cierre) y anidados.
    No interfiere con JSON ni con contenido de backend.
    """
    if not text:
        return text
    # Tags completos con ángulos: <think>...</think> y <thought>...</thought>
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<thought>.*?</thought>", "", text, flags=re.DOTALL | re.IGNORECASE)
    # Tags completos con corchetes: [THINK]...[/THINK] y [THOUGHT]...[/THOUGHT]
    text = re.sub(r"\[THINK\].*?\[/THINK\]", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"\[THOUGHT\].*?\[/THOUGHT\]", "", text, flags=re.DOTALL | re.IGNORECASE)
    # Tags incompletos (abiertos sin cierre): eliminar desde el tag hasta el final
    text = re.sub(r"<think>.*$", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<thought>.*$", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"\[THINK\].*$", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"\[THOUGHT\].*$", "", text, flags=re.DOTALL | re.IGNORECASE)
    return text.strip()


def strip_thinking_tags_stream(chunk_generator):
    """Wrapper para generadores de streaming que elimina bloques <think>/<thought>.

    Acumula chunks internamente y solo emite texto que está fuera de tags de
    pensamiento. Maneja el caso donde un tag abre en un chunk y cierra en otro.
    """
    buffer = ""
    inside_tag = False
    # Soporta <think>, <thought>, [THINK], [THOUGHT] (case-insensitive)
    tag_pattern_open = re.compile(r"<(think|thought)>|\[(think|thought)\]", re.IGNORECASE)
    tag_pattern_close = re.compile(r"</(think|thought)>|\[/(think|thought)\]", re.IGNORECASE)

    for chunk in chunk_generator:
        buffer += chunk

        while True:
            if inside_tag:
                # Buscar cierre del tag
                close_match = tag_pattern_close.search(buffer)
                if close_match:
                    # Descartar todo hasta el cierre (inclusive)
                    buffer = buffer[close_match.end() :]
                    inside_tag = False
                else:
                    # Aún dentro del tag, no emitir nada; seguir acumulando
                    break
            else:
                # Buscar apertura de tag
                open_match = tag_pattern_open.search(buffer)
                if open_match:
                    # Emitir texto antes del tag
                    before = buffer[: open_match.start()]
                    if before:
                        yield before
                    buffer = buffer[open_match.end() :]
                    inside_tag = True
                else:
                    # Sin tag a la vista: emitir buffer dejando un margen por si
                    # llega un tag partido entre chunks (ej: "<thi" + "nk>")
                    safe_len = len(buffer) - 10  # margen para tag más largo
                    if safe_len > 0:
                        yield buffer[:safe_len]
                        buffer = buffer[safe_len:]
                    break

    # Emitir lo que quede en el buffer (si no estamos dentro de un tag)
    if not inside_tag and buffer:
        yield buffer
