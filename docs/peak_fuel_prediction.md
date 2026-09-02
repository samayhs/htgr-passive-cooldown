# Peak Fuel Temperature During Passive Cooldown — HTGR Prismatic Block

**Prediction report and accuracy-assessment context**
Model: MHTGR-350-class prismatic fuel block, 3D conjugate heat transfer (OpenFOAM 7).
Reference: OECD/NEA *Coupled Neutronic/Thermal-Fluids Benchmark of the MHTGR-350 MW Core
Design* (NEA/NSC/R(2017)4) — a **code-to-code** benchmark, not experimentally validated.

---

## 0. Read this first — what the prediction is, and what it is not

This model resolves **one prismatic fuel block / one coolant-channel column**, not the full
annular core. That scope decision governs how the result must be read:

- **The block-scale passive-cooldown prediction is *illustrative* and *non-conservative* for
  the true core peak.** A single block radiates directly to the Reactor Cavity Cooling System
  (RCCS) sink from its own outer surface. In the real core, decay heat must first conduct
  *radially across ~660 blocks* before it reaches the RCCS; that thermal resistance is what
  traps heat and produces the benchmark's delayed peak. Our single block has none of it, so it
  **over-cools** and its peak forms at *t ≈ 0*, not at the 50–74 h the full core exhibits.
- **The number the team should carry for the block deliverable:** peak fuel **≈ 793 °C** at the
  onset of the transient, giving **≈ 807 °C margin** to the 1600 °C TRISO/SiC limit — *for an
  average-power column, at block scale, on the grid-converged mesh, with the caveats below.*
- **The number that governs the real safety case** — the full-core delayed peak, **1391 K
  (≈1118 °C) at 50 h** (benchmark block model) / **1237 K at 74 h** (ring model) — **cannot be
  reproduced by this model** and is named here as the next-fidelity step.

If you need a defensible bounding peak-fuel temperature for the MHTGR-350 passive cooldown, use
the benchmark's full-core value and treat this block result as a verified, correctly-scoped
building block toward it — not as the answer.

---

## 1. Headline prediction

### 1a. Steady state (normal operation) — the validated baseline

| Quantity | This model (grid-converged) | Benchmark reference | Agreement |
|---|---|---|---|
| Coolant outlet (area-avg) | **688 °C** | 687 °C (core-average) | **0.2% — comparable** |
| Peak fuel (average column) | **≈799 °C** (Richardson; 793 °C on the 9.15 M mesh, GCI ~1%) | — (core max is a *peak*-column quantity) | see note & §6d |

*(A 4-mesh grid study (1.14–9.15 M cells) demonstrates convergence at near-second order,
GCI ~0.95%; the 2.64 M mesh used for the LOFC-case IC under-resolves the peak by ~17 °C — see §6d.)*

*Note:* the widely-cited benchmark steady peak fuel **~1282 °C** is the *core maximum* — the
hottest 1/6-block in the hottest (peak-power) column. Our **average-power** column peaks lower
(793 °C ≈ outlet 688 °C + fuel-to-coolant ΔT ~105 °C), which is physically consistent.

**Peak-column run (power ×1.85 → 46 MW/m³ fuel-local, fine mesh):** steady peak fuel **1268 °C**
vs benchmark **~1282 °C** — **within ~1%**, so the peak column reproduces the benchmark core max.
(Its coolant outlet, ~1050 °C, is *not* benchmark-comparable — ×1.85 power at the same channel
flow heats the coolant ~1.85×; in the real core the peak column is orificed.) The peak-column
**LOFC case**: peak fuel **1268 °C** at t≈0, **margin ~332 °C** to TRISO, cooling monotonically to
~367 °C (τ ~59–108 min). Note the peak-column steady (1268 °C) is the normal-op max and the block
LOFC cools from it; the benchmark full-core DCC delayed peak (1118 °C) sits *below* the steady
peak — i.e. the MHTGR-350 passive cooldown does not exceed normal-operation fuel temperatures.

