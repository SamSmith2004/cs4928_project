"""
basic statistics regarding the selected projects should be reported to help readers better understand the dataset.
This includes information on project size, the number of MS components, stars, and the number of issues and commits.
"""

import os
import subprocess
import sys
import traceback
from tqdm import tqdm
import pydriller
import pytz
import requests
from components.utility import DATA_PATH, SCC_PATH, read_tokens, delete_repo, TIOBE_INDEX, countdown, get_headers
import pandas as pd
from dateutil.relativedelta import relativedelta
from datetime import datetime
import json
import random
from git import Repo
import ijson
import logging

# --------------------------------------
# Setup Logging
# --------------------------------------
LOG_DIR = os.path.join(DATA_PATH, "basic_table_logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "basic_stats.log")
os.remove(LOG_FILE)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "basic_stats.log"),
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(console_handler)


def get_stars(project_name):
    tokens = read_tokens()
    if not tokens:
        logger.warning("No tokens found.")
        return 0

    token_index = 0
    github_token = tokens[token_index]

    stargazers_url = f"https://api.github.com/repos/{project_name}/stargazers"
    page_num = 1
    stargazers = 0
    while True:

        params = {'per_page': 100, 'state': 'all', 'page': page_num}
        headers = get_headers(github_token, True)
        repo_response = requests.get(stargazers_url, headers=headers, params=params)

        # Handle rate limiting
        remaining = int(repo_response.headers.get('X-RateLimit-Remaining', 0))
        if remaining < 10:
            if token_index < len(tokens) - 1:
                token_index += 1
                github_token = tokens[token_index]
                logger.warning(f"Rate limit low, switching to token {token_index + 1}/{len(tokens)}")
                continue
            else:
                logger.warning("All tokens exhausted. Sleeping for 1 hour.")
                countdown(3600)
                token_index = 0
                github_token = tokens[token_index]
                continue

        if repo_response.status_code != 200:
            logger.warning(f"Failed to get stargazers for {project_name}: {repo_response.status_code}")
            return 0
        response_json = repo_response.json()
        if len(response_json) == 0:
            return stargazers
        else:
            for stargazer in response_json:
                stargazers += 1
        page_num += 1


def is_directory_empty(dir_path):
    """
    Check if a directory is empty, ignoring hidden files and folders.
    """

    return not any(
        entry for entry in os.scandir(dir_path)
        if not entry.name.startswith('.')  # Ignore hidden files/folders
    )


def process_language_data(temp_csv_path):
    """
        Processes the CSV file to check languages in a given list, sum the Code column for matched languages,
        and find the language(s) with the highest Code value.

        :param csv_file: Path to the CSV file.
        :return: Tuple (matched_languages_count, total_code_sum, highest_code_languages)
        """

    # Load the CSV into a DataFrame
    df = pd.read_csv(temp_csv_path)
    # Convert provided language list to lowercase for case-insensitive comparison
    language_set = {lang.lower() for lang in TIOBE_INDEX}
    # Filter the DataFrame for languages that exist in the given list (case insensitive)
    df["Language_lower"] = df["Language"].str.lower()
    matched_df = df[df["Language_lower"].isin(language_set)]
    # Count matched languages
    matched_languages_count = matched_df.shape[0]
    # Sum of Code column for matched languages
    total_code_sum = matched_df["Code"].sum()
    # Find the highest Code value among matched languages
    max_code_value = matched_df["Code"].max()
    # Get the language(s) with the highest Code value
    highest_code_languages = matched_df[matched_df["Code"] == max_code_value]["Language"].tolist()
    try:
        return matched_languages_count, total_code_sum, highest_code_languages[0]
    except IndexError as e:
        logger.error(e)
        logger.error("Traceback: {}".format(traceback.format_exc()))
        return matched_languages_count, total_code_sum, 0

def get_size(project_name, repos_path):

    repo_name = project_name.split("/")[-1]
    repo_path = os.path.join(repos_path, repo_name)
    temp_csv_path = os.path.normpath(os.path.join(str(DATA_PATH), "temp.csv"))
    subprocess.run([SCC_PATH, repo_path, "-f", "csv", "-o", temp_csv_path], shell=False, check=True)
    matched_languages_count, total_code_sum, highest_code_language = process_language_data(temp_csv_path)
    os.remove(temp_csv_path)

    return matched_languages_count, total_code_sum, highest_code_language


def read_json_to_list(final_projects_path):

    with open(final_projects_path, 'r', encoding="utf-8") as file:
        data = json.load(file)

    return data


