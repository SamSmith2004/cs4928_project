# M1: Freeze the Reproduction Plan

**CS4928 Group Project · Group G06 · Pack P09: Long-Term Ripple Effects of Refactoring**

| Item | Details |
|---|---|
| Group / Pack | G06 / P09: Long-Term Ripple Effects of Refactoring |
| Paper | Robredo et al., "Analyzing the ripple effects of refactoring", *Empirical Software Engineering* 31:134 (2026), DOI 10.1007/s10664-025-10801-3 |
| Authors' artefact | Zenodo record 15209118, v1.0 (2025-04-25), `submitted-replication-package.zip` |
| Results file used | `Results/cross_project_raw_results.csv` from that zip (in our repo)|

---

## 1. Research questions and target result

**RQ1.** Can we replicate the paper's findings, that most code refactorings only affect future changes for a short time when testing a smaller set of Java projects?

**RQ2.** Does it transfer to a held-out project/refactoring family?

| | RQ1 | RQ2 |
|---|---|---|
| **Source anchor** | Paper §4.1 (RQ1 results) and the authors' figure "Distribution of RE duration by refactoring family" (`Figures/RQ1/RQ1_RT-NoRef.pdf` in the artefact). Underlying data: `Results/cross_project_raw_results.csv`, columns `#refactorings` and `lcs_remaining_probs` | Same claim and data, applied to a project not used in RQ1 |
| **Target result** | The paper's claim that a refactoring's ripple effect (RE) **usually lasts fewer than 10 later refactorings**, with a few lasting much longer (over 190) | The same claim holds in the held-out project **any23** |
| **What our run produces** | For Move and Rename separately: how many of 12 cases last fewer than 10, and how many of 12 cases have recalculated remaining-code values that match the paper's. Plus a redrawn version of the paper's chart for Move and Rename | The same outputs for the any23 sample |


### Out of scope at M1
- Any refactoring family other than Move and Rename (the paper has 20).
- Any project other than the 4 named in Section 2.
- The paper's RQ2 (change and defect proneness) and RQ3 (developer effort).
- The Bayesian measure (`bayesian_remaining_probs`) and the paper's statistical tests (Kruskal-Wallis, Dunn). We compare Move and Rename by description only.
- Re-running the authors' mining pipeline (RefactoringMiner, SCC, `01_proneness_calculator.py`). We use their published results and recalculate only the remaining-code values for our 48 cases.

---

## 2. Bounded sample
| Element | Frozen value |
|---|---|
| Unit of analysis | One case (one `class_id`) |
| Source/version | `Results/cross_project_raw_results.csv` from Zenodo 15209118 v1.0. For Check 2, the projects' git history from GitHub (`apache/<project>`) at the exact commit hashes in the CSV's `hash` column |
| Size | 48 cases: RQ1 = 12 Move + 12 Rename across 3 projects; RQ2 = 12 Move + 12 Rename from any23 |
| Selection rule, projects | Keep projects with at least 12 Move cases **and** at least 12 Rename cases. Exclude `hop` and `incubator-hop`, which are the same project listed twice. **RQ1:** the 3 projects with the fewest rows in the CSV. **RQ2:** of the remaining eligible projects, the first alphabetically |
| Selection rule, cases | RQ1: the first 4 Move and first 4 Rename cases from each project. RQ2: the first 12 Move and first 12 Rename cases. "First" means sorted by case number (the leading integer of `class_id`), then by `class_id`, then by first date |
| Exclusions | `hop` / `incubator-hop` (duplicate project). No other exclusions |

If the coordinator releases a different held-out project for RQ2, we apply the same case rule to it and log an amendment.

### RQ1 projects
| Project | Rows in CSV | Move cases | Rename cases |
|---|---|---|---|
| sling-whiteboard | 213 | 23 | 22 |
| incubator-tamaya-sandbox | 225 | 33 | 25 |
| ofbiz-framework | 1,020 | 14 | 60 |

