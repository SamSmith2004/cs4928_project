"""
Performs the change proneness and defect proneness of the analyzed projects
"""

import os
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import partial
from pickle import GLOBAL

import pandas as pd
import sys
from git import Repo
import pydriller as pydrill
import pickle
import regex as re
import psutil
import logging
from py_email import send_email
from datetime import datetime

from components.utility import (DATA_PATH, clone_repo, delete_repo, open_json_file, get_study_repos,
                                      check_class_modification, get_eloc, checkout_git_repo, read_csv_to_df,
                                      write_csv_from_dict, read_csv_to_dict, write_dict_to_pickle, setup_logger)
from proneness_status_monitoring import inspect_project

MAX_RETRIES = 3
GLOBAL_LOG_FILE = os.path.join(str(DATA_PATH), "change_proneness_global.log")
GLOBAL_LOGGER = logging.getLogger("GLOBAL")
GLOBAL_LOGGER.setLevel(logging.INFO)
global_handler = logging.FileHandler(GLOBAL_LOG_FILE, mode='w')
global_handler.setFormatter(logging.Formatter('%(asctime)s - %(processName)s - %(funcName)s - %(levelname)s - %(message)s'))
GLOBAL_LOGGER.addHandler(global_handler)

def get_refactoring_commits(repo_name, repo_logger):
    """
    Gets the refactoring commits from the JSON file and stores them in order in a csv to be stored within the
    version control order.
    :param repo_name:
    :return: Ordered dict of commits
    """
    refactorings_path = DATA_PATH / 'back-up' / 'output_data' / 'refactoring_commits' / f"{repo_name}.json"
    data_json = open_json_file(json_file=str(refactorings_path))

    pickle_path = DATA_PATH / 'change_proneness_data' / repo_name / 'ordered_commits.pkl'

    # If we already processed this project, we can fetch the dict from the serialized pickle file
    if os.path.exists(str(pickle_path)):
        repo_logger.info(f"The repo {repo_name} already has ordered_commits dict in {str(pickle_path)}, skipping traversing.")
        GLOBAL_LOGGER.info(f"The repo {repo_name} already has ordered_commits dict in {str(pickle_path)}, skipping traversing.")
        return pickle.load(open(str(pickle_path), 'rb'))

    ordered_commits = {"id": [], "hash": []}
    i = 0
    total_ref_commits = len(data_json[0]["commits_data"])
    for commit_data in reversed(data_json[0]["commits_data"]):
        ordered_commits["id"].append(i)
        ordered_commits["hash"].append(commit_data["commit_hash"])
        i+=1
    ordered_commits_df = pd.DataFrame.from_dict(ordered_commits)
    change_data_path = DATA_PATH / "change_proneness_data"
    os.makedirs(str(change_data_path), exist_ok=True)
    os.makedirs(os.path.join(str(change_data_path), repo_name), exist_ok=True)
    # Commits chronologically ordered in a CSV
    ordered_commits_df.to_csv(os.path.join(str(change_data_path), repo_name, f"ordered_commits.csv"), index=False)
    pickle.dump(ordered_commits, open(str(pickle_path), 'wb'))  # Commits chronologically ordered in a pickle file

    repo_logger.info(f"Refactoring commits chronically ordered for repo {repo_name}")
    GLOBAL_LOGGER.info(f"Refactoring commits chronically ordered for repo {repo_name}")
    return ordered_commits


