"""Fixtures comunes: semillas fijas y documentadas (CLAUDE.md §4.8)."""

import pytest
from hypothesis import settings

# Sin deadline: los tests de propiedades sobre generadores son lentos por diseño (CLAUDE.md §4.5).
settings.register_profile("nnsim", deadline=None)
settings.load_profile("nnsim")

#: Semilla principal del proyecto (la del plan, sección 6.1).
BASE_SEED = 2025


@pytest.fixture
def seed() -> int:
    """Semilla fija principal."""
    return BASE_SEED


@pytest.fixture
def seeds() -> list[int]:
    """Semillas fijas para tests que necesitan varias réplicas."""
    return [BASE_SEED + k for k in range(10)]
