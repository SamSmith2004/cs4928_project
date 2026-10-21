"""Developers effort component: collects total TLOC for each refactoring and developer"""

import csv
import json
import os
import subprocess
from configparser import ConfigParser
from csv import writer
from operator import itemgetter
from pprint import pprint

import git
import pandas as pd


class DevEffort:
    """Class for developers effort; initialized with a GitHub project path"""

    tiobe_index = {
        "Visual FoxPro", "1C", "4th Dimension", "ABAP", "ABC", "ActionScript", "Ada",
        "Agilent VEE", "Algol", "Alice", "Angelscript", "Apex", "APL", "Applescript",
        "Arc", "AspectJ", "Assembly language", "ATLAS", "AutoHotkey", "AutoIt", "AutoLISP",
        "Awk", "Bash", "Basic", "bc", "BCPL", "BETA", "Bourne shell", "Brainfuck", "C shell",
        "C#", "C++", "C", "Caml", "Carbon", "Ceylon", "CFML", "Chapel", "CHILL", "CIL",
        "Clojure", "COBOL", "CoffeeScript", "Crystal", "Curl", "D", "Dart", "Delphi/Object Pascal",
        "DiBOL", "Dylan", "E", "ECMAScript", "Eiffel", "Elixir", "Elm", "Emacs Lisp", "Erlang",
        "F#", "Factor", "Falcon", "Fantom", "Forth", "Fortran", "FreeBASIC", "GAMS", "GLSL",
        "Go", "Groovy", "Hack", "Harbour", "Haskell", "Haxe", "Heron", "Icon", "IDL", "Idris",
        "Io", "J", "JADE", "Java", "JavaScript", "Julia", "Korn shell", "Kotlin", "LabVIEW",
        "Ladder Logic", "Lasso", "Lingo", "Lisp", "Logo", "LotusScript", "Lua", "MAD", "Magic",
        "Magik", "MANTIS", "Maple", "MATLAB", "Max/MSP", "MAXScript", "MEL", "Mercury", "ML",
        "Modula-2", "Modula-3", "Monkey", "MQL5", "MS-DOS batch", "MUMPS", "NATURAL", "Nim",
        "NQC", "Objective-C", "OCaml", "OpenCL", "OpenEdge ABL", "OPL", "Oz", "Pascal", "Perl",
        "PHP", "Pike", "PostScript", "PowerBasic", "PowerShell", "Processing", "Prolog",
        "PureBasic", "Python", "R", "Racket", "REBOL", "Red", "REXX", "Ring", "RPG", "Ruby",
        "Rust", "SAS", "Scala", "Scheme", "sed", "Seed7", "Simula", "Simulink", "Smalltalk",
        "Smarty", "Solidity", "SPARK", "SPSS", "SQL", "SQR", "Squirrel", "Standard ML", "Stata",
        "Swift", "SystemVerilog", "Tcl", "Transact-SQL", "TypeScript", "Uniface", "Vala/Genie",
        "VBScript", "VHDL", "Visual Basic", "WebAssembly", "Wolfram", "X++", "X10", "XBase",
        "XBase++", "XC", "Xen", "Xojo", "XQuery", "XSLT", "Xtend", "Z shell", "Zig"
    }

    def __init__(self, json_path, config: ConfigParser):
        self.config = config
        self.json_path = json_path

    def get_project_dir(self, project):
        """Returns project directory"""
        project_path = f"{self.config['path']['project_path'] + '/' + project}"
        return project_path

    def collect_commit_details(self, project, project_repo):
        """Collects commit details: hash, author, date, lines changed, files changed"""
        commit_details_list = []
        # print(project_dir)
        for commit_hash in project[0]["commits"]:
            # print(commit_hash)
            # print(project_repo)
            commit = project_repo.commit(commit_hash)
            try:
                commit = project_repo.commit(commit_hash)
                commit_details = {
                    "commit_hash": commit_hash,
                    "author": commit.author.name,
                    "date": commit.committed_datetime.strftime("%Y-%m-%d %H:%M:%S")
                }
                commit_details_list.append(commit_details)

            except ValueError as value_error:
                print(f"Warning: Commit {commit_hash} could not be resolved. Skipping.")
                print(f"Value Error: {value_error}")
                return None
        return commit_details_list

    def filter_programming_languages(self, scc_file):
        """Removes non-programming languages using the TIOBE index"""
        # filtered_data = []

        with open(scc_file, 'r', encoding='utf-8') as file:
            scc_data = json.load(file)

            # Filter out non-programming languages
            for entry in scc_data:
                language = entry.get("Name")
                if language not in self.tiobe_index:
                    scc_data.remove(entry)

        # filtered_scc_file = f"filtered_{scc_file}"
        # Save the filtered data to a new JSON file
        with open(scc_file, 'w', encoding='utf-8') as filtered_scc_file:
            json.dump(scc_data, filtered_scc_file, indent=4)

        # print(f"Filtered data saved to {scc_file}")

    def get_loc(self, project, output_directory, commit, is_refactoring):
        """Switches current repository to specified commit"""
        subprocess.run(["git", "checkout", f"{commit}"], check=False)
        scc_directory = f"{output_directory}{self.config['output']['path'][1:]}/{project}/scc"
        if not os.path.exists(scc_directory):
            os.mkdir(scc_directory)

        if is_refactoring:
            scc_file = f"{scc_directory}/refactoring_{commit}.json"
        else:
            scc_file = f"{scc_directory}/commit_{commit}.json"
        subprocess.run(["scc", "-f", "json", "-o", scc_file], check=False)

        # print(scc_file)

        self.filter_programming_languages(scc_file)

        loc_counter = 0
        with open(scc_file, 'r', encoding='utf-8') as file:
            scc_data = json.load(file)
            for language in scc_data:
                loc = language['Code']
                loc_counter += loc

        # print(loc_counter)
        return loc_counter

    def touched_lines_of_code(self, current_dir, project_dir, project_name, commit_details_list):
        """Gets the touched lines of code for each commit of a project"""

        output_directory = os.getcwd()
        dev_effort_csv = f"{self.config['output']['path']}/{project_name}/dev_effort.csv"

        # tloc_list = []
        for commit in commit_details_list:
            os.chdir(project_dir)
            commit_hash = commit['commit_hash']
            current_loc = self.get_loc(project_name, output_directory, commit_hash, 1)

            rev_parse_command = subprocess.check_output(["git", "rev-parse", f"{commit_hash}^1"])
            previous_commit = rev_parse_command.decode('utf-8').strip()
            previous_loc = self.get_loc(project_name, output_directory, previous_commit, 0)

            tloc = abs(current_loc - previous_loc)
            csv_row = [f"{commit_hash}", f"{previous_commit}", f"{tloc}"]
            os.chdir(current_dir)
            with open(dev_effort_csv, 'a', encoding='utf-8') as csv_file:
                writer_object = writer(csv_file)
                writer_object.writerow(csv_row)
                csv_file.close()
        os.chdir(current_dir)

    def effort_by_developer(self, project_name):
        """Organizes the scc output by developer"""
        output_dir = f"{self.config['output']['path']}/{project_name}"

        commit_details_file = f"{output_dir}/commit_details.json"
        dev_dir = f"{output_dir}"
        if not os.path.exists(dev_dir):
            os.makedirs(dev_dir)

        with open(commit_details_file, 'r', encoding='utf-8') as file:
            commit_data = json.load(file)

        # print(f"\033[91m{commit_data}\033[00m")

        csv_file = pd.read_csv(f"{self.config['output']['path']}/{project_name}/dev_effort.csv")

        # Process the data to get the output
        dev_list = {}
        for commit in commit_data:
            dev = commit['author']
            target_hash = commit['commit_hash']
            tloc_result = csv_file.loc[csv_file['refactoring_hash'] == target_hash, 'TLOC']

            if not tloc_result.empty:
                tloc_value = int(tloc_result.iloc[0])
                if dev in dev_list:
                    dev_list[dev] += tloc_value
                else:
                    dev_list[dev] = tloc_value
            else:
                print("No matching row found for refactoring hash: ", target_hash)

        # print(f"\033[91m{dev_list}\033[00m")

        # Write the output_data to a new JSON file
        dev_file = f"{dev_dir}/dev.json"
        with open(dev_file, 'w', encoding='utf-8') as file:
            json.dump(dev_list, file, indent=4)

        # print(f"\033[91mOutput has been written to {dev_file}\033[00m")

    def mine_projects(self, project_json):
        """Mines a project"""
        project_file = f"{self.config['commits_hash']['commits_path']}/{project_json}"
        with open(project_file, 'r', encoding='utf-8') as json_file:
            project = json.load(json_file)

        project_name = project[0]["project"]
        project_dir = self.get_project_dir(project_name)
        project_repo = git.Repo(project_dir)

        commit_details_list = self.collect_commit_details(project, project_repo)
        sorted_commit_details = sorted(commit_details_list, key=itemgetter('date'))

        output_dir = f"{self.config['output']['path']}/{project_name}"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        csv_file = f"{output_dir}/dev_effort.csv"
        with open(csv_file, 'w', encoding='utf-8') as csv_file:
            csvwriter = csv.writer(csv_file)
            fields = ['refactoring_hash', 'previous_hash', 'TLOC']
            csvwriter.writerow(fields)

        cd_file = f"{output_dir}/commit_details.json"
        with open(cd_file, 'w', encoding='utf-8') as cd_file:
            json.dump(sorted_commit_details, cd_file)

        pretty_print = 0
        if pretty_print:
            pprint(sorted_commit_details)
        # print(len(sorted_commit_details))

        cwd = os.getcwd()
        self.touched_lines_of_code(cwd, project_dir, project_name, sorted_commit_details)
        self.effort_by_developer(project_name)