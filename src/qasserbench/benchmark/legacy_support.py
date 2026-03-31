"""Utilities for wrapping copied legacy benchmark artifacts."""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
import inspect
from pathlib import Path
import sys
from types import SimpleNamespace
from typing import Any, Callable
from uuid import uuid4

from qiskit import transpile

from qasserbench.execution.backends import get_backend
from qasserbench.execution.interfaces import (
    ExecutionConfig,
    ExecutionResult,
    GoldAssertionResult,
    ProgramDefinition,
)
from qasserbench.execution.runtime import normalize_counts


def _load_module(module_path: Path) -> Any:
    search_path = str(module_path.parent)
    restore_path = search_path not in sys.path
    if restore_path:
        sys.path.insert(0, search_path)

    spec = spec_from_file_location(
        f"qasserbench_legacy_{module_path.stem}_{uuid4().hex}",
        module_path,
    )
    try:
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module from {module_path}")
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        if restore_path:
            sys.path.remove(search_path)


def load_local_object(module_path: str | Path, object_name: str) -> Any:
    """Load one object from a local copied legacy module."""

    module_file = Path(module_path).resolve()
    module = _load_module(module_file)
    return getattr(module, object_name)


def _call_with_supported_kwargs(func: Callable[..., Any], **kwargs: Any) -> Any:
    signature = inspect.signature(func)
    supported_kwargs = {
        name: value
        for name, value in kwargs.items()
        if name in signature.parameters
    }
    return func(**supported_kwargs)


def _instantiate_legacy_class(
    module_path: Path,
    class_name: str,
    init_kwargs: dict[str, Any] | None = None,
) -> Any:
    legacy_class = load_local_object(module_path, class_name)
    init_payload = dict(init_kwargs or {})
    return _call_with_supported_kwargs(legacy_class, **init_payload)


def _coerce_counts(output: Any, instance: Any, *, counts_attr: str) -> dict[str, int]:
    if isinstance(output, dict):
        return normalize_counts(output)
    counts = getattr(instance, counts_attr, None)
    if isinstance(counts, dict):
        return normalize_counts(counts)
    raise ValueError("Legacy runner did not produce counts.")


def make_legacy_program_definition(
    *,
    task_id: str,
    module_path: str | Path,
    class_name: str,
    mode: str,
    init_kwargs: dict[str, Any] | None = None,
    call_method: str | None = None,
    counts_attr: str = "counts",
    call_kwargs: dict[str, Any] | None = None,
) -> ProgramDefinition:
    """Build a ProgramDefinition around one copied legacy class."""

    legacy_module_path = Path(module_path).resolve()

    def build_program() -> Any:
        return _instantiate_legacy_class(legacy_module_path, class_name, init_kwargs)

    def run_program(config: ExecutionConfig) -> ExecutionResult:
        instance = _instantiate_legacy_class(legacy_module_path, class_name, init_kwargs)
        if hasattr(instance, "backend"):
            instance.backend = get_backend(config.backend)
        if hasattr(instance, "shots"):
            instance.shots = config.shots

        if mode == "build":
            builder = getattr(instance, call_method or "build")
            circuit = _call_with_supported_kwargs(builder)
            backend = get_backend(config.backend)
            compiled = transpile(circuit, backend)
            run_kwargs = {"shots": config.shots}
            if config.seed is not None:
                run_kwargs["seed_simulator"] = config.seed
            job = backend.run(compiled, **run_kwargs)
            counts = normalize_counts(job.result().get_counts())
        elif mode in {"run", "build_and_run"}:
            runner = getattr(instance, call_method or mode)
            runner_kwargs = dict(call_kwargs or {})
            runner_kwargs.setdefault("shots", config.shots)
            output = _call_with_supported_kwargs(runner, **runner_kwargs)
            counts = _coerce_counts(output, instance, counts_attr=counts_attr)
        else:
            raise ValueError(f"Unsupported legacy program mode: {mode}")

        return ExecutionResult(
            counts=counts,
            shots=config.shots,
            backend=config.backend,
            metadata=dict(config.metadata),
        )

    def _placeholder_gold_assertion(_: ExecutionResult) -> GoldAssertionResult:
        return GoldAssertionResult(
            passed=False,
            details={"note": "Loader should replace this placeholder gold evaluator."},
        )

    return ProgramDefinition(
        task_id=task_id,
        build_program=build_program,
        run_program=run_program,
        evaluate_gold_assertion=_placeholder_gold_assertion,
    )


def make_legacy_gold_evaluator(
    *,
    module_path: str | Path,
    class_name: str,
    gold_source: str,
    init_kwargs: dict[str, Any] | None = None,
    extra_globals: dict[str, Any] | None = None,
) -> Callable[[Any], GoldAssertionResult]:
    """Build an evaluator that executes copied gold-source code on ExecutionResult."""

    legacy_module_path = Path(module_path).resolve()

    def evaluate_gold_assertion(result: Any) -> GoldAssertionResult:
        context_object = _instantiate_legacy_class(legacy_module_path, class_name, init_kwargs)
        counts = dict(result.counts)
        if hasattr(context_object, "shots"):
            context_object.shots = result.shots
        setattr(context_object, "counts", counts)

        program = getattr(context_object, "program", None)
        if program is not None and hasattr(program, "counts"):
            program.counts = counts

        exec_globals = {"__builtins__": __builtins__}
        exec_globals.update(extra_globals or {})
        exec_locals = {
            "counts": counts,
            "shots": result.shots,
            "result": result,
            "self": context_object,
            "qft_runner": context_object,
            "runner": context_object,
            "program": program,
            "context": context_object,
        }

        try:
            exec(gold_source, exec_globals, exec_locals)
        except AssertionError as exc:
            return GoldAssertionResult(
                passed=False,
                details={
                    "error_type": "assertion_failed",
                    "message": str(exc),
                    "counts": counts,
                },
            )
        except Exception as exc:  # noqa: BLE001
            return GoldAssertionResult(
                passed=False,
                details={
                    "error_type": exc.__class__.__name__,
                    "message": str(exc),
                    "counts": counts,
                },
            )

        return GoldAssertionResult(
            passed=True,
            details={"counts": counts},
        )

    return evaluate_gold_assertion


def namespace(**kwargs: Any) -> SimpleNamespace:
    """Convenience namespace builder for generated wrappers."""

    return SimpleNamespace(**kwargs)
