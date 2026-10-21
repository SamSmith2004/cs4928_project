# M1: Study, RQs and Preregistration

**CS4928 Group Project · Group G06 · Pack P09: Long-Term Ripple Effects of Refactoring · Version 4.1**

> **Status: draft for group review.** When the group agrees, commit this plan and tag it `M1_PLAN` **before** running any analysis. After that, don't edit it. Any later change goes in a dated "Amendments" section with the reason.

| Item | Details |
|---|---|
| Group / Pack | G06 / P09: Long-Term Ripple Effects of Refactoring |
| Paper | Robredo et al., "Analyzing the ripple effects of refactoring", *Empirical Software Engineering* 31:134 (2026), DOI 10.1007/s10664-025-10801-3 |
| Authors' data and code | Zenodo record 15209118 (version 1, in our repo). The newer version 17275710 (2025-10-06) also includes the raw data (5.9 GB download) |
| Task set by the pack | Reproduce one small part of the paper: compare two refactoring families, recreate one table or plot, and check how much one threshold affects the result |

---

## 1. Research questions

**RQ1.** Can we replicate the paper's findings, that most code refactorings only affect future changes for a short time when testing a smaller set of Java projects?

**RQ2.** Does it transfer to a held-out project/refactoring family?

### What these mean in practice
- **RQ1:** In 3 of the paper's projects, do most Move and Rename refactorings have an effect that lasts **fewer than 10** later refactorings? And when we recalculate the paper's numbers for these cases, do we get the same values?
- **RQ2:** Do we get the same answer in a different project (**any23**) that RQ1 doesn't use?

### The finding we are testing
The paper says the effect of a refactoring **usually lasts for fewer than 10 later refactorings**, though a few last much longer (over 190). (Paper section 4.1.)

We will redraw the paper's chart of how long effects last for each refactoring family (`Figures/RQ1/RQ1_RT-NoRef.pdf`), using only Move and Rename and only our sample.

### Key terms

| Term | What it means here |
|---|---|
| Refactoring | A change that cleans up code without changing what it does (e.g. moving a method to another class, renaming a variable) |
| Refactoring family | A group of related refactoring types, named by the first word. **Move** = Move Method, Move Class, Move Attribute, etc. **Rename** = Rename Method, Rename Variable, etc. |
| Case | One refactoring in one Java class, followed over time. Each case has an ID in the paper's results file (`class_id`) |
| How long the effect lasts | The number of later refactorings of the same type in the same class. The paper calls this the ripple effect (RE) duration |
| "A short time" | Fewer than 10 later refactorings (the paper's own cut-off) |
| "Most" | More than half |
| Code still remaining | How much of the class's original code is still there after each later change, from 0 (none) to 1 (all). The paper measures this by comparing the class's lines before and after |
| The 1% rule | The paper says the effect has ended once less than 1% of the original code remains |

### Why Move and Rename
- They show the paper's main contrast: **big structural changes** (moving code between classes) vs **small local changes** (renaming).
- Both are common (about 7,000 Move and 15,000 Rename examples), so even small projects have enough cases.
- The paper reports a direct comparison of these two families: Rename's effects last longer than Move's. We will check whether our sample agrees.

---

## 2. Sample

### RQ1: which projects
**Rule:** from the paper's 47 projects, keep those with at least 12 Move cases **and** at least 12 Rename cases. Leave out `hop` and `incubator-hop`, which are the same project listed twice. Then take the **3 smallest** (fewest rows in the paper's results, so the cheapest to analyse).

| # | Project | Rows in results | Move cases | Rename cases |
|---|---|---|---|---|
| 1 | sling-whiteboard | 213 | 23 | 22 |
| 2 | incubator-tamaya-sandbox | 225 | 33 | 25 |
| 3 | ofbiz-framework | 1,020 | 14 | 60 |

### RQ1: which cases
**Rule:** from each project, take the **first 4 Move and first 4 Rename cases**, giving 12 of each in total.

"First" means in a fixed order: by case number, then by class name, then by date. This means anyone can redraw the same sample, and we can't pick cases that suit us.

*Why 4 from each project:* the pack suggests "the first 12". But taking the first 12 across all three projects together would take nothing from incubator-tamaya-sandbox. Taking 4 from each project makes sure all three are included.

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

### RQ2: which project and cases
**Rule:** from the remaining projects that pass the same check (at least 12 of each family), take the first in alphabetical order. That is **any23**. From it, take the **first 12 Move and first 12 Rename cases** in the same fixed order.

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

## 3. Method
1. **Set up.** Use a fresh Python environment with only the packages we need. Write down the versions used.
2. **Get the data.** Use the paper's results file from our repo (`Results/cross_project_raw_results.csv`). Download the newer Zenodo version to get the code history for each project.
3. **Check the claim.** For each sample and each family, count how many cases have an effect lasting fewer than 10 later refactorings. Redraw the paper's chart for Move and Rename.
4. **Recalculate the numbers.** For each of the 48 cases, take the class's code at the original refactoring and at each later one. Work out how much of the original code remains, using the authors' own code. Compare our numbers with the paper's.
5. **Compare the families.** Report whether Move or Rename effects last longer in our samples. With only 12 cases per family this is a description, not proof.
6. **Check the 1% rule (sensitivity check).** Repeat step 3 with the cut-off at 1% (the paper), 5% and 10%.
7. **Keep everything.** Commit every script and its output to the repo. Never edit results by hand.