def get_creation_year(project_full_name, repo_path):
    """
    Parses automatically the first commit of the cloned repository and fetches it's creation year
    :param project_full_name: full name of the project
    :return:
    """
    try:
        creation_date = None
        last_date = None
        first_hash = None
        last_hash = None
        for commit in pydriller.Repository(path_to_repo=repo_path, order="date-order").traverse_commits():
            creation_date = commit.author_date
            first_hash = commit.hash
            break
        for commit in pydriller.Repository(path_to_repo=repo_path, order="reverse").traverse_commits():
            last_date = commit.author_date
            last_hash = commit.hash
            break

        commits = []
        contributors = set()
        for commit in pydriller.Repository(path_to_repo=repo_path, from_commit=first_hash, to_commit=last_hash).traverse_commits():
            commits.append(commit.hash)
            if "bot" not in commit.author.email:
                contributors.add(commit.author.email)

        # Normalize both to UTC
        dt1_utc = creation_date.astimezone(pytz.UTC)
        dt2_utc = last_date.astimezone(pytz.UTC)
        delta = dt2_utc - dt1_utc
        age_in_years = round(delta.days / 365.25, 2)
        return creation_date.year, age_in_years, len(commits), len(contributors)
    except Exception as e:
        logger.exception(f"Error {e} calculating creation year for {project_full_name}")
        logger.exception(f"Traceback: {traceback.format_exc()}")
        return None, None, 0, 0


def clone_repo(repo_name, repos_path):
    """
    Clone repository into the specified path

    :param repo_name: Short name of the repository
    :return: The path of the repository clonned
    """
    clone_url = f"https://github.com/{repo_name}.git"
    os.makedirs(repos_path, exist_ok=True)
    repo_path = os.path.join(repos_path, repo_name.split("/")[-1])
    if os.path.exists(repo_path) and is_directory_empty(repo_path) is False:
        return repo_path
    subprocess.run(["git", "config", "--global", "core.longpaths", "true"])
    subprocess.run(['git', 'clone', clone_url, repo_path], check=True)
    return repo_path


def clone_repositories(projects_list, repos_path):

    final_projects_list = []
    for repo_full_name in projects_list:
        try:
            logger.info(f"Cloning {repo_full_name} repository...")
            clone_repo(repo_full_name, repos_path)
            logger.info(f"Repository {repo_full_name} successfully cloned!")
            final_projects_list.append(repo_full_name)
        except Exception as e:
            logger.error(f"Error at clonning the repository {repo_full_name}: {e}")
            logger.error("Traceback: ", traceback.format_exc())

    return final_projects_list

def get_issues(project_name):

    tokens = read_tokens()
    if not tokens:
        logger.warning("No GitHub tokens found.")
        return 0

    token_index = 0
    github_token = tokens[token_index]

    stargazers_url = f"https://api.github.com/repos/{project_name}/issues"
    page_num = 1
    num_closed_issues = 0
    num_open_issues = 0
    while True:

        params = {'per_page': 100, 'state': 'all', 'page': page_num}
        headers = get_headers(github_token, False)
        repo_response = requests.get(stargazers_url, headers=headers, params=params)

        # Handle rate limiting
        remaining = int(repo_response.headers.get('X-RateLimit-Remaining', 0))
        if remaining < 10:
            if token_index < len(tokens) - 1:
                token_index += 1
                github_token = tokens[token_index]
                logger.warning(f"Rate limit reached. Switched to token {token_index + 1}")
                continue
            else:
                logger.warning("All tokens exhausted. Sleeping for 1 hour.")
                countdown(3600)
                token_index = 0
                github_token = tokens[token_index]
                continue

        if repo_response.status_code != 200:
            return 0, 0, 0
        response_json = repo_response.json()
        if len(response_json) == 0:
            return num_closed_issues, num_open_issues, num_closed_issues+num_open_issues
        else:
            for issue_object in response_json:
                try:
                    state = issue_object["state"]
                    if state == "open":
                        num_open_issues += 1
                    else:
                        num_closed_issues += 1
                except Exception as e:
                    logger.exception(f"Error {e} getting refactoring data for {project_name}")
                    logger.error("Traceback: ", traceback.format_exc())
                    num_open_issues += 1
        page_num += 1


def get_ref_info(project_name):
    """
    Fetches information refactoring the refactoring mining for the considered projects
    :param project_name:
    :return: commits with mined refactorings, and total number of refactorings
    """

    ref_type_path = os.path.join(DATA_PATH, "back-up/output_data/refactor_types", f"{project_name}.json")
    ref_commit_path = os.path.join(DATA_PATH, "back-up/output_data/refactoring_commits", f"{project_name}.json")
    ref_type_count = 0
    ref_num = 0
    ref_commit_count = 0

    try:
        with open(ref_type_path, 'rb') as f:
            parser = ijson.items(f, 'item')
            for project_entry in parser:
                if project_entry.get("project") == project_name:
                    count_per_type = project_entry.get("count_per_type", {})
                    ref_type_count = len(count_per_type)
                    ref_num = sum(count_per_type.values())
                    break

        with open(ref_commit_path, 'rb') as f:
            parser = ijson.items(f, 'item')
            for project in parser:
                if project.get('project') == project_name:
                    # Stream over commits_data directly to avoid loading the whole list
                    f.seek(0)  # Rewind to re-parse from beginning
                    commits_parser = ijson.items(f, 'item.commits_data.item')
                    ref_commit_count = sum(1 for _ in commits_parser)

        return ref_type_count, ref_num, ref_commit_count
    except Exception as e:
        logger.exception(f"Error {e} getting refactoring data for {project_name}")
        logger.error("Traceback: ", traceback.format_exc())
        return 0, 0, 0


