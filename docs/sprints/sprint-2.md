# Sprint 2 — Monte Carlo: réplicas, inicialización y cuánto pesa la semilla

| Campo | Valor |
|---|---|
| Fechas | jue 26 nov → mié 2 dic 2026 |
| Horas estimadas | 10 h |
| Versión al cerrar | `v0.2.0` |
| Rama de integración | `sprint/2` |
| Milestone de GitHub | `Sprint 2` |
| Capítulos de la cátedra | Cap. 3 (aplicaciones, réplicas, IC), Cap. 5 (Monte Carlo, error 1/√N) |

## Objetivo del sprint

> Un runner reproducible corre cientos de entrenamientos con números aleatorios comunes y responde, con intervalos de confianza, cuánto importa la inicialización (E2) y cuántas réplicas hacen falta (E3).

## Backlog del sprint

| ID | Título | Archivos (propiedad) | Depende de | Tipo | h |
|---|---|---|---|---|---|
| S2-01 | SGD con minibatch y mezcla Fisher-Yates usando el `RNG` | `src/nnsim/trainers/sgd.py`, `src/nnsim/sampling.py`, tests | Sprint 1 | TDD núcleo | 1,5 |
| S2-02 | Métricas: precisión, régimen estable (últimas k épocas), épocas a converger | `src/nnsim/metrics.py`, `tests/test_metrics.py` | — | TDD núcleo | 1 |
| S2-03 | Estadística: media, desvío, IC 95 % con t de Student, R requerido | `src/nnsim/stats.py`, `tests/test_stats.py` | — | TDD núcleo | 1 |
| S2-04 | Configuración tipada del experimento + esquema del CSV de resultados | `src/nnsim/config.py`, `tests/test_config.py` | — | TDD núcleo | 1 |
| S2-05 | Runner: R réplicas, semillas derivadas, números aleatorios comunes, devuelve registros | `src/nnsim/runner.py`, `tests/test_runner.py` | S2-01..S2-04 | TDD núcleo | 1,5 |
| S2-06 | Capa de I/O de experimentos: escribir CSV y figuras con nombre fijo, flag `--quick` | `experiments/_io.py`, `experiments/_cli.py`, tests | S2-04 | TDD núcleo | 0,5 |
| S2-07 | Experimento E2: distribución de inicialización (7 inits × espirales × R = 100) | `experiments/e2_init.py`, `figures/e2_*.png`, `results/e2_*.csv` | S2-05, S2-06 | Experimento | 1,5 |
| S2-08 | Experimento E3: variabilidad entre semillas, R = 500, ancho del IC contra R | `experiments/e3_seeds.py`, `figures/e3_*.png`, `results/e3_*.csv` | S2-05, S2-06, mejor config de E2 | Experimento | 1 |
| S2-09 | Docs: ODD v2, ADR-003 (scipy solo para estadística), nota de aprendizaje, secciones del informe | `docs/ODD.md`, `docs/adr/0003-*.md`, `docs/learning/sprint-2.md`, `docs/informe/` | todo | Docs | 1 |

**Paralelización sugerida**
- Ola 1: S2-01, S2-02, S2-03 y S2-04 en paralelo (archivos disjuntos).
- Ola 2: S2-05 y S2-06.
- Ola 3: S2-07 y, cuando esté su resultado, S2-08 (depende de la mejor configuración de E2).
- Ola 4: S2-09.

## Criterios de aceptación (Dado / Cuando / Entonces)

**S2-01 — SGD**
- Dado Fisher-Yates con el `RNG`, cuando mezclo n índices muchas veces, entonces cada posición recibe cada índice con frecuencia ≈ 1/n (χ²) y la salida siempre es una permutación.
- Dado B = n (lote completo), cuando entreno, entonces el resultado coincide exactamente con el `gd.py` del Sprint 1 (prueba de regresión).
- Dada la misma semilla, cuando entreno dos veces, entonces θ final es idéntico bit a bit.

**S2-02 / S2-03 — Métricas y estadística**
- Dadas muestras normales simuladas con media conocida, cuando calculo el IC 95 % en 1000 repeticiones, entonces la cobertura empírica está entre 0,93 y 0,97.
- Dados s = 0,05 y E = 0,01, cuando calculo R requerido, entonces da ⌈(1,96·0,05/0,01)²⌉ = 97.
- Dada una curva de pérdida que cruza el umbral 0,1 en la época 12, cuando calculo las épocas a converger, entonces da 12; si nunca lo cruza, da el tope E.

