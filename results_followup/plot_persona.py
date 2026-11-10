#!/usr/bin/env python3
"""Small dot plot: H9 vs H8 vs PersonaAxes (score, plus, minus), from scores.csv."""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SURFACE, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1"
DOT = "#2a78d6"
ENTRIES = ["H9", "H8", "HPersonaAxes"]  # top → bottom
LABEL = {"H9": "H9 · human psychology", "H8": "H8 · persona theory", "HPersonaAxes": "PersonaAxes (outside entry)"}

df = pd.read_csv("scores.csv", dtype={"entry": str}, keep_default_na=False, na_values={c: [""] for c in ["plus_n", "minus_n"]})
z = df[df.rule == "zero"].set_index("entry")
null, ceil = z.loc["null"], z.loc["ceiling"]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.5, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK})

fig, axes = plt.subplots(1, 3, figsize=(11, 3.1), facecolor=SURFACE, sharey=True)
for ax, (col, title) in zip(axes, [("score", "Headline score"), ("plus", "Plus ρ"), ("minus", "Minus ρ")]):
    ax.set_facecolor(SURFACE)
    ax.axvspan(null[f"{col}_lo"], null[f"{col}_hi"], color=GRID, lw=0, zorder=0)
    ax.axvline(0, color=MUTED, lw=1.2, zorder=1)
    ax.axvline(ceil[col], color=INK2, lw=1.2, ls=(0, (4, 3)), zorder=1)
    for i, e in enumerate(reversed(ENTRIES)):
        r = z.loc[e]
        ax.errorbar(r[col], i, xerr=[[r[col] - r[f"{col}_lo"]], [r[f"{col}_hi"] - r[col]]], fmt="o", ms=7,
                    color=DOT, ecolor=DOT, elinewidth=1.6, capsize=0, mec=SURFACE, mew=1.2, zorder=3)
        ax.text(r[f"{col}_hi"] + 0.02, i, f"{r[col]:.2f}", va="center", fontsize=9, color=INK2)
    ax.set_yticks(range(len(ENTRIES)))
    ax.set_yticklabels([LABEL[e] for e in reversed(ENTRIES)])
    ax.set_ylim(-0.6, len(ENTRIES) - 0.4)
    ax.set_xlim(-0.12, 1.0)
    ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
    ax.tick_params(axis="y", length=0)
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.set_title(title, loc="left", fontsize=11, color=INK, pad=26)
    top = len(ENTRIES) - 0.45
    ax.text(0, top, "no information", fontsize=8.3, color=INK2, ha="center", va="bottom", clip_on=False)
    ax.text(ceil[col], top, f"max ≈ {ceil[col]:.2f}", fontsize=8.3, color=INK2, ha="center", va="bottom", clip_on=False)
    ax.set_xlabel("Spearman ρ")
for t in axes[0].get_yticklabels():
    if "outside" in t.get_text():
        t.set_fontweight("bold")
fig.text(0.01, 0.01, "Bars = bootstrap 95% CI. Grey band = 95% range for an entry with no information. "
         "Max = the observed matrix averaged over the three models, used as the prediction.", fontsize=7.8, color=INK2)
fig.tight_layout(rect=(0, 0.06, 1, 1))
fig.savefig("fig_persona.png", dpi=200, facecolor=SURFACE)
print("wrote fig_persona.png")
