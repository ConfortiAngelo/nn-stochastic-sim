"""Tests del congruencial lineal X_{i+1} = (a·X_i + c) mod m. Referencia: Cap. 2, Hull-Dobell."""

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
