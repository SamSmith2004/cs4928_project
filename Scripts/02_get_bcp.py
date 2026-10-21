"""
Calculates the bayesian posterior distribution of each of the collected refactoring cases. The approach needs to be
studied beforehand to be reshaped.
"""
from collections import deque

from prompt_toolkit.key_binding.key_bindings import GlobalOnlyKeyBindings

from components.utility import (DATA_PATH, clone_repo, delete_repo, get_study_repos, write_csv_from_dict,
                                read_csv_to_dict, setup_logger)
import os
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
import psutil
import subprocess
import difflib
import pandas as pd
import git
import pickle
from datetime import datetime
import traceback
import itertools
import sys
import pydriller

PRONENESS_DATA_PATH = DATA_PATH / "change_proneness_data"
MAX_RETRIES = 3
FAILED_REPOS_FILE = os.path.join(str(DATA_PATH), "bcp_failed_repositories.txt")
GLOBAL_LOG_FILE = os.path.join(str(DATA_PATH), "bcp_estimation_global.log")
GLOBAL_LOGGER = logging.getLogger("GLOBAL")
GLOBAL_LOGGER.setLevel(logging.INFO)
global_handler = logging.FileHandler(GLOBAL_LOG_FILE, mode='w')
global_handler.setFormatter(logging.Formatter('%(asctime)s - %(processName)s - %(funcName)s - %(levelname)s - %(message)s'))
GLOBAL_LOGGER.addHandler(global_handler)


def get_optimal_workers():
    """
    Determines an optimal number of worker processes based on system resources.
    """
    num_cores = os.cpu_count() or 4  # Default to 4 if detection fails
    total_memory = psutil.virtual_memory().total  # Total memory in bytes
    available_memory = psutil.virtual_memory().available  # Available memory in bytes

    # Estimate memory usage per process (Assume ~1GB per process as a placeholder)
    estimated_memory_per_worker = 1 * 1024 ** 3  # 1GB in bytes

    # Max workers based on available memory
    memory_based_workers = available_memory // estimated_memory_per_worker

    # Ensure we don’t exceed available memory or CPU cores
    optimal_workers = min(num_cores - 1, memory_based_workers)

    # Ensure at least one worker is available
    return max(1, optimal_workers)


def compute_change_ratio(repo_path, file_path, commit1, commit2):
    """Calculates the proportion of lines changed between two commits."""
    repo = git.Repo(repo_path)

    try:
        diff = repo.git.diff(commit1, commit2, file_path)
        changed_lines = sum(
            1 for line in diff.split("\n") if line.startswith(('+', '-')) and not line.startswith(('+++', '---')))

        commit1_content = repo.git.show(f"{commit1}:{file_path}")
        total_lines = len(commit1_content.split("\n"))

        return changed_lines / total_lines if total_lines > 0 else 0
    except git.exc.GitCommandError:
        return 0


def get_cumulative_probabilities(refactoring_hash, repo_path, refactoring_filepath, subsequent_hashes_dict,
                                 subsequent_class_history_df, repo_logger):
    """
    Gets lists of cumulative remaining code probabilities and individual change ratios.

    :param refactoring_hash: First refactoring hash, not to be included in the return list.
    :param repo_path: Path to the Git repository.
    :param refactoring_filepath: File path of the first refactoring.
    :param subsequent_hashes_dict: Dict of subsequent commit hashes (keys) with class_id (payload).
    :param subsequent_class_history_df: Dataframe with changes in class throughout the commit history.

    :return: (list of remaining original code probabilities, list of individual change ratios)
    """

    repo_logger.info(f"Starting cumulative probability calculation for {refactoring_filepath}")
    GLOBAL_LOGGER.info(f"Starting cumulative probability calculation for {refactoring_filepath}")
    individual_change_ratios = []
    cumulative_remaining_probs = []  # The inverse of cumulative change probability
    cumulative_prob_of_change = 0

    # Build chronologically ordered list of commits
    subsequent_commits_deque = deque(subsequent_hashes_dict.keys())
    subsequent_commits_deque.appendleft(refactoring_hash)
    subsequent_commits_list = list(subsequent_commits_deque)

    for i in range(1, len(subsequent_commits_list)):
        try:
            if i == 1:
                file_path = refactoring_filepath  # First file path
            else:
                # Fetch the filepath for this commit
                file_path = subsequent_class_history_df[subsequent_class_history_df["hash"] == subsequent_commits_list[i]][
                    "full-path"].values[0]

            # Compute change ratio
            change_ratio = compute_change_ratio(repo_path, file_path, subsequent_commits_list[i - 1],
                                                subsequent_commits_list[i])
            individual_change_ratios.append(change_ratio)

            # Update cumulative probability of change
            cumulative_prob_of_change = 1 - (1 - cumulative_prob_of_change) * (1 - change_ratio)

            # Calculate remaining probability (1 - cumulative change)
            remaining_prob = 1 - cumulative_prob_of_change
            cumulative_remaining_probs.append(remaining_prob)
        except Exception as e:
            repo_logger.error(f"Error in cumulative probability calculation at {subsequent_commits_list[i]}: {e}")
            GLOBAL_LOGGER.error(f"Error in cumulative probability calculation at {subsequent_commits_list[i]}: {e}")

    repo_logger.info(f"Completed cumulative probability calculation for {refactoring_filepath}")
    GLOBAL_LOGGER.info(f"Completed cumulative probability calculation for {refactoring_filepath}")
    return cumulative_remaining_probs, individual_change_ratios


