# DARPA Quantum Benchmarking → Finagler (Quilla): resource-profile adapter

This branch adds a **working local JSON resource-profile normalization and comparison API** to Quilla's Finagler backend. Routes:

- `POST /research/quantum/normalize` — validate submitted counts.
- `POST /research/quantum/compare` — compare two records for the same algorithm.

Payload:
```json
{"provider":"pyliqtr","algorithm":"example-algorithm","upstream_version":"X.Y","logical_qubits":8,"t_count":600,"t_depth":60}
```

Resource counts are **supplied**, not computed by Finagler. The response is always `UNVERIFIED_EXTERNAL_ESTIMATE`; the adapter does not falsely claim to have executed BenchQ or pyLIQTR.

## Actual upstream quantum backends — deployment requirements

- `https://github.com/zapatacomputing/benchq` — DARPA QB BenchQ, resource estimation. Its published README lists **Python 3.9–3.11 Linux** support; this Finagler backend specifies Python 3.12. Run BenchQ in a **separate pinned Python 3.11 worker**, not in the backend's Python 3.12 environment. BenchQ graph-state pipelines may require Julia.
- `https://github.com/isi-usc-edu/pyLIQTR` — quantum circuit decomposition/resource estimate tooling; isolate because it adds Cirq/Qualtran and scientific dependencies.
- Both require circuit/algo compatibility before comparing estimates, and licensing/accuracy review. Never assume a `t_count` from one pipeline is directly equivalent to another without harmonized error budgets and decomposition.
- `https://github.com/The-OpenROAD-Project/OpenROAD` is chip design tooling, not a quantum algorithm estimator.

## Tests

From `finagler-backend`: `python -m unittest discover -s tests -v`.

No cloud providers, credentials, changes to corpus, LM Studio, or existing chat routing are introduced.
