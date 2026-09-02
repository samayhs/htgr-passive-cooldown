# HTGR prismatic block — peak fuel temperature during passive cooldown

**Question this repo answers:** *for an HTGR prismatic fuel block, what is the peak fuel
temperature during a passive (loss-of-forced-cooling) cooldown, and what is the margin to the
1600 °C TRISO limit?*

Answered with a 3D conjugate heat-transfer model of an MHTGR-350 fuel block, **validated in
normal operation against the OECD/NEA MHTGR-350 benchmark**, then applied to a single
block-scale **LOFC conduction cooldown**:

- **LOFC** — loss-of-forced-cooling conduction cooldown, solid-dominated (forced cooling lost,
  primary depressurised/stagnant → in-channel helium inert, heat leaves by conduction +
  radiation to the RCCS). Corresponds to the benchmark's depressurised/stagnant **DCC** family.
- **PCC** (pressurised) is **out of block scope** — its convective/recirculation mechanism is
  core-scale, and the active-fluid closed-channel model is numerically singular at block scale
  (109 disconnected sealed enclosures). See [`docs/validation_plan.md`](docs/validation_plan.md).

## Scope — block level (stated honestly up front)

This models a **single fuel block / single coolant-channel column**, not the full annular
core. Consequence, stated plainly so results are never over-claimed:

- The **benchmark DCC/PCC peak is a full-core phenomenon** — it forms 50–74 hours in, deep in
  the core, governed by radial conduction across ~660 blocks to the reactor-cavity cooling
  system. A single block with adiabatic lateral walls **cannot** reproduce that delayed peak.
- What this model **does** deliver: (a) a **steady-state** result validated to the benchmark
  block reference, and (b) a **block-scale conduction cooldown** — a verified, cross-checked,
  correctly-scoped accident calculation. The full-core DCC is named as the next fidelity step,
  with the benchmark's numbers ([`benchmark/README.md`](benchmark/README.md)) as its target.

## Validation targets (from the MHTGR-350 benchmark)

| Phase | Case | Metric | Reference target | Source confidence |
|---|---|---|---|---|
| 0 | steady, normal op | peak fuel; coolant in/out | **~1282 °C**; 259 / 687 °C | 1282 secondary; in/out from spec |
| 1 | transient verification | cooldown τ; energy conservation | analytic lumped-capacitance τ | self (analytic) |
| LOFC | conduction cooldown (illustrative) | peak fuel(t), time-to-peak, margin | block-scale — **cannot** reproduce the full-core DCC peak **1,391 K @ 50 h** | benchmark (code-to-code) |

> The MHTGR-350 benchmark is a **code-to-code** comparison — **not experimentally validated**.
> "Validated to benchmark" means agreement with the reference codes (PHISICS/RELAP5-3D), not
> with measured reality. See [`benchmark/README.md`](benchmark/README.md).

## Repository layout

```
htgr-passive-cooldown/
├── benchmark/       MHTGR-350 reference: distilled data (README) + source PDFs (spec/, refs/)
├── geometry/        block mesh generators (gmsh, Python) — make_full_block.py + LOFC tooling
├── solver/          custom temperature-based CHT solver (chtMultiRegionTFoam)
├── case_template/   base OpenFOAM case config (0.orig, system, constant/*) — no run outputs
├── cases/
│   ├── phase0_steady/                  normal-op steady, validated to benchmark
│   ├── phase1_transient_verification/  transient machinery vs analytic τ
│   └── phase_lofc/                     block-scale LOFC conduction cooldown (illustrative)
├── docs/            validation plan + metric acceptance criteria
└── RUNNING.md       how to build the solver, mesh, and run each phase
```

## Status

Scaffold. Reusable assets (benchmark reference, block geometry generator, T-solver, case
config) are ported from the parent `prismatic-microreactor-thermal` project; the four phase
cases are stubs to be built out per [`docs/validation_plan.md`](docs/validation_plan.md).

## Provenance

The solver (`chtMultiRegionTFoam`), the benchmark block geometry, and the LOFC tooling are
carried over from `prismatic-microreactor-thermal` (where the solver bug that motivated the
temperature-based formulation was found and fixed). This repo re-scopes that work to the single
question above and anchors it to the MHTGR-350 benchmark operating point.
