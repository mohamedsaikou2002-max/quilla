# Actual upstream quantum worker integration

Real local, opt-in invocation of the published **pyLIQTR** and **BenchQ** resource estimation APIs. No web-facing endpoints call these workers.

## Run

Use an isolated environment, separate from Finagler's Python 3.12 application:

```bash
# pyLIQTR environment: install with its documented dependency constraints
python -m pip install pyLIQTR
cd finagler-backend
python -m app.providers.quantum_workers --provider pyliqtr --spec examples/quantum_circuit.json

# BenchQ: use separate Linux Python 3.11 environment, Qiskit and optional Julia
python -m pip install benchq qiskit
python -m app.providers.quantum_workers --provider benchq --spec examples/quantum_circuit.json
```

Source API: [pyLIQTR resource_analysis.estimate_resources](https://github.com/isi-usc-edu/pyLIQTR/blob/main/src/pyLIQTR/utils/resource_analysis.py) and [BenchQ ex_1_from_qasm](https://github.com/zapatacomputing/benchq/blob/main/examples/ex_1_from_qasm.py).

**Limits:** bounded 16-qubit, 256-operation gate DSL (h, x, t, cx); no uploaded Python programs or shell commands. The BenchQ compiler may require Julia and takes significant time. Build a separate job queue with CPU/memory limits before exposing any remote execution. No claims about quantum hardware operation. Tests validate only DSL; actual estimators require scientific dependencies and have **not** been executed in CI.

The previous `/research/quantum/normalize` and `/compare` routes still accept *externally supplied* estimates and explicitly label them unverified. This worker's partial output is intentionally **not** silently converted into a complete resource profile. In particular, missing T-depth is not zero.
