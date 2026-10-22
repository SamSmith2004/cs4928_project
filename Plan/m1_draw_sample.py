"""
M1 feasibility check: load the results CSV and redraw the sample from the plan's rules.

Run command:  python Plan/m1_draw_sample.py
"""
from pathlib import Path

import pandas as pd

df = pd.read_csv("Results/cross_project_raw_results.csv")
print(f"Loaded {len(df)} rows, {df['project_id'].nunique()} projects")
rows_per_project = df["project_id"].value_counts()

df["family"] = df["refactoring_type"].str.split().str[0]
cases = (df[df["family"].isin(["Move", "Rename"])]
         .groupby("class_id")
         .agg(project=("project_id", "first"), family=("family", "first"), first_date=("time_stamp", "min"))
         .reset_index())
cases["case_no"] = cases["class_id"].str.split("_").str[0].astype(int)
cases = cases.sort_values(["case_no", "class_id", "first_date"])

# Projects with 12+ Move and 12+ Rename cases, minus the duplicate hop project
counts = cases.groupby(["project", "family"]).size().unstack(fill_value=0)
eligible = counts[(counts["Move"] >= 12) & (counts["Rename"] >= 12)].drop(["hop", "incubator-hop"], errors="ignore")
rq1_projects = rows_per_project[eligible.index].sort_values().index[:3]
rq2_project = sorted(set(eligible.index) - set(rq1_projects))[0]
print(f"RQ1 projects: {list(rq1_projects)}  RQ2 project: {rq2_project}")

sample = []
for family in ["Move", "Rename"]:
    for project in rq1_projects:
        sample += list(cases[(cases["project"] == project) & (cases["family"] == family)]["class_id"][:4])
    sample += list(cases[(cases["project"] == rq2_project) & (cases["family"] == family)]["class_id"][:12])

plan = Path("Plan/G06_P09_M1_Plan.md").read_text()
missing = [cid for cid in sample if f"`{cid}`" not in plan]
print(f"Cases drawn: {len(sample)}, all in plan: {not missing} {missing or ''}")
