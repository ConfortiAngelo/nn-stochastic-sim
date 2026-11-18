"""Antepone ``src/`` a ``sys.path`` para correr ``python experiments/eX.py`` sin instalar nnsim.

No se usa ``pip install -e .`` porque, con worktrees, el editable apuntaría al checkout
principal (ADR-001). Cada experimento empieza con ``import _path  # noqa: F401``.
"""

import sys
from pathlib import Path

_SRC = str(Path(__file__).resolve().parent.parent / "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
