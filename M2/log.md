# M2 Reproduction Log

**Frozen plan:** [Plan/G06_P09_M1_Plan.md](../Plan/G06_P09_M1_Plan.md) (commit `044bcea`, tag `M1_PLAN`)
**Data:** `Results/cross_project_raw_results.csv` + selected authors' files from Zenodo 15209118 v1.0
**Environment:** Python 3.14.8, packages in [env.txt](env.txt)

## How to run (from repo root)
```
python3 -m venv M2/.venv && source M2/.venv/bin/activate
pip install -r M2/env.txt
python M2/scripts/sample.py
python M2/scripts/check1.py
python M2/scripts/pack_tasks.py
python M2/scripts/fetch_inputs.py
git clone https://github.com/apache/<project>.git M2/repos/<project>   # once per project in inputs/repos.csv
python M2/scripts/check2.py
```
Downloaded files (`inputs/zenodo/`, `repos/`) aren't committed. What was used is recorded in [inputs/zenodo_manifest.csv](inputs/zenodo_manifest.csv) and [inputs/repos.csv](inputs/repos.csv).

---

## Result (2026-10-22)

| | Check 1: short cases | Check 2: matching cases | Verdict |
|---|---|---|---|
| RQ1 Move | 12/12 | 12/12 | REPRODUCED |
| RQ1 Rename | 12/12 | 12/12 | REPRODUCED |
| RQ2 Move | 12/12 | 12/12 | REPRODUCED |
| RQ2 Rename | 9/12 | 12/12 | REPRODUCED |

**RQ1: REPRODUCED. RQ2: REPRODUCED.** All 225 recalculated values match the paper (largest difference 1.1e-16).
**M1 prediction was NOT REPRODUCED** (we expected Check 2 to fail). It's left unchanged in M1; see note 6 for why it was wrong.

**Pack task** ([sensitivity.csv](derived/sensitivity.csv), [plot](derived/re_duration_boxplot.png)):
- Median RE duration: RQ1 Move 3 vs Rename 2; RQ2 Move 5 vs Rename 6. No consistent winner between families.
- Sensitivity: counts don't change at 1%, 5% or 10% (note 5).

Files: [check1_summary](derived/check1_summary.csv) · [check2_summary](derived/check2_summary.csv) · raw values [check2_values.csv](raw/check2_values.csv)

---

## Traced example

**RQ2 Rename, Check 1 = 9 of 12 short**
1. [derived/check1_summary.csv](derived/check1_summary.csv): `RQ2,Rename,12,9,REPRODUCED`
2. [derived/check1_cases.csv](derived/check1_cases.csv): the 3 non-short cases are plan rows 9–11 (`…SingleDocumentExtraction`), RE duration 15 each
3. [raw/sample_rows.csv](raw/sample_rows.csv): `53_1_rename-parameter_any23-1-SingleDocumentExtraction` has 15 rows, `#refactorings` 1 → 15 (authors' rows, unchanged)
4. Made by `scripts/check1.py` from `Results/cross_project_raw_results.csv`
5. Case chosen by the M1 rule: M1 plan, "RQ2 sample: Rename in any23", row 9

---

## Notes

No material deviations from M1.

**1. Setup.** A fresh virtual environment with only the packages the scripts import, at the authors' versions. The `M1_PLAN` tag was added on 2026-10-22, after Check 1 ran but before Check 2. The plan file was unchanged since commit `044bcea`.

**2. Inputs for Check 2.** `fetch_inputs.py` downloads only the 56 authors' files needed (42 MB) from the 5.9 GB Zenodo zip, same version as M1. Zenodo rate-limited the first two attempts; the third completed. The 4 projects were cloned from GitHub, and every commit the sample needed was there.

**3. Two path repairs (not material).** The authors' files aren't edited; `check2.py` makes both fixes at runtime.
- Their data folder is hard-coded to `C:\Users\Mikel\...`. We point it at a local log folder.
- Their saved file paths use Windows `\`, which only matches on Windows. On Linux every value silently comes back 0.0, so we change `\` to `/`. Evidence: [raw/check2_no_path_fix.log](raw/check2_no_path_fix.log).
- AI identified the Windows path-separator issue; we verified it by running the pilot with and without the repair (raw/check2_no_path_fix.log).

**4. Pilot and runs.** The pilot on M1 case 1 matched 3/3 ([raw/check2_pilot_values.csv](raw/check2_pilot_values.csv)). The full run was done twice, because the first run's logs were mixed with the pilot's. Both runs gave identical values.

**5. Interpretation decisions (decided before running).**
- 4 any23 cases ending in `-2-` have 1 row whose `#refactorings` continues from the `-1-` case (e.g. 6). The M1 rule (largest `#refactorings`) gives 6, not 1. Both are under 10, so the verdict is the same either way.
- Sensitivity: the row where remaining code drops below the cut-off is counted. It made no difference, because the only rows below 10% are six `0.0` values that are already the last row of their case.
- Check 2 matches each recalculated value to our rows by commit hash.

**6. Audit finding: the six 0.0 values are file moves.** At those commits `git show --stat -M` (any23) shows the class files were moved with **0 lines changed** (`cb777c4`, `242b130`). All the code was still there, but the method records 0% remaining. We get the same zeros because we run the authors' code unchanged, which is why our M1 prediction (Check 2 fails) was wrong. This is a **validity threat to the paper's metric** (moved code counts as deleted), not a reproduction failure. It doesn't change our Check 1 results.