def get_refactorings(repo_name, commit_dict, repo_logger):
    """
    Builds a comprehensive data structure for refactoring commits to start processing the change proneness of the
    involved files.

    :param repo_name:
    :param commit_dict: order (key), hash (payload)
    :return: Returns data structure with the order of refactorings with their files.
    """

    # Check if we have already processed this project from the pickle file
    pickle_path = DATA_PATH / 'change_proneness_data' / repo_name / 'ordered_refactorings.pkl'
    if os.path.exists(str(pickle_path)):
        repo_logger.info(f"The repo {repo_name} already has ordered refactorings dict in {str(pickle_path)}, skipping traversing.")
        GLOBAL_LOGGER.info(f"The repo {repo_name} already has ordered refactorings dict in {str(pickle_path)}, skipping traversing.")
        return pickle.load(open(str(pickle_path), 'rb'))

    refactorings_dict = {"id": [], "refactoring": [], "hash": [], "description": [], "filepath": [],
                         "codeElementTypes": [], "descriptions": [], "codeElements": []}

    refactorings_path = DATA_PATH / 'back-up' / 'output_data' / 'refactoring_commits' / f"{repo_name}.json"
    data_json = open_json_file(json_file=str(refactorings_path))
    refactoring_data_list = data_json[0]["commits_data"]

    # Loop through the commit_dict in order to get the refactoring data.
    ids, commits = commit_dict.items()
    j = 0

    # Iterating chronologically through the commit history
    for current_commit in commit_dict['hash']:
        # We find where the commit has its refactoring data stored.
        for refactoring_log in refactoring_data_list:
            if refactoring_log["commit_hash"] == current_commit:
                # Check the existing refactorings for this commit
                for ref_case in refactoring_log["refactorings"]:
                    refactorings_dict["id"].append(j)
                    refactorings_dict["refactoring"].append(ref_case["type"])
                    refactorings_dict["hash"].append(current_commit)
                    refactorings_dict["description"].append(ref_case["description"])
                    # Some refactorings might not provide any information as they are just moves, e.g. "Move Source Folder"
                    try:
                        refactorings_dict["filepath"].append(ref_case["rightSideLocations"][0]["filePath"])
                    except IndexError as e:
                        refactorings_dict["filepath"].append(None)
                        refactorings_dict["codeElementTypes"].append([])
                        refactorings_dict["descriptions"].append([])
                        refactorings_dict["codeElements"].append([])
                        repo_logger.error(f"error: {e} - for {ref_case["type"]} in hash {current_commit} - traceback: {e.with_traceback()}")
                        GLOBAL_LOGGER.error(f"error: {e} - for {ref_case["type"]} in hash {current_commit} - traceback: {e.with_traceback()}")
                        continue

                    # IMPORTANT: Within the RMiner's output, the leftSideLocations attribute stands as the code which existed in
                    # parent commit, while the rightSideLocations attribute contains the code components which exist in
                    # the child commit. That is, the code components resulting from the refactoring.
                    code_element_types = []
                    code_element_descriptions = []
                    code_elements = []
                    for ref_component in ref_case["rightSideLocations"]:
                        code_element_types.append(ref_component["codeElementType"])
                        code_element_descriptions.append(ref_component["description"])
                        try:
                            code_elements.append(ref_component["codeElement"])
                        except:
                            code_elements.append(None)
                            repo_logger.warning(f"No identified codeElements for refactoring case {ref_case["type"]} in hash {current_commit}")
                            GLOBAL_LOGGER.warning(f"No identified codeElements for refactoring case {ref_case["type"]} in hash {current_commit}")

                    refactorings_dict["codeElementTypes"].append(code_element_types)
                    refactorings_dict["descriptions"].append(code_element_descriptions)
                    refactorings_dict["codeElements"].append(code_elements)
                    repo_logger.info(f"Processing refactoring {ref_case["type"]} - hash {current_commit} - ref count {j+1}")
                    GLOBAL_LOGGER.info(f"Processing refactoring {ref_case["type"]} - hash {current_commit} - ref count {j+1}")
                    j+=1

    ordered_refs_df = pd.DataFrame.from_dict(refactorings_dict)
    change_data_path = DATA_PATH / "change_proneness_data"
    os.makedirs(str(change_data_path), exist_ok=True)
    os.makedirs(os.path.join(str(change_data_path), repo_name), exist_ok=True)
    ordered_refs_df.to_csv(os.path.join(str(change_data_path), repo_name, f"ordered_refactorings.csv"), index=False)
    pickle.dump(refactorings_dict, open(str(pickle_path), 'wb'))
    repo_logger.info(f"Repo {repo_name} processed for ordered refactorings dict in {str(pickle_path)}.")
    GLOBAL_LOGGER.info(f"Repo {repo_name} processed for ordered refactorings dict in {str(pickle_path)}.")
    return refactorings_dict


def get_commit_history(repo_path, begin_sha, refactoring_commits):
    """
    Loops through repo version control history to return the list in a chronological order.
    :param repo_path:
    :return: list
    """

    project_name = os.path.basename(repo_path)

    if refactoring_commits is True:

        ordered_commits_pkl_path = DATA_PATH / 'change_proneness_data' / project_name / 'ordered_commits.pkl'
        ordered_commits_dict = pickle.load(open(str(ordered_commits_pkl_path), 'rb'))
        refactoring_commits = ordered_commits_dict["hash"]
        try:
            start_index = refactoring_commits.index(begin_sha) + 1
            commit_list = refactoring_commits[start_index:]
        except ValueError:
            # Handle the case where `begin_sha` is not found
            commit_list = []

        return commit_list

    else:
        commit_list= []
        for commit in pydrill.Repository(str(repo_path), only_modifications_with_file_types=['.java']).traverse_commits():
            if commit.hash == begin_sha:
                continue
            commit_list.append(commit.hash)

        return commit_list


