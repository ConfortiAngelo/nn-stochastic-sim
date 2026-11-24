# S1-01 (issue #1) — Interfaz `RNG` + congruencial lineal: plan de implementación

> **Para el trabajador:** este plan lo ejecuta un agente `implementer` del proyecto (worktree
> aislado, TDD). No usar subagent-driven-development ni using-git-worktrees (CLAUDE.md §2).

**Objetivo:** un LCG validado contra Hull-Dobell que cumple el puerto `RNG` y es el generador
principal del proyecto (Cap. 2).

**Arquitectura:** `nnsim.generators.lcg.LCG` es un adaptador estructural (sin herencia) del
`Protocol RNG` ya existente en `generators/base.py` (ADR-001). Aritmética exacta con `int` de
Python; `generators` no importa nada del resto de `nnsim`.

**Stack:** Python ≥ 3.11, NumPy, pytest, Hypothesis.

**Diseño:** aprobado en la conversación del 2026-11-23 (resumen en "Decisiones" abajo).
Fuentes: issue #1, `docs/sprints/sprint-1.md` (S1-01), sección 6.1 de
`docs/Proyecto_Simulacion_IA_detalle.pdf`.

## Restricciones globales

- Archivos exclusivos: `src/nnsim/generators/base.py`, `src/nnsim/generators/lcg.py`,
  `tests/generators/test_lcg.py`. Nada más.
- Sin `np.random`, sin `print`, sin dependencias nuevas, sin SciPy en `lcg.py`.
- Type hints completos (`NDArray[np.float64]`), mypy estricto, docstrings NumPy con fórmula y
  `Referencia: Cap. 2`.
- Contratos con `ValueError`/`TypeError`, nunca `assert` en `src/`.
- Funciones ≤ ~40 líneas. Comentarios en español, identificadores en inglés, commits en inglés.
- Tolerancias estadísticas derivadas de la teoría; prohibido aflojarlas.

## Decisiones (rulings del orquestador)

| # | Decisión | Por qué |
|---|---|---|
| R1 | r_i = (X_i + 0,5) / m | El plan (§6.1) usa X/m, que da 0 exacto y rompe el intervalo abierto y Box-Muller. Con m = 2^32 el máximo es 1 − 2^-33 < 1, representable en float64. Lo documenta ADR-002 en S1-10. |
| R2 | `check_full_period=True` por defecto | Seguro por defecto (diseño por contrato). Quien quiera un LCG sin período completo lo pide explícito. |
| R3 | `uniform(n)` con bucle simple sobre `int` | CLAUDE.md §7 lo permite en generadores; 10^5 valores ≈ 30 ms. Sin jump-ahead (YAGNI). |
| R4 | `seed(s)`: `int` (no `bool`) en [0, m) | Precondición explícita; fuera de rango → `ValueError`, tipo incorrecto → `TypeError`. |
| R5 | `next_int()` avanza y devuelve X_{i+1} | Coincide con la docstring del Protocol ("avanza la recurrencia y devuelve el siguiente X_i"). |
| R6 | `base.py` no cambia de interfaz | El Protocol ya existe (S0-04). Solo se permite precisar docstrings si hace falta. |

## Criterios de aceptación → tests

| ID | Dado / Cuando / Entonces | Test |
|---|---|---|
| C1 | **Dado** un LCG con m = 2^16, a = 25173 (= 4·6293 + 1) y c = 13849 (impar), **cuando** genero desde una semilla hasta que el estado se repite, **entonces** el período es exactamente m = 65536. | `test_s1_01_lcg_full_period` |
| C2 | **Dado** el LCG con m = 2^32, a = 1664525, c = 1013904223 y semilla 2025, **cuando** genero 10^5 uniformes, **entonces** todos están en (0, 1), \|x̄ − ½\| < 4·σ/√n con σ = 1/√12, y \|s² − 1/12\| < 4·√((μ₄ − σ⁴)/n) = 4·√(1/(180·n)). | `test_s1_01_lcg_uniform_moments` |
| C3 | **Dado** el mismo generador y la misma semilla, **cuando** lo corro dos veces (dos instancias, y `seed()` de nuevo sobre la misma), **entonces** la secuencia es idéntica bit a bit. | `test_s1_01_lcg_reproducible` |
| C4 | **Dados** parámetros que no cumplen Hull-Dobell (m = 2^16 con: c par; a par; a ≡ 3 mod 4), **cuando** construyo con `check_full_period=True`, **entonces** `ValueError` cuyo mensaje nombra "Hull-Dobell" y la condición violada. | `test_s1_01_lcg_rejects_non_hull_dobell` (parametrizado) |
| C5 | Propiedad (Hypothesis, §4.5): para cualquier semilla en [0, 2^32) y n en [1, 200], toda uniforme cae en (0, 1). | `test_s1_01_lcg_uniform_in_open_interval` |
| C6 | **Dado** un `LCG`, **cuando** lo chequeo con `isinstance(_, RNG)`, **entonces** cumple el puerto. | `test_s1_01_lcg_satisfies_rng_protocol` |
| C7 | **Dados** argumentos inválidos (seed negativa, seed ≥ m, seed `bool`/`float`, n < 0, m < 2, a o c fuera de [0, m)), **cuando** construyo o llamo, **entonces** `ValueError`/`TypeError` con mensaje claro; y con `check_full_period=False` los mismos parámetros de C4 se aceptan. | `test_s1_01_lcg_validates_arguments`, `test_s1_01_lcg_check_disabled_accepts_any_params` |

