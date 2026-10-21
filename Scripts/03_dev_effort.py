"""
Calculates the developer effort in terms of touched lines of code in two diverse approaches.

- Calculates the TLOC considering the inter-refactoring changes
- Calculates the TLOC only in the refactoring commits considering the previous commit.
"""

from concurrent.futures import ProcessPoolExecutor
import pydriller
from tqdm import tqdm
from functools import partial
import os
import pandas as pd
from git import Repo
import git
from components.utility import (DATA_PATH, clone_repo, delete_repo, get_study_repos, write_csv_from_dict, setup_logger)
import logging
from datetime import datetime
import pickle
import sys

GLOBAL_LOG_FILE = os.path.join(str(DATA_PATH), "dev_effort_global.log")
GLOBAL_LOGGER = logging.getLogger("GLOBAL")
GLOBAL_LOGGER.setLevel(logging.INFO)
global_handler = logging.FileHandler(GLOBAL_LOG_FILE, mode='w')
global_handler.setFormatter(logging.Formatter('%(asctime)s - %(processName)s - %(funcName)s - %(levelname)s - %(message)s'))
GLOBAL_LOGGER.addHandler(global_handler)


def get_tloc(path_to_repo, first_hash, second_hash, class_path):
    """

    :param path_to_repo:
    :param first_hash:
    :param second_hash:
    :return:
    """
    repo = Repo(path_to_repo)
    assert not repo.bare
    total_tloc = 0
    for c in pydriller.Repository(path_to_repo=str(path_to_repo),
                                  from_commit=first_hash,
                                  to_commit=second_hash).traverse_commits():


        for mod_file in c.modified_files:
            try:
                old_path = os.path.normpath(mod_file.old_path) if mod_file.old_path else None
                new_path = os.path.normpath(mod_file.new_path) if mod_file.new_path else None
            except Exception as e:
                old_path, new_path = None, None  # Ensure paths are valid

            # Check if this file is the class of interest
            if new_path == os.path.normpath(class_path) or old_path == os.path.normpath(class_path):

                # Handle potential None values for added and deleted lines
                added = mod_file.added_lines if mod_file.added_lines is not None else 0
                deleted = mod_file.deleted_lines if mod_file.deleted_lines is not None else 0

                # Compute the total lines of code changed in this commit
                tloc = abs(added) + abs(deleted)
                total_tloc += tloc  # Accumulate changes

    return total_tloc


def get_class_path(class_id,refactoring_id, repo_name):
    """

    :param class_id:
    :param refactoring_id:
    :param repo_name:
    :return:
    """

    csv_path = DATA_PATH / "change_proneness_data" / repo_name / "class_change_history" / refactoring_id
    class_id_df = pd.read_csv(csv_path)
    result = class_id_df.loc[class_id_df['classID'] == class_id, 'full-path']
    return result.iloc[0]


def get_parent_hash(repo_path, commit_hash):
    """
    Given a commit hash, retrieve the previous commit in the version control history.

    :param repo_path: Path to the local git repository.
    :param commit_hash: The commit hash to find the parent for.
    :return: The hash of the previous commit or None if it's the first commit.
    """
    repo = git.Repo(repo_path)

    commit = repo.commit(commit_hash)  # Get the commit object
    if commit.parents:
        return commit.parents[0].hexsha