def store_classes_data(repo_path, file_path, hashes, paths, refactoring_id):
    """
    Based on the class changes in each refactoring case, we store in a csv the existing class path and name changes
    during the development process.

    :param repo_path:
    :param file_path:
    :param hashes:
    :param paths:
    :return:
    """

    # We need to control for changes in the path of the file with class id, therefore any unique path needs to be related to an ID
    unique_file_paths = set()
    counter = 0

    class_change_history_data = DATA_PATH / "change_proneness_data" / os.path.basename(repo_path) / "class_change_history"
    os.makedirs(str(class_change_history_data), exist_ok=True)
    if os.path.exists(os.path.join(str(class_change_history_data), refactoring_id)):
        data_dict = read_csv_to_dict(os.path.join(str(class_change_history_data), refactoring_id))
        return data_dict
    else:
        data_dict = {"classID": [], "full-path": [], "class-name": [], "hash": []}

        for hash, path in zip(hashes, paths):

            if path not in unique_file_paths:
                unique_file_paths.add(path)
                counter += 1

            # first number: Refactoring type global order
            # second number: Refactoring type order within the same commit if the type is not unique
            # third number: class path identifier, if the path has changed.
            data_dict["classID"].append(f"{refactoring_id}-{counter}-{os.path.basename(file_path).rsplit('.')[0]}")
            data_dict["full-path"].append(path)
            data_dict["class-name"].append(os.path.basename(file_path))
            data_dict["hash"].append(hash)

        write_csv_from_dict(dictionary=data_dict, path=os.path.join(str(class_change_history_data), refactoring_id))

        return data_dict


def check_file_changes(repo_path, file_path, commit_1, following_commits, refactoring_id):
    """
    Checks if during the development activity of the project the file went through changes

    :param repo_path:
    :param file_path:
    :param commit_1: Commit where the refactoring being analyzed was detected
    :param following_commits: Subsequent commits in the version control history
    :return: hashes (in which the file was modified) | paths ()
    """

    temp_file_path = os.path.normpath(str(file_path))
    hashes = []
    paths = []

    for next_hash in following_commits:
        mod_path, hash = check_class_modification(repo_path=str(repo_path), file_path=temp_file_path, commit=next_hash)

        # The class wasn't modified in this commit
        if mod_path == None and hash == None:
            continue
        # The class was deleted from the repository
        elif mod_path == None and hash != None:
            break
        else:
            hashes.append(hash)
            paths.append(mod_path)

    classes_dict = store_classes_data(str(repo_path), file_path, hashes, paths, refactoring_id)

    return hashes, paths, classes_dict


def get_defect_proneness(commit_message, max_errors=1):
    """
    Finds Jira-style (e.g., JIRA-1000) and GitHub-style (e.g., #123) issue tickets in a commit message using fuzzy matching.

    :param commit_message: The commit message to search within.
    :param max_errors: Maximum allowed errors for fuzzy matching.
    :return: A list of matched issue tickets, or an empty list if none found.
    """

    # Define the regex patterns for Jira and GitHub issue tickets
    jira_pattern = r"[A-Z]{2,}-\d+"
    jira_pattern_2 = r"\d{4,}"
    github_pattern = r"#\d+"

    # Add fuzzy matching to the patterns
    fuzzy_jira_pattern = f"({jira_pattern}){{e<={max_errors}}}"
    fuzzy_jira_2_pattern = f"({jira_pattern_2}){{e<={max_errors}}}"
    fuzzy_github_pattern = f"({github_pattern}){{e<={max_errors}}}"

    # Find all matches for both patterns
    jira_matches = re.findall(fuzzy_jira_pattern, commit_message)
    jira_2_matches = re.findall(fuzzy_jira_2_pattern, commit_message)
    github_matches = re.findall(fuzzy_github_pattern, commit_message)

    if len(jira_matches) != 0 or len(github_matches) != 0 or len(jira_2_matches) != 0:
        return True
    else:
        return False


def make_refactoring_id(order_id, refactoring_type, ref_type_count_cache, project_name):
    """
    Generates the identifier name for each of the analyzed refactorings.
    :param order_id: ID showing the order in which initially RMiner identified the commits.
    :param refactoring_dict: Dict with all the refactoring data ordered chronologically.
    :param refactoring_type: Type of the refactoring that is being analyzed currently
    :return: refactoring_id (str)
    """

    # tokenize the refacotoring type.
    lowered_refactoring_type = refactoring_type.lower()
    tokenized_refactoring_type = lowered_refactoring_type.replace(" ", "-")
    id = f"{order_id}_{ref_type_count_cache}_{tokenized_refactoring_type}_{project_name}"
    return id


