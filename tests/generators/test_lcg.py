"""Tests del congruencial lineal X_{i+1} = (a·X_i + c) mod m. Referencia: Cap. 2, Hull-Dobell."""

import numpy as np
import pytest
from hypothesis import example, given
from hypothesis import strategies as st

from nnsim.generators.base import RNG
from nnsim.generators.lcg import LCG, satisfies_hull_dobell


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


#: Parámetros que violan Hull-Dobell con m = 2^16 (a=25173, c=13849 sí lo cumplen).
NON_HULL_DOBELL = [
    pytest.param(25173, 13848, "coprim", id="c_par"),
    pytest.param(25172, 13849, "primo", id="a_par"),
    pytest.param(25175, 13849, "4", id="a_3_mod_4"),
]


@pytest.mark.parametrize(("a", "c", "cond"), NON_HULL_DOBELL)
def test_s1_01_lcg_rejects_non_hull_dobell(a: int, c: int, cond: str) -> None:
    """Dados parámetros que no cumplen Hull-Dobell (m=2^16 con c par; a par; a ≡ 3 mod 4),
    cuando construyo con check_full_period=True, entonces ValueError que nombra
    "Hull-Dobell" y la condición violada.

    Referencia: Cap. 2, Hull-Dobell.
    """
    ok, reason = satisfies_hull_dobell(2**16, a, c)
    assert not ok
    assert cond in reason
    with pytest.raises(ValueError, match="Hull-Dobell") as exc:
        LCG(m=2**16, a=a, c=c, seed=1)
    assert cond in str(exc.value)


def test_s1_01_lcg_satisfies_hull_dobell_accepts_valid() -> None:
    """Dados parámetros válidos, cuando consulto satisfies_hull_dobell, entonces (True, "").

    Referencia: Cap. 2, Hull-Dobell.
    """
    assert satisfies_hull_dobell(2**16, 25173, 13849) == (True, "")
    assert satisfies_hull_dobell(2**32, 1664525, 1013904223) == (True, "")


def test_s1_01_lcg_full_period_non_power_of_two() -> None:
    """Dado m=45=3²·5, a=16 (a-1=15=3·5) y c=2, cuando recorro el ciclo, entonces el
    período es 45 (Hull-Dobell con m que no es potencia de 2).

    Referencia: Cap. 2, Hull-Dobell.
    """
    lcg = LCG(m=45, a=16, c=2, seed=0)
    seen = {lcg.next_int() for _ in range(45)}
    assert len(seen) == 45
    assert lcg.next_int() in seen


def test_s1_01_lcg_validates_arguments() -> None:
    """Dados argumentos inválidos (seed negativa, seed ≥ m, seed bool/float, n<0, m<2,
    a o c fuera de [0, m)), cuando construyo o llamo, entonces ValueError/TypeError claro;
    uniform(0) devuelve shape (0,) y dtype float64.

    Referencia: Cap. 2, Hull-Dobell (diseño por contrato, CLAUDE.md sección 4.6).
    """
    with pytest.raises(ValueError, match="seed"):
        LCG(seed=-1)
    with pytest.raises(ValueError, match="seed"):
        LCG(seed=2**32)
    with pytest.raises(TypeError, match="seed"):
        LCG(seed=True)
    with pytest.raises(TypeError, match="seed"):
        LCG(seed=1.5)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="m"):
        LCG(m=1, a=0, c=0, seed=0, check_full_period=False)
    with pytest.raises(ValueError, match="a"):
        LCG(m=16, a=16, c=1, seed=0, check_full_period=False)
    with pytest.raises(ValueError, match="c"):
        LCG(m=16, a=5, c=-1, seed=0, check_full_period=False)

    lcg = LCG()
    with pytest.raises(ValueError, match="seed"):
        lcg.seed(-5)
    with pytest.raises(TypeError, match="seed"):
        lcg.seed(False)
    with pytest.raises(ValueError, match="n"):
        lcg.uniform(-1)
    with pytest.raises(TypeError, match="n"):
        lcg.uniform(2.0)  # type: ignore[arg-type]

    empty = lcg.uniform(0)
    assert empty.shape == (0,)
    assert empty.dtype == np.float64


@pytest.mark.parametrize(("a", "c", "cond"), NON_HULL_DOBELL)
def test_s1_01_lcg_check_disabled_accepts_any_params(a: int, c: int, cond: str) -> None:
    """Dados los parámetros de C4, cuando construyo con check_full_period=False, entonces
    se aceptan y el generador funciona.

    Referencia: Cap. 2, Hull-Dobell.
    """
    lcg = LCG(m=2**16, a=a, c=c, seed=1, check_full_period=False)
    assert lcg.uniform(5).shape == (5,)


@given(seed=st.integers(min_value=0, max_value=2**32 - 1), n=st.integers(1, 200))
@example(seed=0, n=1)
def test_s1_01_lcg_uniform_in_open_interval(seed: int, n: int) -> None:
    """Propiedad: para toda semilla en [0, 2^32) y n en [1, 200], toda uniforme cae en (0, 1).

    Referencia: Cap. 2, Hull-Dobell (CLAUDE.md sección 4.5).
    """
    x = LCG(seed=seed).uniform(n)
    assert x.shape == (n,)
    assert np.all((x > 0.0) & (x < 1.0))


def test_s1_01_lcg_extremes_stay_open() -> None:
    """Dado X_i = m-1 (a=1, c=1, semilla m-2), cuando genero una uniforme, entonces
    0 < r < 1 estricto, porque r = (X+0.5)/m.

    Referencia: Cap. 2, Hull-Dobell (intervalo abierto, requerido por Box-Muller).
    """
    r = LCG(m=2**32, a=1, c=1, seed=2**32 - 2).uniform(1)[0]
    assert 0.0 < r < 1.0


@pytest.mark.parametrize("check", [True, False])
def test_s1_01_lcg_rejects_modulus_above_2_32(check: bool) -> None:
    """Dado un m > 2^32, cuando construyo el LCG (con o sin check_full_period), entonces
    ValueError que menciona el máximo 2^32; m = 2^32 se acepta. Así el puerto garantiza
    r en (0, 1) en float64 (y la factorización por división de prueba termina).

    Referencia: Cap. 2, Hull-Dobell (intervalo abierto, requerido por Box-Muller).
    """
    for m in (2**32 + 1, 2**64):
        with pytest.raises(ValueError, match="2\\^32"):
            LCG(m=m, a=5, c=1, seed=0, check_full_period=check)
    ok = LCG(m=2**32, a=5, c=1, seed=0, check_full_period=check)
    assert ok.m == 2**32
