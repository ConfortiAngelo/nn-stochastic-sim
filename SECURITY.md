# Security Policy

## Supported versions

Only the latest release on `main` is supported. This is an academic project: there are no
long-term support branches.

## Reporting a vulnerability

Please **do not open a public issue** for security problems.

Use GitHub's private vulnerability reporting instead:
**Security → Advisories → Report a vulnerability** on this repository
(<https://github.com/ConfortiAngelo/nn-stochastic-sim/security/advisories/new>).

Please include what you found, how to reproduce it and the affected file or commit. You can
expect a first answer within 7 days.

## Scope

In scope:

- code in `src/`, `experiments/` and `tools/` (for example unsafe deserialization, `eval`/`exec`,
  shell injection, path traversal when writing results);
- the CI workflows in `.github/workflows/` and the pre-commit hooks;
- pinned dependencies in `requirements*.txt`;
- accidentally committed secrets or personal data.

Out of scope:

- the statistical quality of the intentionally bad generators (middle-square, RANDU): being bad
  is their purpose;
- vulnerabilities in upstream dependencies that are already tracked by Dependabot or pip-audit
  (please report those upstream).

The project only uses **synthetic data** and stores no credentials.
