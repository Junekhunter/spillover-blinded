"""Build webapp/baselines.json: the host's H1–H9 specs + their frozen predictions.

Run by stage.sh at deploy time, from a checkout that has the history. Specs
come from the commit that last held hypotheses/ and predictions from the
freeze commit, so the server shows exactly what was locked. The output is
NOT committed: predictions are only served to participants who have
submitted their own (then locked) entry.

Usage: python webapp/build_baselines.py <out.json>
"""
import csv
import io
import json
import re
import subprocess
import sys

SPEC_COMMIT = "1fa4674"   # "Add H6; rename specs to H#.md; ..." — last commit with hypotheses/H*.md
FREEZE_COMMIT = "2b41eda"  # "Freeze blinded predictions: frozen-20260520T134011Z"

GROUPS = [
    ("H1", ["H1"]), ("H2", ["H2"]), ("H3", ["H3"]), ("H4", ["H4"]), ("H5", ["H5"]), ("H6", ["H6"]),
    ("H7a", ["H7a_r1", "H7a_r2", "H7a_r3"]), ("H7b", ["H7b_r1", "H7b_r2", "H7b_r3"]),
    ("H8", ["H8"]), ("H9", ["H9"]),
]
HEADERS = ["Statement of the hypothesis", "Definitions", "Literature", "Operationalization",
           "Prerequisites for testing", "Falsifiers"]


def git_show(commit, path):
    r = subprocess.run(["git", "show", f"{commit}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def title_of(spec):
    first = next((l for l in spec.splitlines() if l.strip()), "")
    t = re.sub(r"^#+\s*", "", first).strip()
    t = re.sub(r"^(Hypothes[ie]s\s*\d*\s*[:.]\s*|Hypothesis\s*:\s*)", "", t, flags=re.I).strip()
    return t[:120]


def to_markdown(spec):
    """Plain-text specs use bare header lines; promote them so they render as headings."""
    if re.search(r"^#{1,3} ", spec, re.M):
        return spec
    out = []
    for i, line in enumerate(spec.splitlines()):
        s = line.strip()
        if i == 0 and s:
            out.append("# " + s)
        elif any(s.lower().startswith(h.lower()) and len(s) < len(h) + 40 for h in HEADERS):
            out += ["", "## " + s, ""]
        else:
            out.append(line)
    return "\n".join(out)


def check_matrix(text, n_rows):
    rows = list(csv.reader(io.StringIO(text.strip())))
    assert len(rows) == n_rows + 1 and all(len(r) == 30 for r in rows), "bad matrix shape"


def main(out_path):
    examples = []
    for gid, members in GROUPS:
        spec = git_show(SPEC_COMMIT, f"hypotheses/{members[0]}.md")
        if spec is None:
            sys.exit(f"missing spec for {members[0]} at {SPEC_COMMIT}")
        runs = []
        for m in members:
            files = {k: git_show(FREEZE_COMMIT, f"predictions/{m}/{f}") for k, f in
                     (("plus_csv", "logitz_plus.csv"), ("minus_csv", "logitz_minus.csv"),
                      ("method_md", "method.md"), ("falsifiers_md", "falsifiers.md"))}
            if not files["plus_csv"] or not files["minus_csv"]:
                sys.exit(f"missing frozen predictions for {m} at {FREEZE_COMMIT}")
            check_matrix(files["plus_csv"], 29)
            check_matrix(files["minus_csv"], 14)
            runs.append({"id": m, **files})
        examples.append({"id": gid, "title": title_of(spec), "spec_md": to_markdown(spec).strip() + "\n",
                         "spec_text": spec, "runs": runs})
    json.dump({"spec_commit": SPEC_COMMIT, "freeze_commit": FREEZE_COMMIT, "examples": examples},
              open(out_path, "w"), indent=1)
    print(f"wrote {out_path}: {len(examples)} examples, {sum(len(e['runs']) for e in examples)} frozen runs")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "webapp/baselines.json")
