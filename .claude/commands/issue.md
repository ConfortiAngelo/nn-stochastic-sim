Trabajá la issue #$ARGUMENTS de este repositorio como **orquestador** (CLAUDE.md §2). No se escribe código de producción hasta que yo apruebe el plan. Si algo de este comando choca con CLAUDE.md, manda CLAUDE.md: pará y preguntame.

## FASE 1 — Entender y planificar (vos, Opus)

1. Leé la issue con sus comentarios: `gh issue view $ARGUMENTS --comments`. Del milestone sacá el sprint N; la rama de integración es `sprint/N`.
2. Leé, en este orden, solo lo necesario: CLAUDE.md, los ADRs de `docs/adr/` que apliquen, `docs/sprints/sprint-N.md` (criterios y DoD) y el código que la issue toca, hasta poder explicar cómo funciona hoy y qué va a cambiar.
3. Usá superpowers:brainstorming. Si la issue ya trae criterios claros, no me hagas preguntas de más: una sola pregunta, sobre lo que más cambiaría el resultado, o directamente el diseño corto para aprobar. Señalá cualquier contradicción entre la issue, el sprint, los ADRs y el código.
4. Cuando apruebe el diseño, usá superpowers:writing-plans y guardá el plan en `docs/sprints/sprint-N-issue-$ARGUMENTS-plan.md`. Además de lo que pide la skill, el plan incluye:
   - Los criterios de aceptación en formato **Dado / Cuando / Entonces** (BDD liviano, sin Gherkin, CLAUDE.md §4.2) y, para cada uno, el test que lo prueba con nombre `test_<id>_<comportamiento>`.
   - Por cada tarea: el agente (`implementer` para `src/`, `tests/` y `experiments/`; `docs-writer` para docs), sus **archivos exclusivos**, el test que falla primero (red), la implementación mínima (green), el refactor, los commits y el comando de verificación.
   - Olas: tareas con archivos disjuntos pueden ir en la misma ola (máximo 3 agentes en paralelo); si una depende de otra, va en una ola posterior, porque el worktree del agente solo ve lo que ya está mergeado en `sprint/N`.
   - Riesgos y si hace falta un ADR (romper una regla de §3 o agregar una dependencia lo exige: en ese caso, frená y pedí aprobación).
5. Mostrame un resumen del plan (olas, tareas, criterio → test, riesgos) y DETENETE. No sigas hasta que escriba "aprobado".

## FASE 2 — Ejecutar (después de "aprobado")

6. Ubicate en `sprint/N` (`git switch sprint/N`). Si no existe, preguntame antes de crearla desde `main`. Commiteá el plan ahí (`docs(plan): ...`, en inglés, `Refs #$ARGUMENTS`).
7. Por cada ola, lanzá los agentes del proyecto con la herramienta Agent (`subagent_type: implementer` o `docs-writer`). **No uses** superpowers:subagent-driven-development, superpowers:using-git-worktrees ni agentes `general-purpose`: los agentes del proyecto ya traen modelo, worktree aislado y restricciones. Cada prompt incluye: ID de la issue, rama de integración `sprint/N`, archivos exclusivos, criterios Dado/Cuando/Entonces, test esperado por criterio y comando de verificación.
8. Al volver cada agente, verificá su JSON contra la evidencia real, no contra lo que dice:
   - `git log --oneline sprint/N..<rama>`: hay un commit `test:` antes de cada `feat:`/`fix:`, y no hay atribución a IA.
   - `git diff --stat sprint/N...<rama>`: solo tocó sus archivos exclusivos (nada en `.claude/`, `CLAUDE.md` ni `requirements*.txt`).
   - Si reporta `blockers`, frená la ola y mostrámelos.
9. Integrá: `git merge --no-ff <rama>` en `sprint/N`, con mensaje en inglés y `Refs #$ARGUMENTS` (en el merge de la última tarea, `Closes #$ARGUMENTS`, que cierra la issue cuando la PR del sprint llegue a `main`). Después de **cada** ola: `python tools/check.py`. Si falla, investigá la causa raíz (CLAUDE.md §5); podés corregir vos solo errores de integración de menos de 10 líneas, el resto vuelve al agente.
10. Revisión independiente, con contexto fresco, sobre `git diff <commit previo a la issue>..sprint/N`:
    - `reviewer` (siempre) y `security-auditor` (si se tocó `src/`, dependencias, CI o `tools/`). Podés lanzarlos en paralelo.
    - Si hay hallazgos **altos o medios**, relanzá el `implementer` con los hallazgos concretos (archivo:línea y corrección) y volvé al paso 8.
    - Máximo **2 rondas** de corrección por tarea. Si a la segunda sigue sin pasar, pará y reportalo como bloqueo, con lo que se intentó.
11. Antes de dar algo por terminado, usá superpowers:verification-before-completion: corré `python tools/check.py` (sin `--fast`) y, si la issue agregó tests `slow`, `python -m pytest -m slow`. Mostrame la salida real, no un resumen.

## FASE 3 — Cerrar

12. No abras ninguna PR: la PR es una por sprint (`sprint/N → main`) y la arma el cierre del sprint. No uses superpowers:finishing-a-development-branch.
13. Push solo a `sprint/N`, solo con `tools/check.py` en verde y solo si te lo confirmo en esta conversación. Nunca push a `main`, ni force, ni `--no-verify`, ni merge de PRs.
14. Borrá los worktrees y ramas locales de los agentes ya mergeados (`git worktree remove`, `git branch -d`), sin tocar ramas remotas.

Al terminar, dame:
- Los commits de merge en `sprint/N` (hash y mensaje).
- La tabla: criterio (Dado/Cuando/Entonces) → test → estado.
- La salida final de `python tools/check.py`.
- Los veredictos de `reviewer` y `security-auditor`, y qué hallazgos quedaron (bajos) sin corregir.
- Las decisiones que tomaste por tu cuenta (los "Ruling") y lo que quedó afuera del alcance.
