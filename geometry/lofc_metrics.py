#!/usr/bin/env python3
"""
LOFC transient metrics. Run from the case directory after run_lofc.sh has solved
and reconstructed. Produces (all under runs/lofc/):
  * peak_trajectory.csv : t [s], peak fuel T [C]        (parsed from the solver log)
  * peak.txt            : passive quasi-steady peak + location + margin to TRISO
  * config.txt          : the LOFC conditions, for the results ledger
and prints a summary (captured into runs/lofc/summary.txt by the runner).
"""
import os, re, math, glob

CASE = os.getcwd()
OUT = os.path.join(CASE, "runs/lofc"); os.makedirs(OUT, exist_ok=True)
TRISO = 1600.0
K = 273.15


def decay_q_at(t):
    """Decay q''' [W/m^3] at time t, read from constant/solid/heatSource. Handles the
    Function1 table form (qVol table ((t0 q0)...)) and the bare-scalar form."""
    hs = os.path.join(CASE, "constant/solid/heatSource")
    if not os.path.isfile(hs):
        return 0.0
    txt = open(hs).read()
    mt = re.search(r"qVol\s+table\s*\((.*)\)\s*;", txt, re.S)
    if mt:
        pts = sorted(tuple(float(v) for v in p.split())
                     for p in re.findall(r"\(\s*([0-9.eE+-]+\s+[0-9.eE+-]+)\s*\)", mt.group(1)))
        if not pts:
            return 0.0
        if t <= pts[0][0]:
            return pts[0][1]
        if t >= pts[-1][0]:
            return pts[-1][1]
        for (t0, q0), (t1, q1) in zip(pts, pts[1:]):
            if t0 <= t <= t1:
                return q0 + (q1 - q0) * (t - t0) / (t1 - t0)
    ms = re.search(r"qVol\s+([0-9.eE+-]+)\s*;", txt)
    return float(ms.group(1)) if ms else 0.0

# ---------------------------------------------------------------------------
# trajectory from the solver log:  peak(t) = max(T) at each time
# ---------------------------------------------------------------------------
log = open(os.path.join(CASE, "log.lofc.solve")).read()
traj = []            # (t, peakC)
t_cur = None
for line in log.splitlines():
    m = re.match(r"\s*Time = ([0-9.eE+-]+)", line)
    if m:
        t_cur = float(m.group(1)); continue
    m = re.search(r"Min/max T:\s*([0-9.eE+-]+)\s+([0-9.eE+-]+)", line)
    if m and t_cur is not None:
        traj.append((t_cur, float(m.group(2)) - K))
# collapse to one (last) peak per time
seen = {}
for t, p in traj:
    seen[t] = p
traj = sorted(seen.items())

with open(os.path.join(OUT, "peak_trajectory.csv"), "w") as f:
    f.write("t_s,peak_fuel_C\n")
    for t, p in traj:
        f.write("%.3f,%.4f\n" % (t, p))

# ---------------------------------------------------------------------------
# cooldown time-constant tau (first-order): T(t) = Tinf + (T0-Tinf) exp(-t/tau)
# ---------------------------------------------------------------------------
tau_63 = tau_fit = float("nan")
T0 = Tinf = drop = float("nan")
if len(traj) >= 3:
    T0 = traj[0][1]; Tinf = traj[-1][1]; drop = T0 - Tinf
    if abs(drop) > 1.0:
        # tau_63: time to cover 63.2% of the total drop
        target = T0 - 0.632 * drop
        for (t1, p1), (t2, p2) in zip(traj, traj[1:]):
            if (p1 - target) * (p2 - target) <= 0 and p1 != p2:
                tau_63 = t1 + (target - p1) * (t2 - t1) / (p2 - p1); break
        # log-linear fit of ln((T-Tinf)/drop) = -t/tau over the resolved decay
        xs, ys = [], []
        for t, p in traj:
            frac = (p - Tinf) / drop
            if frac > 0.02 and t > 0:
                xs.append(t); ys.append(math.log(frac))
        if len(xs) >= 3:
            n = len(xs); sx = sum(xs); sy = sum(ys)
            sxx = sum(x * x for x in xs); sxy = sum(x * y for x, y in zip(xs, ys))
            slope = (n * sxy - sx * sy) / (n * sxx - sx * sx)
            if slope < 0:
                tau_fit = -1.0 / slope

# ---------------------------------------------------------------------------
# final field: peak fuel T + location (r,z), and outer-surface T range
# ---------------------------------------------------------------------------
def latest_time():
    ts = []
    for d in glob.glob(os.path.join(CASE, "[0-9]*")):
        b = os.path.basename(d)
        if os.path.isdir(d) and re.fullmatch(r"[0-9.eE+-]+", b) and os.path.isfile(os.path.join(d, "solid/T")):
            try: ts.append((float(b), b))
            except ValueError: pass
    return max(ts)[1] if ts else None

def read_internal(path):
    txt = open(path).read()
    m = re.search(r"internalField\s+nonuniform[^(]*\((.*?)\)\s*;", txt, re.S)
    if m:
        return [float(x) for x in m.group(1).split()], txt
    m = re.search(r"internalField\s+uniform\s+([0-9.eE+-]+)\s*;", txt)
    return None, txt

def read_vec_internal(path):
    txt = open(path).read()
    m = re.search(r"internalField\s+nonuniform[^(]*\(\s*(.*?)\)\s*;", txt, re.S)
    body = m.group(1)
    return [tuple(float(v) for v in tok.strip("() ").split())
            for tok in re.findall(r"\([^()]*\)", body)]

