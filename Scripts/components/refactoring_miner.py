'''
TBW'''
import json
import os
import subprocess
import time
from datetime import datetime
from typing import List, Tuple

from github import Auth, Github
from pydriller import Repository

from .helper import get_config_variable
from .utility import NoInternetConnectionError, check_internet_connection

auth = Auth.Token(get_config_variable("API_KEY", [], {}))
pwd = os.getcwd()
g = Github(auth=auth)


refactoring_miner_path = f"/RefactoringMiner-3.0.9/bin"

print(f"Current working directory: {refactoring_miner_path}")
print(pwd)


class RefactoringMiner:
    '''
    Class to mine refactoring data from the cloned repositories'''

    def __init__(self):
        pass

    def get_all_commits(self, github_repos) -> List[str]:
        """Get list of all commit hashes in chronological order"""
        project_commit_hashes = []
        for github_repo in github_repos:
            github_repo_path = f"{pwd}/cloned_repos/{github_repo}"
            print(f"Getting commits for {github_repo}")
            if github_repo == "plc4x":
                print(f"Skipping {github_repo}")
                continue
            try:
                result = subprocess.run(
                    ['git', 'log', '--reverse', '--format=%H'],
                    cwd=github_repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                project_commit_hashes.append({
                    "project": github_repo,
                    "commit_hashes": result.stdout.strip().split('\n')
                })
                # return result.stdout.strip().split('\n')

            except subprocess.CalledProcessError as e:
                print(f"Failed to get commits: {e}")
                return []
        return project_commit_hashes

    def split_commits_into_batches(self, commits: List, batch_size) -> List:
        """Split commits into batches of specified size"""
        batches = []
        for project_commits in commits:
            # skip the projects with over 5000 commits
            # if len(project_commits['commit_hashes']) > 5000:
            #     print(
            #         f"Skipping {project_commits['project']} with over 5000 commits")
            #     continue
            project_batches = []
            for i in range(0, len(project_commits['commit_hashes']), batch_size):
                batch_commits = project_commits['commit_hashes'][i:i + batch_size]
                if batch_commits:
                    project_batches.append({
                        f"batch_{i // batch_size + 1}": {
                            "commits": (batch_commits[0], batch_commits[-1])
                        }
                    })
            batches.append({
                "project": project_commits['project'],
                "batches": project_batches,
                "repo_path": f"{pwd}/cloned_repos/{project_commits['project']}"
            })
        return batches

    def get_refactorings(self, github_repos):
        '''
        TBW'''
        # use subprocess to run RefactoringMiner on the cloned repositories
        if os.getcwd() != refactoring_miner_path:
            os.chdir(refactoring_miner_path)
        # create the output folder
        if "output" not in os.listdir(pwd):
            os.mkdir(f"{pwd}/output")
        for index, github_repo in enumerate(github_repos):
            # check is json file already exists in the output folder
            if f"{github_repo['project']}.json" in os.listdir(f"{pwd}/output"):
                print(
                    f"Refactoring data for {github_repo['project']} already exists")
                continue
            for batch in github_repo['batches']:
                for key, value in batch.items():
                    start_commit = value['commits'][0]
                    end_commit = value['commits'][1]
                    repo_path = github_repo['repo_path']
                    print(
                        f"Running RefactoringMiner on {github_repo['project']} from {start_commit} to {end_commit}")
                    subprocess.run(["./RefactoringMiner",
                                    "-bc",
                                    repo_path,
                                    start_commit,
                                    end_commit,
                                    '-json',
                                    f"{pwd}/output/{github_repo['project']}_{key}.json"], check=False)
                    # cooldown for 10 seconds
                    print("Cooling down for 60 seconds")
                    time.sleep(25)
        os.chdir(pwd)

    def get_refactoring_types(self, refactoring_data_path):
        '''
        TBW
        '''
        print(os.path.abspath(refactoring_data_path))

        # go through the files in the directory
        for ref_file in os.listdir(refactoring_data_path):
            if ref_file in os.listdir(f"{pwd}/refactor_type"):
                print(f"Refactoring types for {ref_file} already exists")
                continue
            # skip the apache isis repository
            if ref_file == "isis.json":
                continue
            ref_file_path = os.path.join(refactoring_data_path, ref_file)
            # open the json file
            with open(ref_file_path, "r", encoding="utf-8") as json_file:
                refactoring_types = []
                refactoring_data = json.load(json_file)

                print(refactoring_data)

                for index_ref, refactoring in enumerate(refactoring_data):
                    refactoring_types.append(
                        {
                            "project": refactoring['project'],
                            "refactoring_type": [],
                            "count_per_type": {}
                        })
                    for index, ref in enumerate(refactoring["commits_data"]):
                        print(index)
                        if len(ref["refactorings"]) != 0:
                            for ref_type in ref["refactorings"]:
                                refactoring_types[index_ref]["refactoring_type"].append(
                                    ref_type['type'])
                # make the refactoring types unique
                for refac in refactoring_types:
                    print("Counting refactoring types for", refac["project"])
                    refac["count_per_type"] = {ref_type: refac["refactoring_type"].count(
                        ref_type) for ref_type in refac["refactoring_type"]}
                    refac["refactoring_type"] = list(
                        set(refac["refactoring_type"]))

                # create the refactor_type directory if it doesn't exist
                refactor_type_dir = f"{pwd}/refactor_type"
                if not os.path.exists(refactor_type_dir):
                    os.mkdir(refactor_type_dir)

                # store each refactoring type in a json file
                for refac in refactoring_types:
                    project_name = refac["project"]
                    with open(f"{refactor_type_dir}/{project_name}.json", "w", encoding="utf-8") as json_file:
                        json.dump(refactoring_types, json_file, indent=4)

                # return refactoring_types

    def get_commits_hash(self, refactoring_data_path):
        '''
        Gets the commit hash for each commit with refactoring data
        '''
        gen_commit_hash = []
        for ref_file in os.listdir(refactoring_data_path):
            if ref_file in os.listdir(f"{pwd}/commits_hash"):
                print(f"Commits hash for {ref_file} already exists")
                continue
            # skip the apache isis repository
            if ref_file == "isis.json":
                continue
            ref_file_path = os.path.join(refactoring_data_path, ref_file)
            with open(ref_file_path, "r", encoding="utf-8") as json_file:
                refactoring_data = json.load(json_file)

            commits_hash = []
            for index, refactoring in enumerate(refactoring_data):
                commits_hash.append(
                    {
                        "project": refactoring['project'],
                        "commits": []
                    })
                gen_commit_hash.append({
                    "project": refactoring['project'],
                    "commits": []
                })
                for ref in refactoring["commits_data"]:
                    commits_hash[index]["commits"].append(ref["commit_hash"])
                    gen_commit_hash[index]["commits"].append(ref["commit_hash"])
            # create the commit_hash directory if it doesn't exist
                commits_hash_dir = f"{pwd}/commits_hash"
                if not os.path.exists(commits_hash_dir):
                    os.mkdir(commits_hash_dir)
                    # write commits_hash to a json file
                with open(f"{commits_hash_dir}/{ref_file}", "w", encoding="utf-8") as json_file:
                    json.dump(commits_hash, json_file, indent=4)
        return gen_commit_hash

    def get_interefactoring_commit_period(self, commits_hash_path):
        '''
        Gets the interafactoring commit period between commits
        '''

        for ref_file in os.listdir(commits_hash_path):
            if ref_file in os.listdir(f"{pwd}/interefactoring_commit_period"):
                print(
                    f"Interefactoring commit period for {ref_file} already exists")
                continue
            # skip the apache isis repository
            if ref_file == "isis.json":
                continue
            ref_file_path = os.path.join(commits_hash_path, ref_file)
            with open(ref_file_path, "r", encoding="utf-8") as json_file:
                commits_hash = json.load(json_file)

            repo_data = []

            # check internet connection
            try:
                is_internet_connection = check_internet_connection()
                if is_internet_connection:
                    for index, commits in enumerate(commits_hash):
                        # get the name of the repository
                        repo = g.get_repo(f"apache/{commits['project']}")
                        repo_data.append({
                            "project": commits['project'],
                            "commits": []
                        })
                        for commit in commits['commits']:
                            # get the commit period
                            commit_period = repo.get_commit(
                                commit).commit.author.date
                            repo_data[index]['commits'].append({
                                "commit_hash": commit,
                                "commit_period": commit_period
                            })
                    # convert datetime to string in the repo_data
                    for repo in repo_data:
                        for commit in repo['commits']:
                            commit['commit_period'] = commit['commit_period'].strftime(
                                "%Y-%m-%d %H:%M:%S")

                    # create the interefactoring_commit_period directory if it doesn't exist
                    interefactoring_commit_period_dir = f"{pwd}/interefactoring_commit_period"
                    if not os.path.exists(interefactoring_commit_period_dir):
                        os.mkdir(interefactoring_commit_period_dir)
                        # write commits_hash to a json file
                    with open(f"{interefactoring_commit_period_dir}/{ref_file}", "w", encoding="utf-8") as json_file:
                        json.dump(repo_data, json_file, indent=4)

            except NoInternetConnectionError:
                print('No internet connection')
                return "No internet connection"
            # return repo_data

    def get_average_time_between_refactorings(self, interefactoring_commit_period_path):
        '''
        Gets the average time between refactorings in days
        '''

        for ref_file in os.listdir(interefactoring_commit_period_path):
            if ref_file in os.listdir(f"{pwd}/average_time_between_refactorings"):
                print(
                    f"Average time between refactorings for {ref_file} already exists")
                continue
            # skip the apache isis repository
            if ref_file == "isis.json":
                continue
            ref_file_path = os.path.join(
                interefactoring_commit_period_path, ref_file)
            with open(ref_file_path, "r", encoding="utf-8") as json_file:
                interefactoring_commit_period_data = json.load(json_file)
            commit_time_diff = []
            for index, refactoring in enumerate(interefactoring_commit_period_data):
                commit_time_diff.append({
                    "project": refactoring['project'],
                    "commits_diff": [],
                    "average_time_between_refactorings": 0,
                })
                for commit in refactoring['commits']:
                    commit['commit_period'] = datetime.strptime(
                        commit['commit_period'], "%Y-%m-%d %H:%M:%S")
                for i in range(1, len(refactoring['commits'])):
                    time_diff = refactoring['commits'][i]['commit_period'] - \
                        refactoring['commits'][i-1]['commit_period']
                    # convert all negative time_diff to positive with absoulte
                    # time_diff = abs(time_diff)
                    # convert time_diff to string
                    # time_diff = str(time_diff)
                    # convert time_diff to seconds
                    time_diff = time_diff.total_seconds()
                    time_diff = abs(time_diff)
                    commit_time_diff[index]['commits_diff'].append(time_diff)
            # add key for average time between refactorings
            for index, refactoring in enumerate(commit_time_diff):
                print(commit_time_diff[index])
                if len(refactoring['commits_diff']) != 0:
                    commit_time_diff[index]['average_time_between_refactorings'] = sum(
                        refactoring['commits_diff']) / len(refactoring['commits_diff'])
                    # convert average time between refactorings to days
                    commit_time_diff[index]['average_time_between_refactorings_in_days'] = commit_time_diff[
                        index]['average_time_between_refactorings'] / 86400
                else:
                    commit_time_diff[index]['average_time_between_refactorings'] = 0
                    commit_time_diff[index]['average_time_between_refactorings_in_days'] = 0
                    commit_time_diff[index]['message'] = "No refactorings found"
            # create the average_time_between_refactorings directory if it doesn't exist
            average_time_between_refactorings_dir = f"{pwd}/average_time_between_refactorings"
            if not os.path.exists(average_time_between_refactorings_dir):
                os.mkdir(average_time_between_refactorings_dir)
                # write commits_hash to a json file
            with open(f"{average_time_between_refactorings_dir}/{ref_file}", "w", encoding="utf-8") as json_file:
                json.dump(commit_time_diff, json_file, indent=4)
            # return commit_time_diff

        # get the name of the repository
        # for index, commits in enumerate(commits_hash):
        #     repo_name = commits['project']
        #     # format the repository name
        #     repo_name = repo_name.split('/')[-1]
        #     if repo_name in os.listdir(f"{pwd}/cloned_repos"):
        #         repo_path = f"{pwd}/cloned_repos/{repo_name}"
        #         repo_data.append(
        #             {
        #                 "project": repo_name,
        #                 "path": repo_path,
        #                 "commits": []
        #             }
        #         )
        #         # get the commits
        #         print(f"Getting commits for {repo_name}")
        #         print(f"Repository path: {repo_path}")
        #         repo = Repository(repo_path)

        #         for commit in repo.traverse_commits():
        #             if commit.hash in commits['commits']:
        #                 print(commit.hash, commit.author.name, commit.author.email, commit.msg)
        #                 # get the commit period
        #                 commit_period = commit.committer_date
        #                 print(commit_period)
        #                 repo_data[index]['commits'].append({
        #                     "commit_hash": commit.hash,
        #                     "commit_period": commit_period
        #                 })

        # # convert datetime to string in the repo_data
        # for repo in repo_data:
        #     for commit in repo['commits']:
        #         commit['commit_period'] = commit['commit_period'].strftime("%Y-%m-%d %H:%M:%S")

        # return repo_data

# refac = RefactoringMiner()

# refac.get_refactorings()
