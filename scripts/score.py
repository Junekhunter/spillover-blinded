#!/usr/bin/env python3
"""
score.py — score frozen blinded predictions against observed results.

OPTION 1 design:
  * Hypotheses predict only logitz_plus and logitz_minus.
  * logitz is scored directly (off-diagonal Spearman), 29 evals.
  * theta is a DERIVED, range-normalized view, 14 bipolar evals only.
        theta(p) = (s(p) - anchor_lo_obs(p)) / (anchor_hi_obs(p) - anchor_lo_obs(p))
    BOTH observed theta and predicted theta use the SAME observed anchors
    (the directly-SFT'd diagonal poles). theta therefore tests nothing the
    logitz prediction did not already commit to — it is the same prediction
    re-expressed in a cross-eval-comparable unit. No hypothesis predicts
    ranges; the anchors come from RESULTS for both sides.

  * The logitz board (29 evals) and the theta board (14 evals) are reported
    SEPARATELY and are never averaged into one number. Different N, and
    theta is not independent of logitz.

Run only AFTER ./scripts/freeze.sh has tagged the predictions and observed
matrices are present in ./RESULTS/.
"""
import sys
import pathlib
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = pathlib.Path(__file__).resolve().parent.parent
PRED = ROOT / "predictions"
RESULTS = ROOT / "RESULTS"

BIPOLAR = [
    "agreeableness", "certainty", "cooperation", "effort", "harm-elaboration",
    "harm-refusal", "honest-humble", "neuroticism", "power-seeking",
    "resource-acquisition", "self-preservation", "spending-advice",
    "spitefulness", "trust-in-user-intentions",
]


def load_matrix(path):
    """Load a transfer matrix CSV: first column = treatment, rest = eval cols."""
    df = pd.read_csv(path, index_col=0)
    df = df.loc[[i for i in df.index if i != "reward-hacking"]]
    df = df[[c for c in df.columns if c != "reward-hacking"]]
    return df


def off_diagonal_spearman(pred, obs):
    """Spearman over off-diagonal cells common to both matrices."""
    rows = [r for r in pred.index if r in obs.index]
    cols = [c for c in pred.columns if c in obs.columns]
    pv, ov = [], []
    for r in rows:
        for c in cols:
            if r == c:
                continue  # off-diagonal only
            p, o = pred.at[r, c], obs.at[r, c]
            if pd.isna(p) or pd.isna(o):
                continue
            pv.append(p)
            ov.append(o)
    if len(pv) < 3:
        return np.nan, len(pv)
    rho, _ = spearmanr(pv, ov)
    return rho, len(pv)


def logitz_to_score(logitz):
    """Map logit-space movement to score space (0-100). Logistic around 50."""
    return 100.0 / (1.0 + np.exp(-logitz))


def derive_theta(score_df, anchor_lo, anchor_hi):
    """Range-normalize a score matrix using OBSERVED anchors. Bipolar cols only."""
    out = score_df.copy()
    for c in score_df.columns:
        if c not in BIPOLAR:
            out[c] = np.nan
            continue
        lo, hi = anchor_lo.get(c), anchor_hi.get(c)
        if lo is None or hi is None or hi == lo:
            out[c] = np.nan
            continue
        out[c] = (score_df[c] - lo) / (hi - lo)
    return out[[c for c in score_df.columns if c in BIPOLAR]]


def main():
    obs_plus = RESULTS / "observed_logitz_plus.csv"
    obs_minus = RESULTS / "observed_logitz_minus.csv"
    anchors_path = RESULTS / "observed_anchors.csv"
    for p in (obs_plus, obs_minus, anchors_path):
        if not p.exists():
            sys.exit(f"Missing observed file: {p}\n"
                     f"score.py runs only after freeze + results placement.")

    obs_p = load_matrix(obs_plus)
    obs_m = load_matrix(obs_minus)

    # observed_anchors.csv: columns = eval, anchor_lo, anchor_hi (the
    # directly-SFT'd minus/plus diagonal poles, in score space).
    anc = pd.read_csv(anchors_path)
    anchor_lo = dict(zip(anc["eval"], anc["anchor_lo"]))
    anchor_hi = dict(zip(anc["eval"], anc["anchor_hi"]))

    obs_theta_p = derive_theta(logitz_to_score(obs_p), anchor_lo, anchor_hi)
    obs_theta_m = derive_theta(logitz_to_score(obs_m), anchor_lo, anchor_hi)

    logitz_board, theta_board = [], []

    for d in sorted(PRED.iterdir()):
        if not d.is_dir():
            continue
        H = d.name
        fp, fm = d / "logitz_plus.csv", d / "logitz_minus.csv"
        if not (fp.exists() and fm.exists()):
            print(f"SKIP {H}: missing matrices")
            continue
        pred_p, pred_m = load_matrix(fp), load_matrix(fm)

        # --- logitz board (29 evals, scored directly) ---
        rp, np_ = off_diagonal_spearman(pred_p, obs_p)
        rm, nm_ = off_diagonal_spearman(pred_m, obs_m)
        logitz_board.append({
            "hypothesis": H,
            "logitz_plus_rho": rp, "n_plus": np_,
            "logitz_minus_rho": rm, "n_minus": nm_,
            "logitz_mean_rho": np.nanmean([rp, rm]),
        })

        # --- theta board (14 bipolar evals; DERIVED from same logitz) ---
        pred_theta_p = derive_theta(logitz_to_score(pred_p), anchor_lo, anchor_hi)
        pred_theta_m = derive_theta(logitz_to_score(pred_m), anchor_lo, anchor_hi)
        tp, tnp = off_diagonal_spearman(pred_theta_p, obs_theta_p)
        tm, tnm = off_diagonal_spearman(pred_theta_m, obs_theta_m)
        theta_board.append({
            "hypothesis": H,
            "theta_plus_rho": tp, "n_plus": tnp,
            "theta_minus_rho": tm, "n_minus": tnm,
            "theta_mean_rho": np.nanmean([tp, tm]),
        })

    lb = pd.DataFrame(logitz_board).sort_values("logitz_mean_rho", ascending=False)
    tb = pd.DataFrame(theta_board).sort_values("theta_mean_rho", ascending=False)

    print("\n=== LOGITZ leaderboard (absolute movement, 29 evals) — PRIMARY ===")
    print(lb.to_string(index=False, float_format=lambda x: f"{x:+.3f}"))
    print("\n=== THETA leaderboard (range-normalized, 14 bipolar evals) — DERIVED ===")
    print("NOTE: theta is a re-expression of the logitz prediction, normalized")
    print("by OBSERVED anchors. It is NOT independent of the logitz board and")
    print("MUST NOT be averaged with it (different N, non-independent).")
    print(tb.to_string(index=False, float_format=lambda x: f"{x:+.3f}"))

    lb.to_csv(ROOT / "logitz_leaderboard.csv", index=False)
    tb.to_csv(ROOT / "theta_leaderboard.csv", index=False)
    print(f"\nWrote logitz_leaderboard.csv and theta_leaderboard.csv to {ROOT}")


if __name__ == "__main__":
    main()