def inter_refactoring_tloc(repo_path, input_path, repo_logger):
    """

    :param repo_path:
    :return: table header {"refactoring_id", "next_refactoring_hash", "tloc_until_then"}
    """

    # tloc: Inter-refactoring tloc quantification, where all the changes in the given class between the two refactoring
    # commits are considered.
    # raw_tloc: TLOC is only calculated in the considered refactoring commit based on the changes between the refactoring
    # commit and its parent commit.

    # Handle checkpointing for saving already done work
    project_name = os.path.basename(repo_path)
    pickle_path = DATA_PATH / "dev_effort_data"
    if os.path.exists(os.path.join(str(pickle_path), f"{project_name}.csv")):
        repo_logger.info(f"Repository {project_name} already processed, skipping")
        GLOBAL_LOGGER.info(f"Repository {project_name} already processed, skipping")
        with open(os.path.join(str(pickle_path), f"{project_name}.pkl"), "rb") as f:
            output_dict = pickle.load(f)
        return output_dict

    if os.path.exists(os.path.join(str(pickle_path), f"{project_name}.pkl")):
        with open(os.path.join(str(pickle_path), f"{project_name}.pkl"), "rb") as f:
            output_dict = pickle.load(f)
    else:
        output_dict = {"idx": [], "project_id": [], "refactoring_id": [], "next_refactoring_hash": [], "class_id": [],
                       "tloc": [], "raw_tloc": []}


    project_input_data_path = input_path / project_name
    # Data with the proneness results
    proneness_df = pd.read_csv(project_input_data_path / "proneness_results.csv")
    refactoring_ids_from_proneness_data = proneness_df["refactoring_id"].tolist()
    hashes_from_proneness_data = proneness_df["hash"].tolist()
    class_ids_from_proneness_data = proneness_df["class_id"].tolist()

    # Data with the initial mined refactoring types/hashes
    initial_refactorings_df = pd.read_csv(project_input_data_path / "ordered_refactorings.csv")
    initial_refactoring_hashes = initial_refactorings_df["hash"].tolist()

    # TRAVERSE LOGIC: We anchor the loop on the proneness results. Through the refactoring ID of this table we fetch the first
    # commit from the RMiner output and start calculating the tloc based on that.
    current_refactoring_idx = ""
    previous_hash = ""

    repo_logger.info(f"Starting traverse logic for repo {project_name}")
    GLOBAL_LOGGER.info(f"Starting traverse logic for repo {project_name}")
    already_computed_cases = output_dict["idx"]
    for i in range(len(refactoring_ids_from_proneness_data)):

        if i in already_computed_cases:
            repo_logger.info(f"Index case {i} already computed for repo {project_name}")
            GLOBAL_LOGGER.info(f"Index case {i} already computed for repo {project_name}")
            continue

        # First we start with the logic for the inter-refactoring "tloc" approach
        refactoring_id = refactoring_ids_from_proneness_data[i]
        id_prefix = refactoring_id.split("_")[0]
        class_path = get_class_path(class_id=class_ids_from_proneness_data[i],refactoring_id=refactoring_id, repo_name=project_name)
        if current_refactoring_idx != id_prefix:  # If we are moving into a different mined refactoring case.
            current_refactoring_idx = id_prefix
            anchor_hash = initial_refactoring_hashes[int(id_prefix)]
            subsequent_refactoring_hash = hashes_from_proneness_data[i]
            repo_logger.info(f"Getting tloc from different refactoring case {current_refactoring_idx}")
            GLOBAL_LOGGER.info(f"Getting tloc from different refactoring case {current_refactoring_idx} for repo {project_name}")
            try:
                tloc = get_tloc(path_to_repo=repo_path, first_hash=anchor_hash, second_hash=subsequent_refactoring_hash,
                                class_path=class_path)
            except Exception as e:
                repo_logger.info(f"Failed getting tloc from different refactoring case {current_refactoring_idx} with error {e}")
                GLOBAL_LOGGER.info(f"Failed getting tloc from different refactoring case {current_refactoring_idx} for repo {project_name} with error {e}")
                sys.exit(1)

            previous_hash = subsequent_refactoring_hash  # Will change also kin the other scenario
        else:  # If we are still within the same refactoring case

            anchor_hash = previous_hash
            subsequent_refactoring_hash = hashes_from_proneness_data[i]
            repo_logger.info(f"Getting tloc from same refactoring case {current_refactoring_idx}")
            GLOBAL_LOGGER.info(f"Getting tloc from same refactoring case {current_refactoring_idx} for repo {project_name}")
            try:
                tloc = get_tloc(path_to_repo=repo_path, first_hash=anchor_hash, second_hash=subsequent_refactoring_hash,
                                class_path=class_path)
            except Exception as e:
                repo_logger.info(
                    f"Failed getting tloc from same refactoring case {current_refactoring_idx} with error {e}")
                GLOBAL_LOGGER.info(
                    f"Failed getting tloc from same refactoring case {current_refactoring_idx} for repo {project_name} with error {e}")
                sys.exit(1)

            previous_hash = subsequent_refactoring_hash

        # Now we compute the "raw_tloc" approach.
        parent_hash = get_parent_hash(repo_path=repo_path, commit_hash=hashes_from_proneness_data[i])
        repo_logger.info(f"Getting RAW tloc from same refactoring case {current_refactoring_idx}")
        GLOBAL_LOGGER.info(f"Getting RAW tloc from same refactoring case {current_refactoring_idx} for repo {project_name}")
        try:
            raw_tloc = get_tloc(path_to_repo=repo_path, first_hash=parent_hash, second_hash=subsequent_refactoring_hash,
                                class_path=class_path)
        except Exception as e:
            repo_logger.info(
                f"Failed getting RAW tloc from same refactoring case {current_refactoring_idx} with error {e}")
            GLOBAL_LOGGER.info(
                f"Failed getting RAW tloc from same refactoring case {current_refactoring_idx} for repo {project_name} with error {e}")
            sys.exit(1)

        output_dict["idx"].append(i)
        output_dict["project_id"].append(project_name)
        output_dict["refactoring_id"].append(refactoring_id)
        output_dict["next_refactoring_hash"].append(hashes_from_proneness_data[i])
        output_dict["class_id"].append(class_ids_from_proneness_data[i])
        output_dict["tloc"].append(tloc)
        output_dict["raw_tloc"].append(raw_tloc)

        with open(os.path.join(str(pickle_path), f"{project_name}.pkl"), "wb") as f:
            pickle.dump(output_dict, f)

        repo_logger.info(f"Refactoring ID {refactoring_id} completed {i}/{len(refactoring_ids_from_proneness_data)}")
        GLOBAL_LOGGER.info(f"Refactoring ID {refactoring_id} completed {i}/{len(refactoring_ids_from_proneness_data)}")
    return output_dict


