# Read the 48 frozen case IDs straight from the M1 plan tables.

import re
from pathlib import Path

import pandas as pd

plan = Path("Plan/G06_P09_M1_Plan.md").read_text().splitlines()

rows = []
rq = family = None
for line in plan:
    heading = re.match(r"#### (RQ\d) sample: (Move|Rename)", line)
    if heading:
        rq, family = heading.groups()
        continue
    if line.startswith("#"):
        rq = family = None
    case = re.match(r"\| (\d+) \| `([^`]+)` \|", line)
    if case and rq:
        rows.append({"rq": rq, "family": family, "plan_row": int(case.group(1)), "class_id": case.group(2)})

sample = pd.DataFrame(rows)
print(sample.groupby(["rq", "family"]).size().to_string())
assert len(sample) == 48 and sample["class_id"].is_unique, "Expected 48 unique case IDs in the M1 plan"

sample.to_csv("M2/inputs/sample_cases.csv", index=False)
print(f"Wrote {len(sample)} cases to M2/inputs/sample_cases.csv")
