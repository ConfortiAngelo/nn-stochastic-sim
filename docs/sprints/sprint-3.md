# Sprint 3 — Dinámica: SGD como caminante al azar, como Euler y contra Metropolis

| Campo | Valor |
|---|---|
| Fechas | jue 3 dic → mié 9 dic 2026 |
| Horas estimadas | 10 h |
| Versión al cerrar | `v0.3.0` |
| Rama de integración | `sprint/3` |
| Milestone de GitHub | `Sprint 3` |
| Capítulos de la cátedra | Cap. 4 (caminante al azar, MSD), Cap. 6 (Markov, Metropolis), Cap. 7 (Euler, logística) |

## Objetivo del sprint

> Mostrar con evidencia cuantitativa que el SGD se comporta como un caminante al azar con deriva (E4) y como el método de Euler con Δt = η (E5), y comparar el gradiente contra un recocido simulado con criterio de Metropolis (E6).

## Backlog del sprint

| ID | Título | Archivos (propiedad) | Depende de | Tipo | h |
|---|---|---|---|---|---|
| S3-01 | Registro de la trayectoria de θ cada k pasos (callback del entrenador) | `src/nnsim/trainers/callbacks.py`, tests | Sprint 2 | TDD núcleo | 1 |
| S3-02 | MSD, ajuste de pendiente log-log y PCA 2D con SVD de NumPy | `src/nnsim/dynamics.py`, `tests/test_dynamics.py` | — | TDD núcleo | 1,5 |
| S3-03 | Validación analítica: GD sobre una cuadrática = Euler hacia adelante | `tests/test_euler_quadratic.py` | — | TDD (validación) | 0,5 |
| S3-04 | Ajuste logístico A(t) = Amax / (1 + e^(−k(t−t0))) | `src/nnsim/fitting.py`, `tests/test_fitting.py` | — | TDD núcleo | 1 |
| S3-05 | Entrenador por recocido simulado (Metropolis, enfriamiento geométrico) | `src/nnsim/trainers/annealing.py`, tests | — | TDD núcleo | 1,5 |
| S3-06 | Experimento E4: MSD con B ∈ {1, 8, 32, lote completo}, R = 50 | `experiments/e4_msd.py`, `figures/e4_*`, `results/e4_*` | S3-01, S3-02 | Experimento | 1 |
| S3-07 | Experimento E5: barrido de η en escala logarítmica entre 1e-3 y 10, R = 30 | `experiments/e5_learning_rate.py`, `figures/e5_*`, `results/e5_*` | S3-04 | Experimento | 1 |
| S3-08 | Experimento E6: grilla T0 × α × σ contra SGD con igual número de evaluaciones de la pérdida | `experiments/e6_annealing.py`, `figures/e6_*`, `results/e6_*` | S3-05 | Experimento | 1,5 |
| S3-09 | Docs: ODD v3, ADR-004 (presupuesto de evaluaciones como eje de comparación), aprendizaje, informe | `docs/...` | todo | Docs | 1 |

**Paralelización sugerida**
- Ola 1: S3-01, S3-02, S3-03, S3-04 y S3-05 en paralelo. Son 5 tareas: en Pro conviene partirlas en 2 tandas de 2 o 3 agentes.
- Ola 2: S3-06, S3-07 y S3-08 en paralelo (cada uno con sus propios archivos).
- Ola 3: S3-09.

## Criterios de aceptación (Dado / Cuando / Entonces)

**S3-01 — Trayectoria**
- Dado k = 10 y 1000 pasos, cuando entreno con el callback, entonces se guardan exactamente 101 vectores θ (incluido θ(0)), y el entrenamiento sin callback da el mismo θ final (el callback no altera la dinámica).

**S3-02 — MSD y PCA**
- Dado un caminante simulado puramente difusivo, cuando calculo el MSD, entonces la pendiente log-log ajustada es ≈ 1.
- Dado un movimiento rectilíneo uniforme, cuando calculo el MSD, entonces la pendiente es ≈ 2.
- Dada una trayectoria, cuando la proyecto con PCA, entonces la varianza explicada informada está en [0, 1] y las componentes son ortonormales.

**S3-03 — Euler (validación del Cap. 7)**
- Dada L(θ) = ½·λ·θ² con λ conocido, cuando aplico n pasos de GD con η, entonces θ_n = (1 − ηλ)^n · θ_0 exactamente.
- Dado η > 2/λ, cuando aplico GD, entonces |θ_n| crece (divergencia); con 1/λ < η < 2/λ oscila con signo alternado y converge; con η < 1/λ converge sin oscilar.