**S2-04 / S2-05 — Configuración y runner**
- Dada una configuración inválida (η ≤ 0, B < 1, inicialización desconocida), cuando la construyo, entonces se lanza `ValueError`.
- Dadas dos configuraciones que solo difieren en la inicialización, cuando las corro con las mismas R semillas, entonces la réplica i de ambas usa el mismo dataset y el mismo orden de datos (números aleatorios comunes).
- Dado el runner, cuando lo ejecuto, entonces devuelve una fila por réplica con: seed, generator, init, eta, batch_size, final_accuracy, epochs_to_converge, final_loss, wall_time_s. No escribe archivos: eso lo hace `experiments/_io.py`.

**S2-07 — E2 (hipótesis, no resultado esperado)**
- Dado E2 completo, cuando leo la tabla, entonces cada inicialización tiene media e IC 95 % de precisión y de épocas, con R explícito.
- Dado el caso "ceros", cuando reviso los resultados, entonces se informa si la red quedó simétrica (todas las neuronas ocultas iguales). Esto valida la teoría.
- Dado `e2_weight_hist.png`, cuando lo miro, entonces cada histograma de pesos está superpuesto a su densidad teórica.

**S2-08 — E3**
- Dado `e3_ci_vs_R.png`, cuando ajusto log(ancho) contra log(R), entonces la pendiente informada es ≈ −0,5 con su IC, y se compara contra el 1/√N del Cap. 5.
- Dado E3, cuando reporto el R requerido para E = 0,01, entonces se muestra el cálculo con el s observado.

**Rendimiento**
- Dado `--quick`, cuando corro E2 y E3, entonces cada uno termina en menos de 60 s. La corrida completa de cada uno queda documentada con su tiempo real.

## Puntos críticos

1. **Números aleatorios comunes.** Derivar sub-semillas independientes por réplica y por uso (dataset, inicialización, orden de datos) con una función determinista en `sampling.py`. Si un mismo flujo alimenta todo, la comparación entre configuraciones queda contaminada.
2. **Tiempo de cómputo.** 7 × 100 entrenamientos: redes chicas (H = 8), 400 puntos y NumPy vectorizado. Medirlo antes de lanzar la corrida completa.
3. **t de Student.** Con R < 30 no usar 1,96. Usar `scipy.stats.t` (ADR-003: scipy permitido solo en `stats.py` y `generators/quality.py`, nunca para la red).
4. **Separación de capas.** El runner no importa matplotlib ni escribe en disco (lo verifica `import-linter`).

## Definition of Done del sprint

- [ ] `python tools/check.py` termina con exit 0.
- [ ] `docs/sprints/sprint-2-review.md` mapea los criterios a sus tests; sin hallazgos altos ni medios.
- [ ] E2 y E3 regenerables con un comando cada uno; CSV y PNG versionados.
- [ ] Tablas de E2 y E3 con media, IC 95 % y R en `docs/informe/`.
- [ ] ODD v2, ADR-003, `docs/learning/sprint-2.md` y CHANGELOG.
- [ ] PR `sprint/2 → main` preparada, esperando tu confirmación.

## Condición sugerida para `/goal`

```
/goal El Sprint 2 cumple su Definition of Done de docs/sprints/sprint-2.md: (1) ejecutaste `python tools/check.py` y mostraste el exit 0; (2) corriste `python experiments/e2_init.py --quick` y `python experiments/e3_seeds.py --quick`, ambos con exit 0 y en menos de 60 s cada uno, y mostraste el tiempo; (3) docs/sprints/sprint-2-review.md mapea cada criterio a un test que pasa y no tiene hallazgos altos o medios abiertos; (4) ningún test existente se debilitó; (5) no hiciste push ni creaste una PR. O pará después de 25 turnos y reportá qué falta.
```

## Entregables para el informe

- Tabla E2 (inicialización × precisión y épocas, con IC 95 %), `e2_boxplot.png` y `e2_weight_hist.png`.
- `e3_hist.png` con la normal ajustada, `e3_ci_vs_R.png` y el R requerido.

## Plan de recorte

1. E3 con R = 300 en vez de 500.
2. Sacar `U(−3; 3)` y `N(0; 0,01)` de E2 (quedan ceros, U(−0,5; 0,5), N(0; 1), Xavier y He).
3. **Lo que no se recorta:** números aleatorios comunes e IC con R explícito.

## Retro (completar al cierre)

- ¿Qué salió bien? / ¿Qué trabó? / ¿Qué cambio en `CLAUDE.md` o en los agentes? / Horas reales:
