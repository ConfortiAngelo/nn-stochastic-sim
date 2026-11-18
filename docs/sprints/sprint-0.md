# Sprint 0 — Arranque: estructura, calidad automática y GitHub

| Campo | Valor |
|---|---|
| Fechas | mié 18 nov → jue 19 nov 2026 |
| Horas estimadas | 2 a 3 h (sale del margen del cronograma) |
| Versión al cerrar | `v0.0.1` |
| Cómo se ejecuta | Con `PROMPT_ARRANQUE_CLAUDE_CODE.md` (no sigue las fases de ORQUESTACION.md) |

## Objetivo del sprint

> El repo existe en GitHub con la arquitectura del plan, los controles de calidad y seguridad automáticos (pre-commit + CI), las reglas de Claude Code y el backlog de los sprints 1 a 4 cargado como issues, milestones y un Project. Todavía no tiene código de dominio.

## Backlog

| ID | Título |
|---|---|
| S0-01 | Verificar requisitos: git, gh autenticado (con scope `project`), Python ≥ 3.11 e identidad de git |
| S0-02 | Estructura de carpetas `src/nnsim/...`, `tests/`, `experiments/`, `results/`, `figures/`, `docs/`, `tools/` |
| S0-03 | `pyproject.toml` (ruff, mypy, pytest, coverage, import-linter), `requirements*.txt` con versiones fijas |
| S0-04 | Interfaz `RNG` (solo el Protocol) y un test de humo; contratos de arquitectura que pasan |
| S0-05 | `tools/check.py`, pre-commit con commit-msg (Conventional Commits) |
| S0-06 | `.claude/settings.json` (permisos, atribución vacía) y `.claude/agents/*.md` |
| S0-07 | CI de GitHub Actions, CodeQL, Dependabot, plantillas de issue y PR, SECURITY.md, LICENSE |
| S0-08 | Repo en GitHub, protección de `main`, labels, milestones, issues de los sprints 1 a 4, Project |
| S0-09 | ADR-001 (arquitectura en capas con el RNG como puerto) y `docs/ODD.md` v0 |

## Definition of Done

- [ ] `python tools/check.py` termina con exit 0 en local.
- [ ] El primer run de CI en GitHub está verde.
- [ ] `main` protegida: requiere PR y CI verde, sin force-push.
- [ ] Issues S1-xx a S4-xx creadas con su milestone y en el Project.
