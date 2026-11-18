"""El puerto RNG es un Protocol verificable en tiempo de ejecución. Referencia: Cap. 2."""

import numpy as np
from numpy.typing import NDArray

from nnsim.generators.base import RNG


class _DummyRNG:
    """Adaptador mínimo que cumple el contrato estructural del puerto."""

    def __init__(self) -> None:
        self._x = 1

    def seed(self, s: int) -> None:
        self._x = s

    def next_int(self) -> int:
        self._x += 1
        return self._x

    def uniform(self, n: int) -> NDArray[np.float64]:
        return np.full(n, 0.5)


class _Incomplete:
    """Le falta uniform(): no cumple el puerto."""

    def seed(self, s: int) -> None: ...

    def next_int(self) -> int:
        return 0


def test_s0_04_dummy_satisfies_rng_protocol() -> None:
    """Dada una clase con seed, next_int y uniform, cuando la chequeo, entonces es un RNG."""
    rng = _DummyRNG()
    assert isinstance(rng, RNG)
    rng.seed(7)
    assert rng.next_int() == 8
    assert rng.uniform(3).shape == (3,)


def test_s0_04_incomplete_class_is_not_rng() -> None:
    """Dada una clase sin uniform(), cuando la chequeo, entonces no es un RNG."""
    assert not isinstance(_Incomplete(), RNG)
