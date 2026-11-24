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

    @property
    def m(self) -> int:
        """Módulo m."""
        return self._m

    @property
    def a(self) -> int:
        """Multiplicador a."""
        return self._a

    @property
    def c(self) -> int:
        """Incremento c."""
        return self._c

    def seed(self, s: int) -> None:
        """Fija el estado inicial X_0 = s."""
        self._x = s

    def next_int(self) -> int:
        """Avanza la recurrencia y devuelve X_{i+1}."""
        self._x = (self._a * self._x + self._c) % self._m
        return self._x

    def uniform(self, n: int) -> NDArray[np.float64]:
        """Devuelve ``n`` uniformes en (0, 1).

        r_i = (X_i + 0.5) / m. El desplazamiento de 0.5 evita 0 exacto (rompería Box-Muller)
        y deja el máximo en 1 - 1/(2m) < 1.
        """
        out = np.empty(n, dtype=np.float64)
        for i in range(n):  # recurrencia secuencial por definición (CLAUDE.md sección 7)
            out[i] = (self.next_int() + 0.5) / self._m
        return out
