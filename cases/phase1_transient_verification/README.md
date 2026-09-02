# Phase 1 — transient verification (no accident)

**Goal:** prove the transient time-integration is correct before trusting the LOFC conduction
cooldown — a pure verification step, no external reference needed.

- **Check 1 — energy conservation over time:** ∫ decay-heat dV dt = ΔU_stored + ∫ Q_out dt.
- **Check 2 — analytic τ:** fitted cooldown time constant vs lumped-capacitance
  τ = ρc·V / (h·A_eff).
- **Check 3 — Δt independence:** peak and τ stable under time-step refinement.
- **Acceptance:** energy imbalance < 1 %; τ within ~10 % of the analytic estimate.

**Results** (via an in-solver energy monitor — `ENERGYMON` line each step: ∫ρh dV, ∫Q dV,
∫−κ∇T·n over outerWall):

| Check | Result | Verdict |
|---|---|---|
| Energy conservation `ΔU = ∫P_decay − ∫Q_out` | **0.08%** (Δt_max 100 s), **0.24%** (Δt_max 50 s), **0.80%** on the 9.15 M grid-converged mesh | PASS (<1%) |
| Δt independence | peak fuel identical at both Δt; ΔU matches to 0.05% | PASS |
| Cooldown τ vs analytic lumped-capacitance | CFD ~121 min vs analytic 128 min (~5%) | pass (sanity) |

Verifies the transient integrator the LOFC case rides on; the closure transfers across meshes.
Full write-up: [`../../docs/peak_fuel_prediction.md`](../../docs/peak_fuel_prediction.md).

_Status: complete — PASS._