**S3-04 — Ajuste logístico**
- Dada una curva logística sintética con ruido y parámetros conocidos, cuando la ajusto, entonces recupero Amax, k y t0 dentro del 5 %.

**S3-05 — Recocido**
- Dado ΔE ≤ 0, cuando evalúo el criterio, entonces la propuesta se acepta siempre.
- Dado ΔE > 0 y T fija, cuando evalúo el criterio 10^5 veces, entonces la tasa de aceptación empírica ≈ e^(−ΔE/T).
- Dado T → 0, cuando corro el recocido, entonces se comporta como un descenso aleatorio (casi no acepta subidas).
- Dada una propuesta, cuando la genero, entonces usa el `RNG` inyectado (nunca `np.random`).

**S3-06 — E4 (hipótesis)**
- Dado `e4_msd_loglog.png`, cuando lo miro, entonces tiene rectas de referencia de pendiente 1 y 2, y el informe dice en qué tramo el MSD se parece a cada régimen, con la pendiente ajustada y su IC por tamaño de batch.

**S3-07 — E5 (hipótesis)**
- Dado el barrido de η, cuando reporto, entonces cada η se clasifica como converge / oscila / diverge con un criterio numérico explícito (no "a ojo"), y se relaciona con S3-03.
- Dada la mejor η, cuando ajusto la logística a la precisión por época, entonces se informan los parámetros con su R².

**S3-08 — E6 (hipótesis)**
- Dado un presupuesto de N evaluaciones de la pérdida, cuando comparo recocido contra SGD, entonces ambos usan exactamente el mismo presupuesto y se reporta precisión final con IC 95 % (R = 30).
- Dado `e6_acceptance.png`, cuando lo miro, entonces muestra la tasa de aceptación por tramo de temperatura.

## Puntos críticos

1. **Memoria.** Guardar θ en cada paso con B = 1 explota la memoria. Usar k > 1, float32 para la trayectoria y archivos `.npz` en `results/trajectories/`, que **no se versionan** (están en `.gitignore`).
2. **Comparación justa en E6.** El eje es "evaluaciones de la pérdida", no "épocas": un paso de SGD sobre un minibatch y una propuesta de recocido no cuestan lo mismo. Hay que definirlo en ADR-004.
3. **Divergencia en E5.** Con η grande aparecen `inf` o `nan`: capturarlos, marcar la réplica como "diverge" y no romper el experimento.
4. **Las hipótesis pueden fallar.** Si el MSD no muestra el cambio de t² a t, se reporta lo que salió. Es un resultado válido.

## Definition of Done del sprint

- [ ] `python tools/check.py` termina con exit 0.
- [ ] `docs/sprints/sprint-3-review.md` mapea los criterios a sus tests; sin hallazgos altos ni medios.
- [ ] E4, E5 y E6 regenerables con `--quick` (< 90 s cada uno) y en versión completa.
- [ ] ODD v3, ADR-004, `docs/learning/sprint-3.md`, secciones del informe y CHANGELOG.
- [ ] PR `sprint/3 → main` preparada, esperando tu confirmación.

## Condición sugerida para `/goal`

```
/goal El Sprint 3 cumple su Definition of Done de docs/sprints/sprint-3.md: (1) ejecutaste `python tools/check.py` y mostraste el exit 0; (2) corriste e4, e5 y e6 con `--quick`, cada uno con exit 0 en menos de 90 s, y mostraste los tiempos; (3) el test analítico de Euler sobre la cuadrática pasa; (4) docs/sprints/sprint-3-review.md mapea cada criterio a un test que pasa y no tiene hallazgos altos o medios; (5) ningún test existente se debilitó; (6) no hiciste push ni creaste una PR. O pará después de 30 turnos y reportá qué falta.
```

## Entregables para el informe

- `e4_msd_loglog.png`, `e4_trajectory_pca.png` y la tabla de pendientes por B.
- `e5_loss_by_eta.png`, `e5_final_loss_vs_eta.png`, `e5_logistic_fit.png` y la clasificación por η.
- `e6_loss_curves.png`, `e6_acceptance.png` y la tabla comparativa.

## Plan de recorte

1. E6 con una grilla reducida (T0 ∈ {1; 10}, α = 0,995, σ ∈ {0,05; 0,1}).
2. Sacar la PCA de E4 (queda el MSD).
3. **Lo que no se recorta:** E4 (MSD), E5 y el test analítico de Euler. Son núcleo mínimo según el plan.

## Retro (completar al cierre)

- ¿Qué salió bien? / ¿Qué trabó? / ¿Qué cambio en `CLAUDE.md` o en los agentes? / Horas reales:
