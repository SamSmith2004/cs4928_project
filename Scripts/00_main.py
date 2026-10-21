'''
TBW'''
import os
import sys
from components.get_github_url import CSVHandler
from components.refactoring_miner import RefactoringMiner
from components.get_commit_diff import process_commit_diff
from components.helper import get_config_variable
from configparser import ConfigParser
from threading import Thread
from components.its_miner import ITSMiner
import logging
import json

def setup_logger():
    """
    Setup and configure the logger for this module
    """

    # Setting up module level logger
    logger = logging.getLogger(__name__)
    console_handler = logging.StreamHandler()
    logger.addHandler(console_handler)
    formatter = logging.Formatter(
        fmt="{asctime} - {name} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
    )
    console_handler.setFormatter(formatter)
    logger.setLevel(get_config_variable("LOGGING_LEVEL", ["logging", "level"], config))
    return logger

def mine_issue_data(config: ConfigParser, repos: list):
    """
    Mine the issue data for repos.
    This method needs to run in a thread

    :param config: Configuration object
    :param repos: list of projects
    """

    total = len(repos)
    miner = ITSMiner(config)

    for num, repo in enumerate(repos):
        miner.logger.info(f"Mining repository ({num+1}/{total})")
        data = miner.mine_issue_data(repo)

        if data:
            with open(f"./issues/{repo.replace("/","_")}.json", "w") as f:
                json.dump(data,f)

def banner():
    print(r'''
    
        $$$$$$$\  $$$$$$$$\ $$$$$$$\   $$$$$$\          $$\      $$\ $$$$$$\ $$\   $$\ $$$$$$$$\ $$$$$$$\  
        $$  __$$\ $$  _____|$$  __$$\ $$  __$$\         $$$\    $$$ |\_$$  _|$$$\  $$ |$$  _____|$$  __$$\ 
        $$ |  $$ |$$ |      $$ |  $$ |$$ /  $$ |        $$$$\  $$$$ |  $$ |  $$$$\ $$ |$$ |      $$ |  $$ |
        $$$$$$$  |$$$$$\    $$$$$$$  |$$ |  $$ |$$$$$$\ $$\$$\$$ $$ |  $$ |  $$ $$\$$ |$$$$$\    $$$$$$$  |
        $$  __$$< $$  __|   $$  ____/ $$ |  $$ |\______|$$ \$$$  $$ |  $$ |  $$ \$$$$ |$$  __|   $$  __$$< 
        $$ |  $$ |$$ |      $$ |      $$ |  $$ |        $$ |\$  /$$ |  $$ |  $$ |\$$$ |$$ |      $$ |  $$ |
        $$ |  $$ |$$$$$$$$\ $$ |       $$$$$$  |        $$ | \_/ $$ |$$$$$$\ $$ | \$$ |$$$$$$$$\ $$ |  $$ |
        \__|  \__|\________|\__|       \______/         \__|     \__|\______|\__|  \__|\________|\__|  \__|
                                                                                                        
    ''')

if __name__ == "__main__":
    banner()
    config = ConfigParser()
    config.read("config.ini")
    logger = setup_logger()


    # instance of CSVHandler
    csv_handler = CSVHandler(get_config_variable("INPUT_FILE", ["input","path"], config))

    # instance of refactoring miner
    refactoring_miner = RefactoringMiner()

    # read the csv file
    rows = csv_handler.read_csv()

    # get project name column
    all_projects = csv_handler.get_project_name_column(rows)
    logger.info(f"Total projects are: {len(all_projects)}")

    # format project names
    formatted_projects = csv_handler.format_project_name(all_projects)

    # get unique projects
    unique_projects = csv_handler.get_unique_projects(formatted_projects)

    # write unique projects to a csv file
    csv_handler.write_json(unique_projects, 'unique_projects.json')

    # build the github url for the projects
    unique_projects_url = csv_handler.build_github_url(unique_projects)

    # write the unique projects url to a json file
    csv_handler.write_json(unique_projects_url, 'unique_projects_url.json')

    # get issue data for all repos
    issue_thread = Thread(target=mine_issue_data, args=(config, unique_projects,) )
    issue_thread.start()

    # cloning repositories -> data is stored in the cloned_repos folder
    csv_handler.clone_repo(unique_projects_url)

    # getting the local repo names
    local_repo_name = csv_handler.local_repo_name()

    # get project all commit hashes
    project_commit_hashes = refactoring_miner.get_all_commits(local_repo_name)
    csv_handler.write_json(project_commit_hashes, 'project_commit_hashes.json')

    # split the project commit hashes
    split_project_commit_hashes = refactoring_miner.split_commits_into_batches(project_commit_hashes, 300)
    csv_handler.write_json(split_project_commit_hashes, 'split_project_commit_hashes.json')

    # run refactoring miner
    refactoring_miner.get_refactorings(split_project_commit_hashes)

    # analyze each json file to get the project data to work with
    csv_handler.merge_json_files_by_project_and_cleanup()

    # parse the json files and creates the refactoring_commits folder
    csv_handler.parse_json_files()

    # get refactoring types and save to a json file
    refactoring_miner.get_refactoring_types("./refactoring_commits")

    # get the commit hash
    commits_hash = refactoring_miner.get_commits_hash("./refactoring_commits")
    # csv_handler.write_json(commits_hash, 'commits_hash.json')

    # get interefactoring commit period from commit hash (actual mining)
    interefactoring_commit_period = refactoring_miner.get_interefactoring_commit_period('./commits_hash')

    # get the average time between commits
    refactoring_miner.get_average_time_between_refactorings('./interefactoring_commit_period')

    # get commit diff
    process_commit_diff('./commits_hash')

    issue_thread.join()

