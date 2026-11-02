# CS4928 P09 — Event A Results and Interpretation

**Project:** Long-Term Ripple Effects of Refactoring  
**Study:** Robredo et al., *Analyzing the Ripple Effects of Refactoring*  
**Source artefact:** [Zenodo record 15209118](https://zenodo.org/records/15209118), version 1.0 (as recorded in the selection manifest)

## 1. Frozen sample and prediction

Event A tests whether the Move/Rename short-duration pattern found in M2 transfers to **one additional held-out Java project**, using the existing M2 method without changing its analysis or decision thresholds.

- **Held-out project:** `commons-numbers` (as indicated by the selected case identifiers; check the authoritative project name in `EventA/inputs/selection_record.md`).
- **Sample:** 24 distinct cases: the first 12 eligible **Move** cases and first 12 eligible **Rename** cases selected by the frozen selection rule.
- **Not reused from M2:** The selection procedure excludes `sling-whiteboard`, `incubator-tamaya-sandbox`, `ofbiz-framework`, and `any23`, and checks that case IDs do not overlap with the M2 sample.
- **Exact case IDs, selected project, source checksum, observation dates, and commit references:** `EventA/inputs/heldout_cases.csv`, `EventA/inputs/selection_record.md`, and `EventA/inputs/heldout_commit_references.csv`.
- **Frozen prediction:** **REPRODUCED**, recorded before Event A analysis in `EventA/prediction.md` and the Student Tracker. The prediction and M2 record are preserved unchanged.

The source-data extraction for the Event A sample contained **52 authors' result rows**, corresponding to **24 distinct sampled cases**. Rows and cases are not interchangeable counts.

## 2. Frozen analysis and decision rules

The existing M2 procedure and thresholds were retained:

1. **Check 1 — short duration:** A case is short-lived when the recorded ripple-effect duration is **fewer than 10 subsequent refactorings**. Each family passes if **more than half** of its 12 cases are short-lived (at least 7/12).
2. **Check 2 — numerical recalculation:** A case matches when its recalculated LCS-based measurements agree with the original authors' values within an absolute tolerance of **0.02**. Each family passes when **at least 10/12** cases match.
3. **Overall decision:** Under the frozen M1 rules, both checks passing for both families yields **REPRODUCED**; the remaining classifications follow the original M1 plan. No classification ambiguity occurs here because both families passed both checks.
4. **Sensitivity:** Repeat the short-duration summary using remaining-similarity cut-offs of **1%, 5%, and 10%**, and compare with durations reported as published. Sensitivity analysis is reported separately; it does not replace the primary frozen decision.

The Event A scripts are copies/adaptations of the M2 scripts with the analysis input and output paths redirected to `EventA/` so that M2 evidence is not overwritten.

## 3. Event A results

### 3.1 Check 1 — short-lived ripple effects

| Family | Cases analysed | Cases lasting <10 subsequent refactorings | Proportion short-lived | Check 1 decision |
|---|---:|---:|---:|---|
| Move | 12 | 12 | 100% | **PASS** |
| Rename | 12 | 12 | 100% | **PASS** |
| **Total** | **24** | **24** | **100%** | **PASS** |

No selected cases were missing from the authors' CSV or lacked a `#refactorings` value, according to the execution output. The **median published duration is 2.0 subsequent refactorings** for each family.

**Evidence:** `EventA/derived/check1_summary.csv`, `EventA/derived/check1_cases.csv`, `EventA/raw/sample_rows.csv`, and `EventA/raw/check1_run.log`.

### 3.2 Check 2 — similarity-value recalculation

| Family | Cases matching the authors | Cases mismatching | Cases not recalculated | Check 2 decision |
|---|---:|---:|---:|---|
| Move | 12 | 0 | 0 | **PASS** |
| Rename | 12 | 0 | 0 | **PASS** |
| **Total** | **24** | **0** | **0** | **PASS** |

**All 24 selected cases matched** the authors' values according to the frozen Check 2 rule. The original output displays examples of agreement, including `15_7_rename-variable_commons-numbers-1-BoostErf` at observation 1 (**0.937575** published versus **0.937575** recalculated) and `103_0_rename-variable_commons-numbers-1-Sum` at observation 1 (**0.360225** versus **0.360225**). The complete value-level evidence is in `EventA/raw/check2_values.csv`; the summary does not independently establish a total count of individual recalculated observations.

**Evidence:** `EventA/derived/check2_summary.csv`, `EventA/derived/check2_cases.csv`, `EventA/raw/check2_values.csv`, and `EventA/raw/check2_run.log`.

### 3.3 Sensitivity analysis

| Cut-off | Move: short cases | Move: median duration | Rename: short cases | Rename: median duration |
|---|---:|---:|---:|---:|
| None (published durations) | 12/12 | 2.0 | 12/12 | 2.0 |
| 1% | 12/12 | 2.0 | 12/12 | 2.0 |
| 5% | 12/12 | 2.0 | 12/12 | 2.0 |
| 10% | 12/12 | 2.0 | 12/12 | 2.0 |

The number of short-lived cases and median durations **did not change** under the three tested cut-offs. Consequently, the overall Event A decision remains **REPRODUCED** at 1%, 5%, and 10%.

**Evidence:** `EventA/derived/sensitivity.csv`.

### 3.4 Overall Event A decision

**REPRODUCED under the preregistered M2 decision rules.** Both Move and Rename passed Check 1 (**12/12 short-lived in each family**) and Check 2 (**12/12 matching cases in each family**). The sensitivity checks did not change the decision. This agrees with the frozen pre-analysis prediction.

## 4. Comparison with M2: what transfers?

| Sample | Move: short-lived | Rename: short-lived | Move: matching | Rename: matching |
|---|---:|---:|---:|---:|
| M2 RQ1 — three original projects | 12/12 | 12/12 | 12/12 | 12/12 |
| M2 RQ2 — `any23` | 12/12 | 9/12 | 12/12 | 12/12 |
| **Event A — new held-out project** | **12/12** | **12/12** | **12/12** | **12/12** |

**What transfers:** The qualitative pattern that most selected Move and Rename ripple-effect cases are short-lived transfers to the Event A project; in this sample **all 24 cases** are short-lived. The ability to reproduce the authors' reported LCS values within **±0.02** also transfers for all 24 cases. Both families pass the original M2 rules.

**What differs:** In the M2 `any23` sample, **9/12 Rename** cases were short-lived; in Event A, **12/12 Rename** cases were short-lived. The observed Rename proportion therefore differs across the held-out projects, even though the decision category is the same. The Event A results do not establish that every Java project or refactoring family will exhibit this pattern.

**Strongest supporting evidence:** The case-level Check 1 and Check 2 CSVs, the 24/24 pass counts, the 52 original source rows, and the unchanged sensitivity outcomes. These allow the aggregate conclusions to be checked against individual selected cases and source values.

## 5. Software-design and maintainability implication

The short observed persistence of both Move and Rename refactorings suggests that **developers should not choose a refactoring merely because they expect its ripple effect to be long-lived**. Instead, a refactoring should address a specific design pressure: for example, moving a method to reduce inappropriate coupling or renaming an element to improve code clarity. The change should remain **behaviour-preserving** and should be verified using relevant tests and a review of cohesion, coupling, and maintainability.

No additional design pattern is justified by these results alone. A numerical similarity match is not proof that a change improves software quality, reduces defects, or causes a specific long-term maintenance benefit.

## 6. Limitations, audit notes, and deviations

- **Bounded sample and selection bias:** Only 24 selected cases from one additional Java project were examined; cases were chosen using the frozen deterministic ordering rule, not random sampling. This limits generalisation.
- **Dependence on the authors' data:** Check 1 uses published duration values; Check 2 recalculates and compares against the authors' published similarity measurements. Agreement establishes numerical reproducibility for these cases, not independent validation of every underlying mining decision.
- **Metric validity:** As identified in the M2 audit, file moves may produce a remaining-similarity value of zero because the tracked path changes, even when the code itself remains. Reproducing that value does not resolve the underlying measurement limitation.
- **Historical coverage:** The analysis is restricted to the observation window, commits and cases recorded in the frozen Event A selection files. It does not infer unseen changes after that window.
- **Environment troubleshooting:** Initial Check 2 executions failed because Python dependencies (`requests`, then `pydriller`) were missing. The logs of failed attempts should be preserved alongside the successful run. Installing missing dependencies did **not** change the frozen analysis method or thresholds.
- **Method changes:** No changes to the frozen decision rules or cut-offs are reported. Any later improvements must be recorded separately from this first Event A result.

## 7. Reproducibility and evidence index

| Artefact | Purpose |
|---|---|
| `EventA/prediction.md` | Frozen pre-analysis prediction and decision criteria |
| `EventA/inputs/selection_record.md` | Held-out project, selection rule, source, checksum and observation window |
| `EventA/inputs/heldout_cases.csv` | Exact 24 case IDs |
| `EventA/inputs/heldout_commit_references.csv` | Supporting source commit/time references |
| `EventA/inputs/sample_cases.csv` | Input manifest for the M2-derived Event A scripts |
| `EventA/scripts/check1.py` | Frozen Check 1 logic adapted to Event A paths |
| `EventA/scripts/check2.py` | Frozen Check 2 logic adapted to Event A paths |
| `EventA/derived/check1_summary.csv` | Check 1 group results |
| `EventA/derived/check1_cases.csv` | Check 1 case-level results |
| `EventA/derived/check2_summary.csv` | Check 2 group results |
| `EventA/derived/check2_cases.csv` | Check 2 case-level results |
| `EventA/derived/sensitivity.csv` | Cut-off sensitivity results |
| `EventA/raw/sample_rows.csv` | 52 source-result rows used for the selected cases |
| `EventA/raw/check2_values.csv` | Value-level published/recalculated comparison |
| `EventA/raw/check1_run.log`, `EventA/raw/check2_run.log` | Execution logs; retain earlier failed-attempt logs as well |

**Final conclusion:** Event A **REPRODUCED** the M2 relative short-duration pattern and numerical matching checks on the new held-out sample. The result supports transfer **within the stated 24-case Move/Rename sample**. It does not establish universal refactoring durability or causal improvements in code quality.
