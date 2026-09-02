#!/usr/bin/env python3
"""Plot the LOFC full-block cooldown: peak fuel temperature vs time, with the
first-order fit and the passive quasi-steady. Reads runs/lofc/. Run from the case
dir with a matplotlib-enabled Python."""
import os, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "runs/lofc"
t, p = [], []
with open(os.path.join(OUT, "peak_trajectory.csv")) as f:
    next(f)
    for line in f:
        a, b = line.split(","); t.append(float(a)); p.append(float(b))

meta = {}
with open(os.path.join(OUT, "peak.txt")) as f:
    for line in f:
        k, v = line.split(None, 1); meta[k] = float(v) if v.strip().replace(".", "").replace("-", "").isdigit() else v.strip()

T0, Tinf = p[0], meta["passive_quasi_steady_peak_fuel_C"]
tau = meta["cooldown_tau_fit_s"]
tmin = [x / 60.0 for x in t]
fit = [Tinf + (T0 - Tinf) * math.exp(-x / tau) for x in t]

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(tmin, p, "o", ms=3, color="#c0392b", label="CFD peak fuel T(t)")
ax.plot(tmin, fit, "-", lw=1.5, color="#2c3e50",
        label=r"first-order fit, $\tau$ = %.0f s (%.0f min)" % (tau, tau / 60))
ax.axhline(Tinf, ls="--", lw=1, color="#7f8c8d")
ax.axhline(1600, ls=":", lw=1.2, color="#8e44ad")
ax.annotate("passive quasi-steady peak %.0f C" % Tinf, (tmin[-1], Tinf),
            ha="right", va="bottom", fontsize=9, color="#7f8c8d")
ax.annotate("TRISO limit 1600 C (margin %.0f C)" % meta["TRISO_margin_C"],
            (tmin[-1], 1600), ha="right", va="bottom", fontsize=9, color="#8e44ad")
ax.annotate("t=0: normal operation (peak %.0f C),\nforced cooling lost" % T0,
            (0, T0), xytext=(tmin[-1] * 0.28, T0 - 25), fontsize=9,
            arrowprops=dict(arrowstyle="->", color="#c0392b"))
ax.set_xlabel("time after loss of forced cooling [min]")
ax.set_ylabel("peak fuel temperature [C]")
ax.set_title("Full-block LOFC: decay-heat cooldown to passive quasi-steady\n"
             "(solid conduction + radiating/NC outer wall, decay q''' = 0.21 MW/m3)",
             fontsize=11)
ax.set_ylim(min(Tinf, min(p)) - 20, 1650)
ax.grid(alpha=0.3); ax.legend(loc="center right", fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "lofc_cooldown.png"), dpi=130)
print("wrote", os.path.join(OUT, "lofc_cooldown.png"))