def get_dev_effort(repo_name, repo_logger):


    repo_path = clone_repo(repo_name=repo_name, repo_logger=repo_logger)

    effort_path = DATA_PATH / "dev_effort_data"
    proneness_path = DATA_PATH / "change_proneness_data"
    os.makedirs(effort_path, exist_ok=True)

    tloc_dict = inter_refactoring_tloc(repo_path=repo_path, input_path=proneness_path, repo_logger=repo_logger)
    repo_logger.info(f"TLOC quantification performed for repo: {repo_name}")
    GLOBAL_LOGGER.info(f"TLOC quantification performed for repo: {repo_name}")

    # delete_repo(repo_path=repo_path)
    return tloc_dict

def process_repository(repo_name):

    GLOBAL_LOGGER.info(f"Analyzing the developer's effort for refactoring activity in repository: {repo_name}")
    os.makedirs(os.path.join(str(DATA_PATH), "dev_effort_logs"), exist_ok=True)
    repo_log_file = os.path.join(str(DATA_PATH), "dev_effort_logs", f"{repo_name}.log")
    repo_logger = setup_logger(f"{repo_name}", repo_log_file)
    repo_logger.info(f"Analyzing the developer's effort for refactoring activity in repository: {repo_name}")
    tloc_dict = get_dev_effort(repo_name=repo_name, repo_logger=repo_logger)
    effort_data_path = DATA_PATH / "dev_effort_data" / f"{repo_name}.csv"
    write_csv_from_dict(dictionary=tloc_dict, path=str(effort_data_path))
    result = f"Dev effort computed for repository {repo_name}"
    GLOBAL_LOGGER.info(result)
    repo_logger.info(result)
    return result

def parallel_analysis(repo_names):

    with ProcessPoolExecutor() as executor:
        func = partial(process_repository)
        results =list(tqdm(executor.map(func, repo_names), total=len(repo_names), desc="Parallel dev effort analysis"))

    for results in results:
        print(results)

def main():
    begin = datetime.now()
    GLOBAL_LOGGER.info("Global logging initialized. Process started.")
    overall_repos_path = DATA_PATH / "change_proneness_data"
    overall_repos_list = os.listdir(overall_repos_path)
    list_repos = []
    for repo_name in overall_repos_list:
        if os.path.exists(os.path.join(str(overall_repos_path / repo_name / "bcp_proneness_results.csv"))):
            list_repos.append(repo_name)

    GLOBAL_LOGGER.info("Starting developer's effort quantification.")
    parallel_analysis(list_repos)
    end = datetime.now()
    msg = f"> SCRIPT COMPLETED\n> TIME REQUIRED: {end - begin}\n> ENDING HOUR: {end}"
    GLOBAL_LOGGER.info(msg)


if __name__ == '__main__':
    main()