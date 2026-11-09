"""
Change 2 (Measure): recalculate similarity by reading each file directly from git, in a separate column.
The authors' compute_similarity is reused; only the way the content is read differs.

Control: the same method is applied to every frozen row. Every non-flagged row must still match the published
value within the frozen ±0.02, otherwise the new values could not be trusted.

Output: EventB/derived/move_aware_values.csv
"""
import pandas as pd

from common import DERIVED, first_commit, lines_at, load_authors, load_values, project_of, recorded_paths, refactoring_index

TOLERANCE = 0.02
bcp = load_authors()
values = load_values()
flagged_keys = set(zip(*[pd.read_csv(DERIVED / "zero_rows.csv")[c] for c in ("class_id", "hash")]))

paths, initial = {}, {}
results = []
for _, row in values.iterrows():
    project, idx = project_of(row["class_id"]), refactoring_index(row["class_id"])
    key = (row["sample"], project, idx)
    if key not in paths:
        paths[key] = recorded_paths(*key)
        start_hash, start_path = first_commit(*key)
        initial[key] = lines_at(project, start_hash, start_path)
    path = paths[key].get(row["hash"])
    current = None if path is None else lines_at(project, row["hash"], path)
    value = None if initial[key] is None or current is None else bcp.compute_similarity(initial[key], current)
    results.append({"sample": row["sample"], "rq": row["rq"], "family": row["family"], "class_id": row["class_id"],
                    "#refactorings": row["#refactorings"], "hash": row["hash"], "paper_value": row["paper_value"],
                    "move_aware_value": value, "flagged": (row["class_id"], row["hash"]) in flagged_keys})

table = pd.DataFrame(results)
table["diff"] = (table["move_aware_value"] - table["paper_value"]).abs()
table["within_tolerance"] = table["diff"] <= TOLERANCE
table.to_csv(DERIVED / "move_aware_values.csv", index=False)

control = table[~table["flagged"]]
print(f"control: {int(control['within_tolerance'].sum())}/{len(control)} non-flagged rows within ±{TOLERANCE}; "
      f"largest difference {control['diff'].max():.6f}")
print(control[~control["within_tolerance"]][["sample", "class_id", "hash", "paper_value", "move_aware_value"]].to_string(index=False))
print()
flagged = table[table["flagged"]]
print(flagged[["class_id", "#refactorings", "hash", "paper_value", "move_aware_value"]]
      .assign(hash=flagged["hash"].str[:7]).to_string(index=False))
