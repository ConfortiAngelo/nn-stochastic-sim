# Guía de orquestación por sprint (Opus planifica, Sonnet trabaja)

Esta guía tiene los **prompts listos para copiar** de cada fase. Se usa igual en los sprints 1 a 4: solo cambiás `N`.

## Antes de empezar (una sola vez)

1. Abrí Claude Code en la raíz del repo con el entorno virtual activado.
2. En `/config`, activá **Dynamic workflows** (en el plan Pro vienen apagados). El tamaño por defecto en Pro es `small` (menos de 5 agentes). Dejalo así: alcanza para este proyecto y cuida tu límite de uso.
3. Verificá que estén los agentes con `/agents`: `implementer`, `reviewer`, `security-auditor` y `docs-writer`.

## Al empezar cada sesión

```bash
# Linux/macOS: source .venv/bin/activate   |   Windows: .venv\Scripts\activate
claude --model opus --effort high
```

Dentro de la sesión, `/model` y `/effort` confirman el modelo y el esfuerzo. El orquestador es Opus. Los trabajadores son Sonnet, porque así está definido en `.claude/agents/*.md` (`model: sonnet`, `effort: high`).

## Regla de oro de las ramas

- `main`: protegida. Solo recibe PRs que **vos** confirmás y mergeás.
- `sprint/N`: rama de integración del sprint. Solo el orquestador mergea acá.
- Ramas de trabajadores: cada `implementer` trabaja en un **worktree aislado**. Ese worktree nace de `main`, no de `sprint/N`, así que lo primero que hace el agente es `git merge --ff-only sprint/N`. Está en su definición.

---

## Fase 1 — Entender y planificar (Opus, modo plan)

Pasá a modo plan con `Shift+Tab` hasta ver *plan mode* y pegá esto:

```text
Sos el ORQUESTADOR de este proyecto (ver CLAUDE.md, sección "Roles").
Vamos a trabajar el Sprint N. No escribas código en esta fase.

1. Leé completo docs/sprints/sprint-N.md, CLAUDE.md, docs/ODD.md, docs/adr/ y
   docs/Proyecto_Simulacion_IA_detalle.pdf (secciones que apliquen al sprint).
2. Mirá el estado real: `git log --oneline -20`, `git status`, la estructura de src/ y tests/,
   y las issues abiertas con `gh issue list --milestone "Sprint N"`.
3. Devolveme un plan con:
   a) qué entendiste del objetivo del sprint, en 3 líneas;
   b) puntos críticos y riesgos (técnicos y de la teoría de la materia), con mitigación;
   c) grafo de dependencias entre las tareas;
   d) olas de ejecución: por ola, cuántos agentes (máximo 3 en paralelo por el plan Pro),
      qué agente (implementer, docs-writer...), qué issue y qué ARCHIVOS EXCLUSIVOS tiene cada uno;
   e) por tarea: el prompt exacto que va a recibir el trabajador, los criterios Dado/Cuando/Entonces
      que tiene que cubrir con tests, y el comando que prueba que terminó;
   f) qué hacés vos entre olas (merge a sprint/N, `python tools/check.py`, revisión);
   g) la condición /goal final (partí de la sugerida en el sprint y ajustala si hace falta);
   h) preguntas para mí sobre todo lo ambiguo. No asumas: preguntá.
```

Cuando apruebes el plan:

```text
Aprobado. Creá la rama sprint/N desde main (si no existe), guardá el plan en
docs/sprints/sprint-N-plan.md y commitealo con "docs(sprint-N): plan del sprint".
```

## Fase 2 — Ejecutar con un workflow por ola (Sonnet trabaja)

Un workflow no admite que intervengas a mitad de la corrida. Por eso conviene **un workflow por ola**: entre ola y ola, Opus integra y verifica.