---

## 4. How we decide the answer

### Two checks, done for Move and Rename separately
- **Check 1 (the claim):** more than half of the family's cases have an effect lasting fewer than 10 later refactorings.
- **Check 2 (matching numbers):** at least 10 of the 12 cases match the paper. A case matches if every recalculated value is within 0.02 of the paper's value.

### RQ1 answer

| Answer | When |
|---|---|
| **Reproduced** | Both checks pass for both families |
| **Partly reproduced** | Check 1 passes for only one family, **or** Check 1 passes for both but only 6–9 cases match in a family |
| **Not reproduced** | Check 1 fails for both families, **or** fewer than 6 cases match in either family |
| **Couldn't run it** | If we can't get the code history after documented attempts, we answer using Check 1 only (the paper's published numbers) and say so |

### RQ2 answer
The same two checks, on the any23 sample.

| Answer | When |
|---|---|
| **Transfers** | Both checks pass for both families |
| **Partly transfers** | A mixed result |
| **Does not transfer** | Check 1 fails for both families, or fewer than 6 cases match in either family |

**For comparison, the paper's full data:** 87% of all cases last fewer than 10 later refactorings.

---

## 5. Sensitivity check: the 1% rule
The paper says an effect ends once less than 1% of the original code remains. But the authors' code doesn't actually apply this rule: in their data, 829 cases keep going after dropping below 1%.

So we will recount how long each effect lasts if we **stop it** once the remaining code drops below 1%, 5% or 10%, and see how much our results change.

Stopping effects earlier can only make them shorter, so this can't make Check 1 fail. What we report is **how much** the numbers change. If our answer stays the same at every cut-off, we call it **robust**.

---

## 6. What we expect (written before running anything)
- **RQ1: partly reproduced.** We expect most effects to be short (Check 1 passes), but some recalculated numbers won't match. The authors' code records 0 when it can't find a file (for example after it was renamed), and the comparison method behaves differently on very long files.
- **RQ2: partly transfers.** We expect the same pattern in any23.
- **Sensitivity check:** effects get shorter at higher cut-offs, but our answer stays the same.

### What counts as not reproduced
Half or fewer of the cases are short in both families, or fewer than 6 of 12 cases match in either family. If that happens we report it as a result. We don't change the method to get a better match.

---

## 7. Things we noticed before starting
Found by reading the authors' published files and code. No analysis has been run yet.

1. **The paper counts rows, not cases.** The paper's figures (half of effects under 4, three-quarters under 9) come from counting every row in its results file. Long-lasting cases have many rows, so they count many times. Counting each case once gives half under 2 and three-quarters under 5.
2. **The 1% rule isn't applied in the code** (see Section 5).
3. **Missing files are recorded as 0.** When the code can't find a file, it records "no code remaining" instead of "missing".
4. **47 projects, not 48.** The paper says 48, but the data has 47 project names, and two of those (`hop`, `incubator-hop`) look like the same project.
5. **Cases are bunched together.** For example, all four ofbiz-framework Move cases are in the same class on the same day. So the cases aren't fully independent.

---

## 8. Where we differ from the pack
- **RQ1 wording** is our group's own, not the pack's suggestion. We keep it within the pack's scope by limiting it to 3 projects and two families.
- **Sample size:** 4 cases per family from each of 3 projects instead of "the first 12" overall, so every project is included. RQ2 uses the pack's rule as written.
- **Approach:** we use the authors' published results and recalculate a small number of cases. We don't rerun their whole mining tool, as the pack advises.

---

## 9. Link to the Week 9 design decision
The authors' code is hard to run: file paths are hard-coded to their computer, a settings file is missing, and the scripts are very long. This is a likely design problem for Week 9. We'll compare at least two options then, including leaving it as it is.

---

## 10. Evidence we will keep
The Zenodo versions and download date, the version of each project's code we used, the script that draws the sample and its output, our recalculated numbers next to the paper's, the redrawn chart, the sensitivity results, and notes on anything that failed.

---

## Workbook entry (ready to paste)

**RQ1**
> Can we replicate the paper's findings, that most code refactorings only affect future changes for a short time when testing a smaller set of Java projects?

**RQ2**
> Does it transfer to a held-out project/refactoring family?

**Bounded sample / case IDs**
> RQ1: first 4 Move + 4 Rename cases from each of sling-whiteboard, incubator-tamaya-sandbox and ofbiz-framework (the 3 smallest projects with 12+ of each). RQ2: first 12 Move + 12 Rename cases from held-out project any23. Case IDs in the M1 plan.

**Method / metric or decision rule**
> Check 1: over half the cases last fewer than 10 later refactorings. Check 2: at least 10 of 12 recalculated cases match the paper (within 0.02). Both checks pass for both families = reproduced; Check 1 fails for both or fewer than 6 match = not reproduced; anything else = partly. RQ2 uses the same checks. Sensitivity: 1%, 5% and 10% cut-offs.

**Expected result before execution**
> RQ1: partly reproduced (most effects short, some numbers won't match). RQ2: partly transfers to any23. The cut-off won't change the answer.
