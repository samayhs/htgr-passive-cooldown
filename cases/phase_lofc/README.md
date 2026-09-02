# Phase LOFC — conduction cooldown (block-scale, illustrative)

**Goal:** illustrative peak fuel temperature during a loss-of-forced-cooling **conduction
cooldown** of a single block, and the margin to the 1600 °C TRISO limit. Corresponds to the
benchmark's depressurised/stagnant DCC family. (PCC is **out of block scope** — its
convective / recirculation mechanism is core-scale.)

- **Model:** solid-only. Forced cooling lost, primary depressurised/stagnant → in-channel
  helium thermally inert (dropped); channels adiabatic (`zeroGradient`). No `p_rgh` solve.
  Adiabatic channels trap heat → **conservative** (over-predict the peak, safe direction).
- **Decay heat:** time-dependent `q'''(t) = q'''_op · f_decay(t)`, clock from t=0, **ANS-5.1-family**
  standard decay curve (anchored to published fractions), uniform on the fuel zone. `q'''_op` =
  24.83 MW/m³ (average column) or 46.05 (peak column, ×1.8546).
- **Outer BC:** radiation to the RCCS sink (303 K, ε 0.85; `h=1e-3` numerical floor — the BC
  forms 1/h so h=0 is illegal, radiation dominates ~10⁴:1). Axial ends adiabatic.
- **Initial condition:** the Phase-0 operating steady field.
- **Metrics:** peak fuel(t), time-to-peak, quasi-steady peak, cooldown τ, margin to 1600 °C.
- **Verification:** energy balance `∫q'''_decay = ΔU_stored + ∫Q_out`, with Q_out over the outer
  radiative boundary only (channels + axial ends adiabatic → zero).

**Results (grid-converged fine mesh, peak = t≈0 IC, then monotonic cooldown):**

| Column | Peak fuel (t≈0) | Margin to 1600 °C | Quasi-steady | Energy closure |
|---|---|---|---|---|
| Average | ~793 °C | ~807 °C | ~270 °C | <0.8% (PASS) |
| **Peak** (×1.85) | **1268 °C** | **~332 °C** | ~367 °C | 1.84% (>1%, wide-T) |

**Scope (honest):** steady validated-comparable to GA (MHTGR-350); illustrative block-scale LOFC
cooldown, no tolerance gates. It **cannot** reproduce the benchmark full-core DCC delayed peak
(**1,391 K @ 50 h ≈ 1118 °C**) — a whole-core radial-conduction phenomenon (next-fidelity step).
Note that peak sits *below* the peak-column steady/IC (1268 °C), which brackets it from above.

_Config in [`../../case_template/lofc/`](../../case_template/lofc/); run via `bash run_lofc.sh` (Phase 0 first)._
