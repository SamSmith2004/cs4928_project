# Replication package for the Empirical Software Engineering (EMSE) Journal submitted article: *"Analyzing the Ripple Effects of Refactoring"*

This is a replication package and online appendix for the EMSE Journal paper "In Search of Metrics to Guide Developer-Based Refactoring Recommendations".

## Contents

This repository contains the following:

- [INSTALL](INSTALL.md): Detailed installation instructions for each of the used tools as well as the required Python dependencies.

- [Figures](Figures/): Graphical content shared in the manuscript.
  - [Appendix](Figures/Appendix/):
    - [posterior-update.pdf](Figures/Appendix/posterior-update.pdf): Lineplot displaying the posterior probability distribution of a refactoring showing scarcity in its Ripple Effect.
  - [Background](Figures/Background/):
    - [ripple-example-vert.pdf](Figures/Background/ripple-example-vert.pdf): Graphical representation of the theoretical idea on the Ripple Effect applied to the context of refactoring activity
  - [Results](Figures/Results/):
    - [data-analysis-diagram.pdf](Figures/Results/data-analysis-diagram.pdf): Workflow diagram on the data analysos process undergone in the study.
  - [RQ1](Figures/RQ1/):
    - [LCSDistribution.pdf](Figures/RQ1/LCSDistribution.pdf): LCS Distribution by RE duration quartiles.
    - [RQ1 - Ripple Effect Distribution by Macro Type - With Lines and Outliers.pdf](Figures/RQ1/RQ1%20-%20Ripple%20Effect%20Distribution%20by%20Macro%20Type%20-%20With%20Lines%20and%20Outliers.pdf): LCS Distribution considering outliers.
    - [RQ1_RT-NoRef.pdf](Figures/RQ1/RQ1_RT-NoRef.pdf): Distribution of RE duration by refactoring family type.
  - [RQ2](Figures/RQ2/): 
    - [CPDistribution.pdf](Figures/RQ2/CPDistribution.pdf): Change Proneness Distribution by RE duration quartiles.
    - [DPDistribution.pdf](Figures/RQ2/DPDistribution.pdf): Defect Proneness Distribution by RE duration quartiles.
  - [RQ3](Figures/RQ3/):
    - [cpeloc.pdf](Figures/RQ3/cpeloc.pdf): Change Efficiency Distribution by RE duration quartiles.
  - [Study Design](Figures/StudyDesign/):
    - [data-collection-diagram.pdf](Figures/StudyDesign/data-collection-diagram.pdf): Workflow diagram on the data collection process undergone in the study.
    - [Workflow.pdf](Figures/StudyDesign/Workflow.pdf): Workflow diagram on the study design process undergone in the study.
    - [creation-year-hist.pdf](Figures/StudyDesign/creation_year_hist.pdf): Histogram displaying the distribution of the study context projects based on their creation year.
    - [progression-per-age.pdf](Figures/StudyDesign/progression_per_age.pdf): Stacked Ridge plot on multiple software attributes distributed in projects with different age. 


- [Data](Data/) A folder containing all raw data extracted
  - [Commits Diff](Data/commits_diff/): Contains the commit diff data between the subsequent refactoring commits per mined project.
  - [Commits Hash](Data/commits_hash/): Contains the list of commits with detected refactoring activity per mined project.
  - [Issues](Data/issues/): Contains the list of issues repported per mined project.
  - [Refactor Types](Data/refactor_types/): Contains the list of detected refactoring types with their global counts per mined project.
  - [Refactoring Commits](Data/refactoring_commits/): Contains the list of commits with detected refactoring activity per mined project with the mined refactoring content retrieved from RefactoringMiner.
  - [RefactoringMiner Output](Data/refactoring_miner_output/): Raw RefactoringMiner output.
  - [Zipped analyzed software repositories](Data/sw-repositories.zip): Zipped folder with the software repositories cloned at the stage this study was executed
  - [Unique projects](Data/unique_projects.json): List of unique project full names from the PANDORA dataset (The  original dataset did not provide a clean list of projects so we made it removing the duplicates)
  - [change_proneness_data](Data/change_proneness_data/): Contains the output files from the change and defect proneness calculation process per analyzed project.
  - [dev_effort_data](Data/dev_effort_data/): Contains the output files from the Developer's effort calculation process per analyzed project
  - [merged_results](Data/merged_results/): Contains the output files from the two previous computation projects merged per analyzed project.
  - [global_refactoring_counts.json](Data/global_refactoring_counts.json): Contains the summary refactoring counts from all the projects.
  - [mined_total_commit_counts.json](Data/mined_total_commit_counts.json): Contains the summary counts of commits that reported refactoring activity according to RefactoringMiner.
  - [project_refactoring_stats.json](Data/project_refactoring_stats.json): Contains summary counts per project regarding the **number of commits analyzed**, **number of refactorings analyzed**, **number of refactorings with RE persistence history**.
  - [basic_statistics_table.csv](Data/basic_statistics_table.csv): Reports summary counts for all the initially considered projects in the study context. These counts include attributes such as Commits, Issues, GitHub Stars, ... among others in order to describe the shape of the project being analyzed in this study.
  - [descriptive_stats_table.csv](Data/descriptive_stats_table.csv): Reports the summary descriptive statistics resulting from the ```basic_statistics_table.csv``` table, and displayed in the manuscript.


