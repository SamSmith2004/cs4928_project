# Event A — held-out selection (BEFORE ANALYSIS)

- Source: Zenodo record 15209118, v1.0, `Results/cross_project_raw_results.csv`.
- Source file SHA-256: `cb2e3248cb6e94c2b3e60d6de5e79a677358be41c32a814fc2a20ddea17035cd`.
- Held-out project: `commons-numbers` (not used in M2).
- Rule: first alphabetically named project with >=12 **distinct** Move cases and >=12 **distinct** Rename cases; exclude four M2 projects and duplicate hop/incubator-hop.
- Case rule: first 12 per family sorted by leading integer of `class_id`, then full `class_id`, then earliest `time_stamp`. Same M1 selection procedure.
- Dataset observation window (timestamps of the selected cases): 2022-01-20 14:58:26+00:00 to 2024-07-05 14:18:24+01:00.
- Exact selected cases: `EventA/inputs/heldout_cases.csv` (24 rows, 12 per family).
- Historical commit hashes: `EventA/inputs/heldout_commit_references.csv`.
- Counts: Move = 26, Rename = 132 distinct available cases before sampling.
- Confirmed M2 case overlap: none.
- Results: NOT INSPECTED. No `#refactorings` or `lcs_remaining_probs` read.
- **Event A prediction: NOT YET RECORDED.** Freeze it in the tracker and repository before running the event checks.
