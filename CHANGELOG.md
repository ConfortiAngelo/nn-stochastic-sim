# Changelog

Todos los cambios notables del proyecto se documentan en este archivo.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el proyecto usa
[Versionado Semántico](https://semver.org/lang/es/).

## [Unreleased]

## [0.0.1] - 2026-11-18

### Added

- Estructura del repositorio con layout `src/nnsim/` y módulos vacíos, cada uno con la issue
  que lo implementa.
- Puerto `RNG` (`typing.Protocol`, `@runtime_checkable`) en `nnsim.generators.base`.
- Puertas de calidad en `tools/check.py`: ruff, mypy estricto, import-linter, pytest con
  cobertura ≥ 85 %, bandit y pip-audit.
- Contratos de arquitectura (import-linter) y `tests/test_architecture.py` (AST).
- Hooks de pre-commit: higiene de archivos, ruff y Conventional Commits.
- CI de GitHub Actions, Dependabot y plantillas de issues y PR.
- Configuración de Claude Code (`.claude/settings.json`) y agentes `implementer`, `reviewer`,
  `security-auditor` y `docs-writer`.
- ADR-0001 (arquitectura en capas con el RNG como puerto), `docs/ODD.md` v0, `SECURITY.md` y
  licencia MIT.

[Unreleased]: https://github.com/ConfortiAngelo/nn-stochastic-sim/compare/v0.0.1...HEAD
[0.0.1]: https://github.com/ConfortiAngelo/nn-stochastic-sim/releases/tag/v0.0.1
