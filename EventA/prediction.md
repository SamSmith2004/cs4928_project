# Event A — Pre-Analysis Prediction

## Held-out sample

- Project: commons-njmbers
- Source: Zenodo record 15209118, version 1.0
- Sample: 12 Move and 12 Rename refactoring cases
- Exact case IDs and observation window: `EventA/inputs/heldout_cases.csv` and `selection_record.md`
- Selection completed before examining Event A outcomes.

## Prediction

We predict that the findings from M2 will transfer to the new held-out project.

**Check 1 — Ripple-effect duration**

We expect at least 7 of the 12 cases in each refactoring family to have a ripple-effect duration of fewer than 10 subsequent refactorings.

**Check 2 — Recalculation accuracy**

We expect at least 10 of the 12 cases in each family to match the published LCS similarity values within ±0.02 for every recalculated observation.

**Overall prediction: REPRODUCED.**

We expect both Move and Rename to satisfy both checks, consistent with our M2 findings.

## What would challenge our M2 conclusion?

Our M2 conclusion would be challenged if either refactoring family fails Check 1 (6 or fewer short-lived cases) or Check 2 (at least three recalculated cases do not match the published values).

Under our existing M1 decision rules, a failed check in either family produces an overall NOT REPRODUCED verdict. Cases that cannot be recalculated will be reported separately as inconclusive where applicable.

## Frozen methodology

We will retain the original M2 approach:

- One `class_id` represents one case.
- RE duration is the largest published `#refactorings` value for that case.
- A short-lived case has a duration below 10.
- LCS similarity values are recalculated using the same authors' function and verified against the published values.
- Matching tolerance remains ±0.02.
- Sensitivity analysis uses 1%, 5%, and 10% remaining-code cut-offs.
- Sensitivity results are reported separately and do not change the primary decision rule.

No parameters or decision rules will be adjusted after viewing Event A results.