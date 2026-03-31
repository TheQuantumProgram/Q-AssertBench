"""Shared helpers for flattened task-local benchmark assets."""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any, Callable

from qasserbench.benchmark.legacy_support import load_local_object
from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


def _call_with_supported_kwargs(func: Callable[..., Any], **kwargs: Any) -> Any:
    signature = inspect.signature(func)
    supported_kwargs = {
        name: value
        for name, value in kwargs.items()
        if name in signature.parameters
    }
    return func(**supported_kwargs)


def instantiate_local_class(
    module_path: str | Path,
    class_name: str,
    init_kwargs: dict[str, Any] | None = None,
) -> Any:
    """Instantiate one class defined in the current task-local module."""

    class_object = load_local_object(module_path, class_name)
    return _call_with_supported_kwargs(class_object, **dict(init_kwargs or {}))


def build_circuit_from_local_class(
    module_path: str | Path,
    class_name: str,
    *,
    init_kwargs: dict[str, Any] | None = None,
    preferred_build_method: str | None = None,
    build_kwargs: dict[str, Any] | None = None,
) -> Any:
    """Build or recover a circuit object from one task-local program class."""

    instance = instantiate_local_class(module_path, class_name, init_kwargs=init_kwargs)
    candidate_methods: list[Callable[..., Any]] = []

    def _push_method(method_name: str | None) -> None:
        if not method_name:
            return
        candidate = getattr(instance, method_name, None)
        if callable(candidate) and candidate not in candidate_methods:
            candidate_methods.append(candidate)

    _push_method(preferred_build_method)
    _push_method("build")
    _push_method("build_circuit")

    for method in candidate_methods:
        result = _call_with_supported_kwargs(method, **dict(build_kwargs or {}))
        if result is not None:
            return result

        for attr_name in ("qc", "circuit"):
            circuit = getattr(instance, attr_name, None)
            if circuit is not None:
                return circuit

    for attr_name in ("qc", "circuit"):
        circuit = getattr(instance, attr_name, None)
        if circuit is not None:
            return circuit

    raise ValueError(
        f"Could not recover a circuit from {Path(module_path).name}:{class_name}."
    )


def placeholder_gold_assertion(_: ExecutionResult) -> GoldAssertionResult:
    """Fallback gold assertion used until the loader injects the real evaluator."""

    return GoldAssertionResult(
        passed=False,
        details={"note": "Loader should replace this placeholder gold evaluator."},
    )