def get_file_content(commit_hash, file_path, repo_path):
    """
    Get the content of a file at a specific commit.
    """

    try:
        for commit in pydriller.Repository(str(repo_path), only_commits=[commit_hash]).traverse_commits():
            for m in commit.modified_files:

                try:
                    old_path = os.path.normpath(m.old_path)
                except Exception as e:
                    old_path = m.old_path
                try:
                    new_path = os.path.normpath(m.new_path)
                except Exception as e:
                    new_path = m.new_path

                if old_path == os.path.normpath(file_path) or new_path == os.path.normpath(file_path):
                    try:
                        source_code = m.source_code.splitlines()
                        return source_code
                    except Exception as e:
                        return ""
    except Exception as e:
        print(e)
        sys.exit(1)



def compute_similarity(lines_old, lines_new):
    """
    Compute the ratio of unchanged lines using Longest Common Subsequence (LCS).
    """
    sm = difflib.SequenceMatcher(None, lines_old, lines_new)
    return sm.ratio()  # Returns similarity ratio between 0 and 1


def get_lcs_probabilities(refactoring_hash, repo_path, refactoring_filepath, subsequent_hashes_dict,
                          subsequent_class_history_df, repo_logger):
    """
    Gets a list of posterior probabilities based on LCS code change probability.
    LCS: https://en.wikipedia.org/wiki/Longest_common_subsequence

    :param refactoring_hash: First refactoring hash, not to be included in the return list (The one mined with RMiner)
    :param repo_path
    :param refactoring_filepath: File path of the first refactoring, not to be included in the return list (The one mined with RMiner)
    :param subsequent_hashes_dict: Dict with Subsequent commit hashes (key) with its class_id (payload).
    :param subsequent_class_history_df: df with changes in the class happened throughout the commit change history.
    :return: list of probabilities to be appended to the global list which will be appended to the final data file.
    """

    repo_logger.info(f"Starting LCS probability calculation for {refactoring_filepath}")
    GLOBAL_LOGGER.info(f"Starting LCS probability calculation for {refactoring_filepath}")
    initial_content = get_file_content(refactoring_hash, refactoring_filepath, repo_path)
    if initial_content is None:
        repo_logger.warning(f"Could not retrieve initial content for {refactoring_filepath}. Skipping LCS calculation.")
        GLOBAL_LOGGER.warning(f"Could not retrieve initial content for {refactoring_filepath}. Skipping LCS calculation.")
        return list(itertools.repeat(0, len(subsequent_hashes_dict.keys())))

    probabilities = []  # Start with 100% of the lines unchanged
    subsequent_commits_list = list(subsequent_hashes_dict.keys())

    for i in range(0, len(subsequent_commits_list)):
        try:
            # Fetch the filepath for this commit
            file_path = subsequent_class_history_df[subsequent_class_history_df["hash"] == subsequent_commits_list[i]][
                "full-path"].values[0]
            new_content = get_file_content(subsequent_commits_list[i], file_path, repo_path)
            if new_content is None:
                repo_logger.warning(f"Skipping LCS calculation at {subsequent_commits_list[i]} due to missing content.")
                GLOBAL_LOGGER.warning(f"Skipping LCS calculation at {subsequent_commits_list[i]} due to missing content.")
                probabilities.append(0.0)
                continue

            similarity = compute_similarity(initial_content, new_content)
            probabilities.append(similarity)
        except Exception as e:
            repo_logger.error(f"Error computing LCS probability at {subsequent_commits_list[i]}: {e}")
            GLOBAL_LOGGER.error(f"Error computing LCS probability at {subsequent_commits_list[i]}: {e}")

    repo_logger.info(f"Completed LCS probability calculation for {refactoring_filepath}")
    GLOBAL_LOGGER.info(f"Completed LCS probability for {refactoring_filepath}")
    return probabilities


