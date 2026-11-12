#!/usr/bin/env python3
"""Dot plots of every entry under both blank-cell rules, from scores.csv.

fig_score.png       — headline score (mean of plus and minus rho)
fig_plus_minus.png  — plus and minus rho side by side
Entries are sorted by the intended rule (blanks = 0).
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SURFACE, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1"
ZERO_C, DROP_C = "#2a78d6", "#eb6834"  # categorical slots 1, 2
OFF = 0.17

df = pd.read_csv("scores.csv", dtype={"entry": str}, keep_default_na=False, na_values={c: [""] for c in ["plus_n", "minus_n"]})
ent = df[~df.entry.isin(["null", "ceiling"])]
zero = ent[ent.rule == "zero"].set_index("entry")
drop = ent[ent.rule == "dropped"].set_index("entry")
null = df[df.entry == "null"].iloc[0]
ceil = df[df.entry == "ceiling"].iloc[0]
order = zero.sort_values("score", ascending=True).index  # bottom → top
y = {e: i for i, e in enumerate(order)}

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.5, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK})


def panel(ax, col, title, labels=True):
    ax.set_facecolor(SURFACE)
    ax.axvspan(null[f"{col}_lo"], null[f"{col}_hi"], color=GRID, zorder=0, lw=0)
    ax.axvline(0, color=MUTED, lw=1.2, zorder=1)
    ax.axvline(ceil[col], color=INK2, lw=1.2, ls=(0, (4, 3)), zorder=1)
    for e in order:
        for frame, dy, c, mk in [(zero, OFF, ZERO_C, "o"), (drop, -OFF, DROP_C, "D")]:
            r = frame.loc[e]
            ax.errorbar(r[col], y[e] + dy, xerr=[[r[col] - r[f"{col}_lo"]], [r[f"{col}_hi"] - r[col]]],
                        fmt=mk, ms=6.5 if mk == "o" else 5.5, color=c, ecolor=c, elinewidth=1.4,
                        capsize=0, mec=SURFACE, mew=1.2, zorder=3)
    ax.set_yticks(range(len(order)))
    if labels:
        ax.set_yticklabels([zero.loc[e, "label"] for e in order])
        for t, e in zip(ax.get_yticklabels(), order):
            if "outside" in zero.loc[e, "label"]:
                t.set_fontweight("bold")
    ax.set_ylim(-0.7, len(order) - 0.3)
    ax.set_xlim(-0.12, 1.0)
    ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
    ax.tick_params(axis="y", length=0)
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.set_title(title, loc="left", fontsize=11.5, color=INK, pad=34)
    top = len(order) - 0.25
    ax.text(0, top, "wild guessing\n(no information)", fontsize=8.5, color=INK2, va="bottom", ha="center", clip_on=False)
    ax.text(ceil[col], top, f"max possible\n≈ {ceil[col]:.2f}", fontsize=8.5, color=INK2, va="bottom", ha="center", clip_on=False)


def legend(fig):
    h = [plt.Line2D([], [], marker="o", color=ZERO_C, ls="", ms=7, label="Blank cells scored as 0 (intended)"),
         plt.Line2D([], [], marker="D", color=DROP_C, ls="", ms=6, label="Blank cells dropped (as scored)")]
    fig.legend(handles=h, loc="upper left", bbox_to_anchor=(0.01, 0.995), ncol=2, frameon=False, fontsize=9.5)


NOTE = ("Spearman ρ vs observed SFT spillover (Qwen3.5-9B, Qwen3.5-9B-Base, Nemotron-3-Super-120B pooled); bars = 95% CI, bootstrap over whole fine-tuning runs.\n"
        "Only Quine left cells blank, so it is the only entry the rule moves. Grey band = wild guessing (2000 random shuffles of H9's predictions).\n"
        "Max possible = the observed matrix averaged over the three models, used as the prediction (one shared matrix can't match all three exactly).")

fig, ax = plt.subplots(figsize=(8.6, 7.4), facecolor=SURFACE)
panel(ax, "score", "Headline score\n(mean of plus and minus ρ)")
ax.set_xlabel("Spearman ρ")
legend(fig)
fig.text(0.01, 0.005, NOTE, fontsize=7.6, color=INK2, va="bottom")
fig.tight_layout(rect=(0, 0.085, 1, 0.965))
fig.savefig("fig_score.png", dpi=200, facecolor=SURFACE)

fig, (a1, a2) = plt.subplots(1, 2, figsize=(12.4, 7.4), facecolor=SURFACE, sharey=True)
panel(a1, "plus", f"Plus ρ  ({int(zero.plus_n.iloc[0]):,} cells; Quine {int(drop.loc['Hquine_nomech','plus_n'])} if dropped)")
panel(a2, "minus", f"Minus ρ  ({int(zero.minus_n.iloc[0])} cells; Quine {int(drop.loc['Hquine_nomech','minus_n'])} if dropped)", labels=False)
for a in (a1, a2):
    a.set_xlabel("Spearman ρ")
legend(fig)
fig.text(0.01, 0.005, NOTE, fontsize=7.6, color=INK2, va="bottom")
fig.tight_layout(rect=(0, 0.075, 1, 0.965))
fig.savefig("fig_plus_minus.png", dpi=200, facecolor=SURFACE)
print("wrote fig_score.png, fig_plus_minus.png")