```text
use a workflow para ejecutar la Ola K de docs/sprints/sprint-N-plan.md.
- Cada tarea la hace un agente del tipo `implementer` (Sonnet, effort high, worktree aislado),
  con el prompt exacto del plan. Pasale el nombre de la rama de integración: sprint/N.
- Cada agente sigue TDD Red-Green-Refactor (CLAUDE.md) y toca SOLO sus archivos exclusivos.
- Cada agente devuelve, en JSON: issue, rama del worktree, commits (hash + mensaje),
  tests agregados, criterios cubiertos, salida resumida de `python tools/check.py`, bloqueos.
- No hacen push, no crean PRs, no tocan main.
Cuando termine el workflow, integrá vos: mergeá cada rama a sprint/N con `--no-ff`, resolvé
conflictos si los hay, corré `python tools/check.py` y mostrame la salida. Si algo falla,
no avances: explicá la causa y proponé la corrección.
```

Repetís con la Ola K+1 hasta terminar. Para ver el progreso y el consumo usá `/workflows`. Desde ahí podés frenar cualquier agente con `x`.

## Fase 3 — Revisar y forzar el cierre (`/goal`)

**Paso 3.1: revisión independiente.** La hace un agente con contexto fresco, para que no se corrija a sí mismo el que escribió el código.

```text
Revisión del Sprint N. En paralelo:
- `reviewer` sobre `git diff main...sprint/N` contra la checklist de CLAUDE.md y contra la teoría
  de la materia (fórmulas de la sección 8 del plan);
- `security-auditor` sobre el mismo diff.
Después corré `python tools/check.py` y escribí docs/sprints/sprint-N-review.md con:
mapa criterio → test(s) → estado, hallazgos con severidad (alta/media/baja), archivo y línea,
y la corrección propuesta. Commitealo en sprint/N.
```

**Paso 3.2: bucle hasta que esté bien.** Pegá la condición `/goal` del sprint, la que figura en `sprint-N.md` o la que ajustó Opus en el plan:

```text
/goal <condición del sprint>
```

`/goal` hace que Claude siga trabajando: corrige hallazgos (delegando en `implementer` si son de código), vuelve a correr las verificaciones y actualiza el review. Después de cada turno, un modelo evaluador independiente decide si la condición se cumple. Si no se cumple, Claude sigue. Con `/goal` sin argumentos ves los turnos y los tokens gastados. Con `/goal clear` lo cortás.

> `/loop` y `/goal` los escribís **vos**: Claude no puede invocarlos solo. `/loop` repite un prompt **cada cierto tiempo**, así que no sirve para revisar, pero viene muy bien para vigilar el CI (fase 4). Para el ciclo "revisar → si está mal, rehacer → hasta que esté bien" la herramienta es `/goal`.

## Fase 4 — PR, CI y cierre

```text
Prepará la PR sprint/N → main: título en Conventional Commits, cuerpo con resumen, issues que
cierra (Closes #...), evidencia (salida de tools/check.py, figuras nuevas) y checklist de DoD.
Mostrámela y NO la crees hasta que te diga "sí, creala".
```

Después de tu "sí, creala", vigilá el CI:

```text
/loop 5m revisá `gh pr checks <número>`. Si algún check falló, leé el log con `gh run view --log-failed`, corregí en sprint/N con TDD y hacé push a sprint/N (pedime permiso). Si están todos verdes, avisame y pará el loop.
```

El merge lo hacés vos desde GitHub. Después:

```text
Sincronizá main local, cerrá el milestone "Sprint N" si no quedan issues, actualizá CHANGELOG,
proponé el tag v0.N.0 (esperá mi confirmación para crearlo y pushearlo) y completá la retro de
docs/sprints/sprint-N.md. Si la retro deja una lección, proponé el cambio a CLAUDE.md.
```

Terminá con `/clear` antes del sprint siguiente: el contexto queda en los archivos, no en la conversación.

---

## Cuidar el límite del plan Pro

- Opus solo planifica, integra y revisa. El trabajo pesado va a Sonnet.
- Máximo 3 agentes en paralelo y olas cortas.
- `/usage` muestra el consumo por subagentes y skills. Si te acercás al límite, cortá después de integrar una ola: todo queda en git y en el plan.
- Si una corrida de workflow choca con el límite de uso, se pausa y sigue sola cuando el límite se reinicia (en sesión interactiva).
- Las tareas mecánicas (formatear, correr tests) son scripts (`tools/check.py`), no razonamiento del modelo.
