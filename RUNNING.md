# Running

**Environment:** meshes are generated on Windows (Python + gmsh); the OpenFOAM 7 solve runs in
WSL (`of7` alias). Keep the repo path space-free (OpenFOAM rejects spaces). CFD output is
gitignored — tracked source is `case_template/{0.orig,system,constant/*}`, `geometry/*.py`,
`solver/`, and scripts.

## 0. Build the custom solver (once, in WSL)

```bash
cd solver/chtMultiRegionTFoam && ./Allwmake   # forces g++-11 (OF7 won't build under g++-15)
```

`chtMultiRegionTFoam` solves the solid directly in temperature (ρCp(T) ∂T/∂t = ∇·(k∇T) + q‴),
which removes the enthalpy-formulation Cp bias — the reason it exists. Nothing in `/opt` is
modified.

## 1. Generate the block mesh (Windows Python + gmsh)

The validated results use the **8 m / 10-block column** (needed for the 259→687 °C coolant
heat-up). `--lc` sets the cross-section cell size, `--nz` the axial divisions:

```bash
# 8 m column, medium mesh (~2.64 M cells):
python geometry/make_full_block.py --lc 0.004 --nz 120 --length 8.0 --out geometry/full_block.msh
```

Grid-independence study meshes (Phase-0 is grid-converged across these — GCI ~1%):
`--lc 0.0055 --nz 88` (1.14 M) · `--lc 0.004 --nz 120` (2.64 M) · `--lc 0.0028 --nz 168`
(6.14 M) · `--lc 0.0024 --nz 200` (9.15 M). Meshes are gitignored — regenerate as needed.

## 2. Run Phase 0 (steady), then the LOFC cooldown

A run needs `case_template/` + the mesh + `geometry/*.py`. Phase 0 is the base two-region
config; the LOFC cooldown reuses the same mesh and starts from the Phase-0 steady field.

```bash
# Phase 0 — steady, two-region CHT (helium channels + solid), 16-way parallel:
NP=16 bash run.sh          # gmshToFoam -> split -> fuel topoSet -> decompose -> solve -> reconstruct
# steadyState; peak fuel plateaus by ~350-400 iters -> stop on a converged write.

# LOFC conduction cooldown — solid-only, from the Phase-0 field:
bash run_lofc.sh           # snapshots the steady field, stages lofc/ dicts, runs the transient
```

`run_lofc.sh` drops the fluid region (channels adiabatic), applies the RCCS radiation outer BC
(303 K, ε 0.85), and marches the time-dependent decay heat (ANS-5.1-family). **Run Phase 0 first.**

**Average vs peak column.** The base power is the average column (`heatSource` qVol =
24.83 MW/m³ fuel-local). For the **peak column** (×1.85, targets the ~1282 °C core max), set the
power before Phase 0 and scale the LOFC decay table by 1.8546:

```bash
foamDictionary -entry qVol -set 46.05e6 constant/solid/heatSource   # peak-column steady power
# ... run Phase 0, then scale lofc/heatSource decay values x1.8546 for the LOFC run.
```

## 3. Metrics & verification

- **LOFC metrics** — `geometry/lofc_metrics.py` (invoked by `run_lofc.sh`) writes peak fuel(t),
  time-to-peak, quasi-steady peak, cooldown τ, TRISO margin, and an energy-balance check to
  `runs/lofc/`.
- **Phase-1 energy conservation** — the solver emits an `ENERGYMON <t> <U> <P_decay> <Q_out>`
  line each timestep (∫ρh dV, ∫Q dV, ∫−κ∇T·n over outerWall); integrating verifies
  `ΔU = ∫P_decay − ∫Q_out` closes to <1% (achieved: <0.8%, Δt-independent).
- Steady outlet and peak fuel are read from the reconstructed fluid/solid fields.

Results and the full accuracy assessment are in
[`docs/peak_fuel_prediction.md`](docs/peak_fuel_prediction.md).
