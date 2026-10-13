# API contract: KatIA (spec 005)

## `POST /api/ai/socratic`

Authenticated student (`Authorization: Bearer`). Rate limited by `RATE_LIMIT_SOCRATIC`
(default `10/minute`, per session).

### Request

```json
{
  "item_id": "q47",
  "student_message": "No sé por dónde empezar",
  "lang": "es",
  "api_key": "",
  "provider": ""
}
```

| Field | Rule |
|---|---|
| `item_id` | required, 1–128 characters |
| `student_message` | required, ≥ 1 non-blank character; schema cap 2000; the configured limit (`KATIA_MAX_MESSAGE_CHARS`, 500) is enforced by the service (422 `message_too_long`) |
| `lang` | `es` (default) or `en` |
| `api_key` | optional — the student's own key; empty uses the system key |
| `provider` | optional — read only with the student's own key and an unrecognised prefix |

Ignored if sent (old clients keep working): `item_content`, `course_id`, any history.

### Success — `200 text/event-stream`

```text
data: {"token": "¿Qué "}
data: {"token": "observas?"}
data: {"done": true, "full_text": "¿Qué observas?"}
```

The model failing after the checks passed: `200` with `data: {"error": "<plain message>"}` and
nothing stored (#57).

### Refusals — before the stream starts

`detail` is `{"code": "<code>", "message": "<Spanish text>"}`; the chat translates by `code`.

| Status | `code` | When |
|---|---|---|
| 404 | `item_not_found` | unknown item |
| 403 | `not_enrolled` | not enrolled in the item's course |
| 403 | `exam_active` | the item is in the student's open exam |
| 409 | `not_served` | the item was never served to the student |
| 422 | `message_too_long` | message above the configured limit |
| 422 | `katia_not_configured` | no system key and no student key |
| 422 | `unknown_provider` | the student's key has no recognised prefix and no cloud provider was named |
| 503 | `katia_unavailable` | the server's provider configuration is invalid |
| 429 | — (slowapi) | over the request limit |

None of them calls the model or stores a turn.

## `POST /api/student/next-question` — new side effect

When it returns an item, the server records a serving (data-model `item_serves`). The response
is unchanged.