## Review Focus (lo que los criterios no cubren y puede morder)

1. Estado X = 0 → r = 0,5/m > 0: incluido en C5 vía semilla 0 (`@example(seed=0, n=1)`).
2. Estado X = m − 1 → r < 1 estricto: test `test_s1_01_lcg_extremes_stay_open` con
   `LCG(m=2**32, a=1, c=1, seed=2**32 - 2).uniform(1)` (que produce X = m − 1) → valor < 1.0.
3. `uniform(0)` devuelve array vacío de forma `(0,)` y dtype float64 (en C7).
4. Hull-Dobell con m no potencia de 2: c coprimo con m y a − 1 divisible por cada primo de m.
   Test: m = 45 = 3²·5, a = 16 (a − 1 = 15 = 3·5), c = 2 → período 45
   (`test_s1_01_lcg_full_period_non_power_of_two`).
5. `uniform` y `next_int` comparten estado: `next_int()` seguido de `uniform(1)` equivale al
   paso siguiente (cubierto en C3).

---

## Ola 1 (única) — 1 agente `implementer`

### Tarea 1: LCG con Hull-Dobell

**Archivos (exclusivos):**
- Modificar: `src/nnsim/generators/lcg.py` (hoy solo docstring)
- Modificar (solo docstrings, opcional): `src/nnsim/generators/base.py`
- Crear: `tests/generators/test_lcg.py`

**Interfaces:**
- Consume: `nnsim.generators.base.RNG` (Protocol: `seed(s: int) -> None`,
  `next_int() -> int`, `uniform(n: int) -> NDArray[np.float64]`).
- Produce (lo usan S1-02..S1-05, S1-09):
  - `class LCG` con `__init__(self, m: int = 2**32, a: int = 1664525, c: int = 1013904223,
    seed: int = 2025, check_full_period: bool = True) -> None`
  - `seed(s: int) -> None`, `next_int() -> int`, `uniform(n: int) -> NDArray[np.float64]`
  - propiedades de solo lectura `m`, `a`, `c` (`int`)
  - `def satisfies_hull_dobell(m: int, a: int, c: int) -> tuple[bool, str]` (función pública
    del módulo; el `str` explica la condición violada, vacío si cumple).

**Pasos (repetir Red → Green por criterio, en el orden C6, C1, C3, C2, C4, C7, C5, Review Focus):**

- [ ] **Red:** escribir el/los test(s) del criterio con docstring que cite el Dado/Cuando/Entonces
  y `Referencia: Cap. 2, Hull-Dobell`. Correr
  `python -m pytest tests/generators/test_lcg.py -q` y mostrar que falla por la razón correcta
  (ImportError/AttributeError/aserción, no SyntaxError). Commit `test(lcg): ...`.
- [ ] **Green:** mínimo código en `lcg.py`. Commit `feat(lcg): ...`.
- [ ] Detalles que el test no determina:
  - C1: contar pasos con `next_int()` hasta volver a X_0, con tope m + 1 para no colgarse.
  - C2: σ y las tolerancias se calculan en el test a partir de las fórmulas, no como literales.
  - Hull-Dobell: factorizar m por división de prueba (m ≤ 2^32 alcanza); condiciones
    (i) gcd(c, m) = 1, (ii) p | (a − 1) para todo primo p | m, (iii) 4 | (a − 1) si 4 | m.
  - Mensaje de error de ejemplo: `"Los parámetros no cumplen Hull-Dobell: c=2 y m=65536 no son
    coprimos (gcd=2)"`.
- [ ] **Refactor** (opcional, en verde): `refactor(lcg): ...`.
- [ ] **Verificación:** `python tools/check.py --fast` → exit 0 (cobertura global ≥ 85 %).

**Commits esperados (inglés, `Refs #1`):** pares `test(lcg): ...` → `feat(lcg): ...`, sin
atribución a IA.

## Integración (orquestador)

1. Verificar `git log --oneline sprint/1..<rama>` (test antes de feat, sin atribución) y
   `git diff --stat sprint/1...<rama>` (solo los 3 archivos).
2. `git merge --no-ff <rama>` con `Closes #1`; luego `python tools/check.py`.
3. `reviewer` + `security-auditor` en paralelo sobre `git diff <base>..sprint/1`. Hallazgos
   altos/medios → vuelve al implementer (máx. 2 rondas).
4. `python tools/check.py` final (sin `--fast`).

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Test estadístico frágil | Semilla fija 2025, tolerancias 4σ derivadas; nunca se aflojan. |
| Periodo m = 2^16 lento | 65 536 iteraciones de `int` ≈ 20 ms; muy por debajo de 5 s, no es `slow`. |
| Hypothesis lento | `max_examples` por defecto con n ≤ 200; `deadline=None` ya en `conftest.py`. |
| Contradicción X/m vs. (X+0,5)/m | Resuelta por R1; ADR-002 (S1-10) la formaliza. |

**ADR:** no hace falta uno nuevo para esta issue (no se rompe ninguna regla de §3 ni se agrega
dependencia). La decisión R1 se documenta en ADR-002, que ya está planificado en S1-10.

## Fuera de alcance

- Cuadrados medios, RANDU, `numpy_ref`, `quality.py` (S1-02..S1-04).
- ADR-002, ODD y nota de aprendizaje (S1-10).
- Jump-ahead / vectorización de la recurrencia.
