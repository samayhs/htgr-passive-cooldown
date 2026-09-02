#!/bin/bash
# Energy-balance validation on the converged full-block result.
# Runs the unit cell's proven FOs (Tout, mdot, wallHeatFlux) via the all-region
# -postProcess, then the numbers are combined by hand into Q_gen/Q_wall/Q_cool.
source /opt/OpenFOAM-7/etc/bashrc
[ -z "$WM_PROJECT_DIR" ] && { echo "OpenFOAM not loaded"; exit 1; }
cd /mnt/c/Users/samayhs/Documents/PythonProjects/prismatic-microreactor-thermal/cfd_3d_fullblock || exit 1

cp system/controlDict /tmp/cd.fullblock.bak
cat ../cfd_3d_unitcell/validation/energyBalance.functions >> system/controlDict
echo ">> chtMultiRegionFoam -postProcess -latestTime"
chtMultiRegionFoam -postProcess -latestTime > log.energyBalance 2>&1
cp /tmp/cd.fullblock.bak system/controlDict          # restore clean controlDict

echo "=== raw FO output ==="
grep -aE "weightedAverage|sum\(phi\)|areaIntegrate|wallHeatFlux|of T|of phi|min:|max:|integral" log.energyBalance | tail -25
echo ""
echo "=== fuel zone volume (for Q_gen = q''' * V_fuel) ==="
grep -aE "fuel|Volume|cells" log.energyBalance | grep -iE "fuel|zone" | tail -3
