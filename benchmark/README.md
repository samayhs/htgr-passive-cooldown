# MHTGR-350 benchmark — reference data (for the passive-cooldown project)

Distilled reference values for the **OECD/NEA Coupled Neutronic/Thermal-Fluids Benchmark of
the MHTGR-350 MW Core Design**. This is the external reference the passive-cooldown model is
validated against. Local copies of the source documents are in [`spec/`](spec/) and
[`refs/`](refs/); the numbers below were extracted from them (page cites in parentheses).

> **Nature of the benchmark — read first.** The benchmark is a **code-to-code** comparison,
> **not experimentally validated**. The transient results paper states the event sequences
> *"should not be seen as representative of the MHTGR safety case but purely as the basis for
> code-to-code comparisons"* and that *"without experimental data … it is difficult to
> conclude which of the … models are providing a more accurate prediction."* So "validate
> against the benchmark" means **agree with the reference codes (PHISICS/RELAP5-3D)**, not
> agree with measured reality.

---

## 1. Block geometry (matches our generator)

| Parameter | Benchmark | `make_full_block.py` |
|---|---|---|
| Block across-flats | **36 cm** (spec p.17) | 0.36 m ✓ |
| Fuel/coolant pitch | **1.8796 cm** (p.17) | 18.8 mm ✓ |
| Block porosity | **0.186** (p.17) | 0.186 ✓ |
| Fuel : coolant ratio | **2 : 1** (2 fuel holes per coolant hole, p.17) | 2.04 : 1 ✓ |
| Element (block) length | **79.3 cm** (p.17) | 0.8 m ✓ |
| Active core height | **7.93 m** (10 blocks) | 8.0 m column ✓ |
| Fuel hole radius | 0.635 cm (p.17) | — |
| Coolant hole radius | 0.794 cm large / 0.635 cm small (p.17) | — |
| Fuel-handling hole | 3.5 cm dia (p.17) | not modeled |
| LBP holes / element | 6 corner holes (p.17) | not modeled |

## 2. Steady-state operating point (Phase I / normal operation)

| Condition | Value (spec p.16, 20) |
|---|---|
| Thermal power | 350 MW(t) |
| Core power density (block-average) | **5.93 MW/m³** |
| Primary coolant / pressure | Helium, **6.39 MPa** |
| Core inlet / outlet temperature | **259 °C / 687 °C** |
| Core mass flow rate | **157.1 kg/s** (whole core) |
| TRISO/SiC integrity limit | keep fuel **< ~1600 °C** during conduction cooldown |

**Reference steady peak fuel temperature (the Phase-0 validation target):**

> **`Tfuel_max_core` ≈ 1282 °C** (full-power steady state, below the 1600 °C limit).

This is the widely-cited benchmark steady maximum fuel temperature (corroborated across
multiple published analyses of the MHTGR-350 T/F exercises). **Caveat on precision:** the
primary results tables (tandfonline multi-physics steady-state paper; ScienceDirect thermo-
fluid verification paper) are paywalled and could not be opened directly, and the exact value
varies by exercise and by block-vs-ring model — so treat **~1282 °C as the reference peak with
a modest band**, not a single certified digit, until a results table is read directly. Axial
fuel-temperature *profiles* by block are in `refs/OSTI-1248189…` (in figures, not text).
Reported quantities: `Tfuel_max` (max compact temperature in a 1/6 region of a block, over
79.3 cm), `Tfuel_avg`, `Tfuel_max_core`.

## 3. Transient exercises — DCC / PCC (Phase II)

These are the **passive-cooldown** cases. Decay heat is the **DIN 25485** per-block
time-dependent fit (spec Appendix I), started at t=0.

### DCC — Depressurised Conduction Cooldown (Exercise II-1a) — the *bounding* case
- Initiated by a **break in the pressure boundary**; system depressurises to **atmospheric
  (100 kPa)** linearly over 0–20 s; inlet flow → 0 kg/s.
- **Reactor trip at 30 s** (all control rods in). Simulated **100 hours**.
- Starting point: steady state from Exercise I-3a (11 % bypass, variable properties).
- **Reference maximum fuel temperature (PHISICS/RELAP5-3D):**
  - **Block model: 1,391 K (≈ 1,118 °C) at 50 h**
  - **Ring model: 1,237 K (≈ 964 °C) at 74 h**
  - (Strydom transient paper, §IV, Fig. 8)

### PCC — Pressurised Conduction Cooldown (Exercise II-2)
- Helium **retained**; pressure equalises at **5 MPa**; flow → 0; trip at 60 s.
- Natural convection active → peak is **lower and flatter** than DCC (block model up to
  **120 K colder** than DCC). (Strydom transient paper, §V, Figs. 13–14)

**Key physics:** both peaks are **delayed 50–74 h** because heat leaves the core only by
**radial conduction + radiation** through the reflector to the vessel/RCCS — a **full-core**
phenomenon.

## 4. What a BLOCK-LEVEL model can and cannot validate against this

| | Block/column model (ours) | Benchmark reference |
|---|---|---|
| Steady per-block fuel→coolant ΔT, axial peak | ✅ comparable | Phase-I T/F tables |
| **DCC/PCC delayed peak (1,237–1,391 K @ 50–74 h)** | ❌ **cannot reproduce** — it's set by full-core radial conduction to the RCCS, absent in a single block with adiabatic lateral walls | Phase-II Figs. 8/13/14 |

**Scope decision (locked):** the passive-cooldown deliverable is **block-level** — steady
validated to the benchmark block reference, then a **block-scale conduction cooldown** as a
verified, honestly-scoped accident calc. The full-core DCC delayed peak is named as the next
fidelity step, with these reference numbers as its target.

## 5. Sources (local copies + URLs)

- `spec/NEA-NSC-R2017-4_MHTGR-350_VolI-II.pdf` — NEA/NSC/R(2017)4, benchmark spec Vols I & II
  (geometry, steady conditions, decay-heat appendix).
  <https://www.oecd-nea.org/upload/docs/application/pdf/2020-01/dir1/nsc-r2017-4.pdf>
- `refs/Strydom_MHTGR-350_DCC-PCC_transient_results.pdf` — INL, DCC/PCC (Ex. II-1a / II-2)
  transient reference results (PHISICS/RELAP5-3D). Source of the peak-fuel numbers in §3.
  <https://inldigitallibrary.inl.gov/content/uploads/50/2026/04/7146952.pdf>
- `refs/OSTI-1248189_MHTGR-350_steady_multiphysics.pdf` — steady-state multiphysics results
  (block/ring axial fuel-temperature profiles).
  <https://www.osti.gov/pages/servlets/purl/1248189>
- Steady peak-fuel value (~1282 °C) — cited in the multi-physics steady-state analysis
  (paywalled, not opened directly): <https://www.tandfonline.com/doi/full/10.1080/00223131.2017.1299649>
  and the thermo-fluid verification paper: <https://www.sciencedirect.com/science/article/pii/S0306454919307595>
- Benchmark landing page:
  <https://www.oecd-nea.org/jcms/pl_46584/coupled-neutronic/thermal-fluid-benchmark-of-the-mhtgr-350-mw-core-design-results-for-the-lattice-physics-exercises>

*Note: "Volume IV" is the benchmark's internal name for the transient (DCC/PCC) exercise
specification; the published NEA report covers Vols I & II, so the transient **definitions and
reference results** here are sourced from the INL results paper above, not a standalone Vol IV PDF.*