#### RQ1 sample: Move
| # | Case ID | Refactoring type | Project | First date |
|---|---|---|---|---|
| 1 | `27_0_move-and-rename-method_sling-whiteboard-1-TransformationContextImpl` | Move And Rename Method | sling-whiteboard | 2019-08-29 |
| 2 | `29_0_move-method_sling-whiteboard-1-TransformationContextImpl` | Move Method | sling-whiteboard | 2019-08-29 |
| 3 | `30_1_move-method_sling-whiteboard-1-TransformationContextImpl` | Move Method | sling-whiteboard | 2019-08-29 |
| 4 | `31_2_move-method_sling-whiteboard-1-TransformationContextImpl` | Move Method | sling-whiteboard | 2019-08-29 |
| 5 | `153_2_move-method_incubator-tamaya-sandbox-1-ConfigValidationDocumentationReader` | Move Method | incubator-tamaya-sandbox | 2019-05-10 |
| 6 | `154_3_move-method_incubator-tamaya-sandbox-1-ConfigValidationDocumentationReader` | Move Method | incubator-tamaya-sandbox | 2019-05-10 |
| 7 | `155_4_move-method_incubator-tamaya-sandbox-1-ConfigValidationDocumentationReader` | Move Method | incubator-tamaya-sandbox | 2019-05-10 |
| 8 | `161_0_move-and-rename-method_incubator-tamaya-sandbox-1-ConfigValidationDocumentationReader` | Move And Rename Method | incubator-tamaya-sandbox | 2019-05-10 |
| 9 | `15_0_move-method_ofbiz-framework-1-JWTManager` | Move Method | ofbiz-framework | 2019-04-21 |
| 10 | `16_1_move-method_ofbiz-framework-1-JWTManager` | Move Method | ofbiz-framework | 2019-04-21 |
| 11 | `17_2_move-method_ofbiz-framework-1-JWTManager` | Move Method | ofbiz-framework | 2019-04-21 |
| 12 | `18_3_move-method_ofbiz-framework-1-JWTManager` | Move Method | ofbiz-framework | 2019-04-21 |

#### RQ1 sample: Rename
| # | Case ID | Refactoring type | Project | First date |
|---|---|---|---|---|
| 1 | `1_0_rename-method_sling-whiteboard-1-TransformationContextImpl` | Rename Method | sling-whiteboard | 2019-08-29 |
| 2 | `2_0_rename-attribute_sling-whiteboard-1-TransformationResponse` | Rename Attribute | sling-whiteboard | 2019-08-29 |
| 3 | `4_0_rename-variable_sling-whiteboard-1-TransformationWriter` | Rename Variable | sling-whiteboard | 2019-08-29 |
| 4 | `5_1_rename-variable_sling-whiteboard-1-NonceTransformer` | Rename Variable | sling-whiteboard | 2019-08-29 |
| 5 | `69_3_rename-attribute_incubator-tamaya-sandbox-1-EnabledPropertySource` | Rename Attribute | incubator-tamaya-sandbox | 2019-05-10 |
| 6 | `70_4_rename-attribute_incubator-tamaya-sandbox-1-MetaContext` | Rename Attribute | incubator-tamaya-sandbox | 2019-05-10 |
| 7 | `74_0_rename-method_incubator-tamaya-sandbox-1-JavaResolver` | Rename Method | incubator-tamaya-sandbox | 2019-05-10 |
| 8 | `198_2_rename-parameter_incubator-tamaya-sandbox-1-TamayaPropertySourceAdapter` | Rename Parameter | incubator-tamaya-sandbox | 2019-05-10 |
| 9 | `2_0_rename-class_ofbiz-framework-1-SafeObjectInputStream` | Rename Class | ofbiz-framework | 2019-04-12 |
| 10 | `12_0_rename-parameter_ofbiz-framework-1-JWTManager` | Rename Parameter | ofbiz-framework | 2019-04-21 |
| 11 | `13_0_rename-variable_ofbiz-framework-1-JWTManager` | Rename Variable | ofbiz-framework | 2019-04-21 |
| 12 | `14_1_rename-variable_ofbiz-framework-1-JWTManager` | Rename Variable | ofbiz-framework | 2019-04-21 |

