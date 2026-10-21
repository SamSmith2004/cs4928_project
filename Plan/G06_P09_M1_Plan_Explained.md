# Our M1 Plan, Explained Simply

This document explains our M1 plan (`G06_P09_M1_Plan.md`) in plain English. Read this first if the plan feels too technical. It doesn't replace the plan: the plan is what we submit and freeze.

---

## 1. The project in one paragraph

A group of researchers wrote a paper about **refactoring**. They looked at thousands of changes in real Java projects and asked: *after someone cleans up some code, how long does that clean-up keep affecting the code?* Our job is not to redo their whole study. We take **one small part** of it, check whether we get the same answer, and then check whether that answer also holds somewhere they didn't look closely.

---

## 2. The key ideas

### Refactoring
Changing code to make it cleaner **without changing what it does**. For example:
- **Moving** a method from one class to a class where it fits better.
- **Renaming** a variable from `x` to `customerAge` so it's easier to understand.

### Refactoring family
There are about 100 specific kinds of refactoring, so the paper groups them into 20 **families** by the first word of their name:
- The **Move** family: Move Method, Move Class, Move Attribute, and so on.
- The **Rename** family: Rename Method, Rename Variable, Rename Class, and so on.

We compare these two families. Move is a **big, structural** change (code changes location). Rename is a **small, local** change (only a name changes).

### Ripple effect (how long the effect lasts)
Think of dropping a stone in a pond. The ripples spread, then fade. A refactoring is the stone. The paper measures how long its "ripples" last by counting **how many later refactorings of the same kind happen in the same class** while the original change is still having an effect.

- If a class gets renamed things in it 3 more times afterwards, that refactoring's effect lasted **3**.
- The paper calls this the **ripple effect (RE) duration**.

### "Code still remaining"
Each time the class changes again, the paper checks **how much of the original code is still there**, as a number from 0 to 1:
- **1** = all of the original code is still there.
- **0.5** = about half of it is still there.
- **0** = none of it is left.

### The 1% rule
The paper says a refactoring's effect has **ended** once less than 1% of the original code remains (the number drops below 0.01).

### Case
One refactoring, in one class, followed through time. Each case has an ID in the paper's results file, like `15_0_move-method_ofbiz-framework-1-JWTManager`. That one means: a Move Method refactoring in the `JWTManager` class of the ofbiz-framework project.

### What the paper found
The effect of a refactoring **usually lasts fewer than 10 later refactorings**. A few last much longer: over 190.

---

## 3. Our two questions

**RQ1:** *Can we replicate the paper's findings, that most code refactorings only affect future changes for a short time when testing a smaller set of Java projects?*

In plain words: **if we only look at 3 projects, is it still true that most effects are short (under 10)?** And when we recalculate the paper's numbers ourselves, **do we get the same values?**

**RQ2:** *Does it transfer to a held-out project/refactoring family?*

In plain words: **do we get the same answer in a different project that RQ1 didn't use?** That project is called the **held-out** project. Ours is **any23**.

---

## 4. The sample (which data we use)

We can't check all 108,000 rows of the paper's data by hand, so we pick a **small sample**. The project calls this a **bounded sample**: it has fixed, clear limits.

### How we chose it

1. **Pick 3 projects.** We kept every project that has at least 12 Move cases and 12 Rename cases. Then we took the 3 smallest, because they're the quickest to work with:
   - sling-whiteboard
   - incubator-tamaya-sandbox
   - ofbiz-framework
2. **Pick cases from each project.** From each of the 3 projects, we took the **first 4 Move cases and first 4 Rename cases**. That gives **12 Move and 12 Rename** cases in total.
3. **Pick the held-out project for RQ2.** From the projects left over that also qualify, we took the first one alphabetically: **any23**. From it, we took the first 12 Move and first 12 Rename cases.

So we have **48 cases** in total: 24 for RQ1 and 24 for RQ2.

### Why "first" in a fixed order matters
"First" means sorted by case number, then class name, then date. We wrote the rule **before** looking at any results. This matters because:
- **Anyone can repeat it** and get exactly the same cases.
- **We can't cherry-pick** cases that happen to give the answer we want.

### Why 4 from each project instead of "the first 12"
The project brief suggests taking "the first 12" items. But if we took the first 12 across all 3 projects at once, **none** would come from incubator-tamaya-sandbox, and we'd really only be testing 2 projects. Taking 4 from each makes sure all 3 count. We record this change in the plan so the markers can see it.

---

## 5. The method (what we'll actually do)

1. **Set up** a clean Python environment and note the versions we use.
2. **Get the data:** the paper's results file (already in our repo) and the code history of each project (from the authors' download on Zenodo).
3. **Check the claim:** for each family, count how many of our cases have an effect shorter than 10. Redraw the paper's chart for Move and Rename.
4. **Recalculate the numbers:** for each of the 48 cases, work out "how much original code remains" after each later change, using **the authors' own code**. Then compare our numbers with the paper's.
5. **Compare Move and Rename:** say which family's effects last longer in our sample. With only 12 cases each, this is a description, not proof.
6. **Sensitivity check** (explained in Section 7).
7. **Save everything** in the repo: every script and every output. No editing results by hand.

