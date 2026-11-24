"""Congruencial lineal X_{i+1} = (a·X_i + c) mod m. Referencia: Cap. 2, Hull-Dobell."""

import numpy as np
from numpy.typing import NDArray


class LCG:
    """Generador congruencial lineal.

    X_{i+1} = (a·X_i + c) mod m.

    Referencia: Cap. 2, Hull-Dobell.
    """

    def __init__(
        self,
        m: int = 2**32,
        a: int = 1664525,
        c: int = 1013904223,
        seed: int = 2025,
    ) -> None:
        self._m = m
        self._a = a
        self._c = c
        self._x = seed

    def seed(self, s: int) -> None:
        """Fija el estado inicial X_0 = s."""
        self._x = s

    def next_int(self) -> int:
        """Avanza la recurrencia y devuelve X_{i+1}."""
        self._x = (self._a * self._x + self._c) % self._m
        return self._x

    def uniform(self, n: int) -> NDArray[np.float64]:
        """Devuelve ``n`` uniformes en (0, 1)."""
        raise NotImplementedError