- [Results](Results): Data files containing the analyzed results to answer the Research Questions.
  - [Raw results](Results/cross_project_raw_results.csv): CSV file with the raw results from the analyzed refactoring cases, it contains the majority of the mined data into one single file.
  - [RQ1](Results/RQ1/): *"To what extent does the RE of a refactoring activity persist in code?"* 
    - [LCSDistribution.jrp](Results/RQ1/LCSDistribution.jrp): JMP analysis file to compute RQ1.
    - [Hypothesis Testing](Results/RQ1/Hypothesis%20Testing/):
      - [RefactoringFamilyTypeDunn.xlsx](Results/RQ1/Hypothesis%20Testing/RefactoringFamilyTypeDunn.xlsx): Resulting outcome from the Dunn's test on the Refactoring Family significance.
      - [RefactoringFamilyVSREjmp.jmp](Results/RQ1/Hypothesis%20Testing/RefactoringFamilyVSREjmp.jmp): JMP analysis table file with the hypothesis testing on the impact of the refactoring family over the RE.
      - [RefactoringFamilyVSREjmp.xlsx](Results/RQ1/Hypothesis%20Testing/RefactoringFamilyVSREjmp.xlsx): Resulting outcome from the hypothesis testing on the impact of the refactoring family over the RE.
  - [RQ2](Results/RQ2/): *"What is the long-term effect of refactoring on change and defect proneness?"*
    - [CPDistribution.jrp](Results/RQ2/CP%20Distribution.jrp): JMP analysis file to compute RQ2 on the impact of the refactoring effect on the change proneness.
    - [DPDistribution.jrp](Results/RQ2/DPDistribution.jrp): JMP analysis file to compute RQ2 on the impact of the refactoring effect on the defect proneness.
    - [Hypothesis Testing](Results/RQ2/HT/):
      - [CP.xlsx](Results/RQ2/HT/CP.xlsx): Results from the hypothesis testing performed on the impact of the refactoring effect on the change proneness.
      - [DP.xlsx](Results/RQ2/HT/DP.xlsx): Results from the hypothesis testing performed on the impact of the refactoring effect on the defect proneness.
      - [Spearman.xlsx](Results/RQ2/HT/Spearman.xlsx): Spearman Rho correlation test between the RE, and CP and DP.
  - [RQ3](Results/RQ3/): *"What is the benefit/effort ratio of long-term refactoring?"*
    - [cpeloc.jrp](Results/RQ3/cpeloc.jrp): JMP analysis file to compute RQ3 on the impact of the RE on the benefit/effort ratio for performing refactoring activity.
    - [HT.xlsx](Results/RQ3/HT.xlsx): Results from the hypothesis testing performed 
