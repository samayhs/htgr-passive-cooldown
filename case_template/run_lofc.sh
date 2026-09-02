#!/bin/bash
###############################################################################
# Full-block LOFC (loss-of-forced-cooling) conduction cooldown -- solid-only, in place.
#
# Forced cooling is lost and the primary is depressurised/stagnant (benchmark DCC family):
# the in-channel helium is thermally inert and dropped, the channels go adiabatic, and the
# block sheds time-dependent decay heat (heatSource q'''(t)) by conduction to the outer
# surface + radiation to the RCCS (303 K, eps 0.85). Solid-only, so there is no p_rgh solve.
# Time-marched from the normal-operation steady field at t=0 to the quasi-steady peak,
# giving the peak fuel (margin to TRISO 1600 C) and the cooldown time-constant tau.
#
# Reuses the reconstructed solid mesh + the operating steady field at 4000/ (produced by
# run.sh). Does NOT regenerate the mesh. Stages the LOFC dicts from lofc/, runs, extracts
# metrics to runs/lofc/, then restores the tracked base source with git.
#
# Usage (WSL):  bash run_lofc.sh            (LOFC_ENDTIME=2 bash run_lofc.sh  -> smoke)
###############################################################################
source /opt/OpenFOAM-7/etc/bashrc
[ -z "$WM_PROJECT_DIR" ] && { echo "ERROR: OpenFOAM 7 not loaded."; exit 1; }
cd "$(dirname "$(readlink -f "$0")")" || exit 1
CASE="$(pwd)"
NP=16
case "$CASE" in *" "*) echo "ERROR: space in path: $CASE"; exit 1;; esac

# tracked base files this run overwrites, restored on exit
STAGED="constant/regionProperties constant/solid/heatSource constant/solid/fvOptions system/controlDict system/solid/fvSchemes"
restore() { echo ">> restoring tracked base source"; git checkout -- $STAGED 2>/dev/null; \
            git checkout -- constant/solid/polyMesh/boundary 2>/dev/null || true; }
trap restore EXIT

# --- preconditions ---------------------------------------------------------
[ -f constant/solid/polyMesh/owner ]|| { echo "ERROR: solid mesh missing -- run 'bash run.sh' first."; exit 1; }
# protect the operating steady field: snapshot it out of the time namespace so the
# LOFC solver's t=4000 write cannot clobber it (and it survives LOFC re-runs).
if [ ! -f operating_steady/solid/T ]; then
    [ -f 4000/solid/T ] || { echo "ERROR: neither operating_steady/ nor 4000/ present -- run 'bash run.sh' first."; exit 1; }
    echo ">> snapshotting operating steady field 4000/ -> operating_steady/"
    rm -rf operating_steady && cp -r 4000 operating_steady
fi
command -v chtMultiRegionTFoam >/dev/null 2>&1 || {
    echo ">> building chtMultiRegionTFoam (vendored solver/) ..."
    REPO="$(git -C "$CASE" rev-parse --show-toplevel)"
    bash "$REPO/solver/chtMultiRegionTFoam/Allwmake" > log.buildSolver 2>&1 \
        || { echo "solver build failed -- see log.buildSolver"; exit 1; }
    hash -r; }

# --- stage LOFC configuration ---------------------------------------------
echo ">> staging LOFC dicts from lofc/"
cp lofc/regionProperties  constant/regionProperties
cp lofc/heatSource        constant/solid/heatSource
cp lofc/fvOptions         constant/solid/fvOptions
cp lofc/controlDict       system/controlDict
cp lofc/fvSchemes.solid   system/solid/fvSchemes
[ -n "${LOFC_ENDTIME:-}" ] && foamDictionary -entry endTime -set "$LOFC_ENDTIME" system/controlDict >/dev/null

# --- build IC/BC fields (solid-only; channel patch -> wall; setup_lofc_fields.py) -----
echo ">> assembling LOFC fields (setup_lofc_fields.py)"
rm -rf 0
python3 geometry/setup_lofc_fields.py || { echo "field setup failed"; exit 1; }
# clear stale numeric time dirs (operating 4000/ + any prior LOFC output) so the
# LOFC output namespace is clean and nothing collides with the IC snapshot.
for d in [1-9]*; do [ -d "$d" ] && rm -rf "$d"; done

# --- decompose solid-only, run, reconstruct --------------------------------
echo ">> decomposePar -region solid (NP=$NP)"
rm -rf processor*
decomposePar -region solid -time 0 > log.lofc.decompose 2>&1 \
    || { echo "decomposePar failed:"; tail -15 log.lofc.decompose; exit 1; }

echo ">> mpirun -np $NP chtMultiRegionTFoam -parallel  (LOFC transient)"
mpirun -np "$NP" chtMultiRegionTFoam -parallel > log.lofc.solve 2>&1
grep -q "FOAM FATAL" log.lofc.solve && { echo "solver FATAL:"; grep -A8 "FOAM FATAL" log.lofc.solve | head -30; exit 1; }

echo ">> reconstructPar -region solid"
reconstructPar -region solid -newTimes > log.lofc.reconstruct 2>&1

# fields for the visualizer
postProcess -region solid -func writeCellCentres -latestTime > /dev/null 2>&1

# --- metrics ---------------------------------------------------------------
echo ">> extracting metrics -> runs/lofc/"
mkdir -p runs/lofc
python3 geometry/lofc_metrics.py > runs/lofc/summary.txt 2>&1
cat runs/lofc/summary.txt

echo ""
echo "=================================================================="
echo "  LOFC transient done. Summary + trajectory in runs/lofc/."
echo "  (tracked base source is restored on exit; lofc/ is the record.)"
echo "=================================================================="
