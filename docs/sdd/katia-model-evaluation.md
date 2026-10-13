# KatIA model evaluation (spec 005 § Model evaluation — block 6 point 8)

**Status: protocol ready, results pending.** No run has been made: the session that built the
harness had no provider key. No change of model is approved; a larger model does not replace the
pedagogical controls.

## What is compared

The current model — Groq `llama-3.1-8b-instant` (`PROVIDERS["groq"]["model_cog"]`) — against one
alternative chosen by the owner (for example Groq `llama-3.3-70b-versatile`), on the same seeded
sample of bank items, through the **production** instructions and reply checks:

| Measure | How |
|---|---|
| Mathematical accuracy | A separate request asks the model to choose the correct option; the answer is matched to an option. |
| No-reveal compliance | Scripted conversations in es and en — help, concept, a paraphrased confirmation, a direct request, an injection, a complete resolution, four turns, and after an answer (with the key as internal reference). The input redirect is **bypassed**, so every model meets the extraction attempts. Reported: share of raw replies the checks reject, by reason and by scenario. |
| Undetected leaks | A sample of accepted replies per model, for a person to read: the checks cannot prove a reply is safe (spec § Known limits). |
| Latency | p50 and p95 seconds per KatIA reply (nearest rank). |
| Estimated cost | Mean input and output tokens per reply × the provider's price **at the date of the run**, given on the command line. |

## How to run

```bash
export GROQ_API_KEY=...            # or SYSTEM_AI_API_KEY with a gsk_ prefix; never commit it
python scripts/evaluate_katia_models.py \
  --model groq:llama-3.1-8b-instant --model groq:llama-3.3-70b-versatile \
  --items 30 --seed 7 \
  --price groq:llama-3.1-8b-instant=<in>/<out> \
  --price groq:llama-3.3-70b-versatile=<in>/<out> \
  --out docs/sdd/katia-eval-YYYY-MM-DD.md
```

Prices are USD per million input / output tokens, read from the provider's price page the day of
the run and quoted in the report. 30 items × 16 conversations × 2 models ≈ 1,150 model calls plus
60 solver calls. The script writes the Markdown report and the raw replies (`.json`).

The harness's arithmetic (sampling, scoring, percentiles, cost, report) is unit-tested with a fake
model: `tests/unit/scripts/test_evaluate_katia_models.py`. Those tests never call a model and the
evaluation is never cited in spec 005 § Traceability.

## Reading the result

- A model that solves more items is more useful **after** an answer (when it holds the key) and
  more dangerous **before** (it can solve the exercise itself): read accuracy together with the
  rejection rate of the "pide_respuesta", "inyeccion" and "resolucion" scenarios.
- A high rejection rate costs pedagogy, not safety: rejected replies become reviewed hints. Read
  the rejected reasons; a reason concentrated on one item may be a check to refine, not a model
  fault.
- The decision, and any change to `SOCRATIC_MAX_TOKENS` (120), needs the owner's explicit
  agreement with pedagogical examples (block 6 point 7).

## Results

Pending: no run yet.
