# TAREA: Corregir figuras del Semillero — extraer de PDFs originales + arreglar carga en UI

## Rol
Desarrollador Python/Streamlit del proyecto ELO.

## Contexto
- Las figuras generadas con matplotlib son **incorrectas** — no coinciden con los originales
- Las figuras tampoco **cargan en la UI** aunque el campo `image_path` existe en los JSON
- Los PDFs originales de las Olimpiadas UdeA 2020 están en la carpeta del proyecto
- Solución: extraer las figuras directamente de los PDFs con PyMuPDF (recorte preciso por página)

**OBLIGATORIO:** Lee `.claude/skills/items-bank.md` (sección "Preguntas con imágenes").

---

## PROBLEMA 1: Las figuras no cargan en la UI

### Diagnóstico
Buscar en `app.py` cómo se renderiza `image_path`. El campo existe en los JSON pero la imagen no se muestra al estudiante. Posibles causas:

1. `app.py` solo busca `image_url` y NO `image_path`
2. La ruta relativa `items/images/xxx.png` no se resuelve correctamente desde el directorio de ejecución
3. El campo `image_path` no se pasa del JSON a la DB, o no se lee de la DB al mostrar la pregunta

### Corrección requerida
En `app.py`, donde se muestra el enunciado de la pregunta al estudiante, verificar que:

```python
# Debe buscar AMBOS campos
image = item.get('image_url') or item.get('image_path')
if image:
    if os.path.exists(image):
        st.image(image)
    elif image.startswith('http'):
        st.image(image)
```

También verificar que `sync_items_from_bank_folder()` en **ambos repositorios** guarda el campo `image_url` (o `image_path`) en la tabla `items`. La columna `image_url` ya existe en la tabla — verificar que el sync lee ambos campos del JSON:

```python
# Al sincronizar ítems del banco
image = item_data.get('image_url') or item_data.get('image_path', '')
```

### Verificación
Después de corregir, abrir una pregunta que tenga `image_path` y confirmar que la imagen aparece debajo del enunciado.

---

## PROBLEMA 2: Reemplazar figuras incorrectas con extracción de PDFs

### Paso 1: Copiar los PDFs al proyecto

Los 8 PDFs de las Olimpiadas UdeA deben estar accesibles. Copiarlos a una carpeta temporal:

```bash
mkdir -p /tmp/olimpiadas_pdfs
# El usuario debe copiar los PDFs aquí o indicar su ubicación
```

### Paso 2: Script de extracción precisa

Crear `scripts/extract_figures_from_pdfs.py` que use PyMuPDF para recortar regiones específicas de cada página. **PyMuPDF ya está en requirements.txt** (`fitz`).

