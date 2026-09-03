# HTGR prismatic block: peak fuel temperature during passive cooldown

A project for **Radiant Nuclear**.

## What this is

A 3D conjugate-heat-transfer model of an MHTGR-350 prismatic fuel block that answers one
question: **when forced cooling is lost, how hot does the fuel get, and how much margin is left
to the 1600 °C TRISO limit?**

The model is validated against the OECD/NEA MHTGR-350 benchmark in normal operation, then run
through a single-block loss-of-forced-cooling (LOFC) conduction cooldown. It runs on a custom
temperature-based OpenFOAM solver (`chtMultiRegionTFoam`), written to remove a known Cp bias in
the stock enthalpy-based CHT solver.

It exists to estimate the block-scale passive-cooldown peak (grid-converged,
energy-conservation-verified, and compared to the benchmark operating point) while being
explicit about what a single-block scope can and cannot claim.

## Installation & running

Build the solver, generate the mesh, and run each phase per **[RUNNING.md](RUNNING.md)**.

## Results

The peak-power column gives a steady/initial-condition peak fuel of **1268 °C** (margin **~332 °C**
to the 1600 °C TRISO limit), reproducing the benchmark core-maximum fuel temperature (~1282 °C) to
within ~1 %; the steady coolant outlet is **688 °C** against the benchmark 687 °C (0.2 %). The single
block cools from its initial condition and does not reproduce the whole-core delayed peak, which is a
separate full-core calculation.

The full report — methodology, boundary conditions, inputs, assumptions, verification, and accuracy
assessment — is in **[REPORT.md](REPORT.md)**.

## Repository layout

```
htgr-passive-cooldown/
├── benchmark/       MHTGR-350 reference: distilled data (README) + source PDFs (spec/, refs/)
├── geometry/        block mesh generators (gmsh, Python): make_full_block.py + LOFC tooling
├── solver/          custom temperature-based CHT solver (chtMultiRegionTFoam)
├── case_template/   base OpenFOAM case config (0.orig, system, constant/*) — no run outputs
├── cases/
│   ├── phase0_steady/                  normal-op steady, validated to benchmark
│   ├── phase1_transient_verification/  transient machinery vs analytic τ
│   └── phase_lofc/                     block-scale LOFC conduction cooldown
├── docs/            validation & verification plan
├── presentation/    slide deck (source + PDF)
├── REPORT.md        full prediction report (results, methodology, accuracy)
└── RUNNING.md       how to build the solver, mesh, and run each phase
```
