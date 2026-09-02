#!/bin/bash
###############################################################################
# Full-block CHT — PARALLEL run, in place.
#
#   mesh -> gmshToFoam -> splitMeshRegions (-cellZonesOnly: 2 regions) ->
#   fuel cellZone -> decomposePar -> mpirun chtMultiRegionTFoam -> reconstructPar
#
# Requirements:
#   * space-free repo path (OpenFOAM rejects spaces)
#   * OpenFOAM 7 at /opt/OpenFOAM-7
#   * geometry/full_block.msh present  (regenerate on Windows:
#       python geometry/make_full_block.py --lc 0.003 --nz 40)
#   * the custom solver chtMultiRegionTFoam (vendored in solver/); built here
#     if missing.
#
# Notes:
#   * -cellZonesOnly keeps the disconnected coolant channels as ONE fluid
#     region (plain -cellZones would split them into one region per channel).
#   * Heavy solve: 1.28M cells, 2 regions. On 16 cores expect ~15-40 min.
#   * Operating point is still the unit cell's (He 3 MPa, inlet 300 C, 10 m/s,
#     q''' 7 MW/m3). For an MHTGR-350 benchmark, change constant/fluid + 0.orig
#     and constant/solid/heatSource accordingly before running.
#
# Usage (WSL):  bash run.sh          (optionally: NP=8 bash run.sh)
###############################################################################
source /opt/OpenFOAM-7/etc/bashrc
if [ -z "$WM_PROJECT_DIR" ]; then
    echo "ERROR: OpenFOAM 7 did not load (WM_PROJECT_DIR empty)."; exit 1
fi
cd "$(dirname "$(readlink -f "$0")")" || exit 1
CASE="$(pwd)"
NP="${NP:-16}"

case "$CASE" in *" "*) echo "ERROR: space in path: $CASE"; exit 1;; esac
if [ ! -f geometry/full_block.msh ]; then
    echo "ERROR: geometry/full_block.msh not found."
    echo "Generate it first (on Windows):"
    echo "  python geometry/make_full_block.py --lc 0.003 --nz 40"
    exit 1
fi

# build the vendored custom solver if it isn't on PATH yet
if ! command -v chtMultiRegionTFoam >/dev/null 2>&1; then
    echo ">> building chtMultiRegionTFoam (vendored solver/) ..."
    REPO="$(git -C "$CASE" rev-parse --show-toplevel)"
    bash "$REPO/solver/chtMultiRegionTFoam/Allwmake" > log.buildSolver 2>&1 \
        || { echo "solver build failed — see log.buildSolver"; exit 1; }
    hash -r
fi

# clean previous RUN ARTIFACTS only (constant/*/{thermo,fvOptions,heatSource} are source)
rm -rf constant/polyMesh constant/fluid/polyMesh constant/solid/polyMesh
rm -rf 0 [1-9]* processor* postProcessing cellToRegion log.gmshToFoam log.split \
       log.topoSet log.toposet_gen log.decomposePar log.chtMultiRegionTFoam \
       log.reconstructPar *.foam

echo ">> gmshToFoam";                 gmshToFoam geometry/full_block.msh          > log.gmshToFoam 2>&1
echo ">> splitMeshRegions (2 regions)"; splitMeshRegions -cellZonesOnly -overwrite > log.split      2>&1
rm -rf constant/polyMesh
echo ">> topoSet (fuel cellZone)";     python3 geometry/make_toposet.py           > log.toposet_gen 2>&1
                                       topoSet -region solid                       > log.topoSet    2>&1
rm -rf 0 && cp -r 0.orig 0

echo ">> decomposePar -allRegions (NP=$NP)"
decomposePar -allRegions -force > log.decomposePar 2>&1 \
    || { echo "decomposePar failed — see log.decomposePar"; tail -15 log.decomposePar; exit 1; }

echo ">> mpirun -np $NP chtMultiRegionTFoam -parallel   (heavy: ~15-40 min on 16 cores)"
mpirun -np "$NP" chtMultiRegionTFoam -parallel > log.chtMultiRegionTFoam 2>&1

echo ">> reconstructPar -allRegions"
reconstructPar -allRegions -latestTime > log.reconstructPar 2>&1

# fields for the visualizer / ParaView
postProcess -region fluid -func writeCellCentres -latestTime > /dev/null 2>&1
postProcess -region solid -func writeCellCentres -latestTime > /dev/null 2>&1
touch fluid.foam solid.foam

TIME=$(foamListTimes | tail -1)
PEAK=$(awk '/Min.max T/{s=$0; sub(/.*Min.max T:/,"",s); split(s,a," "); if(a[1]+0>500) m=a[2]} END{printf "%.1f", m-273.15}' log.chtMultiRegionTFoam)
echo ""
echo "=================================================================="
echo "  DONE.  peak fuel temperature = ${PEAK} C   (latest time ${TIME})"
NFUEL=$(grep -aoE '[0-9]+ fuel cylinders' log.toposet_gen 2>/dev/null | grep -oE '^[0-9]+')
echo "  Full block: 360 mm across-flats, ${NFUEL:-?} fuel compacts (2:1 fuel:coolant)."
echo "  Output is in this folder (gitignored)."
echo "=================================================================="
