'''
This file contains utility functions that are used in the main script
'''
import json
import os
import logging
import pandas as pd
import requests
from pathlib import Path
import subprocess
import shutil
import sys
import stat
import pydriller as pydrill
import csv
from git import Repo
import time
import pickle

DATA_PATH = Path(r"C:\Users\Mikel\projects\2025\refactoring-ripple-effects\data")
SCC_PATH = r"C:\ProgramData\chocolatey\bin\scc.exe"

TIOBE_INDEX = {
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

class NoInternetConnectionError(Exception):
    """Custom exception for no internet connection."""
    pass

# function to open json file


def open_json_file(json_file):
    '''
    Open a json file and return the data
    '''
    with open(json_file, "r", encoding='utf-8') as f:
        data1 = json.load(f)
    return data1

# function to write json file


def write_json_file(json_file, data):
    '''
    Write data to a json file
    '''
    with open(json_file, "w", encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    return


def check_internet_connection():
    '''
    Check for an internet connection
    '''
    try:
        # Trying to access a website (e.g., Google) to check for an internet
        # connection
        response = requests.get('http://www.google.com', timeout=5)
        response.raise_for_status()  # This will raise an HTTPError for bad responses
        return True
    except requests.ConnectionError:
        return False
    except requests.Timeout:
        return False
    except requests.RequestException:
        return False


def get_study_repos():
    """
    Returns the clean list of project names analyzed in this study
    """

    list_repo_jsons = os.listdir(DATA_PATH / "back-up" / "output_data" / "refactoring_commits")
    clean_list = [json_path.removesuffix(".json") for json_path in list_repo_jsons]
    return clean_list


def is_directory_empty(dir_path):
    """
    Check if a directory is empty, ignoring hidden files and folders.
    """

    return not any(
        entry for entry in os.scandir(dir_path)
        if not entry.name.startswith('.')  # Ignore hidden files/folders
    )


def clone_repo(repo_name, repo_logger):
    """
    Clone repository into the specified path

    :param repo_name: Short name of the repository
    :return: The path of the repository clonned
    """
    clone_url = f"https://github.com/apache/{repo_name}.git"
    repos_path = DATA_PATH / "repos"
    os.makedirs(repos_path, exist_ok=True)
    repo_logger.info(f"Cloning {repo_name} repository...")
    try:
        repo_path = repos_path.joinpath(repo_name)
        if os.path.exists(repo_path) and is_directory_empty(repo_path) is False:
            repo_logger.info(f"The repository {repo_name} already exists in path {repo_path}, skipping.")
            return repo_path
        subprocess.run(["git", "config", "--global", "core.longpaths", "true"])
        subprocess.run(['git', 'clone', clone_url, repo_path], check=True)
        repo_logger.info(f"Repository {repo_name} successfully cloned!")
        return repo_path
    except subprocess.CalledProcessError as e:
        repo_logger.error(f"Error at clonning the repository: {e}")
        sys.exit(e.returncode)


def handle_remove_readonly(func, path, exc_info):
    """
    Callback function to handle read-only files during deletion.
    Changes the permission and retries deletion.
    """
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)  # Change to writeable
        func(path)
    else:
        raise exc_info[1]  # Re-raise the original exception


def on_rm_error(func, path, exc_info):
    #from: https://stackoverflow.com/questions/4829043/how-to-remove-read-only-attrib-directory-with-python-in-windows
    os.chmod(path, stat.S_IWRITE)
    os.unlink(path)

def remove_hidden_dirs(path):
    for i in os.listdir(path):
        if i.endswith('git'):
            tmp = os.path.join(path, i)
            # We want to unhide the .git folder before unlinking it.
            while True:
                subprocess.call(['attrib', '-H', tmp])
                break
            shutil.rmtree(tmp, onerror=on_rm_error)


def delete_repo(repo_path, repo_logger):
    """
    Deletes repository and path from the specified repository.

    :param repo_path: Path to the repository to be deleted
    :return: Nothing
    """

    if os.path.exists(repo_path):
        try:
            # Remove the repository, handling read-only files
            shutil.rmtree(repo_path, onerror=handle_remove_readonly)
            repo_logger.info(f"Successfully deleted repository at: {repo_path}")
        except Exception as e:
            print(f"Error deleting repository: {e}")
            print("Attempting manual deletion of files and directories...")
            repo_logger.error(f"Error deleting repository: {e}")
            repo_logger.warning(f"Attempting manual deletion of files and directories...")

            # Walk through the directory and attempt manual deletion
            for root, dirs, files in os.walk(repo_path, topdown=False):
                for name in files:
                    file_path = os.path.join(root, name)
                    try:
                        os.chmod(file_path, stat.S_IWUSR)  # Make the file writeable
                        os.remove(file_path)
                        print(f"Deleted file: {file_path}")
                    except Exception as e:
                        print(f"Failed to delete file {file_path}: {e}")

                for name in dirs:
                    dir_path = os.path.join(root, name)
                    try:
                        os.rmdir(dir_path)
                        print(f"Deleted directory: {dir_path}")
                    except Exception as e:
                        print(f"Failed to delete directory {dir_path}: {e}")

            # Check if the directory is now empty and attempt to remove it
            if not os.listdir(repo_path):
                try:
                    remove_hidden_dirs(repo_path)
                    os.rmdir(repo_path)
                    print(f"Successfully deleted empty repository directory at: {repo_path}")
                except Exception as e:
                    print(f"Failed to delete empty repository directory: {e}")
            else:
                print(f"Directory {repo_path} is not empty. Please check manually.")

    else:
        print(f"Repository path does not exist: {repo_path}")


def check_class_modification(repo_path, file_path, commit):
    """
    Checks if the path of the Java class changed or not within a specific commit

    :param repo_path:
    :param file_path:
    :return: True (If file has changed the path) / False (If file hasn't changed the path)
             & useable PATH
    """

    temp_file = file_path
    for c in pydrill.Repository(str(repo_path), only_commits=[commit]).traverse_commits():
        for f in c.modified_files:

            try:
                old_path = os.path.normpath(f.old_path)
            except TypeError:
                old_path = None
            try:
                new_path = os.path.normpath(f.new_path)
            except TypeError:
                new_path = None

            # LOGIC: If either old or new path match the path of interest we start
            if old_path == temp_file or new_path == temp_file:
                # If both paths aren't equal and the new path isn't None, means the class path has changed
                if old_path != new_path and new_path != None:
                    temp_file = new_path
                    #print(f"> MOD TYPE: File {old_path} changed to: {new_path} in commit {commit}")
                    return temp_file, commit
                # If both paths are equal means that the class didn't change
                elif old_path == new_path:
                    #print(f"> MOD TYPE: File {old_path} didn't change in commit {commit}")
                    return new_path, commit
                # If the new_path is None means that the class was deleted from the project.
                if new_path == None:
                    #print(f"> MOD TYPE: File {old_path} was deleted from the project in commit {commit}")
                    return None, commit

    # In case no modifications were done
    return None, None


def checkout_git_repo(project_path, git_hash):

    repo = Repo(project_path)
    try:
        repo.git.checkout(git_hash, force=True)
        #print(f"Checkout repo {os.path.basename(project_path)} at {git_hash}")
    except Exception as e:
        print(f"Failed to checkout {git_hash}: {e}")


def get_eloc(file_path, repo_path, c_hash, last_hash):
    """
    Gets the effective lines of code (ELOC) from the specified file path at the stage of the current commit

    :param file_path:
    :param repo_path:
    :param c_hash:
    :return: ELOC
    """

    java_class_path = os.path.normpath(os.path.join(repo_path, file_path))
    checkout_git_repo(project_path=repo_path, git_hash=c_hash)
    project_name = os.path.basename(repo_path)
    try:
        path_prefix = DATA_PATH / "change_proneness_data" / project_name
        temp_json_path = os.path.normpath(os.path.join(str(path_prefix), "temp.json"))
        subprocess.run([SCC_PATH, "-f", "json", java_class_path, "-o", temp_json_path], shell=True, check=True)
        output_list = open_json_file(temp_json_path)
        eloc = output_list[0]["Code"]
        os.remove(temp_json_path)

    except Exception as e:
        print(f"Error getting effective lines of code: {e}")
        checkout_git_repo(project_path=repo_path, git_hash=last_hash)
        sys.exit(1)
    checkout_git_repo(project_path=repo_path, git_hash=last_hash)

    return eloc


def write_csv_from_dict(dictionary, path):
    """
    Writes in an scalable format all dictionaries
    :param dictionary:
    :param path:
    """

    data_df = pd.DataFrame.from_dict(dictionary)
    data_df.to_csv(path, index=False)


def read_csv_to_df(path):
    """
    Reads csv into a pandas dataframe
    :param path:
    :return: df
    """

    return pd.read_csv(path)


def read_csv_to_dict(save_path):
    """
    Loads an existing CSV file into a dictionary matching the changes_data format.
    If the file does not exist, returns an empty dictionary.

    :param save_path: Path to the CSV file.
    :return: Dictionary with existing data or an empty initialized dictionary.
    """
    df = pd.read_csv(save_path)

    # Convert the DataFrame into a dictionary with lists
    existing_data = df.to_dict(orient="list")
    #print(f"Loaded existing data from {save_path}")
    return existing_data


def write_dict_to_pickle(dictionary, path):
    # save dictionary to person_data.pkl file
    with open(path, 'wb') as fp:
        pickle.dump(dictionary, fp)
        print('dictionary saved successfully to file')


def setup_logger(name, log_file, level=logging.INFO):
    """
    Create a logger with the given name and log file.

    :param name: Name of the logger.
    :param log_file: File path for storing logs.
    :param level: Logging level.
    :return: Configured logger instance.
    """
    formatter = logging.Formatter('%(asctime)s - %(processName)s - %(funcName)s - %(levelname)s - %(message)s')

    if os.path.exists(log_file):
        os.remove(log_file)

    handler = logging.FileHandler(log_file, mode='a')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


def read_pw():
    with open(str(DATA_PATH / "email_pw.txt"), "r", encoding="utf-8") as file:
        clean_line = next(file).strip()

    return clean_line


def convert_pickle_to_csv(pickle_file, csv_file):
    """Converts a pickle file storing a dictionary into a CSV."""
    try:
        with open(pickle_file, "rb") as f:
            data_dict = pickle.load(f)

        # Ensure it's a dictionary
        if not isinstance(data_dict, dict):
            print(f"Skipping {pickle_file}: Not a dictionary")
            return

        # Convert dictionary to DataFrame and save as CSV
        df = pd.DataFrame.from_dict(data_dict)
        df.to_csv(csv_file, index=False)

    except Exception as e:
        print(f"Error processing {pickle_file}: {e}")