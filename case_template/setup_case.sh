#!/bin/bash
###############################################################################
# Full-block CHT — SETUP ONLY (stops before the solver).
#
# Runs the preprocessing on the committed case source (0.orig/, constant/,
# system/ are tracked here — this script does NOT copy them from the unit cell):
#   gmshToFoam -> splitMeshRegions -cellZonesOnly -> fuel topoSet
# then reports the two regions, the fuel zone, and the coupled interface.
#
# -cellZonesOnly keeps the disconnected coolant channels as ONE fluid region
# (plain -cellZones would split them into one region per channel). To run, use run.sh.
#
# Requires OpenFOAM 7 and geometry/full_block.msh (regenerate on Windows:
#   python geometry/make_full_block.py --lc 0.003 --nz 40).
###############################################################################
source /opt/OpenFOAM-7/etc/bashrc
if [ -z "$WM_PROJECT_DIR" ]; then
    echo "ERROR: OpenFOAM 7 did not load (WM_PROJECT_DIR empty)."; exit 1
fi
echo "OpenFOAM $WM_PROJECT_VERSION loaded."

cd "$(dirname "$(readlink -f "$0")")" || exit 1
MSH=geometry/full_block.msh
[ -f "$MSH" ] || { echo "ERROR: $MSH not found (run make_full_block.py on Windows)."; exit 1; }

# clean previous run artifacts only (never the tracked case source)
rm -rf constant/polyMesh constant/fluid/polyMesh constant/solid/polyMesh
rm -rf 0 [1-9]* processor* postProcessing cellToRegion log.*

echo ">> gmshToFoam $MSH"
gmshToFoam "$MSH" > log.gmshToFoam 2>&1
if [ $? -ne 0 ]; then echo "gmshToFoam FAILED:"; tail -15 log.gmshToFoam; exit 1; fi

echo ">> splitMeshRegions -cellZonesOnly (keep disconnected channels as ONE region)"
splitMeshRegions -cellZonesOnly -overwrite > log.split 2>&1
if [ $? -ne 0 ]; then echo "splitMeshRegions FAILED:"; tail -15 log.split; exit 1; fi
rm -rf constant/polyMesh          # drop the leftover pre-split base mesh

echo ">> make_toposet.py + topoSet -region solid (carve fuel heat-source zone)"
python3 geometry/make_toposet.py > log.toposet_gen 2>&1 || { echo "make_toposet FAILED"; tail log.toposet_gen; exit 1; }
topoSet -region solid > log.topoSet 2>&1 || { echo "topoSet FAILED"; tail -15 log.topoSet; exit 1; }
grep -a "cellZone\|Added" log.topoSet | tail -2

echo "=== regions (should be exactly fluid + solid) ==="
for r in fluid solid; do
    n=$(grep -a -o 'nCells:[0-9]*' "constant/$r/polyMesh/owner" 2>/dev/null | head -1 | cut -d: -f2)
    echo "   region '$r' : $n cells"
done
echo "=== coupled interface ==="
grep -aA6 "solid_to_fluid" constant/solid/polyMesh/boundary | grep -aE "mappedWall|sampleRegion|samplePatch|nFaces"
echo ">> DONE (mesh + regions + fuel zone ready; no solver run). To run: bash run.sh"
