# Phase 0 — steady state, normal operation

**Goal:** validate the model against the MHTGR-350 benchmark *before* any accident, so the
passive-cooldown results ride on a trusted baseline.

- **Conditions:** He 6.39 MPa, inlet 259 °C, block-average 5.93 MW/m³, forced convection.
- **Validation target:** peak fuel **~1282 °C** (band); core outlet **687 °C**.
- **Verification:** energy balance < 1 %; peak fuel grid-independent (≥ 3 meshes).
- **Acceptance:** outlet within ~3 %; peak within the reference band.

Built from [`../../case_template/`](../../case_template/). Produces the **operating steady
field** used as the initial condition for the LOFC conduction cooldown ([`phase_lofc`](../phase_lofc/README.md)).

_Status: stub — to be built out._
