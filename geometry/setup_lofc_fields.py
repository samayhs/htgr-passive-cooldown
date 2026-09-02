#!/usr/bin/env python3
"""
Assemble the LOFC (loss-of-forced-cooling) conduction-cooldown initial/boundary state
for the SOLID-ONLY full-block case. Run from the case directory after the normal-
operation steady result exists (snapshotted to operating_steady/ by run_lofc.sh).

Physical t=0 = reactor at normal operation, forced cooling just lost. The primary is
depressurised/stagnant (benchmark DCC family): the in-channel helium is thermally inert
and dropped, the channels go adiabatic, and the block sheds decay heat by conduction to
the outer surface + radiation to the RCCS. Solid-only, so there is no p_rgh solve (and
none of the closed-channel pressure-reference pathology of an active-fluid model).

Adiabatic channels TRAP heat -> conservative (over-predict peak). PCC is out of scope
(its convective/recirculation mechanism is core-scale, absent in one block).

Three text-level edits (no OpenFOAM field construction, robust to the solid-only setup
where the fluid region no longer exists):

  1. constant/solid/polyMesh/boundary : solid_to_fluid mappedWall -> wall
     (drop the sampleMode/sampleRegion/samplePatch that pointed at the dropped fluid
     region), preserving nFaces/startFace.
  2. 0/solid/T : internalField copied from the operating steady field (LOFC t=0), with
     the LOFC boundaryField:
        outerWall      -> externalWallHeatFluxTemperature (radiation to RCCS)
                          = 0.85*sigma*(T^4-303^4)  [RCCS sink 303 K, eps 0.85 graphite]
        solidEnds      -> zeroGradient (adiabatic axial ends; interior of column)
        solid_to_fluid -> zeroGradient (adiabatic channels; forced cooling lost)
  3. 0/solid/p : copied from 0.orig/solid/p.
"""
import os, re, shutil, sys

CASE = os.getcwd()
IC_TIME = "operating_steady"           # protected normal-op steady field (LOFC t=0)


def die(msg):
    sys.stderr.write("ERROR: " + msg + "\n"); sys.exit(1)

# ---------------------------------------------------------------------------
# 1. solid polyMesh boundary: mappedWall -> wall for solid_to_fluid
# ---------------------------------------------------------------------------
bpath = os.path.join(CASE, "constant/solid/polyMesh/boundary")
if not os.path.isfile(bpath):
    die("missing " + bpath)
btxt = open(bpath).read()


def fix_patch(m):
    block = m.group(0)
    block = re.sub(r"type\s+mappedWall\s*;", "type            wall;", block)
    block = re.sub(r"\n\s*sampleMode\s+[^;]*;", "", block)
    block = re.sub(r"\n\s*sampleRegion\s+[^;]*;", "", block)
    block = re.sub(r"\n\s*samplePatch\s+[^;]*;", "", block)
    return block


if re.search(r"solid_to_fluid\s*\{[^}]*type\s+wall\s*;", btxt, re.S):
    print("[1/3] boundary: solid_to_fluid already a wall (idempotent skip)")
else:
    new_btxt = re.sub(r"solid_to_fluid\s*\{.*?\}", fix_patch, btxt, count=1, flags=re.S)
    if new_btxt == btxt:
        die("solid_to_fluid patch not converted (pattern not found)")
    open(bpath, "w").write(new_btxt)
    print("[1/3] boundary: solid_to_fluid mappedWall -> wall")

# ---------------------------------------------------------------------------
# 2. 0/solid/T : operating internalField + LOFC boundaryField
# ---------------------------------------------------------------------------
icT = os.path.join(CASE, IC_TIME, "solid/T")
if not os.path.isfile(icT):
    die("missing operating IC " + icT + " (run the base normal case first)")
ic = open(icT).read()
head = ic[: ic.index("boundaryField")]          # header + dimensions + internalField
head = re.sub(r'location\s+"[^"]*"', 'location    "0/solid"', head, count=1)

lofc_bf = """boundaryField
{
    outerWall
    {
        // Radiative rejection to the RCCS ultimate heat sink -- a lumped surrogate for
        // the out-of-core radial path (non-conservative for the peak):
        //   q = eps*sigma*(T^4 - Ta^4) + h*(Ta - T),  Ta = 303 K (RCCS, spec Table I.10),
        //   eps = 0.85 (H-451 graphite, Table AIV.3). h = 1e-3 is a NUMERICAL FLOOR only
        //   (the BC forms 1/h, so h=0 is illegal); radiation dominates by ~1e4:1, so the
        //   convective term is negligible -- effectively radiation-only.
        type            externalWallHeatFluxTemperature;
        mode            coefficient;
        h               uniform 1e-3;
        Ta              constant 303;
        emissivity      0.85;
        kappaMethod     solidThermo;
        value           uniform 532;
    }
    solidEnds
    {
        type            zeroGradient;       // adiabatic axial ends (interior of column)
    }
    solid_to_fluid
    {
        type            zeroGradient;       // adiabatic channels: forced cooling lost
    }
}

// ************************************************************************* //
"""
os.makedirs(os.path.join(CASE, "0/solid"), exist_ok=True)
open(os.path.join(CASE, "0/solid/T"), "w").write(head + lofc_bf)
print("[2/3] 0/solid/T : operating IC internalField + LOFC boundaryField")

# ---------------------------------------------------------------------------
# 3. 0/solid/p
# ---------------------------------------------------------------------------
shutil.copyfile(os.path.join(CASE, "0.orig/solid/p"),
                os.path.join(CASE, "0/solid/p"))
print("[3/3] 0/solid/p : copied from 0.orig")
print("LOFC fields ready (solid-only conduction cooldown).")
