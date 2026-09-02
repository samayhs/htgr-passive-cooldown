# Validation & Verification Plan

Scope: **block-level** peak fuel temperature during passive cooldown, anchored to the OECD/NEA
MHTGR-350 benchmark. Two kinds of evidence, both required:

- **Verification** — *is the math right?* (no external data needed)
- **Validation** — *is it the right physics?* (agreement with the benchmark reference codes)

All benchmark reference values and their caveats live in [`../benchmark/README.md`](../benchmark/README.md).
The benchmark is **code-to-code, not experimental** — validation here means agreement with
PHISICS/RELAP5-3D, not with measured data.

---

## Operating point (all phases, unless noted)

Helium, **6.39 MPa**, core inlet **259 °C**, block-average power density **5.93 MW/m³**
(applied in the fuel compacts), block length **0.793 m** (or 8 m for the 10-block column).

## Phase 0 — steady state, normal operation

| | |
|---|---|
| **Purpose** | Establish the model is trustworthy where reference data exists, *before* any accident. |
| **Verification** | energy balance closes < 1 %; peak fuel grid-independent (≥ 3 meshes). |
| **Validation metric** | peak fuel `Tfuel_max`; core outlet bulk. |
| **Target** | peak fuel **~1282 °C** (secondary source, treat as a band); outlet **687 °C**. |
| **Acceptance** | outlet within ~3 %; peak fuel within the reference band (tighten once a primary table is read). |

## Phase 1 — transient verification (no accident)

| | |
|---|---|
| **Purpose** | Prove the transient time-integration is correct before trusting the LOFC cooldown. |
| **Verification** | energy conserved over time (∫decay-heat = ΔU_stored + ∫Q_out); Δt independence. |
| **Analytic check** | fitted cooldown τ vs lumped-capacitance τ = ρc·V /(h·A_eff). |
| **Acceptance** | energy imbalance < 1 %; τ within ~10 % of the analytic estimate. |

## Phase LOFC — conduction cooldown (single case, solid-dominated)

The DCC/PCC split is collapsed to **one** block-scale LOFC conduction cooldown. Rationale:
the cooldown peak and the PCC−DCC difference are **full-core** phenomena a single block
can't hold, and the active-fluid closed-channel model is numerically singular anyway
(109 disconnected sealed enclosures, one pressure reference). So model the block-scale
conduction cooldown honestly — **illustrative, not matching**. PCC is out of block scope
(its convective/recirculation mechanism is core-scale).

| | |
|---|---|
| **Model** | solid-only: solid conduction + decay heat + radiative RCCS rejection. In-channel He stagnant → channels adiabatic (conservative: traps heat). Corresponds to the benchmark depressurised/stagnant DCC family. |
| **Initiating event** | forced cooling lost, reactor trip; primary depressurised/stagnant; flow → 0. |
| **Decay heat** | `q'''(t) = q'''_op · f_decay(t)`, clock from t=0, **Way–Wigner interim** (DIN 25485 / ANS-5.1 the intended upgrade), uniform on the fuel zone. |
| **Outer BC** | radiation to RCCS sink (303 K, ε 0.85); axial ends adiabatic. |
| **Metrics** | peak fuel(t), time-to-peak, quasi-steady peak, cooldown τ, margin to 1600 °C. |
| **Reference (full core)** | **1,391 K (≈1,118 °C) @ 50 h** (block model) / 1,237 K @ 74 h (ring model) — **not** reproducible at block scale. |
| **Scope** | block-scale illustrative; **cannot** reproduce the 50–74 h full-core delayed peak (whole-core radial conduction to the RCCS) — named as the next-fidelity step (effective-core radial model). |

---

## Reported figures of merit (the LOFC phase)

1. Peak fuel temperature — max over space **and** time
2. Time-to-peak
3. Quasi-steady / asymptotic peak and cooldown τ
4. Peak location (r, z)
5. Margin to 1600 °C (TRISO/SiC limit)
6. Energy-balance closure (verification)

## Scope statement (locked)

Steady state validated-comparable to GA (MHTGR-350). One block-scale LOFC conduction cooldown
(solid conduction + decay heat + radiative RCCS rejection), reported as illustrative — peak
fuel **~793 °C** (average column, grid-converged), margin **~807 °C** to 1600 °C. It cannot
reproduce the benchmark full-core DCC peak (1,391 K @ 50 h); that delayed peak is a whole-core
radial-conduction phenomenon and is named as the next-fidelity step (effective-core radial
model). PCC is out of block scope — its convective/recirculation mechanism is core-scale.

## Status

Phase 0 (steady) **complete, grid-converged** (4 meshes, GCI ~1%; outlet 688 °C vs 687 °C).
Phase 1 (verification) **complete** — energy conservation <0.8%, Δt-independent. LOFC case
**complete** (illustrative): peak fuel ~793 °C, margin ~807 °C. Full write-up:
[`peak_fuel_prediction.md`](peak_fuel_prediction.md).

## Open items

- **Peak-column run** (×1.85 power → ~46 MW/m³ fuel-local) to target the ~1282 °C core max —
  results to date are the *average* column.
- **Full-core / effective-core radial model** — the governing safety peak (1391 K @ 50 h) is a
  whole-core phenomenon the block cannot reach; the next-fidelity step.
- κ(T) upgrade: irradiated EOEC block-avg fluence (Table AIV.2 + Appendix VIII) — currently
  un-irradiated fallback (biases the peak low); needs the fluence file, not in the repo.
- Decay-heat upgrade: DIN 25485 / ANS-5.1 fit to replace the Way–Wigner interim.
- Pin `Tfuel_max` (~1282 °C) to a primary results table for the Phase-0 comparability band.