```python
#!/usr/bin/env python3
"""Extrae figuras geométricas de los PDFs de Olimpiadas UdeA 2020.

Cada figura se recorta de una región precisa de una página específica.
Las coordenadas están en puntos PDF (72 puntos = 1 pulgada).
La página se renderiza a 3x zoom para buena calidad.
"""

import fitz  # PyMuPDF
import os

OUTPUT_DIR = 'items/images'
# Ajustar esta ruta según dónde estén los PDFs
PDF_DIR = '.'  # o la ruta donde el usuario tenga los PDFs

# Mapeo: (archivo_pdf, página_0indexed, (x0, y0, x1, y1)) → nombre_salida
# Las coordenadas son en puntos PDF del documento original
# IMPORTANTE: Estas coordenadas deben ajustarse mirando cada PDF
# El formato es (izquierda, arriba, derecha, abajo)

EXTRACTIONS = {
    # =============================================
    # OCTAVO
    # =============================================
    
    # Q13: Tres cuadrados sobre triángulo con ángulos x, y, z
    ('2020-Taller-OctavoEstudiantes.pdf', 1, (320, 350, 570, 520)):
        'octavo_q13_cuadrados_triangulo.png',
    
    # Q14: Rectángulo 20×32 dentro de 108×98
    ('2020-Taller-OctavoEstudiantes.pdf', 1, (320, 530, 570, 710)):
        'octavo_q14_rectangulos.png',
    
    # Q15: Rectángulo con centro O, triángulo OPQ, zona rayada
    ('2020-Taller-OctavoEstudiantes.pdf', 2, (50, 100, 290, 300)):
        'octavo_q15_centro_O.png',
    
    # Q16: Cuadrado PQRS inscrito en ABCD
    ('2020-Taller-OctavoEstudiantes.pdf', 2, (50, 310, 290, 520)):
        'octavo_q16_cuadrado_inscrito.png',
    
    # Q20: Triángulo ABC con DE‖BC, FE‖DC
    ('2020-Taller-OctavoEstudiantes.pdf', 2, (320, 510, 570, 700)):
        'octavo_q20_triangulo_paralelas.png',

    # =============================================
    # SÉPTIMO
    # =============================================
    
    # Q13: Triángulo rectángulo isósceles + cuadrado superpuestos
    ('2020-Taller-Septimo-Estudiantes.pdf', 1, (320, 380, 570, 520)):
        'septimo_q13_superposicion.png',
    
    # Q14: Dos cuadrados (6cm y 4cm) superpuestos
    ('2020-Taller-Septimo-Estudiantes.pdf', 2, (50, 30, 310, 190)):
        'septimo_q14_cuadrados.png',
    
    # Q15: Dos cuadrados cortados en 5 piezas
    ('2020-Taller-Septimo-Estudiantes.pdf', 2, (50, 220, 310, 400)):
        'septimo_q15_corte_cuadrados.png',

    # =============================================
    # NOVENO
    # =============================================
    
    # Q14: Rombo AECF en rectángulo ABCD (AD=16, AB=12)
    ('2020-Taller-NovenoEstudiantes.pdf', 1, (320, 380, 570, 530)):
        'noveno_q14_rombo.png',
    
    # Q15: Triángulo rectángulo ABC con cuadrado APRS
    ('2020-Taller-NovenoEstudiantes.pdf', 2, (50, 40, 290, 270)):
        'noveno_q15_triangulo_cuadrado.png',
    
    # Q16: Sucesión de triángulos rectángulos isósceles
    ('2020-Taller-NovenoEstudiantes.pdf', 2, (50, 280, 290, 470)):
        'noveno_q16_sucesion_triangulos.png',
    
    # Q20: Triángulo isósceles con M y N puntos medios
    ('2020-Taller-NovenoEstudiantes.pdf', 2, (320, 540, 570, 720)):
        'noveno_q20_isosceles_medianas.png',

    # =============================================
    # DÉCIMO
    # =============================================
    
    # Q12: Diagrama de barras (notas 1-5)
    ('2020-Taller-DecimoEstudiantes.pdf', 1, (320, 180, 570, 340)):
        'decimo_q12_barras.png',
    
    # Q13: Triángulo rectángulo AX=AD, CY=CD
    ('2020-Taller-DecimoEstudiantes.pdf', 1, (320, 310, 570, 490)):
        'decimo_q13_triangulo_XDY.png',
    
    # Q14: Rectángulo ABCD con PQRS (razón 1:2)
    ('2020-Taller-DecimoEstudiantes.pdf', 2, (40, 30, 280, 170)):
        'decimo_q14_paralelogramo.png',
    
    # Q15: Semicírculo diámetro 5, rectángulo altura 2
    ('2020-Taller-DecimoEstudiantes.pdf', 2, (40, 190, 280, 350)):
        'decimo_q15_semicirculo.png',
    
    # Q16: Dos cuadrados cubriendo círculo radio 4
    ('2020-Taller-DecimoEstudiantes.pdf', 2, (40, 370, 280, 510)):
        'decimo_q16_cuadrados_circulo.png',
    
    # Q20: Triángulo ABC con paralelogramo ADEF
    ('2020-Taller-DecimoEstudiantes.pdf', 2, (320, 460, 570, 700)):
        'decimo_q20_paralelogramo_ADEF.png',

    # =============================================
    # UNDÉCIMO
    # =============================================
    
    # Q4: Tablero/grid con puntos A, B, C
    ('2020-Taller-OnceEstudiantes.pdf', 0, (395, 130, 565, 300)):
        'undecimo_q4_tablero.png',
    
    # Q13: Tres cuadrados (lados 9, ?, 4) alineados
    ('2020-Taller-OnceEstudiantes.pdf', 1, (320, 290, 570, 460)):
        'undecimo_q13_tres_cuadrados.png',
    
    # Q14: Paralelogramo ABCD con E y F puntos medios
    ('2020-Taller-OnceEstudiantes.pdf', 1, (320, 480, 570, 630)):
        'undecimo_q14_paralelogramo.png',
    
    # Q15: Triángulo equilátero XYZ dividido en tercios
    ('2020-Taller-OnceEstudiantes.pdf', 2, (40, 30, 300, 210)):
        'undecimo_q15_equilatero_XYZ.png',
    
    # Q16: Triángulo rectángulo ABC con punto P, áreas 2, 8, 18
    ('2020-Taller-OnceEstudiantes.pdf', 2, (40, 220, 300, 440)):
        'undecimo_q16_triangulo_P.png',
    
    # Q20: Rectángulo con diagonal BD
    ('2020-Taller-OnceEstudiantes.pdf', 2, (320, 540, 570, 720)):
        'undecimo_q20_rectangulo_diagonal.png',

    # =============================================
    # SEXTO
    # =============================================
    
    # Q1: Cuadrícula de rectángulos
    ('2020-Taller-Sexto-Estudiantes.pdf', 0, (55, 285, 295, 470)):
        'sexto_q1_rectangulos.png',
    
    # Q14: Circuito para autos
    ('2020-Taller-Sexto-Estudiantes.pdf', 2, (40, 50, 310, 220)):
        'sexto_q14_circuito.png',
    
    # Q15: Triángulo equilátero + cuadrado
    ('2020-Taller-Sexto-Estudiantes.pdf', 2, (40, 310, 310, 530)):
        'sexto_q15_triangulo_cuadrado.png',
    
    # Q16: Rectángulo ABCD sombreado
    ('2020-Taller-Sexto-Estudiantes.pdf', 2, (310, 440, 570, 610)):
        'sexto_q16_rectangulo_sombreado.png',
    
    # Q20: Cuadrado exterior con rombo interior
    ('2020-Taller-Sexto-Estudiantes.pdf', 2, (310, 620, 570, 800)):
        'sexto_q20_cuadrado_rombo.png',

    # =============================================
    # PRIMARIA
    # =============================================
    
    # Q13: Figura tipo L con segmento CD
    ('2020-TallerPrimariaEstudiantes.pdf', 1, (320, 300, 570, 470)):
        'primaria_q13_CD.png',
    
    # Q14: Tres cuadrados I, II, III
    ('2020-TallerPrimariaEstudiantes.pdf', 1, (320, 480, 570, 640)):
        'primaria_q14_cuadrados.png',
    
    # Q16: Arreglo 3×3 de puntos
    ('2020-TallerPrimariaEstudiantes.pdf', 2, (50, 290, 290, 410)):
        'primaria_q16_puntos.png',
    
    # Q20: Triángulo sombreado en rectángulo
    ('2020-TallerPrimariaEstudiantes.pdf', 2, (320, 530, 570, 690)):
        'primaria_q20_triangulo_rect.png',
}


def extract_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    ok = 0
    fail = 0
    
    for (pdf_name, page_num, rect), out_name in EXTRACTIONS.items():
        pdf_path = os.path.join(PDF_DIR, pdf_name)
        
        if not os.path.exists(pdf_path):
            print(f"  SKIP: {pdf_name} no encontrado en {PDF_DIR}")
            fail += 1
            continue
        
        try:
            doc = fitz.open(pdf_path)
            if page_num >= len(doc):
                print(f"  SKIP: página {page_num} no existe en {pdf_name}")
                doc.close()
                fail += 1
                continue
            
            page = doc[page_num]
            clip = fitz.Rect(*rect)
            
            # Renderizar a 3x zoom para buena calidad
            mat = fitz.Matrix(3, 3)
            pix = page.get_pixmap(matrix=mat, clip=clip)
            
            out_path = os.path.join(OUTPUT_DIR, out_name)
            pix.save(out_path)
            
            size_kb = os.path.getsize(out_path) // 1024
            print(f"  OK: {out_name} ({size_kb}KB)")
            ok += 1
            doc.close()
            
        except Exception as e:
            print(f"  ERROR: {out_name} → {e}")
            fail += 1
    
    print(f"\nResultado: {ok} OK, {fail} fallos")
    print(f"Figuras en: {OUTPUT_DIR}/")


def verify_image_paths():
    """Verifica que cada image_path en los JSON apunte a un archivo existente."""
    import json
    
    bank_dir = 'items/bank'
    errors = []
    
    for f in os.listdir(bank_dir):
        if not f.endswith('.json'):
            continue
        items = json.load(open(os.path.join(bank_dir, f), encoding='utf-8'))
        for item in items:
            img = item.get('image_path', '')
            if img and not os.path.exists(img):
                errors.append(f"  {item['id']} → {img} NO EXISTE")
    
    if errors:
        print(f"\n⚠ {len(errors)} image_path rotos:")
        for e in errors:
            print(e)
    else:
        print("\n✓ Todos los image_path apuntan a archivos existentes")


if __name__ == '__main__':
    print("=== Extrayendo figuras de PDFs ===\n")
    extract_all()
    print("\n=== Verificando image_path en JSONs ===")
    verify_image_paths()
```

