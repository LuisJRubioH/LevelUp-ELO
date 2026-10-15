# Checklist antes de abrir la app al público

Pospuesto el 2026-10-12: no es obligatorio mientras la app no esté abierta al público. No incluye
los pasos de la transferencia, que están en [`transfer.md`](transfer.md).

Trasladado de la rama `claude/great-mayer-4617ix` (commit `13d4f76`, que lo añadía a
`docs/v2-plan.md`, un documento histórico) y revisado contra `redesign @ 1d6fcf6` el 2026-10-13.

- [ ] Límite de gasto mensual y alertas (50 % / 80 %) en la consola del proveedor de la key de IA
  del sistema (`SYSTEM_AI_API_KEY` y las `AI_KEY_*` que haya en Render). En Gemini los
  presupuestos solo alertan: el tope real se pone con cuotas de requests/día.
- [ ] Opcional: key aparte para KatIA en `AI_KEY_KATIA` (workspace de Anthropic o proyecto de
  OpenAI con su propio límite), para que un abuso del chat no agote la revisión de procedimientos.
  `redesign` ya la usa para el chat (`api/config.py:40,50`).
- [ ] V1 en Streamlit Community Cloud: la transferencia la desconecta temporalmente
  ([`transfer.md`](transfer.md) § 3.1) y reconectarla es una decisión aparte. Si se decide no
  volver a usarla, borrar la app o, como mínimo, revocar la `GROQ_API_KEY` de sus Secrets. Si se
  reconecta, su formulario de registro sigue abierto
  ([spec 004](../specs/004-identity/spec.md) § Edge Cases).

## Retirado en la revisión

- **Conectar el rate limiting.** En `redesign` ya está conectado: el `Limiter` se registra en
  `api/main.py:91-92` y se aplica al chat socrático (`api/routers/ai.py:28`,
  `RATE_LIMIT_SOCRATIC`), a la revisión de procedimientos (`api/routers/ai.py:148` y
  `api/routers/student.py:536`, `RATE_LIMIT_REVIEW`), al análisis con IA del docente
  (`api/routers/teacher.py:302`) y al login y el registro (`api/routers/auth.py:39,80`). Lo que
  falta sobre límites —por cuenta y global en el login, sin límite por dirección— está en la
  [spec 004](../specs/004-identity/spec.md), entrega E1.
