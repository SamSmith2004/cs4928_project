"""
  1 Recreate one plot: box plot of RE duration, Move vs Rename, per RQ
  2. Compare two families + audit sensitivity to one threshold: stop each case at the first row where
     remaining code < 1%, 5%, 10%, then redo the Check 1 count. The "none" rows give each family's median.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

SHORT = 10
CUTOFFS = [0.01, 0.05, 0.10]

rows = pd.read_csv("M2/raw/sample_rows.csv")
cases = pd.read_csv("M2/derived/check1_cases.csv")

# 1. Box plot
fig, axes = plt.subplots(1, 2, figsize=(8, 4), sharey=True)
for ax, rq in zip(axes, ["RQ1", "RQ2"]):
    data = [cases[(cases["rq"] == rq) & (cases["family"] == f)]["re_duration"] for f in ["Move", "Rename"]]
    ax.boxplot(data, tick_labels=["Move", "Rename"])
    ax.axhline(SHORT, linestyle="--", color="grey", label="Short cut-off (10)")
    ax.set_title(f"{rq} ({'3 projects' if rq == 'RQ1' else 'any23'})")
    ax.set_ylabel("RE duration (later refactorings)")
axes[0].legend()
fig.suptitle("RE duration by refactoring family (12 cases each)")
fig.tight_layout()
fig.savefig("M2/derived/re_duration_boxplot.png", dpi=150)
print("Saved M2/derived/re_duration_boxplot.png")


# 2. Family comparison + sensitivity
def duration_with_cutoff(case_rows, cutoff):
    #Effect ends at the first row where remaining code drops below the cut-off (that row is counted).
    case_rows = case_rows.sort_values("#refactorings")
    below = case_rows[case_rows["lcs_remaining_probs"] < cutoff]
    return below["#refactorings"].iloc[0] if len(below) else case_rows["#refactorings"].max()


results = []
for cutoff in [None] + CUTOFFS:
    for (rq, family), group in cases.groupby(["rq", "family"]):
        if cutoff is None:
            durations = group["re_duration"]
        else:
            durations = [duration_with_cutoff(rows[rows["class_id"] == cid], cutoff) for cid in group["class_id"]]
        durations = pd.Series(durations)
        results.append({"cutoff": "none (as published)" if cutoff is None else f"{cutoff:.0%}",
                        "rq": rq, "family": family,
                        "n_short": int((durations < SHORT).sum()), "median_duration": durations.median()})

sensitivity = pd.DataFrame(results)
sensitivity.to_csv("M2/derived/sensitivity.csv", index=False)
print(sensitivity.to_string(index=False))