### Paso 3: Ajustar coordenadas

Las coordenadas del diccionario `EXTRACTIONS` son aproximadas. Después de la primera ejecución:

1. Abrir cada PNG generada y comparar con el PDF original
2. Si la figura está cortada o incluye texto innecesario, ajustar las coordenadas `(x0, y0, x1, y1)`:
   - **x0**: borde izquierdo (aumentar para recortar desde más a la derecha)
   - **y0**: borde superior (aumentar para bajar el recorte)
   - **x1**: borde derecho (disminuir para recortar antes)
   - **y1**: borde inferior (disminuir para subir el recorte)
3. Volver a ejecutar el script

### Paso 4: Ejecutar

```bash
# Copiar los PDFs al directorio del proyecto (o ajustar PDF_DIR en el script)
python scripts/extract_figures_from_pdfs.py
```

### Paso 5: Eliminar figuras de matplotlib incorrectas

```bash
# Si hay figuras antiguas generadas por matplotlib, el script las sobreescribe
# porque los nombres de archivo son los mismos
```

---

## PROBLEMA 3: Verificar que `image_path` se guarda y se lee correctamente

### En los repositorios (sync de ítems)

Verificar en `sqlite_repository.py` y `postgres_repository.py` que `sync_items_from_bank_folder()` lee el campo del JSON y lo guarda en la columna `image_url` de la tabla `items`:

