'''
TBW
'''
# import requests
import csv
import json
import os
import re
import subprocess
from collections import defaultdict
from json.decoder import JSONDecodeError

# csv file name
filename = "./data/sonar_measures.csv"


class CSVHandler:
    '''
    Class to handle CSV files'''

    def __init__(self, filename_i):
        self.filename = filename_i

    def read_csv(self):
        '''
        Read a CSV file'''
        rows = []
        with open(self.filename, 'r', encoding="utf-8") as csvfile:
            # creating a csv reader object
            csvreader = csv.reader(csvfile)

            # extracting each data row one by one
            for row in csvreader:
                rows.append(row)
        return rows

    def write_csv(self, data, filename_o):
        '''
        Write data to a CSV file'''
        with open(filename_o, 'w', newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(data)

    def write_json(self, data, filename_j):
        '''
        Write data to a JSON file'''
        with open(filename_j, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)

    def read_json(self, filename_j):
        '''
        Read a JSON file'''
        with open(filename_j, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data

    def get_project_name_column(self, rows):
        '''
        Get the project name column from the csv file'''
        all_projects = []
        for row in rows:
            # parsing each column of a row
            for col in row[1:2]:
                all_projects.append(col)
        return all_projects

    def format_project_name(self, project_list):
        '''
        Format the project names'''
        formatted_project_list = []
        for project in project_list:
            if project.startswith("apache_"):
                formatted_project = project.replace("apache_", "apache/")
            elif project.startswith("apache-"):
                formatted_project = project.replace("apache-", "apache/")
            else:
                formatted_project = f"apache/{project}"
            formatted_project_list.append(formatted_project)
        return formatted_project_list

    def get_unique_projects(self, project_list):
        '''
        Get the unique projects'''
        return list(set(project_list))

    def build_github_url(self, unique_projects):
        '''
        Build the GitHub URL for the projects'''
        unique_project_urls = []  # list to store unique project urls
        # limit the number of projects to 5
        print(len(unique_projects))
        # unique_projects = unique_projects[:10]
        for project in unique_projects:
            project_url = f"https://github.com/{project}"
            unique_project_urls.append(project_url)
        return unique_project_urls

    # add logic to ask the user where they want to clone the repos
    def clone_repo(self, unique_project_urls):
        '''
        Clone the repositories'''
        cloned_repos_path = "./cloned_repos"
        repo_names = []
        for project_url in unique_project_urls:
            if project_url == "https://github.com/apache/":
                continue
            # use subprocess to clone the repository
            subprocess.run(["git", "clone", project_url,
                           f"{cloned_repos_path}/{project_url.split('/')[-1]}"], check=False)
            # store the name of the repos
            repo_names.append(project_url.split('/')[-1])
            print(repo_names)
        return repo_names

    def local_repo_name(self):
        '''
        Get the names of the cloned repositories
        '''
        cloned_repos_path = "./cloned_repos"
        folders = [
            name for name in os.listdir(cloned_repos_path) if os.path.isdir(
                os.path.join(
                    cloned_repos_path,
                    name))]
        return folders

    # def get_repo_info(self, unique_projects):
    #     # GitHub API endpoint for getting the languages of a repository
    #     url = f"https://api.github.com/repos/apache/{unique_projects[300]}/languages"
    #     response = requests.get(url, timeout=5)
    #     if response.status_code == 200:
    #         languages = response.json()  # The response is a JSON object
    #         print("Languages used in the repository:")
    #         for language, bytes_of_code in languages.items():
    #             print(f"{language}: {bytes_of_code} bytes")
    #     else:
    #         print('Failed!')

    def merge_json_files_by_project_and_cleanup(self):
        """
        Merge JSON files by project and delete batch files.
        Skips files with JSON errors and logs the issue.
        """
        # Define regex to extract project name from filename
        directory = "./output"
        pattern = re.compile(r'^(?P<project_name>.+?)_batch_\d+\.json$')

        # Dictionary to store project names and output lists
        project_data = defaultdict(list)
        project_files = defaultdict(list)

        # Scan directory and process each file
        for filename in os.listdir(directory):
            match = pattern.match(filename)
            if match:
                project_name = match.group("project_name")
                file_path = os.path.join(directory, filename)

                # Store the file path for cleanup later
                project_files[project_name].append(file_path)

                # Load JSON data and append "commits" to project_data
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        project_data[project_name].extend(data.get("commits", []))
                except JSONDecodeError as e:
                    print(f"Skipping file due to JSON error: {file_path}")
                    print(f"Error details: {e}")

        # Write merged output and delete batch files
        for project_name, commits in project_data.items():
            output_file = os.path.join(directory, f"{project_name}.json")

            # Save the merged JSON
            with open(output_file, 'w') as f_out:
                json.dump({"commits": commits}, f_out, indent=4)

            print(f"Merged files for {project_name} into {output_file}")

            # Delete batch files after merging
            for file_path in project_files[project_name]:
                os.remove(file_path)
                print(f"Deleted file: {file_path}")

    def parse_json_files(self):
        '''
        Parse JSON files in a directory and store commit data in separate JSON files'''

        directory = "./output"
        output_directory = "./refactoring_commits"
        os.makedirs(output_directory, exist_ok=True)
        print(f"We are Processing JSON files in {directory}")
        print(f"Here is the new current working directory {directory}")

        
        print("#############################")
        print(directory)
        print(os.path.abspath(directory))
        print("#############################")
        # Iterate through all files in the directory
        for proc_filename in os.listdir(directory):
            json_data = []
            mined_commit_data = []
            if proc_filename.endswith(".json"):  # Process only .json files
                file_path = os.path.join(
                    os.path.abspath(directory), proc_filename)
                print(f"Processing {file_path}")

                # Open and parse the JSON file
                with open(file_path, 'r', encoding="utf-8") as file:
                  # 
                    print(f'we are currently in {file_path}')
                    data = json.load(file)
                    data = data['commits']

                    # Append the list data from the JSON file to json_data
                    if isinstance(data, list):  # Ensure data is a list
                        json_data.append(data)
                        non_empty_commit_data = []

                        for datum in data:
                            if len(datum['refactorings']) != 0:
                                non_empty_commit_data.append(
                                    {
                                        "commit_hash": datum['sha1'],
                                        "refactorings": datum['refactorings']
                                    }
                                )
                        project_name = proc_filename.split(".")[0]
                        mined_commit_data.append(
                            {"project": project_name,
                                "commits_data": non_empty_commit_data}
                        )

                        # Write the mined commit data to a separate JSON file for each project
                        project_output_file = os.path.join(
                            output_directory, f"{project_name}.json")
                        self.write_json(mined_commit_data,
                                        project_output_file)
                    else:
                        print(f"Data in {proc_filename} is not a list")
        return mined_commit_data