lt = latest_time()
peakC = pr = pz = float("nan")
surf_lo = surf_hi = tmeanC = float("nan")
ebal = float("nan")
Tfield = None
if lt:
    Tfield, ttxt = read_internal(os.path.join(CASE, lt, "solid/T"))
    C = read_vec_internal(os.path.join(CASE, lt, "solid/C"))
    if Tfield and C and len(Tfield) == len(C):
        i = max(range(len(Tfield)), key=lambda k: Tfield[k])
        peakC = Tfield[i] - K
        x, y, z = C[i]; pr = math.hypot(x, y); pz = z
        # block is near-isothermal at the passive quasi-steady: the outer-surface
        # temperature is bracketed by the field min (near-wall) and the mean.
        surf_lo = min(Tfield) - K            # ~ surface (near-wall) temperature
        tmeanC = sum(Tfield) / len(Tfield) - K
        surf_hi = tmeanC
        # energy-balance certification: decay power in vs surface rad+conv out.
        vpath = os.path.join(CASE, lt, "solid/V")       # written by writeCellVolumes
        czpath = os.path.join(CASE, "constant/solid/polyMesh/cellZones")
        if os.path.isfile(vpath) and os.path.isfile(czpath):
            Vc, _ = read_internal(vpath)
            m = re.search(r"fuel.*?cellLabels\s+List<label>\s*\d+\s*\((.*?)\)",
                          open(czpath).read(), re.S)
            if Vc and m:
                ids = [int(x) for x in m.group(1).split()]
                Vfuel = sum(Vc[k] for k in ids)
                qdec = decay_q_at(float(lt))     # decay q''' at the final time [W/m^3]
                Qin = qdec * Vfuel
                zs = [c[2] for c in C]
                A = 6.0 * (0.36 / math.sqrt(3.0)) * (max(zs) - min(zs))  # hex perimeter * L
                sig, eps, Ta = 5.670374e-8, 0.85, 303.0
                Ts = min(Tfield)                 # near-wall (outer) surface temperature [K]
                Qout = eps * sig * (Ts ** 4 - Ta ** 4) * A               # radiation to RCCS
                ebal = Qout / Qin if Qin else float("nan")

# peak fuel over space AND time (figure of merit #1). For a conduction cooldown that
# over-cools (RCCS sink at the block surface), this is the t=0 IC, not the final field --
# so the TRISO margin must be taken to the max-over-time peak, not the quasi-steady peak.
tpeak_max = max((p for _, p in traj), default=peakC)

# ---------------------------------------------------------------------------
# write products + print summary
# ---------------------------------------------------------------------------
with open(os.path.join(OUT, "peak.txt"), "w") as f:
    f.write("peak_fuel_max_over_time_C %.2f\n" % tpeak_max)
    f.write("quasi_steady_final_peak_fuel_C %.2f\n" % peakC)
    f.write("peak_location_r_mm %.1f\n" % (pr * 1000))
    f.write("peak_location_z_mm %.1f\n" % (pz * 1000))
    f.write("block_mean_T_C %.2f\n" % tmeanC)
    f.write("outer_surface_T_C %.2f\n" % surf_lo)
    f.write("TRISO_margin_C %.2f  (to max-over-time peak)\n" % (TRISO - tpeak_max))
    f.write("cooldown_tau_63_s %.1f\n" % tau_63)
    f.write("cooldown_tau_fit_s %.1f\n" % tau_fit)
    f.write("energy_balance_Qout_over_Qin %.3f\n" % ebal)
    f.write("final_time_s %s\n" % (lt or "n/a"))

with open(os.path.join(OUT, "config.txt"), "w") as f:
    f.write("variant lofc_conduction_cooldown\n")
    f.write("model solid-only: conduction + decay heat q'''(t) + radiative RCCS rejection\n")
    f.write("q_decay ANS-5.1-family q'''(t) table (heatSource); q_op 24.83 (avg) or 46.05 (peak) MW/m3 fuel-local\n")
    f.write("outer_wall externalWallHeatFluxTemperature radiation to RCCS Ta=303K emissivity=0.85\n")
    f.write("channels adiabatic (forced cooling lost; He stagnant/dropped)\n")
    f.write("axial_ends adiabatic (interior of column)\n")
    f.write("IC normal-operation steady field (Phase-0)\n")
    f.write("solver chtMultiRegionTFoam, Euler ddt, %s-way parallel\n" % 16)

print("LOFC transient summary")
print("  peak fuel (max over time) : %.1f C  (margin to TRISO 1600 C = %.0f C)"
      % (tpeak_max, TRISO - tpeak_max))
print("  IC (t=0) peak fuel        : %.1f C" % (T0 if not math.isnan(T0) else float('nan')))
print("  final quasi-steady peak   : %.1f C  (at t=%s s)" % (peakC, lt))
print("  peak location (final)     : r = %.0f mm, z = %.0f mm" % (pr * 1000, pz * 1000))
print("  block mean / surface T    : %.0f C / %.0f C  (near-isothermal)" % (tmeanC, surf_lo))
print("  cooldown time-constant    : tau_63 = %.0f s (%.1f min), fit = %.0f s (%.1f min)"
      % (tau_63, tau_63 / 60, tau_fit, tau_fit / 60))
print("  energy balance Qout/Qin   : %.3f  (decay heat in = outer radiation out)" % ebal)
print("  trajectory points         : %d  (0 -> %s s)" % (len(traj), lt))
