"""Opt-in, local quantum research workers: real upstream library invocation.

Runs ONLY from the CLI in a dedicated scientific environment, never from the
Finagler web service. No cloud provider. Results are research estimates and
must not be represented as measured quantum hardware performance.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

GATES = {"h", "x", "t", "cx"}
MAX_GATES = 256
MAX_QUBITS = 16


def validate_spec(spec: Mapping[str, Any]) -> dict[str, Any]:
    n = spec.get("qubits")
    if type(n) is not int or not 1 <= n <= MAX_QUBITS:
        raise ValueError("qubits must be 1..16")
    operations = spec.get("operations")
    if not isinstance(operations, list) or len(operations) > MAX_GATES:
        raise ValueError("operations must be a list of at most 256 gates")
    validated = []
    for op in operations:
        if not isinstance(op, dict) or op.get("gate") not in GATES:
            raise ValueError("Only h, x, t, cx gates are supported")
        qs = op.get("targets")
        if not isinstance(qs, list) or len(qs) != (2 if op["gate"] == "cx" else 1):
            raise ValueError("Wrong operand count")
        if any(type(q) is not int or not 0 <= q < n for q in qs) or len(qs) != len(set(qs)):
            raise ValueError("Invalid, duplicate or out-of-range qubit")
        validated.append({"gate": op["gate"], "targets": qs[:]})
    return {"qubits": n, "operations": validated}


def run_pyliqtr(spec: Mapping[str, Any]) -> dict[str, Any]:
    clean = validate_spec(spec)
    try:
        import cirq
        from pyLIQTR.utils.resource_analysis import estimate_resources
        from importlib.metadata import version
    except ImportError as exc:
        raise RuntimeError("Install pyLIQTR and its Cirq/Qualtran dependencies in a separate worker") from exc

    q = cirq.LineQubit.range(clean["qubits"])
    ops = []
    for entry in clean["operations"]:
        t = entry["targets"]
        g = entry["gate"]
        ops.append({"h": lambda: cirq.H(q[t[0]]), "x": lambda: cirq.X(q[t[0]]),
                    "t": lambda: cirq.T(q[t[0]]),
                    "cx": lambda: cirq.CNOT(q[t[0]], q[t[1]])}[g]())
    # Explicit named arguments follow pyLIQTR's documented estimate_resources API.
    resources = estimate_resources(cirq.Circuit(ops), profile=True)
    if not isinstance(resources, dict) or any(key not in resources for key in ("T", "Clifford")):
        raise RuntimeError("pyLIQTR returned incomplete resource estimates")
    return {
        "provider": "pyliqtr", "upstream_version": version("pyLIQTR"),
        "status": "COMPUTED_BY_INSTALLED_LIBRARY_UNVALIDATED",
        "logical_qubits": clean["qubits"],
        "t_count": int(resources.get("T", 0)),
        "clifford_count": int(resources.get("Clifford", 0)),
        "rotation_count": int(resources.get("Rotations", 0)),
        "t_depth": None,
        "note": "T-depth not returned by this API; do not substitute zero. Research estimate only.",
    }


def run_benchq(spec: Mapping[str, Any]) -> dict[str, Any]:
    clean = validate_spec(spec)
    try:
        from importlib.metadata import version
        from qiskit import QuantumCircuit
        from benchq.algorithms.data_structures import AlgorithmImplementation, ErrorBudget
        from benchq.compilation.graph_states import get_ruby_slippers_circuit_compiler
        from benchq.compilation.graph_states.implementation_compiler import get_implementation_compiler
        from benchq.logical_architecture_modeling.graph_based_logical_architectures import AllToAllArchitectureModel
        from benchq.quantum_hardware_modeling import BASIC_SC_ARCHITECTURE_MODEL
        from benchq.resource_estimators.graph_estimator import GraphResourceEstimator
    except ImportError as exc:
        raise RuntimeError("Install BenchQ and its Qiskit/Julia dependencies in a dedicated Python 3.11 Linux worker") from exc

    circuit = QuantumCircuit(clean["qubits"])
    for entry in clean["operations"]:
        gate, t = entry["gate"], entry["targets"]
        if gate == "cx":
            circuit.cx(*t)
        else:
            getattr(circuit, gate)(t[0])
    algorithm = AlgorithmImplementation.from_circuit(
        circuit, ErrorBudget.from_even_split(total_failure_tolerance=1e-3), 1
    )
    compiler = get_implementation_compiler(
        circuit_compiler=get_ruby_slippers_circuit_compiler(), destination="single-thread"
    )
    result = GraphResourceEstimator(optimization="Time", verbose=False).compile_and_estimate(
        algorithm, compiler, AllToAllArchitectureModel(), BASIC_SC_ARCHITECTURE_MODEL
    )
    return {
        "provider": "benchq", "upstream_version": version("benchq"),
        "status": "COMPUTED_BY_INSTALLED_LIBRARY_UNVALIDATED",
        "result_repr": repr(result)[:4000],
        "logical_qubits": clean["qubits"],
        "t_count": None,
        "t_depth": None,
        "note": "Hardware-resource estimator output is not interchangeable with pyLIQTR gate counts.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=["pyliqtr", "benchq"], required=True)
    parser.add_argument("--spec", type=Path, required=True)
    args = parser.parse_args()
    if not args.spec.is_file() or args.spec.stat().st_size > 65536:
        parser.error("Input file must exist and be <= 64 KiB")
    spec = validate_spec(json.loads(args.spec.read_text(encoding="utf-8")))
    print(json.dumps((run_pyliqtr if args.provider == "pyliqtr" else run_benchq)(spec), indent=2))


if __name__ == "__main__":
    main()
