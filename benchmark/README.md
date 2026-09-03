# MHTGR-350 benchmark — reference data

Distilled reference values for the **OECD/NEA Coupled Neutronic/Thermal-Fluids Benchmark of the
MHTGR-350 MW Core Design** (NEA/NSC/R(2017)4), the external reference this project compares against.
Values are extracted from the documents cited in §4 (page cites in parentheses); the source PDFs are
**not tracked** in this repo — see §4 for URLs.

> **Nature of the benchmark.** It is a **code-to-code** comparison, **not experimentally validated**.
> The transient paper states the event sequences *"should not be seen as representative of the MHTGR
> safety case but purely as the basis for code-to-code comparisons."* So "compare against the
> benchmark" means agree with the reference codes (PHISICS/RELAP5-3D), not with measured reality.

## 1. Block geometry

| Parameter | Value (spec p.17) |
|---|---|
| Block across-flats | 36 cm |
| Fuel/coolant pitch | 1.8796 cm |
| Block porosity | 0.186 |
| Fuel : coolant ratio | 2 : 1 |
| Element (block) length | 79.3 cm |
| Active core height | 7.93 m (10 blocks) |
| Fuel hole radius | 0.635 cm |
| Coolant hole radius | 0.794 cm large / 0.635 cm small |
| Fuel-handling hole | 3.5 cm dia |
| LBP holes / element | 6 corner holes |

## 2. Steady-state operating point (Phase I)

| Condition | Value (spec p.16, 20) |
|---|---|
| Thermal power | 350 MW(t) |
| Core power density (block-average) | 5.93 MW/m³ |
| Primary coolant / pressure | Helium, 6.39 MPa |
| Core inlet / outlet temperature | 259 °C / 687 °C |
| Core mass flow rate | 157.1 kg/s (whole core) |
| TRISO/SiC integrity limit | fuel < ~1600 °C during conduction cooldown |

**Reference steady peak fuel:** `Tfuel_max_core` ≈ **1282 °C** (full-power steady state), the
widely-cited benchmark core maximum. Caveat: the primary results tables (§4, paywalled) could not be
opened directly and the value varies by exercise and block-vs-ring model, so treat ~1282 °C as a
band, not a certified digit.

## 3. Transient exercises — DCC / PCC (Phase II)

The passive-cooldown cases. Decay heat is the DIN 25485 per-block time-dependent fit (spec App. I),
started at t = 0.

- **DCC (Depressurised Conduction Cooldown, Ex. II-1a)** — depressurises to atmospheric over 0–20 s,
  trip at 30 s, 100 h simulated. Reference max fuel (PHISICS/RELAP5-3D): **1391 K (≈ 1118 °C) at
  50 h** (block) / **1237 K (≈ 964 °C) at 74 h** (ring) — Strydom §IV, Fig. 8.
- **PCC (Pressurised Conduction Cooldown, Ex. II-2)** — helium retained at 5 MPa, trip at 60 s.
  Natural convection makes the peak lower and flatter than DCC (up to 120 K colder) — Strydom §V,
  Figs. 13–14.

Both peaks are **delayed 50–74 h** because heat leaves the core only by radial conduction and
radiation through the reflector to the vessel/RCCS — a full-core phenomenon.

## 4. Sources

Cited by URL. Local copies may exist under `spec/` and `refs/` but are **not tracked** (`.gitignore`).

- **NEA/NSC/R(2017)4** — benchmark spec Vols I & II (geometry, steady conditions, decay-heat
  appendix). <https://www.oecd-nea.org/upload/docs/application/pdf/2020-01/dir1/nsc-r2017-4.pdf>
- **Strydom et al., INL** — DCC/PCC transient reference results (PHISICS/RELAP5-3D); source of the
  §3 peak-fuel numbers. <https://inldigitallibrary.inl.gov/content/uploads/50/2026/04/7146952.pdf>
- **OSTI-1248189** — steady multiphysics results (block/ring axial fuel-temperature profiles).
  <https://www.osti.gov/pages/servlets/purl/1248189>
- Steady peak-fuel value (~1282 °C), cited in the multi-physics steady-state and thermo-fluid
  verification papers (paywalled):
  <https://www.tandfonline.com/doi/full/10.1080/00223131.2017.1299649> ·
  <https://www.sciencedirect.com/science/article/pii/S0306454919307595>
- Benchmark landing page:
  <https://www.oecd-nea.org/jcms/pl_46584/coupled-neutronic/thermal-fluid-benchmark-of-the-mhtgr-350-mw-core-design-results-for-the-lattice-physics-exercises>

*Note: "Volume IV" is the benchmark's internal name for the transient (DCC/PCC) exercise spec; the
published NEA report covers Vols I & II, so the transient definitions and reference results here are
from the INL results paper, not a standalone Vol IV PDF.*