### 1b. Passive cooldown — the LOFC case

Run on the grid-converged 9.15 M-cell mesh (IC = the converged Phase-0 field):

| Quantity | Value |
|---|---|
| **Peak fuel (max over space and time)** | **≈793 °C**, at *t ≈ 0* (the grid-converged operating steady state) |
| **Margin to TRISO limit (1600 °C)** | **≈807 °C** |
| Behaviour after t=0 | **monotonic conduction cooldown** to ~270 °C quasi-steady over ~8 h |
| Cooldown time constant τ | ~94 min (63%) to ~121 min (log-fit) |
| Peak location | block centre, hot (outlet) end |
| Energy conservation on this mesh (Phase 1) | 0.80% imbalance — PASS |

The peak is the initial condition: when forced cooling is lost, fission power drops to ~6% decay
*instantly*, and the block radiates its stored heat to the RCCS sink faster than decay replaces
it — so it cools from the start. **This is the block-scale signature of the scope limit in §0.**

---

## 2. Solution methodology / approach

**Code.** OpenFOAM 7 with a **custom temperature-based conjugate-heat-transfer solver**,
`chtMultiRegionTFoam` (vendored in `solver/`).

- **Why temperature-based.** The stock `chtMultiRegionFoam` solves the solid in enthalpy,
  `div(α·grad h)` with `α = κ/Cp`. It inserts Cp as a *nodal* value in α but an *interval-mean*
  in `grad h`; the two cancel only for constant Cp, leaving a mesh-independent bias (~17 °C in
  prior work). The T-solver solves `ρCp(T)·∂T/∂t = ∇·(κ∇T) + q‴` directly, so **steady
  conduction is Cp-independent by construction** and Cp(T) enters only the transient inertia
  term, where it physically belongs. The solver is a deliberate fork; owning it is the point.

**Model construction.**
- **Geometry / mesh:** gmsh, a real block cross-section (36 cm across-flats, 18.8 mm hole pitch)
  extruded to an **8 m / 10-block column**. **2.64 M cells** (solid 1.83 M, fluid 811 k), 109
  coolant channels / 222 fuel holes (2.04:1), with graded near-wall refinement on the channel
  walls. The fuel compacts are a **heat-source cellZone** (343 k cells) inside one uniform
  graphite solid region.
- **Steady (Phase 0):** two-region conjugate heat transfer — **resolved helium channels ↔
  solid** — marched as a `steadyState` pseudo-transient to convergence (peak fuel plateaus by
  ~350 iterations; run stopped on a converged write).
- **Passive cooldown (Phase LOFC):** **solid-only** conduction. Forced cooling is lost and the
  primary is depressurised/stagnant, so the in-channel helium is thermally inert and dropped;
  the channels become adiabatic walls. Time-accurate (implicit Euler, physical seconds) from
  the Phase-0 field, with a **time-dependent decay-heat source**. Solid-only removes the
  pressure equation entirely.

**Why solid-only for the LOFC case (a real finding, not a convenience).** An active-fluid model
with sealed channels was attempted and is **numerically singular** at block scale: the 109
coolant channels are geometrically **disconnected** enclosures, so a closed (sealed-end)
pressure problem has 108 unreferenced null spaces (one `pRefCell` can pin only one). This is
itself a manifestation of the single-block limitation — a single column cannot sustain the
core-scale inter-channel natural circulation that distinguishes pressurised (PCC) from
depressurised (DCC) cooldown. **PCC is therefore out of block scope**; the modeled case is the
depressurised/stagnant (DCC-family) conduction cooldown, with adiabatic channels as a
**conservative** treatment (trapped heat over-predicts the block peak).

**Verification (Phase 1).** The transient integrator was verified with an **in-solver energy
monitor** that emits, each timestep, the exact `∫ρh dV` (stored enthalpy), `∫Q dV` (decay power
in), and `∫ −κ∇T·n dA` over the outer wall (heat radiated out). See §7.

