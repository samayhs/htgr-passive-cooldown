# Phase 0 — steady state, normal operation

**Goal:** validate the model against the MHTGR-350 benchmark *before* any accident, so the
passive-cooldown results ride on a trusted baseline.

- **Conditions:** He 6.39 MPa, inlet 259 °C, block-average 5.93 MW/m³ (avg column), forced convection.
- **Validation target:** core outlet **687 °C**; peak-fuel band **~1282 °C** (the core *max*, a peak-column quantity).
- **Verification:** energy balance; peak fuel grid-independent (≥ 3 meshes).

**Results (8 m column, grid-converged):**

| Metric | Result | Benchmark |
|---|---|---|
| Coolant outlet (area-avg) | **688 °C** | 687 °C — **0.2%**, comparable |
| Peak fuel (average column) | **~793 °C** (Richardson ~799 °C) | — (avg column, not the core max) |
| Peak fuel (**peak column**, ×1.85 power) | **1268 °C** | ~1282 °C — **within ~1%** |
| Grid independence | 4 meshes (1.14–9.15 M), **GCI ~0.95%**, near-2nd-order | — |

Built from [`../../case_template/`](../../case_template/). Produces the **operating steady field**
used as the IC for the LOFC cooldown ([`phase_lofc`](../phase_lofc/README.md)). Full write-up:
[`../../REPORT.md`](../../REPORT.md).

_Status: complete (grid-converged; average + peak columns run)._