```python
# Al leer cada ítem del JSON
image = item_data.get('image_url') or item_data.get('image_path', '')

# Al insertar/actualizar en la DB
cursor.execute(
    "INSERT ... (id, ..., image_url) VALUES (?, ..., ?)",
    (item_id, ..., image)
)
```

### En app.py (mostrar la imagen)

Buscar dónde se renderiza la pregunta al estudiante y verificar que se muestra la imagen:

```python
# Después de mostrar el enunciado (st.markdown del content)
image_url = item.get('image_url', '') or ''
if image_url:
    # Si es ruta local
    if os.path.exists(image_url):
        st.image(image_url, use_container_width=True)
    # Si es URL
    elif image_url.startswith('http'):
        st.image(image_url, use_container_width=True)
```

**IMPORTANTE:** Verificar que el `item` que llega a la UI incluye el campo `image_url`. Si la función que obtiene la pregunta (`get_next_question` o similar) no lo incluye en el SELECT, la imagen nunca se mostrará aunque esté en la DB.

Buscar el SELECT que obtiene el ítem y verificar que incluye `image_url`:
```sql
-- DEBE incluir image_url
SELECT id, content, options, correct_option, difficulty, topic, image_url
FROM items WHERE ...
```

---

## Orden de ejecución

1. Primero arreglar la carga de imágenes en la UI (PROBLEMA 1)
2. Luego ejecutar el script de extracción de PDFs (PROBLEMA 2)
3. Verificar con `verify_image_paths()` que todo enlaza correctamente

## Entregables
1. Fix en `app.py` para mostrar `image_path`/`image_url`
2. Fix en repos si `sync_items_from_bank_folder()` no lee `image_path`
3. Script `scripts/extract_figures_from_pdfs.py` funcional
4. 35 figuras correctas en `items/images/`
5. Verificación de que las imágenes se muestran en la sala de estudio

## Criterios de calidad
- Al abrir una pregunta con imagen, la figura aparece debajo del enunciado
- Las figuras coinciden con las de los PDFs originales (misma geometría, mismos labels)
- Las preguntas sin imagen siguen funcionando
- No hay regresiones en el resto de la app
