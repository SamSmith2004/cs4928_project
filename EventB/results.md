# Event B — Results

**Conclusion: the Week 9 decision is partly supported.** Keeping the published calculation was right, as no verdict changes. Documenting only the zero values was not enough, because moves also cut off tracking and understate durations.

## Responses
| Response | Main trade-off | Outcome |
|---|---|---|
| A. No structural change: document only | Reproducibility is untouched, but the impact cannot be measured | Rejected: it would not have found the tracking problem |
| **B. Separate audit scripts under `EventB/`** | Frozen evidence is untouched, but affected cases have two values to explain | **Implemented** |
| C. Make the calculation move-aware in place | One value only, but the scripts no longer test the authors' method | Analysed only |

## What each change found

**1. Detect** (`EventB/derived/zero_rows.csv`): 6 of 277 rows are zero, all in any23 Move, and none are in Event A. All six are pure renames with 0 lines added or deleted. PyDriller gives no source code for these, `get_file_content` catches the resulting error and returns an empty result, and the similarity scores 0. The recorded path is correct, and the files have 86–186 lines in git.

**2. Measure** (`EventB/derived/move_aware_values.csv`): the six zeros become 0.48–1.00 when the content is read directly from git. The same method matches the published value on all 271 other rows, with no difference.

| Case | Published | Move-aware |
|---|---:|---:|
| `31_0` IssueReport | 0.00 | 1.00 |
| `93_1` IssueReport | 0.00 | 1.00 |
| `123_2` ExtractorDocumentation | 0.00 | 0.59 |
| `124_3` MicrodataParser | 0.00 | 0.62 |
| `125_4` MimeDetector | 0.00 | 0.48 |
| `126_5` PluginVerifier | 0.00 | 0.62 |

**3. Follow through** (`EventB/derived/check1_move_aware.csv`, `move_aware_cases.csv`, `sensitivity_move_aware.csv`): `check_file_changes` in `Scripts/01_proneness_calculator.py` never updates the path it searches for, so tracking stops at a file's first move. Walking history with the same stale path reproduces the published commits for all 72 cases, so this explains the published data for our sample. Following the path instead extends all six flagged cases, and one reaches the 10-refactoring limit.

| Sample | Short, published | Short, move-aware | Short, whole refactoring | Verdict |
|---|---:|---:|---:|---|
| any23 Move | 12/12 | **11/12** | **9/12** | REPRODUCED (unchanged) |
| any23 Rename | 9/12 | 9/12 | 9/12 | REPRODUCED (unchanged) |
| M2 RQ1 Move | 12/12 | 12/12 | 12/12 | REPRODUCED (unchanged) |
| M2 RQ1 Rename | 12/12 | 12/12 | 12/12 | REPRODUCED (unchanged) |
| Event A Move | 12/12 | 12/12 | 12/12 | REPRODUCED (unchanged) |
| Event A Rename | 12/12 | 12/12 | 12/12 | REPRODUCED (unchanged) |

"Move-aware" gives the extra commits only to a refactoring's last `class_id` segment. "Whole refactoring" counts each case across all its segments, and was added as a robustness check after the first results. Move-aware medians are unchanged. Any23 Move also drops from 12/12 to 11/12 at the 1%, 5% and 10% cut-offs, and no other sample's short count changes.

## Prediction against outcome

| Prediction | Outcome |
|---|---|
| Pressure falls on file-path handling, not the LCS algorithm | **Partly right.** The LCS algorithm is not at fault. The zeros come from content retrieval and the recorded path is correct, but the tracking cut-off is a path-handling fault |
| Published values and Check 2 hold | **Right.** No frozen file changed |
| Check 1 and sensitivity verdicts hold | **Right**, although any23 Move's short count falls |

## Change spread against the frozen state

| | B (implemented) | Same changes in place (estimated, not implemented) |
|---|---|---|
| Existing files edited | 0 | 6: both `check2.py`, both `check1.py`, `M2/scripts/pack_tasks.py`, `EventA/run.py` |
| Repeated edits | 0 | 4 pairs: `check2.py` for changes 1 and 2, then `check1.py` and the sensitivity rule for change 3 |
| New files | 4 scripts (about 330 lines) | 0 |
| Frozen outputs changed | 0 (`git diff pre_event_b` on `M2`, `EventA`, `Scripts`, `Results`) | Would overwrite them unless output paths also changed |

A true fix in the authors' code would go further, because correcting tracking means rerunning their mining pipeline, which M1 ruled out of scope.

## Trade-off and remaining risk

- **Trade-off accepted:** affected cases now have published and move-aware values. The published value stays the reproduction result, and the move-aware value is audit evidence only.
- **Risk remaining:** the `except` in `get_file_content` hides a failure as a measurement of 0%, and the copied M2 and Event A scripts remain duplicated. Both are left as they are because they are frozen evidence.

## Limitations

- **Corrects `M2/log.md` note 6:** the note says the limitation does not change Check 1 results. The verdict holds, but the any23 Move count does change.
- **Event A says little about this limitation:** it has no zero rows or moved cases, so its 24/24 match does not test it.
- **Scale is untested:** across the full results file, 13.5% of `class_id`s (3,790 of 28,129) have a later path segment, and 1.2% of rows (1,322 of 108,523) are zero. We checked only our 72 cases, so we do not claim the paper's overall result would change.
- **Rename detection:** this uses git's default 50% similarity. A move with heavier edits looks like a delete and an add, so durations could still be understated.
- **Later clones:** `sling-whiteboard` and `ofbiz-framework` are at newer heads than in M2 (`EventB/inputs/repos.csv`). Only commits in the authors' refactoring list count, and the 72/72 control still passes.
- **Verdict criteria:** the supported, partly supported and revise rules were not in the tagged prediction. They were written in an earlier draft of the prediction, before any change was run, and removed before tagging: partly supported means verdicts hold, but durations or sensitivity results change more than the documented limitation implied.

## Run code
```bash
M2/.venv/bin/python EventB/scripts/detect_zeros.py
M2/.venv/bin/python EventB/scripts/measure_moves.py
M2/.venv/bin/python EventB/scripts/follow_through.py
```
