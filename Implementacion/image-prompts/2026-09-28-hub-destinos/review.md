# Destinos de los hubs — completado 2026-09-30

23 ilustraciones originales 1536×1024, revisadas visualmente y guardadas en frontend/public/leccion/hub-destinos:

- Ciudad N2: seis edificios.
- Fábrica N3: cinco máquinas.
- Puerto N4: seis destinos.
- Kemet: cuatro lugares.
- Bagdad: dos alas del patio.

Prompts exactos en n2-prompts.json, n3-prompts.json, n4-prompts.json y algebra-prompts.json. Cada grupo usa su cabecera reciente como referencia visual. Escenarios protagonistas, habitantes felinos secundarios, sin KatIA en primer plano. El intento inicial de Cantera falló por conexión; el reintento se completó.

Integración: HubDestinationArt.tsx asigna los 23 IDs a imágenes. Los renderers LevelTwoLesson, LevelThreeLesson y LevelFourLesson conservan símbolos, textos y lógica de apertura. La presentación de tarjetas usa imagen horizontal completa sobre su contenido; carga diferida, dimensiones explícitas y nombres accesibles en botones.

Validación:

- pnpm run build: TypeScript, Vite y PWA completados. La primera ejecución en sandbox falló por spawn EPERM; la ejecución autorizada fuera del sandbox pasó.
- Prueba en navegador Edge sin ventana con renderers reales y contenido de los cinco hubs, sin sesión de usuario ni llamadas de interacción: 1280 y 375 píxeles.
- Diez vistas, 46 cargas de imagen verificadas (23 por tamaño), cero errores de JavaScript y cero desbordamientos horizontales.
- Capturas preview-*.png y resultados DOM en validation.json. Inspección visual de N2 escritorio, N3 móvil y Bagdad escritorio completada.
- No se probó persistencia de progreso contra el backend; sus handlers no fueron modificados.

Sin commit, push ni despliegue.
