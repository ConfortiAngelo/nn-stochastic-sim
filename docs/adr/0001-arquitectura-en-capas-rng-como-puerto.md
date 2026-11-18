# ADR-0001: Arquitectura en capas con el RNG como puerto

- **Estado:** aceptado
- **Fecha:** 2026-11-18
- **Sprint / issue:** Sprint 0 (S0-04, S0-09)

## Contexto

El proyecto estudia el entrenamiento de una red neuronal como un **experimento estocástico**
(Cap. 1). Para que las conclusiones valgan, hacen falta tres cosas:

1. **Controlar todo el azar.** Los experimentos E1 y E7 cambian el generador (LCG, cuadrados
   medios, RANDU, NumPy) y miden su efecto. Si alguna parte del código usara `np.random` por su
   cuenta, el experimento quedaría contaminado.
2. **Reproducibilidad bit a bit** y **números aleatorios comunes** entre configuraciones
   (CLAUDE.md §4.8).
3. **Testear el núcleo sin I/O** (TDD, V&V), con funciones puras que reciben θ y datos.

Se evaluaron dos estilos:

- **Hexagonal completa** (puertos y adaptadores para todo: RNG, almacenamiento, gráficos,
  reloj, logging). Es muy flexible, pero para un proyecto de 4 sprints con una sola fuente
  externa relevante (el azar) agrega interfaces que nadie va a implementar dos veces.
- **Núcleo funcional con una capa externa de I/O.** El núcleo (`src/nnsim`) es puro: recibe
  parámetros y devuelve resultados. Solo `experiments/` y `tools/` escriben CSV y PNG. El único
  puerto formal es el RNG, porque es lo único que **sí** tiene varias implementaciones.

## Decisión

Núcleo funcional con una capa externa de I/O, y el RNG como **puerto**:

```
experiments/  →  runner  →  trainers  →  nn
     │                         │
     └── I/O (CSV, PNG)        └──→ RNG (puerto) ← generators/* (adaptadores)
                                    distributions, datasets, sampling → RNG
```

- `nnsim.generators.base.RNG` es un `typing.Protocol` con `@runtime_checkable`:
  `seed(s)`, `next_int()` y `uniform(n)` (valores en el intervalo **abierto** (0, 1)).
- Cada generador (`lcg`, `middle_square`, `randu`, `numpy_ref`) es un adaptador que cumple el
  Protocol de forma estructural, sin herencia.
- `distributions`, `datasets`, `sampling` y los entrenadores reciben un `RNG` por parámetro.
  Nunca crean uno propio.
- `nnsim.nn` no conoce el azar: recibe θ ya inicializado.

Se hace cumplir de forma automática (`python tools/check.py`):

| Regla | Mecanismo |
|---|---|
| `nn` no importa generadores, distribuciones, datos, entrenadores, runner, métricas, stats ni config | import-linter, contrato "nn es independiente" |
| `generators` no importa el resto de `nnsim` | import-linter + `tests/test_architecture.py` |
| `nnsim` no importa `matplotlib` | import-linter, contrato "el núcleo no hace I/O gráfico" |
| `runner` (y todo `src/`) no importa `experiments` | import-linter + `tests/test_architecture.py` |
| `np.random` solo en `generators/numpy_ref.py` | `tests/test_architecture.py` (AST) |
| Sin `print`, `eval`, `exec`, `pickle`, ni PyTorch/TF/JAX/sklearn/Keras en `src/` | `tests/test_architecture.py` (AST) |
| SciPy solo en `stats.py` y `generators/quality.py` | `tests/test_architecture.py` (la justificación formal llega en ADR-003, S2-09) |

## Consecuencias

- **Positivas.** Cambiar de generador es cambiar un argumento. Los tests del núcleo no tocan
  disco. Las violaciones de capa rompen el CI en vez de depender de la revisión manual.
- **Negativas.** Hay que pasar el `RNG` explícitamente por varias funciones (más parámetros).
  Los gráficos y CSV quedan fuera de la cobertura de `src/`. Su lógica reutilizable tiene que
  vivir en `src/` para poder testearla.
- **Revisar si** aparece una segunda fuente externa con varias implementaciones (por ejemplo,
  distintos formatos de almacenamiento): ahí se justificaría otro puerto.

## Notas

### Sin instalación editable; `pythonpath = src`

No se usa `pip install -e .`. Los implementadores trabajan en **worktrees** aislados, y un
editable apuntaría siempre al checkout principal: los tests de cada worktree probarían el
código equivocado sin dar ningún error. En su lugar:

- pytest: `pythonpath = ["src"]` en `pyproject.toml`;
- mypy: `mypy_path = "src"`;
- import-linter: `tools/check.py` exporta `PYTHONPATH=src` (import-linter no tiene una opción
  de configuración para esto, así que `lint-imports` suelto falla con *Could not find package
  'nnsim'*; hay que correrlo a través de `check.py` o con `PYTHONPATH=src lint-imports`);
- experimentos: `experiments/_path.py` antepone `src/` a `sys.path`, y cada script empieza con
  `import _path  # noqa: F401`.

### Layout `src/nnsim/` en lugar del de la sección 5 del plan

La sección 5 de `docs/Proyecto_Simulacion_IA_detalle.pdf` pone los módulos directamente en
`src/`. Se usa `src/nnsim/` porque:

- un paquete con nombre permite imports absolutos (`from nnsim.generators.base import RNG`) y
  contratos de import-linter, que necesitan un `root_package`;
- evita choques de nombres con la biblioteca estándar o con terceros (`stats`, `datasets`...);
- el archivo de pruebas de calidad del generador se llama `generators/quality.py` y no
  `generators/tests.py`, para que pytest no lo confunda con un módulo de tests.

Además se agregan módulos que el plan describe pero no ubica: `sampling.py`, `stats.py`,
`config.py`, `dynamics.py`, `fitting.py`, `poisoning.py`, `trainers/gd.py` y
`trainers/callbacks.py`.