def fetch_class_id_from_dict(current_hash, classes_dict):
    """
    Fetches the class ID from a dictionary based on the hash provided.

    :param path:
    :param classes_dict: {"classID": [], "full-path": [], "class-name": [], "hash": []}
    :return: classID
    """

    index_pos = classes_dict['hash'].index(current_hash)
    return classes_dict['classID'][index_pos]


def record_processed_refactorings(i, refactoring_type, project_name):
    """
    Records already processed refactorings.

    :param i: refactoring id from the initial table of ordered_refactorings
    :param refactoring_type:
    :return: None
    """

    path = DATA_PATH / "change_proneness_data" / project_name / "processed_refactorings.txt"

    with open(str(path), 'a+', encoding="utf-8") as f:
        f.write(f'{i},{refactoring_type}\n')


def check_processed_refactorings(i, project_name, repo_logger):
    path = DATA_PATH / "change_proneness_data" / project_name / "processed_refactorings.txt"

    if os.path.exists(str(path)):
        try:
            with open(str(path), 'rb') as f:
                # Check if the file is empty
                f.seek(0, os.SEEK_END)
                if f.tell() == 0:
                    repo_logger.info(f"No processed refactorings yet for {project_name} in check_processed_refactorings()")
                    GLOBAL_LOGGER.info(f"No processed refactorings yet for {project_name} in check_processed_refactorings()")
                    return False  # Empty file, nothing to compare

                # Move back from end to find the last line
                f.seek(-2, os.SEEK_END)  # Start from second-last byte
                while f.read(1) != b'\n':
                    f.seek(-2, os.SEEK_CUR)
                    if f.tell() == 0:  # Prevent infinite loop
                        f.seek(0)
                        break

                last_line = f.readline().decode().strip()  # Read last line safely

            # Ensure the last line is properly formatted
            if "," in last_line:
                last_id = last_line.split(",")[0].strip()  # Extract first value
                if last_id.isdigit():  # Ensure it's a valid integer
                    repo_logger.info(
                        f"Last processed refactoring index found for {project_name} in check_processed_refactorings() - {last_id}")
                    GLOBAL_LOGGER.info(f"Last processed refactoring index found for {project_name} in check_processed_refactorings() - {last_id}")
                    return i <= int(last_id)

            return False  # If format is invalid, assume unprocessed
        except Exception as e:
            repo_logger.error(f"Error reading {path}: {e} in check_processed_refactorings() - traceback {e.with_traceback()}")
            GLOBAL_LOGGER.error(f"Error reading {path}: {e} in check_processed_refactorings() - traceback {e.with_traceback()}")
            return False  # Fail safely
    else:
        return False


def get_class_history_subset(existing_class_history_dict, refactoring_hash):
    """
    Given an existing class history path for the same type of refactoring, I just get the subset of it so that I don't
    have to traverse through the entire commit history again.
    """

    index_pos = existing_class_history_dict['hash'].index(refactoring_hash)
    # Slice all elements below the found index
    subset_dict = {key: values[index_pos + 1:] for key, values in existing_class_history_dict.items()}
    hashes = subset_dict['hash']
    paths = subset_dict['full-path']
    return hashes, paths, subset_dict