def make_table():
    # Define the new dictionary structure with nested columns
    table_dict = {
            "Project": [],
            "Creation year": [],
            "Age": [],
            "Size": [],
            "Main Language": [],
            "Stars": [],
            "Open issues": [],
            "Closed issues": [],
            "Overall issues": [],
            "Commits": [],
            "Contributors": [],
            "# Languages": [],
            "# Refactoring Types": [],
            "# Mined Refactoring Commits": [],
            "# Mined Refactorings": []
        }

    output_path = os.path.join(DATA_PATH, "basic_statistics_table.csv")
    final_projects_path = os.path.join(DATA_PATH, "back-up/output_data", "unique_projects.json")
    projects_list = read_json_to_list(final_projects_path)

    # Load existing CSV if it exists and populate table_dict
    existing_projects = set()
    if os.path.exists(output_path):
        existing_df = pd.read_csv(output_path)
        existing_projects = set(existing_df["Project"].tolist())  # Get existing projects
        for column in existing_df.columns:
            if column in table_dict:
                table_dict[column] = existing_df[column].tolist()

    # Clone repositories so that the process can be parallelized afterward
    repos_path = os.path.join(DATA_PATH, "repos_2")
    if os.path.exists(repos_path):
        final_projects_list = os.listdir(repos_path)
        final_projects_list = [f"apache/{project}" for project in final_projects_list]
    else:
        os.makedirs(repos_path, exist_ok=True)
        final_projects_list = clone_repositories(projects_list, repos_path)

    for project_full_name in tqdm(final_projects_list, desc="Processing Projects", unit="project"):

        project_name = project_full_name.split("/")[-1]

        # Skip project if it's already in the output CSV
        if project_name in existing_projects:
            logger.info(f"Skipping existing project: {project_name}")
            continue

        logger.info(f"Starting processing of project: {project_full_name}")
        table_dict["Project"].append(project_name)

        # We  get creation year from the first commit in the VCH
        repo_path = os.path.join(repos_path, project_name)
        creation_year, project_age, num_commits, num_contributors = get_creation_year(project_full_name=project_full_name, repo_path=repo_path)
        table_dict["Creation year"].append(creation_year)
        table_dict["Age"].append(project_age)
        table_dict["Commits"].append(num_commits)
        table_dict["Contributors"].append(num_contributors)

        # Get GitHub stars
        num_stars = get_stars(project_name=project_full_name)
        table_dict["Stars"].append(num_stars)

        # Get num_languages, project size and main language
        num_languages, project_size, main_language = get_size(project_name=project_full_name, repos_path=repos_path)
        table_dict["# Languages"].append(num_languages)
        table_dict["Size"].append(project_size)
        table_dict["Main Language"].append(main_language)

        # Get num of issues
        num_closed_issues, num_open_issues, num_total_issues = get_issues(project_full_name)
        table_dict["Open issues"].append(num_open_issues)
        table_dict["Closed issues"].append(num_closed_issues)
        table_dict["Overall issues"].append(num_total_issues)

        # Get num of refactorings mined
        ref_type_count, num_refactorings, num_refactoring_commits = get_ref_info(project_name)
        table_dict["# Refactoring Types"].append(ref_type_count)
        table_dict["# Mined Refactoring Commits"].append(num_refactoring_commits)
        table_dict["# Mined Refactorings"].append(num_refactorings)

        # Convert new row into DataFrame and append to CSV
        new_row = {
            "Project": project_name,
            "Creation year": creation_year,
            "Age": project_age,
            "Size": project_size,
            "Main Language": main_language,
            "Stars": num_stars,
            "Open issues": num_open_issues,
            "Closed issues": num_closed_issues,
            "Overall issues": num_total_issues,
            "Commits": num_commits,
            "Contributors": num_contributors,  # Without bots
            "# Languages": num_languages,
            "# Refactoring Types": ref_type_count,
            "# Mined Refactoring Commits": num_refactoring_commits,
            "# Mined Refactorings": num_refactorings
        }

        final_df = pd.DataFrame([new_row])
        # Append row to CSV
        final_df.to_csv(output_path, mode='a', header=not os.path.exists(output_path), index=False)

    logger.info(f"> Table saved at {output_path}")

def main():
    make_table()


if __name__ == "__main__":
    main()