---

## 6. How we decide the answer

We use **two checks**, done separately for Move and for Rename.

**Check 1 (is the claim true for our sample?)**
More than half of the family's cases have an effect that lasts fewer than 10 later refactorings.

**Check 2 (do our numbers match the paper's?)**
At least 10 of the 12 cases match. A case "matches" if every number we recalculate is within 0.02 of the paper's number (e.g. the paper says 0.85 and we get anything from 0.83 to 0.87).

### Putting them together

| Result | What has to happen |
|---|---|
| **Reproduced** | Both checks pass for both Move and Rename |
| **Not reproduced** | Check 1 fails for both families, **or** fewer than 6 cases match in either family |
| **Partly reproduced** | Anything in between |

RQ2 uses exactly the same checks, just on the any23 cases.

### An imaginary example (not real results)
Say that for Move, 9 of 12 cases are under 10 (Check 1 passes), and 11 of 12 match the paper (Check 2 passes). For Rename, 8 of 12 are under 10 (Check 1 passes), but only 7 of 12 match (Check 2 is in the 6–9 range). Then the answer is **partly reproduced**.

### What if it fails?
That's fine. The brief says a failed or partial reproduction **can still get high marks** if our method and evidence are solid. What matters is that we report honestly and don't change the method afterwards to get a better match.

---

## 7. The sensitivity check

A **sensitivity check** asks: *if we change one setting, does our answer change?*

The setting we test is the **1% rule**. The paper says an effect ends when less than 1% of the original code remains, but when we read the authors' code, **it doesn't actually use this rule**: in their data, 829 cases keep going after dropping below 1%.

So we'll try stopping each effect when the remaining code drops below **1%, 5% and 10%**, and see how much the results change.

Stopping effects earlier can only make them **shorter**, so this can't make Check 1 fail. What we report is **how much** the numbers change. If our answer stays the same at every setting, we call it **robust**.

---

## 8. What we expect, and why we write it down first

We have to write our expected result **before** running anything. This is called **preregistration**. It stops anyone, including us, from quietly changing the story after seeing the results.

Our expectations:
- **RQ1: partly reproduced.** We think most effects will be short, but some of our recalculated numbers won't match. One reason: when the authors' code can't find a file (for example because it was renamed), it records 0 instead of "missing".
- **RQ2: partly transfers.** We expect the same kind of result in any23.
- **Sensitivity check:** effects will get shorter at higher cut-offs, but our answer won't change.

If we turn out to be wrong, that's fine. It's a finding, and we report it.

---

## 9. Things we noticed before starting

These come from reading the authors' files and code. They're useful to mention in our report, because spotting problems is part of the job.

1. **The paper counts rows, not cases.** In the paper's results file, a case that lasts 20 refactorings takes up 20 rows; a case that lasts 1 takes up 1 row. The paper's summary numbers count rows, so long cases count many times. It's like averaging class sizes by asking every student how big their class is: big classes get asked more often, so the average looks bigger than it is.
2. **The 1% rule isn't used in their code** (see Section 7).
3. **Missing files count as 0.** "We couldn't find the file" is recorded the same as "none of the code is left".
4. **47 projects, not 48.** The paper says 48, but the data has 47 names, and two of them look like the same project under an old and new name.
5. **Cases are bunched together.** For example, all 4 ofbiz-framework Move cases are in the same class on the same day, so they aren't fully independent of each other.

---

## 10. Where we differ from the project pack

- **RQ1 wording** is our group's own, not the pack's suggested wording. We keep it small by using only 3 projects and 2 families.
- **4 cases per project** instead of "the first 12", so every project is included (see Section 4).
- **We don't rerun the authors' whole tool.** We use their published results and recalculate a small number of cases. The pack recommends this.

---

## 11. What happens next

1. **Everyone reads the plan** and agrees with it, especially the numbers (0.02 for matching, 10 of 12 and 6 of 12).
2. **Paste the workbook text** into the Student Tracker under Week 5.
3. **Freeze it:** commit the plan to the repo and tag it `M1_PLAN`.
4. **Only then** start downloading data and running the analysis.

---

## Quick glossary

| Word | Meaning |
|---|---|
| **Refactoring** | Cleaning up code without changing what it does |
| **Family** | A group of related refactorings (e.g. all the "Move" ones) |
| **Case** | One refactoring in one class, followed over time |
| **Ripple effect (RE)** | How long a refactoring keeps affecting the code, counted in later refactorings |
| **Bounded sample** | A small, clearly limited set of data we study |
| **Held-out project** | A project we keep aside to test whether the result holds elsewhere |
| **Reproduce** | Do the same thing and check we get the same answer |
| **Preregistration** | Writing down our plan and expected result before we start |
| **Sensitivity check** | Changing one setting to see if the answer changes |
| **Robust** | The answer stays the same when we change the setting |
| **Freeze / tag** | Lock the plan in git so it can't be quietly changed later |
