"""Única definición de "verde" del proyecto (CLAUDE.md §5).

Corre las puertas de calidad en orden y corta en el primer fallo, devolviendo su código::

    python tools/check.py               # todo, menos los tests lentos
    python tools/check.py --fast        # sin pip-audit (necesita red)
    python tools/check.py --with-slow   # incluye los tests marcados slow

Multiplataforma y sin dependencias externas: cada herramienta se invoca con
``sys.executable -m <herramienta>`` y lista de argumentos, nunca con ``shell=True``.
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable

# import-linter no trae __main__: se llama a su entry point de click.
LINT_IMPORTS = "from importlinter.cli import lint_imports_command as c; c()"


def build_steps(fast: bool, with_slow: bool) -> list[tuple[str, list[str]]]:
    """Arma la lista ordenada de pasos (nombre, comando)."""
    pytest_cmd = [PY, "-m", "pytest", "--cov=nnsim", "--cov-fail-under=85"]
    if not with_slow:
        pytest_cmd += ["-m", "not slow"]
    steps = [
        ("ruff check", [PY, "-m", "ruff", "check", "."]),
        ("ruff format --check", [PY, "-m", "ruff", "format", "--check", "."]),
        ("mypy", [PY, "-m", "mypy"]),
        ("lint-imports", [PY, "-c", LINT_IMPORTS]),
        ("pytest" + (" (con slow)" if with_slow else ' -m "not slow"'), pytest_cmd),
        ("bandit", [PY, "-m", "bandit", "-r", "src", "-q"]),
    ]
    if not fast:
        steps.append(("pip-audit", [PY, "-m", "pip_audit", "-r", "requirements.txt"]))
    return steps


def _env() -> dict[str, str]:
    # Sin editable install (ADR-001): las herramientas ven el paquete por src/.
    env = dict(os.environ)
    src = str(ROOT / "src")
    env["PYTHONPATH"] = os.pathsep.join(p for p in (src, env.get("PYTHONPATH", "")) if p)
    return env


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Puertas de calidad de nnsim.")
    parser.add_argument("--fast", action="store_true", help="saltea pip-audit (necesita red)")
    parser.add_argument("--with-slow", action="store_true", help="incluye los tests slow")
    args = parser.parse_args(argv)

    results: list[tuple[str, int, float]] = []
    for name, cmd in build_steps(args.fast, args.with_slow):
        print(f"\n=== {name}", flush=True)
        start = time.perf_counter()
        code = subprocess.run(cmd, cwd=ROOT, env=_env(), check=False).returncode
        results.append((name, code, time.perf_counter() - start))
        print(f"{'✔' if code == 0 else '✘'} {name}", flush=True)
        if code != 0:
            break

    print("\n--- resumen")
    for name, code, secs in results:
        print(f"{'✔' if code == 0 else '✘'} {name:<28} {secs:6.1f} s")
    failed = [code for _, code, _ in results if code != 0]
    if failed:
        print(f"✘ ROJO (exit {failed[0]})")
        return failed[0]
    skipped = " (pip-audit salteado por --fast)" if args.fast else ""
    print(f"✔ VERDE{skipped}")
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    sys.exit(main())
