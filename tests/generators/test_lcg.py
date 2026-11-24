"""Tests del congruencial lineal X_{i+1} = (a·X_i + c) mod m. Referencia: Cap. 2, Hull-Dobell."""

import numpy as np

from nnsim.generators.base import RNG
from nnsim.generators.lcg import LCG


def test_s1_01_lcg_satisfies_rng_protocol() -> None:
    """Dado un LCG, cuando lo chequeo con isinstance(_, RNG), entonces cumple el puerto.

    Referencia: Cap. 2, Hull-Dobell.
    """
    assert isinstance(LCG(), RNG)


def test_s1_01_lcg_full_period() -> None:
    """Dado m=2^16, a=25173 (4·6293+1) y c=13849 (impar), cuando genero hasta volver a X0,
    entonces el período es exactamente m = 65536.

    Referencia: Cap. 2, Hull-Dobell (período completo).
    """
    m = 2**16
    x0 = 1
    lcg = LCG(m=m, a=25173, c=13849, seed=x0)
    steps = 0
    # Tope m + 1 para que un LCG defectuoso no cuelgue el test
    while steps <= m:
        steps += 1
        if lcg.next_int() == x0:
            break
    assert steps == m


def test_s1_01_lcg_reproducible() -> None:
    """Dado el mismo generador y la misma semilla, cuando lo corro dos veces (dos instancias y
    seed() de nuevo sobre la misma), entonces la secuencia es idéntica bit a bit; además
    next_int() seguido de uniform(1) equivale al paso siguiente.

    Referencia: Cap. 2, Hull-Dobell (reproducibilidad, sección 4.8).
    """
    a = LCG(seed=2025).uniform(1000)
    b = LCG(seed=2025).uniform(1000)
    assert np.array_equal(a, b)

    lcg = LCG(seed=2025)
    first = lcg.uniform(1000)
    lcg.seed(2025)
    assert np.array_equal(first, lcg.uniform(1000))

    # Estado compartido: next_int() consume un paso y uniform(1) usa el siguiente
    shared = LCG(seed=7)
    x1 = shared.next_int()
    u2 = shared.uniform(1)[0]
    ref = LCG(seed=7)
    ref.next_int()
    x2 = ref.next_int()
    assert x1 != x2
    assert u2 == (x2 + 0.5) / ref.m


def test_s1_01_lcg_uniform_moments() -> None:
    """Dado m=2^32, a=1664525, c=1013904223 y semilla 2025, cuando genero 10^5 uniformes,
    entonces todas están en (0,1), |media-0.5| < 4·σ/√n y |var-1/12| < 4·sqrt(1/(180·n)).

    Referencia: Cap. 2, Hull-Dobell; momentos de U(0,1): μ=1/2, σ²=1/12.
    """
    n = 10**5
    x = LCG(m=2**32, a=1664525, c=1013904223, seed=2025).uniform(n)
    assert x.shape == (n,)
    assert np.all((x > 0.0) & (x < 1.0))

    sigma = np.sqrt(1.0 / 12.0)
    tol_mean = 4.0 * sigma / np.sqrt(n)
    # Var(s²) ≈ (μ4 - σ⁴)/n con μ4 = 1/80 y σ⁴ = 1/144 → μ4 - σ⁴ = 1/180
    tol_var = 4.0 * np.sqrt(1.0 / (180.0 * n))
    assert abs(x.mean() - 0.5) < tol_mean
    assert abs(x.var() - 1.0 / 12.0) < tol_var