- [Scripts](Scripts): A folder containing all the scripts.
  - [```components/```](Scripts/components): Contains utils leveraged during the project and main Scripts to run the RefactoringMiner initial data collection. 
    - [```utility.py```](Scripts/components/utility.py): Script with the common global variables used all over the rest of scripts.
    - [```refactoring_miner.py```](Scripts/components/refactoring_miner.py): Script dedicated to the Refactoring Activity Mining with RefactoringMiner.
    - [```its_miner.py```](Scripts/components/its_miner.py): Script dedicated to the Issue Tracking System data mining.
    - [```get_commit_diff.py```](Scripts/components/get_commit_diff.py): Version control miner for commit diff extraction.
    - [```get_github_url.py```](Scripts/components/get_github_url.py): Script to obtain GitHub repository URL links.
    - [```helper.py```](Scripts/components/helper.py): Scriopt dedicated to support scripts with shared help functions.
  - [```00_main.py```](Scripts/00_main.py`): Performs initial refactoring data with RefactoringMiner.
  - [```01_proneness_calculator.py```](Scripts/01_proneness_calculator.py): Calculated the change and defect proneness of the mined refactorings over the entire change history of the analyzed projects. 
  - [```02_get_bcp.py```](Scripts/02_get_bcp.py): Calculates the Ripple Effects of the analyzed refactorings through Bayesian Conditional Probability and LCS approach.
  - [```03_dev_effort.py```](Scripts/03_dev_effort.py): Calculates the Change Efficiency detected during the refactoring posterior lifetime of the code in the analyzed Java class.
  - [```04_merge_crossproject_data.py```](Scripts/04_merge_crossproject_data.py): Merges the collected data per projects into a cross-project dataset. 
  - [```05_bcp_example_collector.py```](Scripts/05_bcp_example_collector.py): Script utilized to mine the specific commit data for the example provided in the Appendix.
  - [```06_summary_statistics.py```](Scripts/06_summary_statistics.py): Script utilized to create ```basic_statistics_table.csv``` table with the software attributes from the initialized considered projects.
  
- [Appendix example](appendix_example): A folder containing all the content generated to provide the demonstration in Appendix B section of the manuscript.

    - [```bcp-examples.R```](appendix_example/bcp-examples.R): R codes to replicate the results presented in the example.
    - [```metadata_jmeter.csv```](appendix_example/metadata_jmeter.csv): Metadata in CSV displaying the input data used for the implementation of this example.
    - [```metadata_jmeter.xlsx```](appendix_example/metadata_jmeter.xlsx): Metadata in XLSX displaying the input data used for the implementation of this example.
    - [```posterior-update.pdf```](appendix_example/posterior-update.pdf): Figure demonstrating the progression of the analyzed example refactoring.


## License

All generated data is provided under [Creative Commons 4.0 Attribution License](DATA_LICENSE).

All scripts are provided under the [MIT License](SCRIPT_LICENSE).

All the analysed projects must be used in accordance with their respective licenses (shared in each project when applicable).


## Running the code
NOTE 1: Please, find the `DATA_PATH` global variable in the `components/utility.py` script and define the path where the program should create all the needed results.
The logic would be that you provide the base path is the location of this replication package in your machine, and you add `data` as the location for the data files.

NOTE 2: The different stages of the study execution are splitted in the ```main.py``` script, from the boolean definitions in
```commons.py``` practitioners can decide which stages want to be manipulated or re-executed again without affecting the other stages.
For a complete execution, set all the boolean global variables to ```True```

### Stage 1: ```MAIN```

Executes script ```00_main.py``` for running the initial data collection incorporating the following sub-steps:

- Gets the unique projects from the source dataset.
- Collects issue-tracking systems' data from GitHub.
- Collects commits from GitHub.
- Clones the repository to be analyzed.
- Runs Refactoring Miner to mine all the refactoring data.

Creates the following directories and files within the path ```DATA_PATH/output_data/```:

- ```average_time_between_refactorings/```
- ```commits_diff/```
- ```commits_hash/```
- ```developers_effort/```    
- ```interefactoring_commit_period/```  
- ```issues```
- ```refactoring_types```
- ```refactoring_commits```
- ```refactoring_miner_output```
- ```sample_refactoring_commits```
- ```project_commit_hashes.json```
- ```split_project_commit_hashes.json```
- ```unique_projects.json```

### Stage 2: ```CALCULATING DEFECT PRONENESS AND CHANGE PRONENESS```

Executes script ```01_proneness_calculator.py``` for running the initial data collection incorporating the following sub-steps:

- Reorders and locates the refactoring data and mined commits for each project.
- Calculates the change proneness and defect proneness for each refactoring case (therefore, commits in which it was introduced and Java class affected).
- Makes logs for each of the projects, therefore connecting the execution with ```proneness_status_monitoring.py```.

Creates the following directories and files within the path ```DATA_PATH/```:

- ```change_proneness_data/```
- ```change_proneness_data/{project_name}```
- ```change_proneness_data/{project_name}/proneness_results.csv```
- ```change_proneness_data/{project_name}/proneness_results.pkl```
- ```change_proneness_data/{project_name}/ordered_commits.csv```
- ```change_proneness_data/{project_name}/ordered_commits.pkl``` 
- ```change_proneness_data/{project_name}/ordered_refactorings.csv```
- ```change_proneness_data/{project_name}/ordered_refactorings.pkl```
- ```change_proneness_data/{project_name}/processed_refactorings.txt```
- ```change_proneness_data/{project_name}/class_change_history``` 
  - NOTE on this last directory, each existing CSV file consists on the class history change of each refactoring mined by 
RefactoringMiner in each mined repository accordingly. This helped on making sure that the same class was being analyzed even if it was renamed or changed of path afterwards. Let's dive into a sample file:
    - Sample CSV file name: ```id1_id2_refactoring-type_project-name```:
      - ```id1```: Refactoring identifier, it basically provides raw id counting the order of analyzed refactorings 
      - ```id2```: Refactoring **type** identified, it counts the number of times a refactoring of the same type as the concerning file has been analyzed so far 
      - ```refactoring-type```: Lowered name of the refactoring type.
      - ```project-name```: Lowered project name.

#### Logic behind Change Proneness calculation:
(The notation will follow the one used in the final table so that the reader finds it easier to relate each process with the final outcome)
- ```cp```: Or "Raw Change Proneness", depicts the changes performed in the affected class in a commit where the same refactoring type was applied on the affected class as compared to the previous similar case. Therefore the first case in the table will provide the number of changes made in the class as compared to the refactoring commit mined by RefactoringMiner in that class, the second row will provide the changes based on the source code of the class at the history point of the first row case, and so on and so forth. 
&nbsp;

<div align="center">

$$
\displaystyle \mathcal{C}(R_{i}, r_{j}) ={\nu_\mathcal{C}(R_{i})}_{r_{j-1} \rightarrow r_{j}}
$$
</div>

- ```cp/eloc```: "Or Adjusted Change Proneness", depicts the same metric as before but is adjusted based on the **effective lines of code** found in that Java class (extracted from [SCC](https://github.com/boyter/scc)). So the formula would be rewritten as follows:
&nbsp;

<div align="center">

$$
\displaystyle \mathcal{C}(R_{i}, r_{j}) = \frac{{\nu_\mathcal{C}(R_{i})}_{r_{j-1} \rightarrow r_{j}}}{ELOC_j}
$$
</div>

#### Logic behind Defect Proneness calculation:

- Performs _fuzzy matching_ of regular expressions based on the commonly used issue tickets in Issue Tracking Systems such as [GitHub](https://github.com) or [JIRA](https://www.atlassian.com/software/jira). The patterns are:
  - ```[A-Z]{2,}-\d+```
  - ```\d{4,}```
  - ```#\d+```

If the pattern is found in the commit message, we consider it a defect-inducing commit, and approximately refactoring as well (note this is a best effort).


### Stage 3: ```CALCULATING THE RIPPLE EFFECTS```

- We mainly used two approaches, implemented in the script ```02_get_bcp.py```:<br />
<br />
  - Bayesian Probability Approximation (```bayesian_remaining_probs```):
    - At each refactoring commit where the same Java class has been affected by the same refactoring type as the one collected by Refactoring Miner **a fraction of the class is modified**
    - The **new cumulative probability of change** accounts for both previous codifications and the **new changes introduced** in the current commit.
    - The **remaining probability** tracks how much of the **original code still exists over time** through probabilistic approximation.

    <div align="center">

       $$
       \displaystyle P_c = 1 - (1 - P_{c_{prev}}) \times (1 - CR)
       $$

       </div>

       where:
       - $P_c$ is the **cumulative probability of change** at the current commit,  
       - $P_{c_{prev}}$ is the **cumulative probability of change** from the previous step,  
       - $CR$ is the **change ratio** (i.e., proportion of modifications in the file).<br />
<br />
  - Longest Common Subsequence (LCS) Approach (```lcs_remaining_probs```) ([more info](https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://en.wikipedia.org/wiki/Longest_common_subsequence%23:~:text%3DA%2520longest%2520common%2520subsequence%2520(LCS,positions%2520within%2520the%2520original%2520sequences.&ved=2ahUKEwjBtMb6wfWLAxXILBAIHQ37ABMQFnoECB4QAw&usg=AOvVaw2a1x3UXrbzTsknFGxuzrKs)))
    - Def: A LCS is the longest subsequence common to all sequences in a set of sequences.
    - For each commit $r_j$, the probability of original code persistence is computed as:
    
    <div align="center">

    $$
    \displaystyle P_r = S = \frac{|LCS(A, B)|}{\max(|A|, |B|)}
    $$

    </div>

    where:
    - $P_r$ is the **posterior probability of code persistence**,
    - $S$ is the **LCS similarity ratio** (same as in `compute_similarity`),
    - $A$ represents the **original file content at refactoring commit**,
    - $B$ represents the **modified file content at commit $r_j$**.

- The files created within the ```DATA_PATH``` directory in this stage are the following ones:

  -  ```change_proneness_data/{project_name}/bcp_proneness_results.csv```
  -  ```change_proneness_data/{project_name}/bcp_results.pkl```
  - ```bcp_logs/{project_name}.log```
  - ```bcp_estimation_global.log```

- Similarly, during the process the script ```bcp_status_monitoring.py``` can be launched to get hourly reports on the process.

### Stage 4: ```CALCULATING DEVELOPER'S EFFORT```

- Here as well, we mainly used two approaches, implemented in the script ```03_dev_effort.py```:<br />
<br />

  - **Inter-Refactoring Touched Lines of Code (```tloc```)**

    - Anchored on the initial refactoring commit mined by Refactoring Miner, it collects the TLOC from each subsequent refactoring of the same type that affected the same Java class.
    - It continues this approach with all subsequent cases, always compared to the anchored refactoring commit version of the Java class.

    <div align="center">
      
      $$
      \displaystyle TLOC = \sum_{k=i}^{j} \left( |A_k| + |D_k| \right)
      $$

    </div>

    - where

	    - $|A_k|$  represents the number of added lines in commit  $k$ ,<br />
	    - $|D_k|$  represents the number of deleted lines in commit  $k$ ,<br />
	    - The summation considers all commits from  $R_i$  to  $R_j$ .
      - **NOTE**: In the results table the summation won't be applied, so each cell in the column will only resemble the actual TLOC in each commit, therefore for the total, the summation should be done.

  - **RAW Inter-Refactoring Touched Lines of Code (```raw_tloc```)**

    - It focuses on each subsequent refactoring commit made to the same class with the same refactoring type and computes the TLOC based on the parent commit.
    - Therefore the computation would be as follows:

    <div align="center">

    $$
    \displaystyle Raw TLOC = |A_i| + |D_i|
    $$

    </div>

    - where:
	    - $|A_i|$  represents the number of added lines in commit  $R_i$ ,
	    - $|D_i|$  represents the number of deleted lines in commit  $R_i$ .
    - **NOTE**: A summation could be done here as well, but for the definition of this metric it doesn't make that much sense. 

- The files created within the ```DATA_PATH``` directory in this stage are the following ones:

  -  ```dev_effort_data/{project_name}.csv```
  -  ```dev_effort_data/{project_name}.pkl```
  - ```dev_effort_logs/{project_name}.log```
  - ```dev_effort_global.log```

### Stage 5: ```GENERATING THE FINAL RESULTS FILE```

- Simple as merging the generated results so far into the same file per per project (```DATA_PATH/merged_results/{projec_name}_merged.csv```)
- And then a global merge for all projects ending into ```DATA_PATH/cross_project_raw_results.csv```
- The rest of the analysis is done through the JMP Software (more info [here](https://www.jmp.com/en/home))

### Stage 6: ```MINING DATA FOR APPENDIX EXAMPLE```

- Small script to gather and build the content displayed in the Appendix to demonstrate the limitations of the Bayesian BCP approach in some corner cases of the study context.

- Following the execution of the Python script ```05_bcp_example_collector.py```, the user should execute the commands on the R Script ```bcp_example.R```

### Stage 7: ```GENERATING SUMMARY STATISTICS```

- The script ```06_summary_statistics.py``` generates the table with the set of summary attributes describing the shape of each considered project in the study context, the output table can be found in ```basic_statistics_table.csv```.
- For an aggregated display of summary descriptive statistics, you can run ```summary-statistics.R``` script in order to retrieve table ```descriptive-stats-table.csv```, visible in the Study Context section of the manuscript.