#!/usr/bin/env python3
"""
score.py — score frozen blinded predictions against observed results.

OPTION 1 design, logitz-space normalization (option 1a):
  * Hypotheses predict only logitz_plus and logitz_minus.
  * logitz is ALREADY z-scored per eval upstream (empirical-logit of the
    0-100 judge score, then z-scored against the full reference panel for
    that eval/metric). So logitz is on a unit-variance, per-eval-comparable
    scale before this script ever sees it.
  * logitz board: off-diagonal Spearman, 29 evals, scored directly.
  * theta board (14 bipolar evals): a range-normalized view. theta is an
    AFFINE rescale of logitz, per eval, using the directly-SFT'd diagonal
    poles as the endpoints:
        theta(t -> e) = (logitz(t -> e)        - logitz(e_minus -> e))
                        / (logitz(e_plus -> e) - logitz(e_minus -> e))
    The two endpoints are DIAGONAL cells of the observed logitz matrices
    (e_plus -> e from observed_logitz_plus, e_minus -> e from
    observed_logitz_minus). Both observed AND predicted theta use the SAME
    observed diagonal endpoints, so theta tests nothing the logitz
    prediction did not already commit to -- it is the same prediction
    re-expressed in a cross-eval-comparable unit.

  Why logitz-space (1a) and not score-space (1b): inverting logitz back to a
  0-100 score requires the per-eval panel mu/sigma, and the panel includes
  every fine-tuned model -- i.e. mu/sigma are functions of the observed
  sweep. Normalizing in score space would pull results-derived per-eval
  quantities into the theta definition. Staying in logitz space keeps theta
  a pure affine function of the logitz matrix, normalized by two cells of
  that same matrix. Nothing new leaks in.

  * The logitz board (29 evals) and the theta board (14 bipolar evals) are
    reported SEPARATELY and never averaged. Different N; theta is a per-eval
    affine transform of logitz and carries little independent information.
    logitz is the headline; theta is a supplementary cut.

Run only AFTER ./scripts/freeze.sh has tagged the predictions and the two
observed matrices are present in ./RESULTS/.
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
    """Load a transfer matrix CSV: first column = treatment, rest = eval cols.
    Drops reward-hacking from both axes."""
    df = pd.read_csv(path, index_col=0)
    df = df.loc[[i for i in df.index if i != "reward-hacking"]]
    df = df[[c for c in df.columns if c != "reward-hacking"]]
    return df


def _eval_of(treatment):
    """Treatment row labels are '<eval>-plus' / '<eval>-minus'. Strip the
    pole suffix to recover the eval name, so the diagonal (a fine-tune scored
    on its own eval) can be identified against the bare eval column names."""
    for suffix in ("-plus", "-minus"):
        if treatment.endswith(suffix):
            return treatment[: -len(suffix)]
    return treatment


def off_diagonal_spearman(pred, obs):
    """Spearman over off-diagonal cells common to both matrices.
    Off-diagonal = the treatment's eval != the column eval. The diagonal
    (on-target effect) is excluded; only cross-eval spillover is scored."""
    rows = [r for r in pred.index if r in obs.index]
    cols = [c for c in pred.columns if c in obs.columns]
    pv, ov = [], []
    for r in rows:
        for c in cols:
            if _eval_of(r) == c:
                continue  # diagonal (on-target) — exclude
            p, o = pred.at[r, c], obs.at[r, c]
            if pd.isna(p) or pd.isna(o):
                continue
            pv.append(p)
            ov.append(o)
    if len(pv) < 3:
        return np.nan, len(pv)
    rho, _ = spearmanr(pv, ov)
    return rho, len(pv)


def diagonal_endpoints(obs_plus, obs_minus):
    """For each bipolar eval e, read the directly-SFT'd diagonal poles:
        anchor_hi[e] = observed logitz of ('<e>-plus'  trained) -> e
        anchor_lo[e] = observed logitz of ('<e>-minus' trained) -> e
    Row labels carry the pole suffix ('<e>-plus' / '<e>-minus'); columns are
    bare eval names. Endpoints come straight off the observed matrices'
    diagonals -- no separate observed_anchors.csv to produce or mismatch."""
    hi, lo = {}, {}
    for e in BIPOLAR:
        r_plus, r_minus = f"{e}-plus", f"{e}-minus"
        if r_plus in obs_plus.index and e in obs_plus.columns:
            hi[e] = obs_plus.at[r_plus, e]
        if r_minus in obs_minus.index and e in obs_minus.columns:
            lo[e] = obs_minus.at[r_minus, e]
    return lo, hi


def derive_theta(logitz_df, anchor_lo, anchor_hi):
    """Affine-rescale a logitz matrix into theta, per eval, using the
    observed diagonal endpoints. Bipolar columns only; others -> NaN."""
    out = logitz_df.copy()
    for c in logitz_df.columns:
        if c not in BIPOLAR:
            out[c] = np.nan
            continue
        lo, hi = anchor_lo.get(c), anchor_hi.get(c)
        if lo is None or hi is None or not np.isfinite(hi - lo) or hi == lo:
            out[c] = np.nan
            continue
        out[c] = (logitz_df[c] - lo) / (hi - lo)
    return out[[c for c in logitz_df.columns if c in BIPOLAR]]


def main():
    obs_plus_p = RESULTS / "observed_logitz_plus.csv"
    obs_minus_p = RESULTS / "observed_logitz_minus.csv"
    for p in (obs_plus_p, obs_minus_p):
        if not p.exists():
            sys.exit(f"Missing observed file: {p}\n"
                     f"score.py runs only after freeze + results placement.")

    obs_p = load_matrix(obs_plus_p)
    obs_m = load_matrix(obs_minus_p)

    # theta endpoints = diagonal of the observed matrices
    anchor_lo, anchor_hi = diagonal_endpoints(obs_p, obs_m)
    missing_anchor = [e for e in BIPOLAR
                      if e not in anchor_lo or e not in anchor_hi]
    if missing_anchor:
        print(f"WARNING: no diagonal endpoint for {missing_anchor} -- "
              f"theta will be NaN for these evals.")

    obs_theta_p = derive_theta(obs_p, anchor_lo, anchor_hi)
    obs_theta_m = derive_theta(obs_m, anchor_lo, anchor_hi)

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

        # --- theta board (14 bipolar evals; affine view of same logitz) ---
        pred_theta_p = derive_theta(pred_p, anchor_lo, anchor_hi)
        pred_theta_m = derive_theta(pred_m, anchor_lo, anchor_hi)
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

    print("\n=== LOGITZ leaderboard (29 evals, scored directly) -- PRIMARY ===")
    print(lb.to_string(index=False, float_format=lambda x: f"{x:+.3f}"))
    print("\n=== THETA leaderboard (range-normalized, 14 bipolar evals) -- SUPPLEMENTARY ===")
    print("NOTE: logitz is already z-scored per eval upstream. theta is a")
    print("per-eval AFFINE transform of logitz normalized by the observed")
    print("diagonal poles. It is NOT independent of the logitz board and")
    print("MUST NOT be averaged with it (different N, non-independent).")
    print(tb.to_string(index=False, float_format=lambda x: f"{x:+.3f}"))

    lb.to_csv(ROOT / "logitz_leaderboard.csv", index=False)
    tb.to_csv(ROOT / "theta_leaderboard.csv", index=False)
    print(f"\nWrote logitz_leaderboard.csv and theta_leaderboard.csv to {ROOT}")


if __name__ == "__main__":
    main()
