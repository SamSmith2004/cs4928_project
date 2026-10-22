"""
Check 1: for each sample case, RE duration = largest `#refactorings`. Count cases with RE duration < 10.
"""
import pandas as pd

SHORT = 10      # 4.1: "fewer than 10 later refactorings"
MOST = 7        # 7 > half of 12

sample = pd.read_csv("M2/inputs/sample_cases.csv")
df = pd.read_csv("Results/cross_project_raw_results.csv")

rows = df[df["class_id"].isin(sample["class_id"])]
rows.to_csv("M2/raw/sample_rows.csv", index=False)
print(f"Authors' rows for our sample: {len(rows)} (saved to M2/raw/sample_rows.csv)")

durations = rows.groupby("class_id")["#refactorings"].agg(n_rows="count", re_duration="max").reset_index()
cases = sample.merge(durations, on="class_id", how="left")
cases["short"] = cases["re_duration"] < SHORT
cases.to_csv("M2/derived/check1_cases.csv", index=False)

missing = cases[cases["re_duration"].isna()]["class_id"].tolist()
print(f"Cases missing from CSV or without #refactorings: {missing or 'none'}")


def verdict(group):
    if group["re_duration"].isna().any():
        return "INCONCLUSIVE / BLOCKED"
    return "REPRODUCED" if group["short"].sum() >= MOST else "NOT REPRODUCED"


summary = (cases.groupby(["rq", "family"])
           .apply(lambda g: pd.Series({"n_cases": len(g), "n_short": int(g["short"].sum()), "verdict": verdict(g)}),
                  include_groups=False)
           .reset_index())
summary.to_csv("M2/derived/check1_summary.csv", index=False)
print()
print(summary.to_string(index=False))
