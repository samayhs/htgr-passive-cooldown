#!/bin/bash
# Grid-independence study for the full block at the ORIGINAL operating point
# (He 3 MPa, 300 C inlet, 10 m/s, q''' 7 MW/m3). Runs coarse + fine meshes through
# the full parallel pipeline; the prod point (1.28M -> 423.3 C) is reused.
# RUN THIS ONLY AFTER restoring the original BCs (git checkout 0.orig constant/solid/heatSource).
source /opt/OpenFOAM-7/etc/bashrc
[ -z "$WM_PROJECT_DIR" ] && { echo "OpenFOAM not loaded"; exit 1; }
cd /mnt/c/Users/samayhs/Documents/PythonProjects/prismatic-microreactor-thermal/cfd_3d_fullblock || exit 1

# preserve the production mesh (gitignored) before swapping
[ -f geometry/full_block_prod.msh ] || cp geometry/full_block.msh geometry/full_block_prod.msh

echo "mesh,solid_cells,peak_C" > grid_results.csv
echo "prod,921960,423.3   # reused (see earlier run)" >> grid_results.csv

for m in coarse fine; do
    cp geometry/full_block_${m}.msh geometry/full_block.msh
    echo ">>> running $m ..."
    bash run.sh > log.grid_$m 2>&1
    peak=$(grep -a "peak fuel temperature" log.grid_$m | tail -1 | grep -oE "[0-9]+\.[0-9]+")
    cells=$(grep -a -o 'nCells:[0-9]*' constant/solid/polyMesh/owner | head -1 | cut -d: -f2)
    echo "$m,$cells,$peak" >> grid_results.csv
    echo ">>> $m: solid_cells=$cells  peak=$peak C"
done

cp geometry/full_block_prod.msh geometry/full_block.msh   # restore prod mesh
echo "=== grid study ==="; cat grid_results.csv
