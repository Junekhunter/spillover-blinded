#!/usr/bin/env python3
"""Generate the introspection-vs-literature leaderboard figure."""
import csv
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

ROOT = Path(__file__).resolve().parent.parent
LB = ROOT / "logitz_leaderboard.csv"
OUT = ROOT / "introspection_leaderboard.png"

LABELS = {
    "H1": "H1 Spurious correlation",
    "H2": "H2 Simplicity bias",
    "H3": "H3 Causal vs. statistical features",
    "H4": "H4 Subliminal transmission",
    "H5": "H5 Out-of-context reasoning",
    "H6": "H6 Linear/log-linear geometry",
    "H7a_r1": "H7a Anything-goes (r1)",
    "H7a_r2": "H7a Anything-goes (r2)",
    "H7a_r3": "H7a Anything-goes (r3)",
    "H7b_r1": "H7b Pure introspection (r1)",
    "H7b_r2": "H7b Pure introspection (r2)",
    "H7b_r3": "H7b Pure introspection (r3)",
    "H8": "H8 Persona theory",
    "H9": "H9 Human-psychology transfer",
}

def category(h):
    if h.startswith("H7b"):
        return "introspection"
    if h.startswith("H7a"):
        return "anything-goes"
    return "literature"

COLORS = {
    "introspection": "#2E86AB",
    "anything-goes": "#A8DADC",
    "literature":    "#888888",
}

rows = []
with LB.open() as f:
    for row in csv.DictReader(f):
        rows.append({
            "h": row["hypothesis"],
            "plus_rho": float(row["logitz_plus_rho"]),
            "plus_lo":  float(row["logitz_plus_boot_lo"]),
            "plus_hi":  float(row["logitz_plus_boot_hi"]),
            "minus_rho": float(row["logitz_minus_rho"]),
            "minus_lo":  float(row["logitz_minus_boot_lo"]),
            "minus_hi":  float(row["logitz_minus_boot_hi"]),
        })

rows.sort(key=lambda r: r["plus_rho"])
y = list(range(len(rows)))
labels = [LABELS.get(r["h"], r["h"]) for r in rows]
cats = [category(r["h"]) for r in rows]
colors = [COLORS[c] for c in cats]

fig, axes = plt.subplots(1, 2, figsize=(11, 6.2), sharey=True,
                          gridspec_kw={"wspace": 0.08})

for ax, key, title in [
    (axes[0], "plus",  r"$29\times29$  (logitz_plus)"),
    (axes[1], "minus", r"$14\times29$  (logitz_minus)"),
]:
    rho = [r[f"{key}_rho"] for r in rows]
    lo  = [r[f"{key}_rho"] - r[f"{key}_lo"] for r in rows]
    hi  = [r[f"{key}_hi"]  - r[f"{key}_rho"] for r in rows]
    ax.barh(y, rho, color=colors, edgecolor="black", linewidth=0.4, height=0.7)
    ax.errorbar(rho, y, xerr=[lo, hi], fmt="none", ecolor="black",
                elinewidth=0.9, capsize=2.5)
    ax.axvline(0, color="black", linewidth=0.6)
    ax.set_xlim(-0.10, 0.42)
    ax.set_xlabel(r"Spearman $\rho$ vs. observed matrix")
    ax.set_title(title, fontsize=11)
    ax.grid(axis="x", linestyle=":", alpha=0.45)
    ax.set_axisbelow(True)

axes[0].set_yticks(y)
axes[0].set_yticklabels(labels)

handles = [
    mpatches.Patch(facecolor=COLORS["introspection"], edgecolor="black",
                   label="Introspection (H7b)"),
    mpatches.Patch(facecolor=COLORS["anything-goes"], edgecolor="black",
                   label="Anything-goes (H7a)"),
    mpatches.Patch(facecolor=COLORS["literature"], edgecolor="black",
                   label="Literature-grounded"),
]
fig.legend(handles=handles, loc="lower center", ncol=3,
           frameon=False, bbox_to_anchor=(0.5, -0.01))
fig.suptitle("Blinded prediction leaderboard: Claude Opus 4.7 across 14 conditions",
             fontsize=12, y=0.995)
fig.tight_layout(rect=[0, 0.03, 1, 0.97])
fig.savefig(OUT, dpi=180, bbox_inches="tight")
print(f"wrote {OUT}")
