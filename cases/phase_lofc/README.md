# Phase LOFC — conduction cooldown (block-scale, illustrative)

**Goal:** illustrative peak fuel temperature during a loss-of-forced-cooling **conduction
cooldown** of a single block, and the margin to the 1600 °C TRISO limit. Corresponds to the
benchmark's depressurised/stagnant DCC family. (PCC is **out of block scope** — its
convective / recirculation mechanism is core-scale.)

- **Model:** solid-only. Forced cooling lost, primary depressurised/stagnant → in-channel
  helium thermally inert (dropped); channels adiabatic (`zeroGradient`). No `p_rgh` solve.
  Adiabatic channels trap heat → **conservative** (over-predict the peak, safe direction).
- **Decay heat:** time-dependent `q'''(t) = q'''_op · f_decay(t)`, clock from t=0, **Way–Wigner
  interim** (DIN 25485 / ANS-5.1 the intended upgrade), uniform on the fuel zone. `q'''_op` =
  24.83 MW/m³ (average column) or 46.05 (peak column, ×1.8546).
- **Outer BC:** radiation to the RCCS sink (303 K, ε 0.85; `h=1e-3` numerical floor — the BC
  forms 1/h so h=0 is illegal, radiation dominates ~10⁴:1). Axial ends adiabatic.
- **Initial condition:** the Phase-0 operating steady field.
- **Metrics:** peak fuel(t), time-to-peak, quasi-steady peak, cooldown τ, margin to 1600 °C.
- **Verification:** energy balance `∫q'''_decay = ΔU_stored + ∫Q_out`, with Q_out over the outer
  radiative boundary only (channels + axial ends adiabatic → zero).

**Scope (honest):** steady state validated-comparable to GA (MHTGR-350). One block-scale LOFC
conduction cooldown (solid conduction + decay heat + radiative RCCS rejection), reported as
**illustrative** — peak fuel X °C, margin to 1600 °C, no tolerance gates. It **cannot** reproduce
the benchmark full-core DCC peak (**1,391 K @ 50 h**); that delayed peak is a whole-core radial-
conduction phenomenon, named as the next-fidelity step (effective-core radial model).

_Config in [`../../case_template/lofc/`](../../case_template/lofc/); run via `bash run_lofc.sh` (Phase 0 first)._