def get_file_changes_history(refactoring_hash, overall_commit_history, repo_path, file_path, refactoring_id,
                             repo_logger):
    """
    Makes two approaches to obtain the hashes, paths and the classes of the file that the refactoring of interest made.
    At the first case in which that file has been affected, it runs the original version of the code (lengthy)
    If the file has been tracked by another refactoring of the same type, then we check, because the refactoring history
    will be the same.

    :param refactoring_hash: commit hash of the refactoring of interest
    :param overall_commit_history: list of commits of the concerning project covering the entire life.
    :return: hashes, paths, classes_dict
    """

    # 1. Check if any of the already processed refactorings has been of the same type
    class_change_history_path = DATA_PATH / "change_proneness_data" / os.path.basename(repo_path) / "class_change_history"
    refactoring_case_list = refactoring_id.split("_")
    refactoring_type = refactoring_case_list[2]
    try:
        refactoring_type_count = int(refactoring_case_list[1])
    except Exception as e:
        repo_logger.error(f"Error [{e}] while fetching the refactoring type count for {refactoring_id} - traceback: {e.with_traceback()}")
        GLOBAL_LOGGER.error(f"Error [{e}] while fetching the refactoring type count for {refactoring_id} - traceback: {e.with_traceback()}")

    if refactoring_type_count == 0:  # Means that this is the first time this refactoring is being processed.
        # Get the following commit history in which Java files got modified.
        start_index = overall_commit_history.index(refactoring_hash) + 1
        following_overall_commits = overall_commit_history[start_index:]
        # We need to count for the commits in which the class was modified, and simultaneously control that the class path is not modified.

        try:
            hashes, paths, classes_dict = check_file_changes(repo_path=repo_path, file_path=file_path,
                                                             commit_1=refactoring_hash,
                                                             following_commits=following_overall_commits,
                                                             refactoring_id=refactoring_id)
            repo_logger.info(
                f"Looking for entire history of class {file_path} for refactoring {refactoring_id}, first of type {refactoring_type}")
            GLOBAL_LOGGER.info(f"Looking for entire history of class {file_path} for refactoring {refactoring_id}, first of type {refactoring_type}")
        except Exception as e:
            repo_logger.error(f"Error [{e}] when checking file changes for a new type of refactoring [{refactoring_id}]")
            GLOBAL_LOGGER.error(f"Error [{e}] when checking file changes for a new type of refactoring [{refactoring_id}]")
        return hashes, paths, classes_dict

    else:
        # 2. Check if the refactoring of the same type has processed the same filename.
        tracked_refactoring_class_histories = os.listdir(str(class_change_history_path))
        repo_logger.info(
            f"Looking for already collected data used for class {file_path} with refactoring type {refactoring_type}")
        GLOBAL_LOGGER.info(f"Looking for already collected data used for class {file_path} with refactoring type {refactoring_type}")
        # Checks if the refactoring type is the same
        matching_files = [file for file in tracked_refactoring_class_histories if f"_{refactoring_type}_" in file]
        for file in matching_files:
            class_history_dict = read_csv_to_dict(os.path.join(str(class_change_history_path), file))
            if file_path in class_history_dict["full-path"]:  # Checks if the affected file type is the same.

                repo_logger.info(
                    f"Fetching data already used for class {file_path} with refactoring type {refactoring_type}")
                GLOBAL_LOGGER.info(f"Fetching data already used for class {file_path} with refactoring type {refactoring_type}")
                try:
                    hashes, paths, classes_dict = get_class_history_subset(existing_class_history_dict=class_history_dict,
                                                                           refactoring_hash=refactoring_hash)
                except Exception as e:
                    repo_logger.error(f"Error [{e}] while checking already existing class ID changes for ref ID [{refactoring_id}]")
                    GLOBAL_LOGGER.error(f"Error [{e}] while checking already existing class ID changes for ref ID [{refactoring_id}]")
                try:
                    store_classes_data(repo_path, file_path, hashes, paths, refactoring_id)
                except Exception as e:
                    repo_logger.error(f"Error [{e}] while storing the subset of class change history for ref ID [{refactoring_id}]")
                    GLOBAL_LOGGER.error(f"Error [{e}] while storing the subset of class change history for ref ID [{refactoring_id}]")
                repo_logger.info(
                    f"Data successfully found for class {file_path} for ref ID [{refactoring_id}] with refactoring type {refactoring_type}")
                GLOBAL_LOGGER.info(f"Data successfully found for class {file_path} for ref ID [{refactoring_id}] with refactoring type {refactoring_type}")
                return hashes, paths, classes_dict

        repo_logger.info(f"No previous data found for class {file_path} with refactoring type {refactoring_type}")
        GLOBAL_LOGGER.info(f"No previous data found for class {file_path} with refactoring type {refactoring_type}")
        repo_logger.info(f"Fetching new class change data for class {file_path} with refactoring type {refactoring_type} for ref ID {refactoring_id}")
        GLOBAL_LOGGER.info(f"Fetching new class change data for class {file_path} with refactoring type {refactoring_type} for ref ID {refactoring_id}")
        try:

            start_index = overall_commit_history.index(refactoring_hash) + 1
            following_overall_commits = overall_commit_history[start_index:]

            hashes, paths, classes_dict = check_file_changes(repo_path=repo_path, file_path=file_path,
                                                             commit_1=refactoring_hash,
                                                             following_commits=following_overall_commits,
                                                             refactoring_id=refactoring_id)
            repo_logger.info(
                f"Looking for entire history of class {file_path} for refactoring {refactoring_id}, time {refactoring_type_count} of type {refactoring_type} appearing")
            GLOBAL_LOGGER.info(f"Looking for entire history of class {file_path} for refactoring {refactoring_id}, time {refactoring_type_count} of type {refactoring_type} appearing")
        except Exception as e:
            repo_logger.error(f"Error [{e}] when checking file changes for time {refactoring_type_count} type of refactoring [{refactoring_id}] appears")
            GLOBAL_LOGGER.error(f"Error [{e}] when checking file changes for time {refactoring_type_count} type of refactoring [{refactoring_id}] appears")
        return hashes, paths, classes_dict


