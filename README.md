## Links
**Paper:** https://link.springer.com/article/10.1007/s10664-025-10801-3 <br>
**Repo Link:** https://zenodo.org/records/15209118

## Project Details
#### RQ1
Can we replicate the paper’s findings, that most code refactorings only affect future changes for a short time when testing a smaller set of Java projects?
##### Bounded
First 4 Move + 4 Rename cases from each of sling-whiteboard, incubator-tamaya-sandbox and ofbiz-framework (the 3 smallest projects with 12+ of each)
##### Method
Check 1: over half the cases last fewer than 10 later refactorings. Check 2: at least 10 of 12 recalculated cases match the paper (within 0.02). 
Both checks pass for both families = reproduced; Check 1 fails for both or fewer than 6 match = not reproduced; anything else = partly. 
##### Expected Result
Partly reproduced (most effects short, some numbers won’t match)

#### RQ2 
Does it transfer to a held-out project?
##### Bounded
First 12 Move + 12 Rename cases from held-out project any23. Case IDs in the M1 plan.
##### Method
Uses the same checks. Sensitivity: 1%, 5% and 10% cut-offs.
##### Expected Result
Partly transfers to any23. The cut-off won’t change the answer.
