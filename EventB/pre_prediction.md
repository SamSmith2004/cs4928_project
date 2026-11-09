# Event B — Pre-Execution Prediction
## Baseline
Frozen state: commit `8963df2`. Our Week 9 decision is confirmed as recorded in the Student Tracker: keep the original LCS calculation unchanged and document the file-movement limitation, where six M2 observations record 0% remaining code at file moves (`M2/log.md`, note 6).

## New evolution pressure
We will apply three linked follow-up changes in sequence to how the analysis handles moved files:

1. **Detect:** flag every zero value in the M2 and Event A results and confirm why each one occurs.
2. **Measure:** for flagged rows, recalculate similarity using the file's path after the move, in a separate column.
3. **Follow through:** rerun Check 1 and the sensitivity analysis using those values, including whether tracking continues after the move.

## Prediction
We expect the pressure to fall on file-path handling rather than the LCS algorithm, because all six zero values occur at move commits, where `get_lcs_probabilities` depends on the path it passes to `get_file_content`. We expect published values and Check 1, Check 2 and sensitivity verdicts to hold