def get_differences(project_name, repo_path, refactoring_dict, repo_logger):
    """
    Gets the difference across commits to count for the changes starting from a selected commit where the anchored
    refactoring happened, and makes the analysis all the way through the version control history just in the affected
    Java class.

    :param project_name:
    :param repo_path:
    :param refactoring_dict: {"id": [], "refactoring": [], "hash": [], "description": [], "filepath": [],
                         "codeElementTypes": [], "descriptions": [], "codeElements": []}

    :return: TBD
    """

    # path to store the csv
    changes_data_path = DATA_PATH / "change_proneness_data" / project_name / "proneness_results.csv"
    changes_data_pkl_path = DATA_PATH / "change_proneness_data" / project_name / "proneness_results.pkl"

    # Checks if we have already existing collected data in csv format
    if os.path.exists(str(changes_data_path)) and os.path.exists(str(changes_data_pkl_path)):
        changes_data = pickle.load(open(str(changes_data_pkl_path), 'rb'))
        repo_logger.info(f"Repo {project_name} already has processed data in path {str(changes_data_pkl_path)} - OPENING")
        GLOBAL_LOGGER.info(f"Repo {project_name} already has processed data in path {str(changes_data_pkl_path)} - OPENING")
    elif os.path.exists(str(changes_data_path)) and not os.path.exists(str(changes_data_pkl_path)):
        changes_data = read_csv_to_dict(str(changes_data_path))
        pickle.dump(changes_data, open(str(changes_data_pkl_path), 'wb'))
        repo_logger.info(f"Repo {project_name} already has processed data in path {str(changes_data_path)} - OPENING (+ writing in {str(changes_data_pkl_path)})")
        GLOBAL_LOGGER.info(f"Repo {project_name} already has processed data in path {str(changes_data_path)} - OPENING (+ writing in {str(changes_data_pkl_path)})")
    else:
        # "cp": total changes
        changes_data = {"project_id": [], "refactoring_id": [], "refactoring_type": [], "hash": [], "time_stamp": [],
                        "class_id": [], "#refactorings": [], "cp": [], "cp/eloc": [], "dp": []}
        repo_logger.info(f"Repo {project_name} DOES NOT have existing change data - WRITING from 0")
        GLOBAL_LOGGER.info(f"Repo {project_name} DOES NOT have existing change data - WRITING from 0")

    repo = Repo(repo_path)
    assert not repo.bare
    last_official_hash = repo.head.commit.hexsha

    # Current_r_hash will store the commit whose each refactoring type is being analyzed.
    current_r_hash = ""
    ref_types_cache = {}

    # Memory of the changed files so that there's no need to run over their changes in each loop.
    changed_files_memory = {}

    # Get all the commit history.
    overall_commit_history = get_commit_history(repo_path=repo_path, begin_sha="", refactoring_commits=False)
    repo_logger.info(f"Overall commit history collected from Repo {project_name}")
    GLOBAL_LOGGER.info(f"Overall commit history collected from Repo {project_name}")

    for i, refactoring_type, refactoring_hash in zip(refactoring_dict["id"], refactoring_dict["refactoring"],
                                                     refactoring_dict["hash"]):

        # Memory cache logic for refactoring_id definition.
        if refactoring_hash != current_r_hash:
            current_r_hash = refactoring_hash
            ref_types_cache.clear()

        if refactoring_type not in ref_types_cache.keys():
            ref_types_cache[refactoring_type] = 0
        else:
            ref_types_cache[refactoring_type] += 1

        # Check if the refactoring has already been processed
        if check_processed_refactorings(i, project_name, repo_logger):
            repo_logger.info(f"Refactoring {i}-{refactoring_type} ALREADY analyzed - SKIPPING")
            GLOBAL_LOGGER.info(f"Refactoring {i}-{refactoring_type} ALREADY analyzed - SKIPPING")
            continue

        starting_hash = refactoring_dict['hash'][i]
        # Gets the following "Refactoring" commits
        try:
            following_refactoring_commits = get_commit_history(repo_path=repo_path, begin_sha=starting_hash,
                                                               refactoring_commits=True)
            repo_logger.info(f"Following refactoring commits fetched for [repo {project_name} - refactoring {i} - type {refactoring_type} - hash {refactoring_hash}]")
            GLOBAL_LOGGER.info(f"Following refactoring commits fetched for [repo {project_name} - refactoring {i} - type {refactoring_type} - hash {refactoring_hash}]")
        except Exception as e:
            repo_logger.error(f"Error {e} while collecting following refactoring commits for [repo {project_name} - refactoring {i} - type {refactoring_type} - hash {refactoring_hash}] - traceback: {e.with_traceback()}")
            GLOBAL_LOGGER.error(f"Error {e} while collecting following refactoring commits for [repo {project_name} - refactoring {i} - type {refactoring_type} - hash {refactoring_hash}] - traceback: {e.with_traceback()}")
        # In this corner case, filepath from a Class might have changed. In this scenario, we need to dinamically adapt to the
        # new path as the code might remain similar or even untouched. (Done in function check_file_changes > store_classes_data)
        file_path = refactoring_dict['filepath'][i]

        # We need to check for the history order and the frequency in the same commit for generating the refactoring ID
        refactoring_id = make_refactoring_id(order_id=i, refactoring_type=refactoring_type,
                                             ref_type_count_cache=ref_types_cache[refactoring_type],
                                             project_name=project_name)
        repo_logger.info(f"Refactoring ID {refactoring_id} generated for [repo {project_name} - refactoring {i} - type {refactoring_type} - hash {refactoring_hash}]")
        GLOBAL_LOGGER.info(f"Refactoring ID {refactoring_id} generated for [repo {project_name} - refactoring {i} - type {refactoring_type} - hash {refactoring_hash}]")

        # This function checks if there has been some previous refactoring equal to the current that has already processed affected path
        try:
            hashes, paths, classes_dict = get_file_changes_history(refactoring_hash=starting_hash,
                                                                   overall_commit_history=overall_commit_history,
                                                                   repo_path=repo_path, file_path=file_path,
                                                                   refactoring_id=refactoring_id, repo_logger=repo_logger)
            repo_logger.info(
                f"File change history collected for [repo {project_name} - refactoring {i} - type {refactoring_type} - hash {refactoring_hash}]")
            GLOBAL_LOGGER.info(f"File change history collected for [repo {project_name} - refactoring {i} - type {refactoring_type} - hash {refactoring_hash}]")

        except Exception as e:
            repo_logger.error(
                f"Error {e} while collecting file change history for [repo {project_name} - refactoring {i} - type {refactoring_type} - hash {refactoring_hash}] "
                f"traceback: {e.with_traceback()}")
            GLOBAL_LOGGER.error(f"Error {e} while collecting file change history for [repo {project_name} - refactoring {i} - type {refactoring_type} - hash {refactoring_hash}] "
                f"traceback: {e.with_traceback()}")

        posterior_refactorings_count = 0
        # With the hashes and the paths, we calculate the change proneness metrics
        for hash, path in zip(hashes, paths):

            # 1. Check if the hash is within the group of refactoring commits. <hash> and <path> come from commits where
            # its demonstrated that the class was modified. However, we can only consider those changes that happened in a refactoring commit.
            if hash not in following_refactoring_commits:
                continue

            for c in pydrill.Repository(path_to_repo=str(repo_path), only_commits=[hash]).traverse_commits():
                mod_files = c.modified_files
                for mod_file in mod_files:
                    # We just want the path match
                    if mod_file.new_path == path or mod_file.old_path == path:
                        total_changes = int(mod_file.added_lines) + int(mod_file.deleted_lines)
                        eloc = get_eloc(file_path=path, repo_path=repo_path, c_hash=hash, last_hash=last_official_hash)
                        # Checks from the previous class change check the path that is addressed in the current commit and
                        # provides the class id.
                        class_id = fetch_class_id_from_dict(hash, classes_dict)
                        defects = get_defect_proneness(c.msg, max_errors=1)

                        changes_data["project_id"].append(project_name)
                        changes_data["refactoring_id"].append(refactoring_id)
                        changes_data["refactoring_type"].append(refactoring_type)
                        changes_data["hash"].append(hash)
                        changes_data["time_stamp"].append(c.author_date)
                        changes_data["class_id"].append(class_id)
                        changes_data["#refactorings"].append(posterior_refactorings_count+1)
                        changes_data["cp"].append(total_changes)
                        changes_data["cp/eloc"].append(round(total_changes/eloc, 2))

                        if defects is False:
                            changes_data["dp"].append(0)
                        else:
                            changes_data["dp"].append(1)

                        posterior_refactorings_count += 1
                        # We dynamically save the added data into a pickle file.
                        write_dict_to_pickle(dictionary=changes_data, path=str(changes_data_pkl_path))

        record_processed_refactorings(i, refactoring_type, project_name)
        repo_logger.info(f"Refactoring {i}-{refactoring_type} ANALYZED - remaining {i+1}/{len(refactoring_dict["refactoring"])}")
        GLOBAL_LOGGER.info(f"Refactoring {i}-{refactoring_type} ANALYZED - remaining {i+1}/{len(refactoring_dict["refactoring"])}")
    # We dump the last version of the dictionary into a csv file
    write_csv_from_dict(dictionary=changes_data, path=str(changes_data_path))


