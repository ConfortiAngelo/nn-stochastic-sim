"""Reglas de arquitectura y seguridad sobre src/ verificadas con ast (CLAUDE.md §1, §3 y §6).

Complementa a import-linter: cubre lo que un contrato de imports no puede ver (llamadas a
``print``/``eval``, uso de ``np.random`` por atributo, librerías prohibidas).
"""

import ast
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src" / "nnsim"

#: Único adaptador autorizado a usar np.random (CLAUDE.md §3, regla 4).
NUMPY_REF = "generators/numpy_ref.py"
#: SciPy solo en estadística y calidad de generadores (CLAUDE.md §1, ADR-003).
SCIPY_ALLOWED = frozenset({"stats.py", "generators/quality.py"})
FORBIDDEN_LIBS = frozenset({"torch", "tensorflow", "jax", "sklearn", "keras"})
FORBIDDEN_CALLS = frozenset({"eval", "exec", "print"})


def _numpy_aliases(tree: ast.AST) -> set[str]:
    aliases = {"numpy"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            aliases |= {a.asname or a.name for a in node.names if a.name == "numpy"}
    return aliases


def _check_module(module: str, relpath: str, names: list[str]) -> list[str]:
    """Reglas sobre un import absoluto ``module`` (con ``names`` si es from-import)."""
    top = module.split(".")[0]
    found: list[str] = []
    if top in FORBIDDEN_LIBS:
        found.append(f"librería prohibida: {module}")
    if top in {"pickle", "experiments"}:
        found.append(f"import prohibido: {module}")
    if top == "scipy" and relpath not in SCIPY_ALLOWED:
        found.append(f"scipy fuera de stats/quality: {module}")
    uses_np_random = module.startswith("numpy.random") or (module == "numpy" and "random" in names)
    if uses_np_random and relpath != NUMPY_REF:
        found.append(f"np.random fuera de {NUMPY_REF}: {module}")
    in_generators = relpath.startswith("generators/")
    if in_generators and top == "nnsim" and not module.startswith("nnsim.generators"):
        found.append(f"generators importa el resto de nnsim: {module}")
    return found


def find_violations(source: str, relpath: str) -> list[str]:
    """Devuelve las violaciones de ``source``; ``relpath`` es relativo a src/nnsim."""
    tree = ast.parse(source)
    np_aliases = _numpy_aliases(tree)
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found += _check_module(alias.name, relpath, [])
        elif isinstance(node, ast.ImportFrom):
            names = [a.name for a in node.names]
            if node.level == 0 and node.module:
                found += _check_module(node.module, relpath, names)
            elif node.level >= 2 and relpath.startswith("generators/"):
                found.append(f"generators importa el resto de nnsim: {'.' * node.level}")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in FORBIDDEN_CALLS:
                found.append(f"llamada prohibida: {node.func.id}()")
        elif (
            isinstance(node, ast.Attribute)
            and node.attr == "random"
            and isinstance(node.value, ast.Name)
            and node.value.id in np_aliases
            and relpath != NUMPY_REF
        ):
            found.append(f"np.random fuera de {NUMPY_REF}")
    return found


def _src_files() -> list[Path]:
    return sorted(SRC.rglob("*.py"))


# ------------------------------------------------------------------ el detector funciona

BAD_SNIPPETS = [
    ("import numpy as np\nx = np.random.default_rng(0)\n", "nn.py"),
    ("import numpy\nx = numpy.random.rand(3)\n", "datasets.py"),
    ("from numpy import random\n", "sampling.py"),
    ("from numpy.random import default_rng\n", "trainers/sgd.py"),
    ("import numpy.random\n", "distributions.py"),
    ("import torch\n", "nn.py"),
    ("from sklearn.datasets import make_moons\n", "datasets.py"),
    ("import tensorflow as tf\n", "nn.py"),
    ("import jax.numpy as jnp\n", "nn.py"),
    ("import keras\n", "nn.py"),
    ("eval('1+1')\n", "config.py"),
    ("exec('x = 1')\n", "config.py"),
    ("import pickle\n", "runner.py"),
    ("print('debug')\n", "metrics.py"),
    ("import experiments.e1_generators\n", "runner.py"),
    ("from experiments import _io\n", "runner.py"),
    ("from scipy import stats\n", "nn.py"),
    ("from nnsim.nn import forward\n", "generators/lcg.py"),
    ("from ..distributions import normal\n", "generators/lcg.py"),
]

GOOD_SNIPPETS = [
    ("import numpy as np\nx = np.zeros(3)\n", "nn.py"),
    ("from numpy.typing import NDArray\n", "generators/base.py"),
    ("import numpy as np\nrng = np.random.default_rng(0)\n", NUMPY_REF),
    ("from scipy import stats\n", "stats.py"),
    ("from scipy.stats import chi2\n", "generators/quality.py"),
    ("from .base import RNG\n", "generators/lcg.py"),
    ("from nnsim.generators.base import RNG\n", "generators/lcg.py"),
    ("msg = 'print eval exec pickle'\n", "config.py"),
    ("def f(rng):\n    return rng.random\n", "sampling.py"),
]


@pytest.mark.parametrize(("source", "relpath"), BAD_SNIPPETS)
def test_s0_04_detector_flags_forbidden_code(source: str, relpath: str) -> None:
    """Dado código que rompe una regla de CLAUDE.md, cuando lo analizo, entonces se detecta."""
    assert find_violations(source, relpath)


@pytest.mark.parametrize(("source", "relpath"), GOOD_SNIPPETS)
def test_s0_04_detector_accepts_legit_code(source: str, relpath: str) -> None:
    """Dado código legítimo, cuando lo analizo, entonces no hay falsos positivos."""
    assert find_violations(source, relpath) == []


# ------------------------------------------------------------------ el repo cumple


def test_s0_04_src_tree_is_not_empty() -> None:
    """Dado src/nnsim, cuando lo recorro, entonces encuentro los módulos del plan (no es vacuo)."""
    names = {p.relative_to(SRC).as_posix() for p in _src_files()}
    assert {"nn.py", "generators/base.py", NUMPY_REF, "runner.py"} <= names


@pytest.mark.parametrize("path", _src_files(), ids=lambda p: p.relative_to(SRC).as_posix())
def test_s0_04_src_module_respects_rules(path: Path) -> None:
    """Dado un módulo de src/, cuando lo analizo, entonces no usa azar, librerías ni llamadas
    prohibidas, ni importa experiments."""
    relpath = path.relative_to(SRC).as_posix()
    assert find_violations(path.read_text(encoding="utf-8"), relpath) == []
