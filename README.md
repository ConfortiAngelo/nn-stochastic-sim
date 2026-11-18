# nn-stochastic-sim

[![CI](https://github.com/ConfortiAngelo/nn-stochastic-sim/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ConfortiAngelo/nn-stochastic-sim/actions/workflows/ci.yml)

> Training a neural network is a stochastic experiment: a from-scratch MLP studied with
> simulation tools (PRNGs, Monte Carlo, random walks, Metropolis, Euler).

**Status: work in progress.** This is the final project for a university course on Simulation
(Information Systems Engineering). Results, figures and conclusions will be added sprint by sprint.

## What this is

A small multilayer perceptron written from scratch with NumPy, where **every source of randomness**
(weight initialization, data generation, shuffling, annealing proposals) goes through
pseudo-random generators implemented and validated in the project itself. Training is then
treated as a simulation experiment: replications, confidence intervals, random walks in weight
space, Metropolis acceptance and Euler integration.

## Repository layout

```
src/nnsim/          # pure, side-effect-free core (no plotting, no disk I/O)
  generators/       # RNG port (Protocol) + adapters: LCG, middle-square, RANDU, NumPy reference
  distributions.py  # inverse transform, Box-Muller, empirical, Xavier, He
  datasets.py       # blobs, XOR, spirals; train/test split
  nn.py             # MLP: forward, backward, loss, flat θ, gradient check
  trainers/         # GD, SGD (Fisher-Yates), simulated annealing, callbacks
  metrics.py stats.py runner.py dynamics.py fitting.py poisoning.py
experiments/        # E1..E8: the only layer that writes CSV and PNG
results/ figures/   # versioned outputs (CSV / PNG)
tests/              # pytest + Hypothesis, verification & validation tests
tools/check.py      # the single definition of "green"
docs/               # ADRs, ODD model description, sprint plans, report
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -r requirements-dev.txt
pre-commit install --hook-type pre-commit --hook-type commit-msg
python tools/check.py --fast
```

The package is **not** installed in editable mode: pytest and mypy read it from `src/`
(see `docs/adr/0001-arquitectura-en-capas-rng-como-puerto.md`).

## License

[MIT](LICENSE)