def change_proneness(repo_name, repo_logger):
    """
    Calculates the change proneness of a refactoring commit within the subsequent refactoring commits.
    """

    repo_path = clone_repo(repo_name=repo_name, repo_logger=repo_logger)

    # Defect proneness calculation approach
    ordered_r_commits = get_refactoring_commits(repo_name=repo_name, repo_logger=repo_logger)  # Gets ordered list of refactoring commits
    ordered_refactorings = get_refactorings(repo_name=repo_name, commit_dict=ordered_r_commits, repo_logger=repo_logger)  # Gets ordered list of refactorings
    get_differences(project_name=repo_name, repo_path=repo_path, refactoring_dict=ordered_refactorings, repo_logger=repo_logger)

    delete_repo(repo_path=repo_path, repo_logger=repo_logger)


def process_repository(repo_name):
    """
    Processes a single software repository for the given analysis type.
    :param repo_path: Path to the repository
    :param analysis_type: Type of analysis to perform ("change_proneness" or "defect_proneness")
    """

    repo_log_file = os.path.join(str(DATA_PATH), "logs", f"{repo_name}.log")
    repo_logger = setup_logger(f"{repo_name}", repo_log_file)
    result = f"Change proneness analysis completed for {repo_name}"

    last_processed_refactoring, total_refactorings_num, total_really_collected_ref_cases = inspect_project(change_proneness_res_path=os.path.join(str(DATA_PATH), "change_proneness_data"), project=repo_name)
    if total_refactorings_num == 0:
        repo_logger.info(f"repository: {repo_name} - Empty from RMiner")
        GLOBAL_LOGGER.info(f"repository: {repo_name} - Empty from RMiner")
        return result, "Success"
    elif total_refactorings_num == last_processed_refactoring:
        repo_logger.info(f"repository: {repo_name} - Fully processed!")
        GLOBAL_LOGGER.info(f"repository: {repo_name} - Fully processed!")
        return result, "Success"
    else:
        try:
            # Simulate change proneness analysis
            repo_logger.info(f"Analyzing change and defect proneness for repository: {repo_name}")
            GLOBAL_LOGGER.info(f"Analyzing change and defect proneness for repository: {repo_name}")
            change_proneness(repo_name=repo_name, repo_logger=repo_logger)
            repo_logger.info(result)
            GLOBAL_LOGGER.info(result)

            return result, "Success"
        except Exception as e:
            return {e}, "Error"


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
            future_to_repo = {executor.submit(process_repository, repo): repo for repo in pending_repos}

            for repo_name in pending_repos:
                GLOBAL_LOGGER.info(f"> Started processing repository {repo_name}")

            for future in as_completed(future_to_repo):
                repo_name = future_to_repo[future]

                try:
                    result_repo, status = future.result()  # Get the result
                    if "Error" in status:
                        GLOBAL_LOGGER.warning(f"> WARNING: {repo_name} failed: {status}")
                        if retries[repo_name] < MAX_RETRIES:
                            retries[repo_name] += 1
                            failed_repos.append(repo_name)
                        else:
                            GLOBAL_LOGGER.error(f"> ERROR: {repo_name} FAILED after {MAX_RETRIES} retries.")
                    else:
                        GLOBAL_LOGGER.info(f"> Finished processing repository {repo_name}")
                except Exception as e:
                    GLOBAL_LOGGER.warning(f"> WARNING Unexpected failure for {repo_name}: {e} - {e.with_traceback()}")
                    failed_repos.append(repo_name)

        pending_repos = failed_repos  # Retry only failed repositories


def main():
    begin = datetime.now()
    GLOBAL_LOGGER.info("Global logging initialized. Process started.")
    try:

        # Setup the global logger (captures all logs)
        os.makedirs(os.path.join(str(DATA_PATH), "logs"), exist_ok=True)

        # Specify repos to be analyzed
        list_repos = get_study_repos()

        # Parallely analyze defect proneness
        GLOBAL_LOGGER.info(f"Processing {len(list_repos)} repositories in parallel.")
        process_repositories(list_repos)

        end = datetime.now()
        # Notify about the end of the script
        msg = f"> SCRIPT COMPLETED\n> TIME REQUIRED: {end - begin}\n> ENDING HOUR: {end}"
        GLOBAL_LOGGER.info(msg)
        send_email(email="mrobredomanero@gmail.com", subject="Input message data processed", message=msg)
    except Exception as e:
        end = datetime.now()
        msg = f"> ERROR IN SCRIPT: {e}\n> TIME SPENT: {end- begin}\n> CRASHING HOUR: {end}"
        GLOBAL_LOGGER.error(msg)
        send_email(email="mrobredomanero@gmail.com", subject="ERROR: motivation reasoning script", message=msg)


if __name__ == '__main__':
    main()