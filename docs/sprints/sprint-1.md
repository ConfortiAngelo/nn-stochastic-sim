# Sprint 1 — Fundaciones: azar propio, distribuciones y una red que aprende XOR

| Campo | Valor |
|---|---|
| Fechas | jue 19 nov → mié 25 nov 2026 |
| Horas estimadas | 10 h |
| Versión al cerrar | `v0.1.0` |
| Rama de integración | `sprint/1` |
| Milestone de GitHub | `Sprint 1` |
| Capítulos de la cátedra | Cap. 1 (sistema), Cap. 2 (números pseudoaleatorios), Cap. 5 (transformada inversa) |

## Objetivo del sprint (sprint goal)

> Toda la aleatoriedad del proyecto sale de generadores propios validados contra la teoría, y una red neuronal programada desde cero aprueba el gradient check y resuelve XOR.

## Backlog del sprint

Cada ítem es una issue de GitHub. "Archivos" define la **propiedad de archivos**: dos tareas en paralelo nunca tocan el mismo archivo.

| ID | Título | Archivos (propiedad) | Depende de | Tipo | h |
|---|---|---|---|---|---|
| S1-01 | Interfaz `RNG` (Protocol) + congruencial lineal | `src/nnsim/generators/base.py`, `lcg.py`, `tests/generators/test_lcg.py` | — | TDD núcleo | 1,5 |
| S1-02 | Cuadrados medios | `generators/middle_square.py`, `tests/generators/test_middle_square.py` | S1-01 | TDD núcleo | 0,5 |
| S1-03 | RANDU + adaptador de referencia NumPy | `generators/randu.py`, `generators/numpy_ref.py`, tests | S1-01 | TDD núcleo | 0,5 |
| S1-04 | Pruebas de calidad del generador | `generators/quality.py`, `tests/generators/test_quality.py` | S1-01 | TDD núcleo | 1,5 |
| S1-05 | Distribuciones por transformada inversa y Box-Muller | `src/nnsim/distributions.py`, `tests/test_distributions.py` | S1-01 | TDD núcleo | 1,5 |
| S1-06 | Datasets sintéticos (blobs, XOR, espirales), split y normalización | `src/nnsim/datasets.py`, `tests/test_datasets.py` | S1-01, S1-05 | TDD núcleo | 1 |
| S1-07 | MLP desde cero: forward, backward, pérdida, θ plano, gradient check | `src/nnsim/nn.py`, `tests/test_nn.py` | — (recibe θ ya creado) | TDD núcleo | 2 |
| S1-08 | Descenso por gradiente de lote completo (mínimo) + verificación XOR | `src/nnsim/trainers/gd.py`, `tests/test_xor.py` | S1-05, S1-06, S1-07 | TDD núcleo | 0,5 |
| S1-09 | Experimento E1: validación de generadores | `experiments/e1_generators.py`, `figures/e1_*.png`, `results/e1_*.csv` | S1-01..S1-04 | Experimento | 0,5 |
| S1-10 | Documentación del sprint: ODD v1, ADR-002, nota de aprendizaje | `docs/ODD.md`, `docs/adr/0002-*.md`, `docs/learning/sprint-1.md` | todo lo anterior | Docs | 0,5 |

**Paralelización sugerida** (el orquestador decide la final):
- Ola 1: S1-01 y S1-07 en paralelo (no comparten nada).
- Ola 2: S1-02, S1-03, S1-04 y S1-05 en paralelo (todos dependen solo de S1-01).
- Ola 3: S1-06, luego S1-08 y S1-09.
- Ola 4: S1-10, que la hace el orquestador o `docs-writer`.

## Criterios de aceptación (BDD: Dado / Cuando / Entonces)

Cada criterio debe tener **al menos un test** cuyo nombre o docstring lo referencie (por ejemplo `test_s1_01_lcg_full_period`).

**S1-01 — LCG**
- Dado un LCG con m = 2^16, a = 4·k + 1 y c impar (cumple Hull-Dobell), cuando genero desde una semilla hasta que el estado se repite, entonces el período es exactamente m.
- Dado el LCG con los parámetros del plan (m = 2^32, a = 1664525, c = 1013904223) y semilla 2025, cuando genero 10^5 uniformes, entonces todos están en el intervalo abierto (0, 1), la media está a menos de 4·σ/√n de 1/2 y la varianza cerca de 1/12.
- Dado el mismo generador y la misma semilla, cuando lo corro dos veces, entonces la secuencia es idéntica (reproducibilidad).
- Dados unos parámetros que **no** cumplen Hull-Dobell, cuando construyo el LCG con `check_full_period=True`, entonces se lanza `ValueError` con un mensaje claro.

**S1-02 — Cuadrados medios**
- Dada la semilla 2025 con D = 4, cuando genero valores, entonces la secuencia degenera (llega a 0 o entra en un ciclo) antes de 10^4 pasos, y `quality.period()` lo detecta.

**S1-03 — RANDU**
- Dados tríos consecutivos de RANDU, cuando calculo 9·r_i − 6·r_{i+1} + r_{i+2}, entonces el resultado es siempre entero (salvo error de redondeo), que es la causa de los 15 planos.
- Dada una semilla par, cuando construyo RANDU, entonces se lanza `ValueError` (X0 debe ser impar).

**S1-04 — Calidad**
- Dado un generador ideal (referencia NumPy), cuando aplico χ² con k = 20, entonces el estadístico no supera el valor crítico al 99 %.
- Dada una secuencia constante, cuando aplico χ² y la autocorrelación de rezago 1, entonces ambas pruebas la rechazan.

