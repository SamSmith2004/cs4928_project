## Links
**Paper:** https://link.springer.com/article/10.1007/s10664-025-10801-3 <br>
**Repo Link:** https://zenodo.org/records/15209118

## Project Details
#### RQ1
Can we replicate the paper’s findings, that most code refactorings only affect future changes for a short time when testing a smaller set of Java projects? 
##### Bounded
Replicate 3 of the Java projects from the paper's 48 analysed project
##### Method
Collect commits and run pipeline on code
##### Expected Result
Partial reproduction of papers findings on our sample

#### RQ2 
Does the paper’s rule for ideal refactoring duration still hold true on modern Java code, and which refactoring choices give us the best code quality when handling new feature requests
##### Bounded
A manually selected seperate 3 projects which have recent(2024 or later)
##### Method
Collect recent commits and run same pipeline on code
##### Expected Result
Rule only weakly supported or not supported