---

## 3. Boundary conditions

### 3a. Steady state (normal operation)

| Surface | Condition | Rationale |
|---|---|---|
| Coolant inlet | `fixedValue` T = 259 °C (532.15 K); U = 18.8 m/s | benchmark core inlet; velocity from mass flow (§4) |
| Coolant outlet | `inletOutlet` / `pressureInletOutletVelocity` | free outflow |
| Fluid ↔ solid interface | coupled (`turbulentTemperatureCoupledBaffleMixed`) | conjugate heat transfer, T + κ exchanged |
| Outer radial wall | **adiabatic** (`zeroGradient`) | interior-column symmetry (neighbours ≈ same T in normal op) |
| Axial ends | **adiabatic** (`zeroGradient`) | interior of a 10-block stack |

### 3b. Passive cooldown (LOFC)

| Surface | Condition | Rationale / caveat |
|---|---|---|
| Coolant channels | **adiabatic** (`zeroGradient`); helium inert/dropped | forced cooling lost; conservative (traps heat) |
| Axial ends | **adiabatic** | interior of column |
| Outer radial wall | **radiation to RCCS**: `externalWallHeatFluxTemperature`, ε = 0.85, T_amb = 303 K (30 °C RCCS sink), h = 1×10⁻³ | **lumped surrogate for the out-of-core radial path — NON-CONSERVATIVE for the peak** |

**Two boundary-condition caveats the team must weigh:**
1. **Radiation applied at the block surface** collapses the entire radial resistance of the core
   (reflector + core barrel + reactor vessel + stagnant-air gap) to zero. The benchmark's RCCS
   values (303 K, ε 0.85/0.74, stagnant-air radiation, 122.5 cm from the vessel) belong at the
   *vessel* boundary of a full-core model, not on a fuel block. Placing them on the block makes
   it shed heat far too easily — the dominant reason the block shows no delayed peak.
2. **h = 1×10⁻³ is a numerical floor, not a physical convection coefficient.** The BC forms
   `1/h`, so h = 0 (pure radiation) divides by zero; radiation dominates the floor by ~10⁴:1, so
   the wall is effectively radiation-only. (The prior parent-project constants h = 6, T_amb =
   400 K, ε = 0.80 were untraceable to MHTGR-350 and were removed.)

---

## 4. Inputs

All benchmark values trace to NEA/NSC/R(2017)4 (page/table cited where relevant).

### 4a. Operating point

| Input | Value | Source / derivation |
|---|---|---|
| Coolant | Helium, perfect gas, Cp 5193 J/kg·K | spec §AIV.13 |
| Primary pressure | **6.39 MPa** | spec p.16 (sets He density via EoS) |
| Core inlet temperature | **259 °C (532.15 K)** | spec p.16 |
| Inlet velocity | **≈18.8 m/s** | ṁ = 157.1 kg/s ÷ (109 channels × ~66 columns) → per-channel ṁ / (ρ·A_ch); cross-checked against the core energy balance |
| Power density (average) | 5.93 MW/m³ block-avg → **24.83 MW/m³** on the fuel zone | 5.93 / fuel volume fraction 0.2389 |
| Power density (peak column) | 11 MW/m³ block-avg (block 13 / level 8, ×1.85) → **46.05 MW/m³** on the fuel zone | radial×axial peaking; **not yet run** |

### 4b. Materials (H-451 graphite; benchmark verbatim where possible)

| Property | Value | Source | Caveat |
|---|---|---|---|
| Density ρ | **1850 kg/m³** | Table AIV.3 | — |
| Emissivity ε | **0.85** | Table AIV.3 | applied at the LOFC-case outer BC |
| Specific heat Cp(T) | benchmark polynomial (T⁻¹…T⁻⁴ terms), **refit** to a positive-power poly for OpenFOAM (`hPolynomial`), max error **0.28%** over 350–1900 K | Table AIV.3 | refit only re-expresses the curve |
| Conductivity κ(T) | **un-irradiated** fit: `κ = 3.28248e-5·T² − 0.124890·T + 169.2145` W/m·K | Table AIV.2 (un-irradiated row) | **biases the peak LOW** (see §6) |