#### RQ2 sample: Move in any23
| # | Case ID | Refactoring type | First date |
|---|---|---|---|
| 1 | `31_0_move-and-rename-class_any23-1-IssueReport` | Move And Rename Class | 2012-08-13 |
| 2 | `93_1_move-and-rename-class_any23-1-IssueReport` | Move And Rename Class | 2012-08-13 |
| 3 | `121_0_move-class_any23-1-Any23` | Move Class | 2012-05-20 |
| 4 | `123_2_move-class_any23-1-ExtractorDocumentation` | Move Class | 2012-04-03 |
| 5 | `123_2_move-class_any23-2-ExtractorDocumentation` | Move Class | 2017-01-12 |
| 6 | `124_3_move-class_any23-1-MicrodataParser` | Move Class | 2012-04-03 |
| 7 | `124_3_move-class_any23-2-MicrodataParser` | Move Class | 2017-01-12 |
| 8 | `125_4_move-class_any23-1-MimeDetector` | Move Class | 2012-04-03 |
| 9 | `125_4_move-class_any23-2-MimeDetector` | Move Class | 2017-01-12 |
| 10 | `126_5_move-class_any23-1-PluginVerifier` | Move Class | 2012-04-03 |
| 11 | `126_5_move-class_any23-2-PluginVerifier` | Move Class | 2017-01-12 |
| 12 | `127_6_move-class_any23-1-Rover` | Move Class | 2012-04-03 |

#### RQ2 sample: Rename in any23
| # | Case ID | Refactoring type | First date |
|---|---|---|---|
| 1 | `39_1_rename-method_any23-1-ExtractionResultImpl` | Rename Method | 2012-03-23 |
| 2 | `40_2_rename-method_any23-1-ExtractionResultImpl` | Rename Method | 2012-03-23 |
| 3 | `41_3_rename-method_any23-1-ExtractionResultImpl` | Rename Method | 2012-03-23 |
| 4 | `42_4_rename-method_any23-1-ExtractionResultImpl` | Rename Method | 2012-03-23 |
| 5 | `43_5_rename-method_any23-1-ExtractionResultImpl` | Rename Method | 2012-03-23 |
| 6 | `45_0_rename-variable_any23-1-ExtractionResultImpl` | Rename Variable | 2012-03-23 |
| 7 | `47_1_rename-variable_any23-1-ExtractionResultImpl` | Rename Variable | 2012-03-23 |
| 8 | `50_1_rename-attribute_any23-1-ExtractionResultImpl` | Rename Attribute | 2012-03-23 |
| 9 | `53_1_rename-parameter_any23-1-SingleDocumentExtraction` | Rename Parameter | 2012-08-13 |
| 10 | `54_2_rename-attribute_any23-1-SingleDocumentExtraction` | Rename Attribute | 2012-08-13 |
| 11 | `57_2_rename-variable_any23-1-SingleDocumentExtraction` | Rename Variable | 2012-08-13 |
| 12 | `66_4_rename-attribute_any23-1-RDFa11Parser` | Rename Attribute | 2016-08-01 |

---

## 3. Method: inputs → procedure → output

| Inputs | Procedure | Output / decision |
|---|---|---|
| `Results/cross_project_raw_results.csv`, filtered to the 48 case IDs in Section 2 | **Check 1.** For each case, RE duration = largest `#refactorings`. Count the cases with RE duration < 10, per family and per RQ | Number of short cases out of 12 for each family. Compared with the paper's claim using the rule in Section 4 |
| The same 48 cases, plus each project's git history cloned from GitHub at the commit hashes in the CSV | **Check 2.** For each case, recalculate `lcs_remaining_probs` at every later commit using the authors' own function `get_lcs_probabilities` (`Scripts/02_get_bcp.py:167`). We change only the hard-coded file paths. Compare each recalculated value with the CSV value | Number of matching cases out of 12 for each family. Compared using the rule in Section 4 |
| Check 1 RE durations | Box plot of RE duration for Move vs Rename, one per RQ, in the style of `Figures/RQ1/RQ1_RT-NoRef.pdf` | Redrawn chart, compared visually with the paper's. Not used in the verdict |
| Check 1 RE durations | Median RE duration for Move and Rename | Which family lasts longer in our sample. Description only |
| `lcs_remaining_probs` per row | **Sensitivity.** Cut each case off at the first row where remaining code is below 1%, 5% or 10%, then redo the Check 1 count | Short-case counts at each cut-off. Not used in the verdict |

