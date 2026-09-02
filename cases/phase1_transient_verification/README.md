# Phase 1 — transient verification (no accident)

**Goal:** prove the transient time-integration is correct before trusting the LOFC conduction
cooldown — a pure verification step, no external reference needed.

- **Check 1 — energy conservation over time:** ∫ decay-heat dV dt = ΔU_stored + ∫ Q_out dt.
- **Check 2 — analytic τ:** fitted cooldown time constant vs lumped-capacitance
  τ = ρc·V / (h·A_eff).
- **Check 3 — Δt independence:** peak and τ stable under time-step refinement.
- **Acceptance:** energy imbalance < 1 %; τ within ~10 % of the analytic estimate.

_Status: stub — to be built out._