The compact matrix and gap are **not** modeled with distinct conductivities (fuel is a
heat-source zone in uniform graphite); this is a modest approximation for thermal inertia (~2 °C
in prior work).

### 4c. Decay heat (LOFC case)

| Input | Value | Source | Caveat |
|---|---|---|---|
| Form | `q‴(t) = q‴_op · f_decay(t)`, spatially uniform on the fuel zone, clock from t = 0 | benchmark §I.7.4 (decay ∝ steady local power) | — |
| f_decay(t) | **ANS-5.1-family** standard U-235 decay-heat curve, tabulated from published decay fractions; 6.05% @1s → 1.35% @1h → 0.77% @8.3h → 0.36% @100h (monotonic) | standard shutdown decay | exact ANS-5.1 23-group coefficient table not in the repo; this anchored curve reproduces the standard fractions to ~a few % (their read accuracy). Replaced the earlier Way–Wigner interim, which ran ~20–45% low in the mid/long tail |
| q‴_op | 24.83 MW/m³ (average) or 46.05 (peak column) | §4a | — |

---

## 5. Assumptions (the honest list)

1. **Single block / single column**, not the annular core. *(Governs everything — see §0.)*
2. **Adiabatic lateral walls in steady** (interior-column symmetry); **radiation-to-RCCS at the
   block surface in the LOFC case** (lumped surrogate, non-conservative).
3. **Both average and peak columns run** (peak = ×1.85 power); the average column validates the
   outlet, the peak column reaches the benchmark core-max fuel temperature.
4. **Un-irradiated κ(T)** (irradiated data and the fluence file were not available in the
   distributed benchmark materials).
5. **ANS-5.1-family decay** anchored to the standard's published decay fractions, rather than the
   benchmark's exact DIN 25485 / ANS-5.1 coefficient table (not in the distributed materials).
6. **Uniform-in-z power** (no axial power shape).
7. **Fuel as a heat-source zone in uniform H-451** (no distinct compact/gap conductivities).
8. **Fixed post-blowdown pressure**; the 0–20 s depressurisation transient is not modeled
   (negligible vs the hours-scale thermal response).
9. **No control rods, no lumped burnable poison, no fuel-handling hole**, no bypass-flow gaps.
10. **PCC (pressurised cooldown) excluded** — its convective/recirculation mechanism is
    core-scale and singular at block scale.

---

## 6. How to assess the accuracy of this prediction

Two independent kinds of evidence, both required, are reported honestly below.

### 6a. Verification — *is the math right?* (no external data)

