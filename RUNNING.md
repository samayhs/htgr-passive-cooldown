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

```bash
# single 0.793 m block (default af=0.36):
python geometry/make_full_block.py --lc 0.003 --nz 40 --out geometry/full_block.msh
# 8 m / 10-block column (for axial coolant heat-up):
python geometry/make_full_block.py --lc 0.0035 --nz 160 --length 8.0 --out geometry/full_block_stack.msh
```

## 2. Set up and run a phase case

Each `cases/<phase>/` is built from `case_template/` with its phase-specific conditions
(pressure, inlet T, velocity, power, decay heat, boundary treatment) — see the phase README and
[`docs/validation_plan.md`](docs/validation_plan.md). General flow (in WSL):

```bash
cd cases/<phase>
bash setup_case.sh        # gmshToFoam, split regions, apply BCs/fields
NP=16 bash run.sh         # decompose, solve in parallel, reconstruct
```

The transient LOFC cooldown (phase_lofc) starts from the Phase-0 operating steady field — run
Phase 0 first.

## 3. Extract metrics

Peak fuel, coolant profile, energy balance, and cooldown τ are pulled with the `extract_*` /
`*_metrics.py` tooling in `geometry/` (ported from the parent project; adapt per phase).
