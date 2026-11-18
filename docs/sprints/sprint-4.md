# Sprint 4 — Cierre: generador malo, seguridad de IA, informe y release

| Campo | Valor |
|---|---|
| Fechas | jue 10 dic → mié 16 dic 2026 |
| Horas estimadas | 8 a 10 h |
| Versión al cerrar | `v1.0.0` |
| Rama de integración | `sprint/4` |
| Milestone de GitHub | `Sprint 4` |
| Capítulos de la cátedra | Cap. 2 y 3 (E7), Cap. 1 (informe por los 10 pasos), seguridad de IA (E8, opcional) |

## Objetivo del sprint

> Cerrar la pregunta central con E7, dejar el proyecto reproducible con un solo comando y entregar el informe, la presentación y un repositorio público de calidad de portfolio, publicado como `v1.0.0`.

## Backlog del sprint

| ID | Título | Archivos (propiedad) | Depende de | Tipo | h |
|---|---|---|---|---|---|
| S4-01 | Experimento E7: mejor configuración × {LCG, cuadrados medios, RANDU, NumPy}, R = 100 | `experiments/e7_bad_rng.py`, `figures/e7_*`, `results/e7_*` | Sprints 1–3 | Experimento | 1,5 |
| S4-02 | (Opcional) E8: envenenamiento de etiquetas {0, 5, 10, 20, 30, 40 %} × {al azar, cerca de la frontera}, R = 50 | `src/nnsim/poisoning.py`, tests, `experiments/e8_poisoning.py` | S4-01 hecho | TDD + experimento | 1,5 |
| S4-03 | Reproducibilidad total: `tools/reproduce_all.py` regenera todas las figuras y compara hashes de los CSV | `tools/reproduce_all.py`, `tests/test_reproducibility.py` | — | TDD | 1 |
| S4-04 | README en inglés para el portfolio (problema, preguntas, 4 o 5 figuras, cómo reproducir, *Why it matters for AI security*) | `README.md` | resultados | Docs | 1 |
| S4-05 | Informe final en español, estructurado por los 10 pasos del Cap. 1 | `docs/informe/` → `docs/informe.pdf` | resultados | Docs | 2 |
| S4-06 | Presentación de 15 minutos (guion de la sección 11 del plan) | `docs/presentacion.pdf` | S4-05 | Docs | 1 |
| S4-07 | Auditoría final de calidad y seguridad (`security-auditor` + `reviewer` sobre todo el repo) | `docs/sprints/sprint-4-review.md` | todo | Revisión | 0,5 |
| S4-08 | Release: CHANGELOG, tag `v1.0.0`, GitHub Release con figuras y el PDF del informe | `CHANGELOG.md` | todo | Release | 0,5 |

**Paralelización sugerida**
- Ola 1: S4-01 y S4-03 en paralelo; S4-02 solo si al terminar S4-01 quedan al menos 3 h.
- Ola 2: S4-04 y S4-05 en paralelo (`docs-writer`). S4-06 va después de S4-05.
- Ola 3: S4-07, luego S4-08. Esta la ejecuta el orquestador, con tu confirmación para el tag y la Release.

## Criterios de aceptación (Dado / Cuando / Entonces)

**S4-01 — E7 (hipótesis)**
- Dado E7, cuando reporto, entonces hay una tabla con precisión media e IC 95 % por generador y `e7_boxplot.png`, y una discusión de si las pruebas de E1 anticipaban el daño. Cada afirmación va con su número.
- Dado cuadrados medios, cuando entreno, entonces se informa cuántas réplicas tuvieron pesos u órdenes de datos repetidos por el período corto.

**S4-02 — E8 (opcional)**
- Dado un porcentaje p, cuando envenenamos al azar, entonces exactamente ⌊p·n⌋ etiquetas del **train** se invierten y el **test** queda limpio.
- Dado el envenenamiento "cerca de la frontera", cuando lo aplico, entonces elige los puntos de menor margen según un modelo limpio de referencia (criterio documentado).
- Dado `e8_accuracy_vs_poison.png`, cuando lo miro, entonces tiene bandas de IC 95 % para ambas estrategias.

**S4-03 — Reproducibilidad**
- Dado un clon limpio, cuando corro `python tools/reproduce_all.py --quick`, entonces se regeneran todas las figuras sin error, y los CSV de modo quick tienen el mismo hash SHA-256 que los versionados.

**S4-04 — README**
- Dado el README, cuando lo leo, entonces la primera pantalla dice qué demuestra el proyecto en una frase, tiene el badge de CI y una figura clave, y tiene la sección *How to reproduce* con comandos copiables y la sección *Why it matters for AI security* con referencia a MITRE ATLAS.

**S4-05 — Informe**
- Dado el informe, cuando lo reviso, entonces sigue los 10 pasos del Cap. 1, cada resultado tiene IC y R, y cada experimento cita su capítulo según la tabla de la sección 3 del plan.
- Dado el informe, cuando lo reviso, entonces tiene una sección de verificación y otra de validación separadas, y una de limitaciones.

## Puntos críticos

1. **No inventar conclusiones.** El informe y el README solo afirman lo que muestran los CSV. El `reviewer` cruza cada número del texto contra `results/`.
2. **Tiempo.** Es la semana con menos margen: si E8 amenaza la entrega, se corta sin discusión (plan de recorte del plan original: E8 → Vensim → E6 → E7).
3. **Defensa oral.** Antes de entregar, vos tenés que poder explicar backprop, Box-Muller, Metropolis y por qué SGD = Euler sin mirar el código. Revisá los `docs/learning/`.
4. **Datos sensibles.** El repo es público: nada de nombres de compañeros, DNI ni datos de la facultad que no quieras publicar.

## Definition of Done del sprint (y del proyecto)

- [ ] `python tools/check.py` termina con exit 0 y el CI está verde en `main` después del merge.
- [ ] `python tools/reproduce_all.py --quick` termina con exit 0 desde un clon limpio.
- [ ] `docs/sprints/sprint-4-review.md` sin hallazgos altos ni medios; auditoría de seguridad sin hallazgos altos.
- [ ] README, `docs/informe.pdf`, `docs/presentacion.pdf` y `docs/ODD.md` final.
- [ ] Tag `v1.0.0` y GitHub Release, **creados solo con tu confirmación**.
- [ ] Todas las issues de los 4 milestones cerradas o movidas explícitamente a "Trabajo futuro".

## Condición sugerida para `/goal`

```
/goal El Sprint 4 cumple su Definition of Done de docs/sprints/sprint-4.md: (1) ejecutaste `python tools/check.py` y `python tools/reproduce_all.py --quick`, ambos con exit 0, y lo mostraste; (2) docs/sprints/sprint-4-review.md no tiene hallazgos altos o medios abiertos y confirma que cada número del README y del informe coincide con results/; (3) README.md cumple los criterios de S4-04; (4) no creaste PR, tag ni Release sin mi confirmación explícita en esta conversación. O pará después de 30 turnos y reportá qué falta.
```

## Plan de recorte

1. E8 (opcional).
2. El diagrama de Forrester en Vensim o Simlin.
3. Reducir E7 a R = 50.
4. **Lo que no se recorta:** informe, README, reproducibilidad.

## Retro final (completar al cierre)

- Horas totales reales contra las 35–45 estimadas.
- Qué haría distinto. Esto va al informe como "lecciones aprendidas" y suma en la defensa.