| Check | Result | Status |
|---|---|---|
| Transient energy conservation `ΔU = ∫P_decay dt − ∫Q_out dt` (all terms solver-exact, in-solver monitor) | avg column: **0.08%** (Δt 100 s), **0.24%** (Δt 50 s), **0.80%** (9.15 M mesh) — PASS. Peak column: **1.84%** — marginally >1% (wide T swing 1268→367 °C amplifies the cp(T) discretisation error in the T-based ddt) | ✅ avg-column PASS; ⚠️ peak-column 1.84% (peak itself is exact — it's the steady IC; the cooldown trajectory carries ~1.8% slop) |
| Time-step independence | peak fuel identical at both Δt (778.0 °C, medium-mesh Δt study); ΔU matches to 0.05% | ✅ PASS |
| Cooldown τ vs analytic lumped-capacitance `τ = ρc·V/(h_rad·A)` | CFD ~121 min vs analytic 128 min (~5%) | ✅ sanity pass |
| **Steady grid independence (4 meshes)** | near-second-order convergence (p≈2.15), GCI 0.95%, extrapolated peak 799 °C; outlet within 0.2% of benchmark | ✅ PASS (see §6d) |

The energy monitor cross-checks three ways: the solver's `∫ρh` change (−584 MJ), an independent
full-field enthalpy integration (−584 MJ), and the decay-minus-radiation budget all agree.

### 6d. Steady grid-independence study

**Four** 8 m-column meshes spanning ~8× in cell count (Phase-0, average column):

| Mesh | Cells | Peak fuel | Δpeak | Coolant outlet | Gap to benchmark 687 °C |
|---|---|---|---|---|---|
| Coarse | 1.14 M | 772.3 °C | — | 666.7 °C | −20.3 |
| Medium | 2.64 M | 781.9 °C | +9.6 | 676.3 °C | −10.7 |
| Fine | 6.14 M | 791.1 °C | +9.2 | 685.5 °C | −1.5 |
| **Finest** | **9.15 M** | **793.1 °C** | **+2.0** | **688.2 °C** | **+1.2** |

- **The peak fuel is grid-converged.** The first three meshes drift ~9–10 °C/level (the coarse
  mesh is outside the asymptotic range), but the **finest-mesh increment collapses to +2.0 °C** —
  and normalised per unit refinement the increment roughly halves, i.e. it shrinks *faster* than
  the step. A Roache GCI on the asymptotic triplet (medium/fine/finest, unequal ratios) gives
  **apparent order p ≈ 2.15** (near second-order — genuinely asymptotic), **GCI = 0.95%** on the
  finest mesh, and a **Richardson-extrapolated grid-converged peak of ≈799 °C**.
- **Independent cross-check:** the coolant outlet converges to **688.2 °C**, within **0.2%** of the
  benchmark 687 °C (gaps collapse −20 → −11 → −1.5 → +1.2).
- **Mechanism:** on coarse meshes numerical diffusion under-mixes the resolved coolant (lower
  outlet), and the fuel tracks it — that is why peak and outlet drift together by ~9 °C/level;
  it converges out by the finest mesh.
- **Consequence for the reported numbers:** the medium mesh (782 °C) **under-resolves the peak by
  ~17 °C** vs the grid-converged value, so the LOFC case was re-run from the grid-converged
  (9.15 M) Phase-0 field (IC ~793 °C). **Best estimate: steady peak fuel ≈ 799 °C** (Richardson) /
  793 °C on the finest mesh, GCI ~1% (±~7 °C); **margin ≈ 801 °C** to the TRISO limit. This is a
  *steady-state, average-column* value.

### 6b. Validation — *is it the right physics?* (agreement with the benchmark codes)

| Metric | This model | Benchmark | Assessment |
|---|---|---|---|
| Steady coolant outlet | 688 °C | 687 °C | **comparable (0.2%)** — the clean, tabulated validation quantity |
| Steady peak fuel (avg column) | ~793 °C (Richardson ~799) | ~1282 °C is the *core max* (peak column) | consistent for an average column; peak-column run needed to target 1282 °C |
| **LOFC-case peak fuel(t)** | ~793 °C @ t≈0, then cools | 1391 K @ 50 h (block) / 1237 K @ 74 h (ring) | **CANNOT be validated at block scale** — the reference peak is a full-core phenomenon (§0) |

The benchmark is **code-to-code, not experimental**: "validated" means agreement with
PHISICS/RELAP5-3D, not with measured reality.

### 6c. Directional bias of the block-scale LOFC-case prediction

| Assumption | Effect on predicted peak |
|---|---|
| Adiabatic channels (no coolant heat removal) | **conservative** (over-predicts) |
| **Radiation to RCCS at the block surface** (no core radial resistance) | **strongly non-conservative** (under-predicts) — dominant |
| Un-irradiated κ (higher than irradiated) | **non-conservative** (under-predicts; irradiation lowers κ → hotter) |
| ANS-5.1-family decay (replaced Way–Wigner) | tail now standard; Way–Wigner had run ~20–45% low mid/late |

**Net — it depends which column, and it's not one-directional:**
- **Average column:** the non-conservative effects dominate; its 793 °C sits *below* the benchmark
  full-core DCC peak (1118 °C) — an **under-prediction**.
- **Peak column:** its steady/IC peak (**1268 °C**, ≈ benchmark core max 1282 °C) *exceeds* the
  full-core DCC delayed peak (1118 °C), so it **brackets the safety-relevant fuel temperature from
  above** (and the block LOFC only cools from it).

Either way the block cannot reproduce the delayed-peak *mechanism*; it delivers the bounding
steady/IC peak and a cooldown from it. The peak-column steady (1268 °C, margin 332 °C to TRISO) is
the most safety-relevant single number this work produces.

---

## 7. Uncertainty and limitation summary

| Source | Direction / magnitude | Mitigation / next step |
|---|---|---|
| **No core radial conduction path (block ≠ core)** | Large; under-predicts core peak; removes the delayed peak | Full-core or effective-core radial model (see §8) |
| Average vs peak column | Both run: avg 793 °C (validates outlet); peak 1268 °C ≈ benchmark 1282 °C | Done |
| Un-irradiated κ | Under-predicts peak | Obtain EOEC fluence + Table AIV.2 irradiated coefficients |
| Decay heat | ANS-5.1-family (anchored to standard fractions, ~few %) | Exact DIN 25485 / ANS-5.1 23-group table if provided |
| Peak-column transient energy closure | 1.84% (>1%; wide-T cp(T) effect) | Smaller Δt near t=0, or enthalpy-form ddt |
| Steady grid resolution | Converged (p≈2.15, GCI 0.95%); peak grid uncertainty ~±7 °C; outlet within 0.2% of benchmark (§6d) | Closed (4-mesh study) |
| Steady peak-fuel reference (~1282 °C) is a secondary value | Reference-band uncertainty | Pin to a primary results table |

---

## 8. Recommended next-fidelity step

To predict the **safety-relevant** passive-cooldown peak (the delayed full-core peak the block
cannot hold), the model must restore the radial heat path to the RCCS:

- an **effective-core radial model** (or full annular core) with the RCCS boundary at the
  **reactor-vessel** surface (303 K, ε 0.85/0.74, stagnant-air radiation, 122.5 cm gap — the
  benchmark values recorded in `benchmark/README.md`), against the benchmark targets **1391 K @
  50 h** (block) / **1237 K @ 74 h** (ring).

The verified block model, its validated-comparable steady baseline, and the verified transient
integrator are the foundation that step builds on.

---

## 9. Bottom line for the team

- **Trust:** the steady baseline (grid-converged outlet 688 °C vs benchmark 687 °C, **0.2%**) and
  the transient integrator (energy-conservative to <0.25%, step-independent). The methodology is
  verified, the steady physics is comparable to the reference, and the steady peak is
  grid-converged (4-mesh study, p≈2.15, GCI ~1%, ~±7 °C).
- **Do not use as a safety peak:** the block-scale LOFC-case peak (~793 °C, margin ~807 °C).
  It is illustrative and **non-conservative** — it under-predicts the true core peak because a
  single block radiates directly to the RCCS and cannot form the 50–74 h delayed peak.
- **The governing number** for the MHTGR-350 passive-cooldown safety case remains the benchmark
  full-core value, **1391 K (≈1118 °C) at 50 h**, which this work correctly scopes toward rather
  than claims to reproduce.

---

*Provenance: results produced with `chtMultiRegionTFoam` (OpenFOAM 7) on an 8 m / 10-block
column (2.64 M cells). Phase 0 steady converged; Phase LOFC transient run to 30 000 s (8.3 h) at
two time steps; Phase 1 energy conservation verified in-solver. Benchmark data and page cites in
[`../benchmark/README.md`](../benchmark/README.md); verification-and-validation plan in
[`validation_plan.md`](validation_plan.md).*
