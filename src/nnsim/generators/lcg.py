"""Congruencial lineal X_{i+1} = (a·X_i + c) mod m. Referencia: Cap. 2, Hull-Dobell."""

from math import gcd

import numpy as np
from numpy.typing import NDArray

#: Tope de m: garantiza (X+0.5)/m < 1 en float64 y factorización barata (sqrt(m) <= 2^16).
MAX_MODULUS = 2**32


def _prime_factors(n: int) -> list[int]:
    """Primos distintos de ``n`` por división de prueba (alcanza para m <= 2^32)."""
    primes: list[int] = []
    p = 2
    while p * p <= n:
        if n % p == 0:
            primes.append(p)
            while n % p == 0:
                n //= p
        p += 1 if p == 2 else 2  # tras el 2 alcanza con los impares
    if n > 1:
        primes.append(n)
    return primes


def satisfies_hull_dobell(m: int, a: int, c: int) -> tuple[bool, str]:
    """Verifica las condiciones de Hull-Dobell para período completo m.

    El LCG X_{i+1} = (a·X_i + c) mod m tiene período m si y solo si:

    1. gcd(c, m) = 1.
    2. p | (a - 1) para todo primo p que divide a m.
    3. 4 | (a - 1) si 4 | m.

    Parameters
    ----------
    m, a, c : int
        Módulo, multiplicador e incremento.

    Returns
    -------
    tuple[bool, str]
        ``(True, "")`` si cumple; si no, ``(False, motivo)`` con la condición violada.

    Referencia: Cap. 2, Hull-Dobell.
    """
    g = gcd(c, m)
    if g != 1:
        return False, f"c={c} y m={m} no son coprimos (gcd={g})"
    for p in _prime_factors(m):
        if (a - 1) % p != 0:
            return False, f"el primo p={p} divide a m={m} pero no a a-1={a - 1}"
    if m % 4 == 0 and (a - 1) % 4 != 0:
        return False, f"4 divide a m={m} pero no a a-1={a - 1}"
    return True, ""


def _require_int(value: object, name: str) -> int:
    """Exige ``int`` o ``np.integer`` (no ``bool``/``np.bool_``); devuelve ``int`` nativo."""
    if isinstance(value, bool | np.bool_) or not isinstance(value, int | np.integer):
        raise TypeError(f"{name} debe ser int, no {type(value).__name__}")
    return int(value)


def _check_seed(s: object, m: int) -> int:
    """Valida la precondición 0 <= s < m."""
    s = _require_int(s, "seed")
    if not 0 <= s < m:
        raise ValueError(f"seed debe estar en [0, {m}), recibió {s}")
    return s


class LCG:
    """Generador congruencial lineal.

    X_{i+1} = (a·X_i + c) mod m.

    Precondición: 2 <= m <= 2^32. El tope asegura que r = (X + 0.5)/m quede en el
    intervalo abierto (0, 1) en float64 (con m >= 2^53 podría redondear a 1.0) y que
    la verificación de Hull-Dobell por división de prueba termine rápido.

    Referencia: Cap. 2, Hull-Dobell.
    """

    def __init__(
        self,
        m: int = 2**32,
        a: int = 1664525,
        c: int = 1013904223,
        seed: int = 2025,
        check_full_period: bool = True,
    ) -> None:
        m = _require_int(m, "m")
        a = _require_int(a, "a")
        c = _require_int(c, "c")
        if m < 2:
            raise ValueError(f"m debe ser >= 2, recibió {m}")
        if m > MAX_MODULUS:
            raise ValueError(
                f"m debe ser <= 2^32 (recibió {m}): con m mayor (X+0.5)/m puede redondear a 1.0 "
                "en float64 y la factorización por división de prueba se vuelve inviable"
            )
        if not 0 <= a < m:
            raise ValueError(f"a debe estar en [0, {m}), recibió {a}")
        if not 0 <= c < m:
            raise ValueError(f"c debe estar en [0, {m}), recibió {c}")
        if check_full_period:
            ok, reason = satisfies_hull_dobell(m, a, c)
            if not ok:
                raise ValueError(f"Los parámetros no cumplen Hull-Dobell: {reason}")
        self._m = m
        self._a = a
        self._c = c
        self._x = _check_seed(seed, m)

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
        self._x = _check_seed(s, self._m)

    def next_int(self) -> int:
        """Avanza la recurrencia y devuelve X_{i+1}."""
        self._x = (self._a * self._x + self._c) % self._m
        return self._x

    def uniform(self, n: int) -> NDArray[np.float64]:
        """Devuelve ``n`` uniformes en (0, 1).

        r_i = (X_i + 0.5) / m. El desplazamiento de 0.5 evita 0 exacto (rompería Box-Muller)
        y deja el máximo en 1 - 1/(2m) < 1.
        """
        n = _require_int(n, "n")
        if n < 0:
            raise ValueError(f"n debe ser >= 0, recibió {n}")
        out = np.empty(n, dtype=np.float64)
        for i in range(n):  # recurrencia secuencial por definición (CLAUDE.md sección 7)
            out[i] = (self.next_int() + 0.5) / self._m
        return out
