"""
Check 2: recalculate `lcs_remaining_probs` with the authors' own function `get_lcs_probabilities`
(Scripts/02_get_bcp.py:167) and compare every value with the published CSV (match = within ±0.02).

The authors' files are not edited. Two path repairs are made at runtime (see M2/log.md):
  - utility.DATA_PATH (hard-coded Windows folder) points at M2/raw/check2_logs (not committed), where their logs go
  - Windows "\" separators in class_change_history paths become "/", so their path matching works on Linux
"""
import argparse
import importlib.util
import logging
import sys
from pathlib import Path

import pandas as pd

TOLERANCE = 0.02
MATCHES = 10
MISMATCHES = 3

ZENODO = Path("M2/inputs/zenodo/Data/change_proneness_data")
REPOS = Path("M2/repos")
LOGS = Path("M2/raw/check2_logs")
LOGS.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, "Scripts")
import components.utility as utility  
utility.DATA_PATH = LOGS.resolve()
spec = importlib.util.spec_from_file_location("get_bcp", "Scripts/02_get_bcp.py")
bcp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bcp)


def project_of(class_id):
    return class_id.rsplit("-", 2)[0].split("_", 3)[3]


def recalculate(project, idx, cache={}):
    #Run the authors' LCS calculation for one refactoring (all of its classes), exactly as handle_repository does
    if (project, idx) in cache:
        return cache[(project, idx)]
    base = ZENODO / project
    ordered = pd.read_csv(base / "ordered_refactorings.csv")
    proneness = pd.read_csv(base / "proneness_results.csv")

    first = ordered[ordered["id"] == idx].iloc[0]
    rows = proneness[proneness["refactoring_id"].str.startswith(f"{idx}_")]
    subsequent = rows.set_index("hash")["class_id"].to_dict()
    history = pd.read_csv(base / "class_change_history" / rows["refactoring_id"].tolist()[-1])
    history["full-path"] = history["full-path"].str.replace("\\", "/")  # path repair: Windows separators

    logger = logging.getLogger(project)
    if not logger.handlers:
        logger.addHandler(logging.FileHandler(LOGS / f"{project}.log"))
        logger.setLevel(logging.INFO)

    values = bcp.get_lcs_probabilities(refactoring_hash=first["hash"], repo_path=str(REPOS / project),
                                       refactoring_filepath=first["filepath"], subsequent_hashes_dict=subsequent,
                                       subsequent_class_history_df=history, repo_logger=logger)
    note = "" if len(values) == len(subsequent) else f"{len(values)} values for {len(subsequent)} commits"
    cache[(project, idx)] = (dict(zip(subsequent, values)), note)
    return cache[(project, idx)]


parser = argparse.ArgumentParser()
parser.add_argument("--case", help="pilot: run a single class_id")
args = parser.parse_args()

sample = pd.read_csv("M2/inputs/sample_cases.csv")
if args.case:
    sample = sample[sample["class_id"] == args.case]
paper = pd.read_csv("M2/raw/sample_rows.csv")

values = []
for _, case in sample.iterrows():
    project, idx = project_of(case["class_id"]), int(case["class_id"].split("_")[0])
    print(f"{case['rq']} {case['family']} {case['class_id']}", flush=True)
    try:
        ours, note = recalculate(project, idx)
    except Exception as e:  # could not recalculate: counts as neither match nor mismatch
        ours, note = {}, f"not recalculated: {type(e).__name__}: {e}"
    for _, row in paper[paper["class_id"] == case["class_id"]].sort_values("#refactorings").iterrows():
        our_value = ours.get(row["hash"])
        values.append({"rq": case["rq"], "family": case["family"], "class_id": case["class_id"],
                       "#refactorings": row["#refactorings"], "hash": row["hash"],
                       "paper_value": row["lcs_remaining_probs"], "our_value": our_value,
                       "diff": None if our_value is None else abs(our_value - row["lcs_remaining_probs"]),
                       "note": note})

values = pd.DataFrame(values)
values["match"] = values["diff"] <= TOLERANCE
values.to_csv(f"M2/raw/check2_{'pilot_' if args.case else ''}values.csv", index=False)
print()
print(values[["class_id", "#refactorings", "paper_value", "our_value", "match"]].to_string(index=False))
if args.case:
    sys.exit()

cases = (values.groupby(["rq", "family", "class_id"], sort=False)
         .agg(rows=("hash", "count"), rows_matching=("match", "sum"),
              recalculated=("our_value", lambda v: v.notna().all()), note=("note", "first"))
         .reset_index())
cases["status"] = cases.apply(lambda c: "not recalculated" if not c["recalculated"]
                              else "match" if c["rows_matching"] == c["rows"] else "mismatch", axis=1)
cases.to_csv("M2/derived/check2_cases.csv", index=False)


def verdict(group):
    if (group["status"] == "match").sum() >= MATCHES:
        return "REPRODUCED"
    if (group["status"] == "mismatch").sum() >= MISMATCHES:
        return "NOT REPRODUCED"
    return "INCONCLUSIVE / BLOCKED"


summary = (cases.groupby(["rq", "family"])
           .apply(lambda g: pd.Series({"match": int((g["status"] == "match").sum()),
                                       "mismatch": int((g["status"] == "mismatch").sum()),
                                       "not_recalculated": int((g["status"] == "not recalculated").sum()),
                                       "verdict": verdict(g)}), include_groups=False)
           .reset_index())
summary.to_csv("M2/derived/check2_summary.csv", index=False)
print()
print(summary.to_string(index=False))
