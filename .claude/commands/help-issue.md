---
description: Muestra el flujo paso a paso para trabajar una issue con /issue
disable-model-invocation: true
---
Mostrame el texto que está entre las líneas `---8<---` tal cual, en markdown, sin resumirlo ni agregarle nada. No corras comandos, no leas archivos y no empieces ninguna tarea.

---8<---
# Flujo de `/issue N`

## 0. Antes de empezar (una vez por sesión)
1. Abrí la sesión en la raíz del repo, parado en la rama del sprint: `git switch sprint/N`.
2. Modelo de la sesión: **Opus**. Los agentes usan Sonnet solos, por su definición.
3. Si es un clon o una carpeta nueva, aceptá el diálogo de confianza del workspace. Sin eso, las reglas `allow` de `settings.json` no aplican.
4. Comprobá que la base esté verde: `python tools/check.py --fast`.

## 1. Lanzar
`/issue N`. Claude lee la issue, CLAUDE.md, los ADRs, `sprint-N.md` y el código que la issue toca.

## 2. Aprobar el diseño
Claude te hace **una** pregunta o te muestra un diseño corto. Vos:
- confirmás que entendió bien la issue;
- revisás las contradicciones que señale entre la issue, el sprint y el código;
- decidís vos si pide un ADR o una dependencia nueva.

## 3. Aprobar el plan (el punto de control más importante)
El plan queda en `docs/sprints/sprint-N-issue-M-plan.md`. Antes de escribir **"aprobado"**, chequeá:
- [ ] Cada criterio Dado/Cuando/Entonces tiene su test `test_<id>_<comportamiento>`.
- [ ] Cada tarea tiene **archivos exclusivos**, y ningún archivo se repite entre tareas de una misma ola.
- [ ] Las tareas que dependen entre sí están en olas distintas.
- [ ] Las tolerancias de los tests estadísticos salen de la teoría (por ejemplo 4·σ/√n).

Si algo no cierra, pedí el cambio. Solo después escribí `aprobado`.

## 4. Ejecución (automática; vos mirás la evidencia)
Por cada ola, Claude:
1. Lanza los `implementer` (máximo 3 en paralelo), cada uno con TDD en su propio worktree.
2. Revisa el `git log` y el `git diff --stat` de cada rama: un commit `test:` antes de cada `feat:` y solo los archivos asignados.
3. Mergea a `sprint/N` con `--no-ff` y corre `python tools/check.py`.

Después corren `reviewer` y `security-auditor`. Con hallazgos altos o medios hay hasta 2 rondas de corrección. Si siguen, te trae un **bloqueo** y decidís vos.
Te pide permiso para `rm`, `pip` y `git push`. `merge`, `commit` y `worktree` corren solos.

## 5. Cierre de la issue
Claude te entrega los merges, la tabla criterio → test → estado, la salida real de `check.py`, los veredictos y los "Ruling". Tu revisión final:
`git log --oneline --graph main..sprint/N`
Tenés que ver las ramas mergeadas con `--no-ff` y los pares `test:` → `feat:`. Si está todo bien: push a `sprint/N`, confirmando el permiso.
La issue **no** se cierra todavía: el merge lleva `Closes #N` y se cierra cuando la PR del sprint llegue a `main`.

## 6. Repetir
Repetí los pasos 1 a 5 por cada issue. Usá una sesión nueva o `/clear` para cada una, así el contexto arranca limpio.

## Cierre del sprint (no lo hace `/issue`; ver `docs/sprints/ORQUESTACION.md`)
1. `reviewer` y `security-auditor` revisan `main...sprint/N`. Resultado: `sprint-N-review.md`, sin hallazgos altos ni medios.
2. `docs-writer` actualiza `ODD.md` y `CHANGELOG.md` y escribe `docs/learning/sprint-N.md`.
3. Claude te muestra el título, el cuerpo y la rama base de la PR `sprint/N → main`. La crea solo si respondés **"sí, creala"**.
4. **Vos** mergeás la PR en GitHub con merge commit. Ahí se cierran las issues.
5. El tag `v0.N.0` se crea solo con tu confirmación.

## ¿`/issue` o plan de sprint?
- **`/issue N`:** para issues sueltas, una por vez y con más puntos de control.
- **Plan de sprint (ORQUESTACION.md):** todas las issues juntas, en olas paralelas entre issues.
- No mezcles los dos en un mismo sprint.
---8<---
