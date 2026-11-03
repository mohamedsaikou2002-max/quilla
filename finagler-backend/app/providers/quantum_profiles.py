"""Local, dependency-free import/validation boundary for quantum resource estimates.

BenchQ and pyLIQTR run in separate, version-pinned environments. This module
does not execute upstream software or assert that submitted counts are verified.
"""
from __future__ import annotations

import math
from typing import Any, Mapping

_ALLOWED = {"benchq", "pyliqtr"}


def _count(data: Mapping[str, Any], key: str) -> int:
    value = data.get(key)
    if type(value) is not int or value < 0 or value > 10**15:
        raise ValueError(f"{key} must be a bounded nonnegative integer")
    return value


def normalize_profile(data: Mapping[str, Any]) -> dict[str, Any]:
    provider = data.get("provider")
    if provider not in _ALLOWED:
        raise ValueError("provider must be benchq or pyliqtr")
    algorithm = data.get("algorithm")
    if not isinstance(algorithm, str) or not 1 <= len(algorithm.strip()) <= 120:
        raise ValueError("algorithm identifier required")
    version = data.get("upstream_version")
    if not isinstance(version, str) or not 1 <= len(version.strip()) <= 80:
        raise ValueError("upstream_version required")
    t_count = _count(data, "t_count")
    t_depth = _count(data, "t_depth")
    logical_qubits = _count(data, "logical_qubits")
    if t_depth > t_count:
        raise ValueError("t_depth cannot exceed t_count")
    if logical_qubits == 0:
        raise ValueError("logical_qubits must be positive")
    return {
        "provider": provider,
        "algorithm": algorithm.strip(),
        "upstream_version": version.strip(),
        "logical_qubits": logical_qubits,
        "t_count": t_count,
        "t_depth": t_depth,
        "verified": False,
        "status": "UNVERIFIED_EXTERNAL_ESTIMATE",
        "note": "Counts were supplied by a separate tool or user, not independently recomputed by Finagler.",
    }


def compare_profiles(left: Mapping[str, Any], right: Mapping[str, Any]) -> dict[str, Any]:
    a, b = normalize_profile(left), normalize_profile(right)
    if a["algorithm"] != b["algorithm"]:
        raise ValueError("resource profiles must describe the same algorithm")
    return {
        "status": "UNVERIFIED_EXTERNAL_COMPARISON",
        "algorithm": a["algorithm"],
        "left": a,
        "right": b,
        "delta": {key: b[key] - a[key] for key in ("logical_qubits", "t_count", "t_depth")},
        "note": "Differences are only comparable when circuits, decomposition choices, error budgets and algorithms match.",
    }