def get_processed_refactorings(pickle_path):
    """Load processed refactorings from a pickle file if it exists."""
    if os.path.exists(pickle_path):
        try:
            with open(pickle_path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Warning: Could not load {pickle_path} due to {e}. Starting fresh.")
    return {"refactoring_id": [], "bayesian_remaining_probs": [], "lcs_remaining_probs": []}


def update_pickle(pickle_path, data_dict):
    """Save the updated data_dict back to the pickle file dynamically."""
    with open(pickle_path, "wb") as f:
        pickle.dump(data_dict, f)


def handle_repository(repo):
    """
    Deals with the probability approximation for a single repository

    :param repo: the name of the repository
    :return:
    """

    os.makedirs(os.path.join(str(DATA_PATH), "bcp_logs"), exist_ok=True)
    repo_log_file = os.path.join(str(DATA_PATH), "bcp_logs", f"{repo}.log")
    repo_logger = setup_logger(f"{repo}", repo_log_file)

    proneness_repo_dir_path = os.path.join(PRONENESS_DATA_PATH, repo)
    proneness_pickle_path = os.path.join(str(proneness_repo_dir_path), "bcp_results.pkl")

    # Two approaches: RAW approximation (Just numerical difference between changes based on lines) and LCS based ratio.
    ordered_refactorings_dict = read_csv_to_dict(os.path.join(str(proneness_repo_dir_path), "ordered_refactorings.csv"))
    proneness_results_dict = read_csv_to_dict(os.path.join(str(proneness_repo_dir_path), "proneness_results.csv"))
    proneness_results_df = pd.read_csv(os.path.join(str(proneness_repo_dir_path), "proneness_results.csv"))

    # Cleaning unuseful projects
    if len(proneness_results_df["refactoring_id"]) == 0:
        repo_logger.info(f"Repo {repo} doesn't have proneness history results, we skip it")
        GLOBAL_LOGGER.info(f"Repo {repo} doesn't have proneness history results, we skip it")
        if os.path.exists(os.path.join(str(DATA_PATH), "repos", repo)):
            delete_repo(repo_path=os.path.join(str(DATA_PATH), "repos", repo),
                        repo_logger=repo_logger)
    elif len(ordered_refactorings_dict["id"]) == 0:
        repo_logger.info(f"Repo {repo} doesn't have mined refactoring activity, we skip it")
        GLOBAL_LOGGER.info(f"Repo {repo} doesn't have refactoring activity, we skip it")
        if os.path.exists(os.path.join(str(DATA_PATH), "repos", repo)):
            delete_repo(repo_path=os.path.join(str(DATA_PATH), "repos", repo),
                        repo_logger=repo_logger)
    else:

        try:
            repo_path = clone_repo(repo, repo_logger)

            # We get the latest refactoring that got processed for the proneness so that we don't need to iterate through all the
            # identified refactorings
            last_proneness_processed_refactoring_id = proneness_results_dict["refactoring_id"][-1]
            max_id_number = int(last_proneness_processed_refactoring_id.split("_")[0])

            # Check if the pickle file exists, otherwise initialize it
            if os.path.exists(proneness_pickle_path):
                with open(proneness_pickle_path, "rb") as f:
                    bcp_results_dict = pickle.load(f)
                repo_logger.info(f"Loaded existing progress: {len(bcp_results_dict['refactoring_id'])} refactorings processed.")
                GLOBAL_LOGGER.info(f"Loaded existing progress: {len(bcp_results_dict['refactoring_id'])} refactorings processed for repo {repo}.")
            else:
                bcp_results_dict = {"refactoring_id": [], "bayesian_remaining_probs": [], "lcs_remaining_probs": []}
                repo_logger.info("No previous progress found. Starting fresh.")
                GLOBAL_LOGGER.info(f"No previous progress found. Starting fresh for repo {repo}.")

            processed_refactoring_ids = set(bcp_results_dict["refactoring_id"])  # Set for fast lookup

            repo_logger.info(f"Starting processing refactorings for repo {repo}.")
            GLOBAL_LOGGER.info(f"Starting processing refactorings for repo {repo}.")

            for idx in range(max_id_number + 1):

                # Get data from initial commit
                initial_refactoring_id = str(idx)
                # Skip already processed refactorings
                if initial_refactoring_id in processed_refactoring_ids:
                    repo_logger.info(f"Skipping already processed refactoring {initial_refactoring_id} for repo {repo}.")
                    GLOBAL_LOGGER.info(f"Skipping already processed refactoring {initial_refactoring_id} for repo {repo}.")
                    continue

                initial_refactoring_type = ordered_refactorings_dict["refactoring"][idx]
                initial_refactoring_hash = ordered_refactorings_dict["hash"][idx]
                initial_refactoring_filepath = ordered_refactorings_dict["filepath"][idx]

                # Get rows related to this refactoring
                refactoring_proneness_rows_df = proneness_results_df[proneness_results_df["refactoring_id"].str.startswith(f"{initial_refactoring_id}_")]
                subsequent_refactoring_commits = refactoring_proneness_rows_df.set_index("hash")["class_id"].to_dict()
                try:
                    current_refactoring_id = refactoring_proneness_rows_df["refactoring_id"].tolist()[-1]
                except Exception as e:
                    repo_logger.warning(f"There were no posterior refactorings for refactoring {idx}-{initial_refactoring_type} performed on class {initial_refactoring_filepath} in commit {initial_refactoring_hash} for repo {repo}.")
                    GLOBAL_LOGGER.warning(f"There were no posterior refactorings for refactoring {idx}-{initial_refactoring_type} performed on class {initial_refactoring_filepath} in commit {initial_refactoring_hash} for repo {repo}.")
                    continue
                class_change_history_df = pd.read_csv(os.path.join(str(proneness_repo_dir_path), "class_change_history", current_refactoring_id))


                # Probability computations
                try:
                    repo_logger.info(f"Running BCP calculation for {idx} for repo {repo}.")
                    GLOBAL_LOGGER.info(f"Running BCP calculation for {idx} for repo {repo}.")
                    cumulative_remaining_probs, individual_change_ratios = get_cumulative_probabilities(refactoring_hash=initial_refactoring_hash,
                                                                                                        repo_path=repo_path,
                                                                                                        refactoring_filepath=initial_refactoring_filepath,
                                                                                                        subsequent_hashes_dict=subsequent_refactoring_commits,
                                                                                                        subsequent_class_history_df=class_change_history_df,
                                                                                                        repo_logger=repo_logger)
                    repo_logger.info(f"{len(cumulative_remaining_probs)} BCP probs calculated for {idx} for repo {repo}.")
                    GLOBAL_LOGGER.info(f"{len(cumulative_remaining_probs)} BCP probs calculated for {idx} for repo {repo}.")
                except Exception as e:
                    repo_logger.error(f"Error calculating cumulative probability for refactoring {current_refactoring_id}: {e} in repo {repo}.")
                    GLOBAL_LOGGER.error(f"Error calculating cumulative probability for refactoring {current_refactoring_id}: {e} in repo {repo}.")
                    cumulative_remaining_probs = []
                try:
                    repo_logger.info(f"Running LCS calculation for {idx} for repo {repo}.")
                    GLOBAL_LOGGER.info(f"Running LCS calculation for {idx} for repo {repo}.")
                    idx_lcs_probability_list = get_lcs_probabilities(refactoring_hash=initial_refactoring_hash, repo_path=repo_path,
                                                                     refactoring_filepath=initial_refactoring_filepath, subsequent_hashes_dict=subsequent_refactoring_commits,
                                                                     subsequent_class_history_df=class_change_history_df,
                                                                     repo_logger=repo_logger)
                    repo_logger.info(f"{len(idx_lcs_probability_list)} LCS probs calculated for {idx} for repo {repo}.")
                    repo_logger.info(f"{len(idx_lcs_probability_list)} LCS probs calculated for {idx} for repo {repo}.")
                except Exception as e:
                    idx_lcs_probability_list = []
                    repo_logger.error(f"Error calculating LCS probability for refactoring {current_refactoring_id}: {e} in repo {repo}.")
                    GLOBAL_LOGGER.error(f"Error calculating LCS probability for refactoring {current_refactoring_id}: {e} in repo {repo}.")

                # Dynamically update pickle file after processing each refactoring
                bcp_results_dict["refactoring_id"].append(initial_refactoring_id)
                bcp_results_dict["bayesian_remaining_probs"].extend(cumulative_remaining_probs)
                bcp_results_dict["lcs_remaining_probs"].extend(idx_lcs_probability_list)

                with open(proneness_pickle_path, "wb") as f:
                    pickle.dump(bcp_results_dict, f)
                repo_logger.info(f"Probabilities for refactor ID {initial_refactoring_id} completed - {idx} / {max_id_number+1} for repo {repo}.")
                GLOBAL_LOGGER.info(f"Probabilities for refactor ID {initial_refactoring_id} completed - {idx} / {max_id_number+1} for repo {repo}.")

            # Update the df
            proneness_results_df["bayesian_remaining_probs"] = bcp_results_dict["bayesian_remaining_probs"]
            proneness_results_df["lcs_remaining_probs"] = bcp_results_dict["lcs_remaining_probs"]
            proneness_results_df.to_csv(os.path.join(str(proneness_repo_dir_path), "bcp_proneness_results.csv"), index=False)

            return repo_path, "Success"
            #delete_repo(repo_path)
        except Exception as e:
            tb = e.__traceback__
            repo_logger.error(f"Critical failure for repository {repo}: {e}")
            GLOBAL_LOGGER.error(f"Critical failure for repository {repo}: {e}")
            repo_logger.error(traceback.format_exc())
            with open(FAILED_REPOS_FILE, "a") as f:
                f.write(f"{repo},{e}\n")  # Append failed repo to failed_repositories.txt
                traceback.format_exc()

            return e, "Error"


def process_repositories(repo_list):
    """
    Manages the parallel execution of get_input_items with retries.
    """

    # Dictionary to track retries
    retries = {repo_name: 0 for repo_name in repo_list}
    pending_repos = repo_list.copy()  # Copy of repositories to track progress

    while pending_repos:
        failed_repos = []

        max_workers = get_optimal_workers()
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            future_to_repo = {executor.submit(handle_repository, repo): repo for repo in pending_repos}

            for future in as_completed(future_to_repo):
                repo_name = future_to_repo[future]
            try:
                result_repo, status = future.result()  # Get the result
                if "Error" in status:
                    print(f"WARNING: {repo_name} failed: {status}")
                    if retries[repo_name] < MAX_RETRIES:
                        retries[repo_name] += 1
                        failed_repos.append(repo_name)
                    else:
                        print(f"ERROR: {repo_name} FAILED after {MAX_RETRIES} retries.")
                else:
                    print(f"> {repo_name} processed successfully.")

            except Exception as e:
                print(f"WARNING Unexpected failure for {repo_name}: {e}")
                failed_repos.append(repo_name)

        pending_repos = failed_repos  # Retry only failed repositories
        print(failed_repos)
    print("All repositories have been processed.")


def main():
    begin = datetime.now()
    GLOBAL_LOGGER.info("Global logging initialized. Process started.")
    repo_list = os.listdir(PRONENESS_DATA_PATH)
    process_repositories(repo_list=repo_list)
    end = datetime.now()
    msg = f"> SCRIPT COMPLETED\n> TIME REQUIRED: {end - begin}\n> ENDING HOUR: {end}"
    GLOBAL_LOGGER.info(msg)

if __name__ == '__main__':
    main()