### Parameters that affect the result

| Parameter | Value | Where it comes from |
|---|---|---|
| "Short" cut-off | RE duration < 10 | Paper §4.1 |
| End-of-effect threshold | 1% remaining code | Paper. The authors' code does not apply it (829 cases continue below 1%), so Check 1 uses the CSV as published |
| RE duration of a case | Largest `#refactorings` in the case's rows | Group decision: one number per case, using the authors' own counter |
| Count by case or by row | By case (each case counts once) | Group decision: our sample is defined in cases |
| "Most" | More than half: at least 7 of 12 | Group decision: plain meaning of "most" |
| Match tolerance | Within ±0.02 of the CSV value | Group decision: allows for rounding and library differences on a 0–1 scale |
| Matches needed | At least 10 of 12 cases per family | Group decision: allows up to 2 cases hit by the authors' code recording missing files as 0 |
| Selection thresholds | At least 12 cases per family per project; 4 cases per project for RQ1 | Group decision |
| Sensitivity cut-offs | 1%, 5%, 10% | 1% from the paper; 5% and 10% are group decisions |

---

## 4. Expected result and decision rule

### Decision rule
Each check gets a verdict separately for Move and for Rename.

**Check 1** (is the claim true for our sample?)
| Verdict | When |
|---|---|
| REPRODUCED | At least 7 of the 12 cases have RE duration < 10 |
| NOT REPRODUCED | 6 or fewer of the 12 cases have RE duration < 10 |
| INCONCLUSIVE / BLOCKED | Any sample case is missing from the CSV or has no `#refactorings` value |

**Check 2** (do our recalculated numbers match the paper's?) A case matches if **every** recalculated value is within ±0.02 of the CSV value. A case we can't recalculate (for example the commit or file can't be found) is listed with the reason. It counts as neither a match nor a mismatch.
| Verdict | When |
|---|---|
| REPRODUCED | At least 10 cases match |
| NOT REPRODUCED | At least 3 recalculated cases don't match, so 10 matches is impossible |
| INCONCLUSIVE / BLOCKED | Neither of the above, because too many cases couldn't be recalculated. This includes the authors' code not running after documented attempts |

**Overall answer for each RQ** (both checks, both families):
1. **NOT REPRODUCED** if any check is NOT REPRODUCED for either family.
2. Otherwise **INCONCLUSIVE / BLOCKED** if any check is INCONCLUSIVE / BLOCKED.
3. Otherwise **REPRODUCED**.

RQ2 uses the same rule on the any23 sample.

### Expected result (written before running anything)
- **If the finding reproduces:** at least 7 of 12 cases per family have RE duration < 10, and at least 10 of 12 cases per family match.
- **RQ1 prediction:** Check 1 REPRODUCED for both families. Check 2 NOT REPRODUCED for at least one family, because the authors' code records missing files as 0 and LCS behaves differently on very long files. **Predicted overall: NOT REPRODUCED** (the claim holds, the numbers don't fully match).
- **RQ2 prediction:** the same pattern in any23.
- **Sensitivity:** RE durations get shorter at higher cut-offs; the Check 1 verdict doesn't change.

---

## 5. Feasibility check

| Check | Evidence | Result |
|---|---|---|
| Data loads and the sample rules give exactly the 48 case IDs above | `python Plan/m1_draw_sample.py` (output in `Plan/m1_feasibility_output.txt`) | OK |
| Project git histories for Check 2 are reachable | One sample commit per project looked up on GitHub | OK for all 4 |

**No blocker.** Risk for Check 2: the authors' code has hard-coded Windows paths (`Scripts/components/utility.py:20-21`). If it can't be made to run, Check 2 is INCONCLUSIVE / BLOCKED.
