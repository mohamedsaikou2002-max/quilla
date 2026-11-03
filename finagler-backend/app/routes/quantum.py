"""Quantum profile import routes — only calls local normalization utilities."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.providers.quantum_profiles import compare_profiles, normalize_profile

router = APIRouter(prefix="/research/quantum", tags=["quantum-research"])


class ResourceProfile(BaseModel):
    provider: str
    algorithm: str
    upstream_version: str
    logical_qubits: int
    t_count: int
    t_depth: int


class CompareRequest(BaseModel):
    left: ResourceProfile
    right: ResourceProfile


@router.post("/normalize")
def normalize(body: ResourceProfile):
    try:
        return normalize_profile(body.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/compare")
def compare(body: CompareRequest):
    try:
        return compare_profiles(body.left.model_dump(), body.right.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