**S1-05 — Distribuciones**
- Dado U(a, b) por transformada inversa, cuando muestreo 10^5 valores, entonces la media y la varianza coinciden con (a+b)/2 y (b−a)²/12 dentro de la tolerancia estadística.
- Dado Box-Muller sobre el LCG, cuando muestreo N(0, σ²), entonces la media es ≈ 0, la varianza ≈ σ² y nunca se evalúa log(0).
- Dada una tabla empírica discreta, cuando muestreo, entonces las frecuencias observadas coinciden con las teóricas (χ²).
- Dadas capas (n_in, n_out), cuando inicializo con Xavier y con He, entonces la varianza empírica coincide con 2/(n_in+n_out) y 2/n_in respectivamente.
- Propiedad (Hypothesis): para cualquier semilla válida, toda muestra uniforme cae en (a, b).

**S1-06 — Datasets**
- Dado un generador y una semilla, cuando genero espirales dos veces, entonces obtengo exactamente los mismos puntos.
- Dado cualquier dataset, cuando hago el split 80/20 y normalizo, entonces el train queda con media ≈ 0 y desvío ≈ 1, y el test se normaliza **con los parámetros del train** (sin fuga de datos).

**S1-07 — Red neuronal**
- Dada una red 2-8-1 con tanh y θ aleatorio, cuando comparo el gradiente de backprop con diferencias centrales, entonces el error relativo es < 1e-5 (también con ReLU).
- Propiedad (Hypothesis): para cualquier arquitectura chica, `unpack(pack(params)) == params`.
- Dado `nn.py`, cuando reviso sus imports, entonces no importa nada de `generators` ni `distributions` (lo verifica `import-linter`).

**S1-08 — XOR (verificación del Cap. 10 del plan)**
- Dado el dataset XOR, cuando entreno un perceptrón sin capa oculta, entonces la precisión no supera 0,75.
- Dado el dataset XOR, cuando entreno la red 2-8-1 con Xavier y semilla fija, entonces la precisión en test es ≥ 0,95.

**S1-09 — E1**
- Dado `python experiments/e1_generators.py`, cuando lo ejecuto, entonces se generan `results/e1_generators.csv` (período, media, varianza, χ², autocorrelación por generador) y `figures/e1_pairs.png`, `figures/e1_randu_3d.png` y `figures/e1_middle_square_period.png`, de forma determinista.
- Dado `--quick`, cuando lo ejecuto, entonces termina en menos de 30 s.

## Puntos críticos (leer antes de planificar)

1. **Tests estadísticos inestables.** Siempre con semilla fija y tolerancias derivadas de la teoría (por ejemplo 4·σ/√n), nunca "a ojo".
2. **El 0 exacto.** Usar r = (X + 0,5)/m o rechazar 0, porque `log(0)` rompe Box-Muller. Documentarlo en ADR-002.
3. **Desbordes de enteros.** Con m = 2^32, hacer aritmética con `int` de Python o `np.uint64` y no con `int32`. Hay que vectorizar `uniform(n)` sin perder exactitud.
4. **Backprop.** El gradient check va desde el día 1. Si falla, se usa la skill de debugging sistemático; nunca se ajusta la tolerancia para que pase.
5. **XOR con semilla mala.** Si una semilla no converge, no se cambia de semilla en silencio: se documenta. La aceptación pide una semilla fija documentada.

## Definition of Done del sprint

- [ ] `python tools/check.py` termina con exit 0 (ruff, formato, mypy, import-linter, pytest con cobertura ≥ 85 % en `src/`, bandit, pip-audit).
- [ ] Cada criterio de arriba está mapeado a uno o más tests en `docs/sprints/sprint-1-review.md`.
- [ ] Revisión independiente (`reviewer`) sin hallazgos altos ni medios abiertos.
- [ ] Historial TDD visible: cada issue de núcleo tiene un commit `test:` (rojo) antes de su `feat:` (verde).
- [ ] `docs/ODD.md` v1, ADR-002 y `docs/learning/sprint-1.md` escritos.
- [ ] CHANGELOG actualizado; PR `sprint/1 → main` **preparada** (no creada sin tu confirmación).

## Condición sugerida para `/goal`

```
/goal El Sprint 1 cumple su Definition of Done de docs/sprints/sprint-1.md: (1) ejecutaste `python tools/check.py` y mostraste en la salida que terminó con exit 0; (2) docs/sprints/sprint-1-review.md existe, mapea cada criterio Dado/Cuando/Entonces a un test que pasa y no tiene hallazgos altos o medios abiertos; (3) ningún test existente se debilitó o borró para que pase algo; (4) no hiciste push ni creaste una PR. O pará después de 25 turnos y reportá qué falta.
```

## Entregables para el informe

- Tabla de E1 (período, media, varianza, χ², autocorrelación) y las 3 figuras de E1.
- Tabla de elementos del sistema (Cap. 1) en `docs/ODD.md`.
- Histogramas de las distribuciones contra su densidad teórica (los genera un test de verificación visual o el script de E1).

## Plan de recorte (si falta tiempo)

1. Dejar la tabla empírica discreta para el Sprint 2.
2. Dejar el gráfico 3D de RANDU para el Sprint 4 (antes de E7).
3. **Lo que no se recorta:** LCG, Box-Muller, gradient check y XOR.

## Retro (completar al cierre, 10 minutos)

- ¿Qué salió bien?
- ¿Qué trabó?
- ¿Qué cambio en `CLAUDE.md` o en los agentes evita repetirlo?
- Horas reales contra estimadas:
