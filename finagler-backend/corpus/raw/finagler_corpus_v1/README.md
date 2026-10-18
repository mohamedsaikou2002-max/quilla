# Quantum Finagler corpus v1.0 — 58 equations

- `corpus.json`  structured data (equations, routing table, backend limits, honesty rules)
- `corpus.md`    same content for upload to Gemini as a file or reading by humans
- `corpus_loader.py`  keyword retrieval + prompt builder, no dependencies

Domains: quantum mechanics 13, quantum information 12, quantum algorithms 9, statistical physics 4,
probability/statistics 11, hardware noise 3, applied science 6.

Each entry: id, name, LaTeX + plain-text equation, variables, use_when, quantum_link, caveat,
`backend_support` (direct = runs in finagler_quantum, partial = related experiment runs, none = theory only)
and `job_hint` (a ready job spec, validated against finagler_quantum's spec validator).

## Use with Gemini
1. Simple: upload `corpus.md` with the Files API / AI Studio and reference it in the system instruction.
2. Better: retrieve per question, so the context stays small and precise:
       hits = search(user_question, k=6); system = fq.SYSTEM_PROMPT + "\n\n" + as_prompt(hits)
3. Gemini proposes a job from `job_hint`/`routing` via `run_quantum_job`; the backend validates it.

## Caveats
Equations are standard textbook forms; scan them before selling to scientists. `backend_support: none`
entries are theory context only, so the model must say they weren't computed. Finance entries
(Markowitz, Kelly) are not financial advice.
