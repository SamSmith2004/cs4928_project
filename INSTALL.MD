# Installation guide

This file contains instructions on how to install and run each tool used in the data gathering process.

## External CMD tools to be installed for the analysis

The following study required the use of a series of external tools, used explicitly through the ```subprocess``` Python module in order to use
CMD tools within the code execution.

## SCC (*Sloc Cloc and Code*)

A tool to "*For counting the lines of code, blank lines, comment lines, and physical lines of source code in many programming languages.*"

It supports installation in different OS, as a CMD tool, as well as deploying it in Docker.
In order to follow the replication of our study, we recommend the reader to read the following instruction points:

### ```Install```
### ```Usage```

**Link**: https://github.com/boyter/scc \
**Reference**: Boyter (no date) Boyter/SCC: SLOC, Cloc And Code: SCC is a very fast accurate code counter with complexity calculations and Cocomo estimates written in pure go, GitHub. Available at: https://github.com/boyter/scc (Accessed: 06 March 2025). 

## RefactoringMiner

"_RefactoringMiner is a library/API written in Java that can detect refactorings applied in the history of a Java project._"

It supports its usage in different OS as well, and we used it as a CMD tool. We recommend the reader to follow the instructions 
in the following sections of the tool's README file.

### ```How to build RefactoringMiner```
- Be sure to have installed at least Java 17 and Gradle 7.4 (At least at the time we run the study)

### ```How to run RefactoringMiner from the command line```
- Make sure to follow the instructions in this section, and test the tool with a toy repository in the terminal before running the code.

### Additional note on the use of RefactoringMiner

This study explores projects with a large number of commits, therefore the task executed by RefactoringMiner is **notably** memory intensive.
Therefore, we suggest the reader to check the computational power of the machine in which our study will be replicated and follow the next instructions:

- Go to the binaries file within RefactoringMiner tool directory, such file should be in either of the following two paths:
  - ```../build/scripts/RefactoringMiner```
  - ```../bin/RefactoringMiner```

- Look for the ```DEFAULT_JVM_OPTS``` and ```MAX_FD``` attributes and set them as follows:
  - ```DEFAULT_JVM_OPTS="-Xmx57G - Xms28G"``` 
    - Adjust the number with -Xmx for the maximum allowed memory usage (We suggest 80% of your's machine's capability, ONLY AND ONLY IF this machine is not going to have more uses) 
    - Adjust the number with -Xms for the initial amount of memory it wants to be provided to the Java process launched when using this tool.
  - ```MAX_FD=maximum``` to use the maximum available.

If RefactoringMiner still crashes due to heap space limit issues, we suggest the reader to split the version control history of the project in different chunks in order to feed RefactoringMiner with each chunk at a time.

**Link**: https://github.com/tsantalis/RefactoringMiner \
**Reference**: 
Tsantalis, N., Ketkar, A., & Dig, D. (2022). RefactoringMiner 2.0. IEEE Transactions on Software Engineering, 48(3), 930-950.


## Environment Prerequisites

Running the code requires Python3.9. See installation instructions [here](https://www.python.org/downloads/).
The dependencies needed to run the code are all listed in the file `requirements.txt`. They can be installed using pip:
```pip install -r requirements.txt```. Such requirements include classic statistics and ML libraries such as _scikit-learn_, _scipy_ or _statsmodels_ among others.

You might also want to consider using [virtual env](https://packaging.python.org/guides/installing-using-pip-and-virtualenv/). Which we did.