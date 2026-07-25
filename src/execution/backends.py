"""Backend helpers for simulator selection and deprecation-safe defaults."""

from __future__ import annotations

from qiskit_aer import Aer, AerSimulator

DEFAULT_SIMULATOR_BACKEND = "aer_simulator"
LEGACY_SIMULATOR_ALIASES = {"qasm_simulator"}


def resolve_backend_name(name: str | None = None) -> str:
    """Map legacy backend aliases to the canonical simulator backend name."""

    if name is None or name in LEGACY_SIMULATOR_ALIASES:
        return DEFAULT_SIMULATOR_BACKEND
    return name


def get_backend(name: str | None = None):
    """Return a backend instance while hiding deprecated alias handling."""

    resolved_name = resolve_backend_name(name)
    if resolved_name == DEFAULT_SIMULATOR_BACKEND:
        return AerSimulator()
    return Aer.get_backend(resolved_name)
