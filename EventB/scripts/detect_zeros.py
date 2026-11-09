"""
Change 1 (Detect): flag every zero value in the frozen M2 and Event A results and record why it occurs,
using the authors' own get_file_content on the same commit and path.

Output: EventB/derived/zero_rows.csv
"""
import pandas as pd
import pydriller

from common import DERIVED, REPOS, load_authors, load_values, lines_at, project_of, recorded_paths, refactoring_index

bcp = load_authors()
values = load_values()
flagged = values[(values["our_value"] == 0) | (values["paper_value"] == 0)]

results = []
for _, row in flagged.iterrows():
    project, idx = project_of(row["class_id"]), refactoring_index(row["class_id"])
    path = recorded_paths(row["sample"], project, idx)[row["hash"]]
    entry = {"change_type": "not in commit", "old_path": None, "new_path": None, "added": None, "deleted": None,
             "pydriller_source_is_none": None}
    for commit in pydriller.Repository(str(REPOS / project), only_commits=[row["hash"]]).traverse_commits():
        for mod in commit.modified_files:
            if path in (mod.old_path, mod.new_path):
                entry = {"change_type": mod.change_type.name, "old_path": mod.old_path, "new_path": mod.new_path,
                         "added": mod.added_lines, "deleted": mod.deleted_lines,
                         "pydriller_source_is_none": mod.source_code is None}
    returned = bcp.get_file_content(row["hash"], path, str(REPOS / project))
    on_disk = lines_at(project, row["hash"], path)
    results.append({"sample": row["sample"], "rq": row["rq"], "family": row["family"], "class_id": row["class_id"],
                    "#refactorings": row["#refactorings"], "hash": row["hash"], "paper_value": row["paper_value"],
                    "our_value": row["our_value"], "recorded_path": path, **entry,
                    "authors_returned_lines": None if returned is None else len(returned),
                    "lines_in_git": None if on_disk is None else len(on_disk)})

table = pd.DataFrame(results)
table.to_csv(DERIVED / "zero_rows.csv", index=False)
print(f"rows checked: {len(values)}; zero rows flagged: {len(table)}")
print(table.groupby(["sample", "rq", "family"]).size().to_string())
print(table[["class_id", "hash", "change_type", "added", "deleted", "pydriller_source_is_none",
             "authors_returned_lines", "lines_in_git"]].assign(hash=table["hash"].str[:7]).to_string(index=False))
