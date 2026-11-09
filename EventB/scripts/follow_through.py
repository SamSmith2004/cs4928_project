"""
Change 3 (Follow through): rerun Check 1 and the sensitivity analysis with moved files followed.

The authors' check_file_changes never updates the path it searches for, so tracking stops at a file's first move.
This script walks each project's history in two modes, reading only the name and status of changed files:
  - stale path: reproduces the published behaviour. This is the control: it must give the published commits.
  - followed path: the same walk, with the path updated at each rename.

Rules, as in the frozen analysis: only commits in the authors' refactoring-commit list count, RE duration is the
largest #refactorings, and short means under 10. A class_id ends at a path change when the authors recorded a later
path segment for the same refactoring, so only a refactoring's last segment receives the extra commits.

Outputs: EventB/derived/move_aware_cases.csv, check1_move_aware.csv, sensitivity_move_aware.csv
"""
import subprocess
from collections import defaultdict

import pandas as pd

from common import (CUTOFFS, DERIVED, MOST, REPOS, SHORT, first_commit, lines_at, load_authors, load_rows,
                    project_of, refactoring_index, zenodo)

bcp = load_authors()
HISTORY = {}


def history(project):
    """Commits oldest first, each with its (status, old path, new path) file changes."""
    if project not in HISTORY:
        output = subprocess.run(["git", "-C", str(REPOS / project), "log", "--reverse", "-M", "--name-status",
                                 "--format=%x00%H"], capture_output=True, text=True, errors="replace", check=True).stdout
        commits = []
        for block in output.split("\0")[1:]:
            lines = block.strip().split("\n")
            changes = []
            for line in lines[1:]:
                parts = line.split("\t")
                if line and parts[0][0] == "R":
                    changes.append(("R", parts[1], parts[2]))
                elif line and parts[0] == "A":
                    changes.append(("A", None, parts[1]))
                elif line and parts[0] == "D":
                    changes.append(("D", parts[1], None))
                elif line and len(parts) > 1:
                    changes.append(("M", parts[1], parts[1]))
            commits.append((lines[0], changes))
        HISTORY[project] = commits
    return HISTORY[project]


def walk(project, start_hash, start_path, follow):
    """Commits after start_hash that touch the file, as (hash, path, was_renamed)."""
    commits = history(project)
    start = next(i for i, (commit, _) in enumerate(commits) if commit == start_hash)
    path, touched = start_path, []
    for commit, changes in commits[start + 1:]:
        match = next((c for c in changes if path in (c[1], c[2])), None)
        if match is None:
            continue
        status, _, new = match
        if status == "D":
            break
        touched.append((commit, new, status == "R"))
        if follow:
            path = new
    return touched


def counted(touched, sample, project, start_hash):
    """Keep commits in the authors' list of refactoring commits, after the starting commit."""
    ordered = pd.read_csv(zenodo(sample, project) / "ordered_refactorings.csv")["hash"].drop_duplicates().tolist()
    later = set(ordered[ordered.index(start_hash) + 1:])
    return [t for t in touched if t[0] in later]


rows = load_rows()
corrected = pd.read_csv(DERIVED / "move_aware_values.csv")
corrected = {(c, h): v for c, h, v, f in zip(corrected["class_id"], corrected["hash"], corrected["move_aware_value"],
                                             corrected["flagged"]) if f}

case_results, case_rows = [], {}
for (sample, rq, family, class_id), group in rows.groupby(["sample", "rq", "family", "class_id"], sort=False):
    project, idx = project_of(class_id), refactoring_index(class_id)
    start_hash, start_path = first_commit(sample, project, idx)
    proneness = pd.read_csv(zenodo(sample, project) / "proneness_results.csv")
    published = proneness[proneness["refactoring_id"].str.startswith(f"{idx}_")]
    stale = counted(walk(project, start_hash, start_path, False), sample, project, start_hash)
    followed = counted(walk(project, start_hash, start_path, True), sample, project, start_hash)
    control_ok = [t[0] for t in stale] == published["hash"].tolist()

    segment = lambda c: int(c.rsplit("-", 2)[1])
    last_segment = segment(class_id) == published["class_id"].map(segment).max()
    known = set(published["hash"])
    extra = [t for t in followed if t[0] not in known] if last_segment else []

    duration = int(group["#refactorings"].max())
    series = [(int(r["#refactorings"]), corrected.get((class_id, r["hash"]), r["lcs_remaining_probs"]))
              for _, r in group.iterrows()]
    initial = lines_at(project, start_hash, start_path)
    for offset, (commit, path, _) in enumerate(extra, start=1):
        current = lines_at(project, commit, path)
        series.append((duration + offset, bcp.compute_similarity(initial, current or [])))
    case_rows[class_id] = pd.DataFrame(series, columns=["n", "value"]).sort_values("n")

    case_results.append({"sample": sample, "rq": rq, "family": family, "class_id": class_id, "control_ok": control_ok,
                         "published_commits": len(published), "stale_walk_commits": len(stale),
                         "published_duration": duration, "extra_commits": len(extra),
                         "move_aware_duration": duration + len(extra),
                         "whole_refactoring_duration": len(followed),
                         "file_renamed_later": any(t[2] for t in walk(project, start_hash, start_path, True)),
                         "last_segment": last_segment})

cases = pd.DataFrame(case_results)
cases.to_csv(DERIVED / "move_aware_cases.csv", index=False)

check1 = (cases.groupby(["sample", "rq", "family"], sort=False)
          .agg(n_cases=("class_id", "count"),
               published_short=("published_duration", lambda d: int((d < SHORT).sum())),
               move_aware_short=("move_aware_duration", lambda d: int((d < SHORT).sum())),
               whole_refactoring_short=("whole_refactoring_duration", lambda d: int((d < SHORT).sum())),
               published_median=("published_duration", "median"),
               move_aware_median=("move_aware_duration", "median"),
               largest_move_aware=("move_aware_duration", "max"),
               control_ok=("control_ok", "sum"))
          .reset_index())
verdict = lambda n: "REPRODUCED" if n >= MOST else "NOT REPRODUCED"
check1["published_verdict"] = check1["published_short"].map(verdict)
check1["move_aware_verdict"] = check1["move_aware_short"].map(verdict)
check1.to_csv(DERIVED / "check1_move_aware.csv", index=False)


def duration_with_cutoff(case, cutoff):
    # Same rule as the frozen sensitivity analysis: the first row below the cut-off is counted.
    below = case[case["value"] < cutoff]
    return below["n"].iloc[0] if len(below) else case["n"].max()


sensitivity = []
for cutoff in CUTOFFS:
    for (sample, rq, family), group in cases.groupby(["sample", "rq", "family"], sort=False):
        durations = pd.Series([duration_with_cutoff(case_rows[c], cutoff) for c in group["class_id"]])
        sensitivity.append({"cutoff": f"{cutoff:.0%}", "sample": sample, "rq": rq, "family": family,
                            "n_short": int((durations < SHORT).sum()), "median_duration": durations.median()})
sensitivity = pd.DataFrame(sensitivity)
sensitivity.to_csv(DERIVED / "sensitivity_move_aware.csv", index=False)

print(f"control: {int(cases['control_ok'].sum())}/{len(cases)} cases reproduce the published commits with the stale path")
print(cases[~cases["control_ok"]][["class_id", "published_commits", "stale_walk_commits"]].to_string(index=False))
print()
print(check1.to_string(index=False))
print()
print(cases[cases["extra_commits"] > 0][["class_id", "published_duration", "extra_commits", "move_aware_duration",
                                         "control_ok"]].to_string(index=False))
print()
print(sensitivity.to_string(index=False))
