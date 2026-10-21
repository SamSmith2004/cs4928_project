'''
This module contains functions to process commit diffs
'''
import json
import os

from pydriller import Git

from .utility import open_json_file

pwd = os.getcwd()

# import jsonpickle


class DiffFile:
    '''
    Class to store diff information'''
    file_name = ''
    added_lines = 0
    deleted_lines = 0
    changed_by = ''
    diff_content = ''

    def __init__(self, file_name, added_lines, deleted_lines, changed_by, diff_content):
        self.file_name = file_name
        self.added_lines = added_lines
        self.deleted_lines = deleted_lines
        self.changed_by = changed_by
        self.diff_content = diff_content


class CommitInfo:
    '''
    Class to store commit information'''
    commit_hash = ''
    previous_commit_hash = ''
    diff_stats = []

    def __init__(self, commit_hash, previous_commit_hash, diff_stats):
        self.diff_stats = diff_stats
        self.commit_hash = commit_hash
        self.previous_commit_hash = previous_commit_hash


class ProjectInfo:
    '''
    Class to store project information'''
    project_name = ''
    commits = []

    def __init__(self, project_name, commits):
        self.project_name = project_name
        self.commits = commits


def process_commit_diff(commit_hash_path):
    '''
    Process commit diffs from a json file'''
    for json_file in os.listdir(commit_hash_path):
        # if file already exists, skip
        if json_file in os.listdir(f"{pwd}/commits_diff"):
            continue
        
        # skip the apache isis project
        if json_file == 'isis.json':
            continue

        json_file_path = os.path.join(commit_hash_path, json_file)
        data1 = open_json_file(json_file_path)
        project_list = []
        for key in data1:
            print("Project: " + key.get('project'))
            gr = Git('cloned_repos/' + key.get('project'))
            commit_list = []
            for commit_id in key.get('commits'):
                commit = gr.get_commit(commit_id)
                parent_commit_id = ''
                for parent_commit in commit.parents:
                    parent_commit_id = parent_commit
                list_diff = []
                for file in commit.modified_files:
                    list_diff.append(
                        DiffFile(file.filename, file.added_lines,
                                 file.deleted_lines, commit.author, file.diff)
                    )
                commit_list.append(CommitInfo(
                    commit_id, parent_commit_id, list_diff))
            project_list.append(ProjectInfo(key.get('project'), commit_list))

        # create commit diff directory
        commits_diff_dir = f"{pwd}/commits_diff"
        if not os.path.exists(commits_diff_dir):
            os.mkdir(commits_diff_dir)
            # write commits_hash to a json file
        json_str = json.dumps([project.__dict__ for project in project_list],
                              default=lambda o: o.__dict__, indent=4)
        json_obj = json.loads(json_str)
        with open(f"{commits_diff_dir}/{json_file}_diff.json", 'w', encoding="utf-8") as f:
            json.dump(json_obj, f, indent=4)

    # return json_obj
