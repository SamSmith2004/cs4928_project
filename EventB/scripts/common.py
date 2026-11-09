"""
Shared helpers for the Event B audit. Run the scripts from the repository root.

M2 and Event A files are only read. Every Event B output goes under EventB/.
Project histories are expected in M2/repos (git-ignored); see EventB/inputs/repos.csv.
"""
import importlib.util
import subprocess
import sys
from pathlib import Path

import pandas as pd

REPOS = Path("M2/repos")
DERIVED = Path("EventB/derived")
DERIVED.mkdir(parents=True, exist_ok=True)
LOGS = Path("EventB/raw/authors_logs")
LOGS.mkdir(parents=True, exist_ok=True)
SAMPLES = {"M2": Path("M2"), "EventA": Path("EventA")}
SHORT = 10
MOST = 7
CUTOFFS = [0.01, 0.05, 0.10]


def load_authors():
    """Import the authors' unedited calculation, with the same log-folder repair as check2.py."""
    sys.path.insert(0, "Scripts")
    import components.utility as utility
    utility.DATA_PATH = LOGS.resolve()
    spec = importlib.util.spec_from_file_location("get_bcp", "Scripts/02_get_bcp.py")
    bcp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bcp)
    return bcp


def project_of(class_id):
    return class_id.rsplit("-", 2)[0].split("_", 3)[3]


def refactoring_index(class_id):
    return int(class_id.split("_")[0])


def zenodo(sample, project):
    return SAMPLES[sample] / "inputs/zenodo/Data/change_proneness_data" / project


def load_values():
    """Frozen Check 2 values from M2 and Event A, with the sample each row came from."""
    frames = [pd.read_csv(path / "raw/check2_values.csv").assign(sample=name) for name, path in SAMPLES.items()]
    return pd.concat(frames, ignore_index=True)


def load_rows():
    """Frozen source rows from M2 and Event A, with each case's rq and family."""
    frames = []
    for name, path in SAMPLES.items():
        cases = pd.read_csv(path / "inputs/sample_cases.csv")[["rq", "family", "class_id"]]
        rows = pd.read_csv(path / "raw/sample_rows.csv")
        frames.append(rows.merge(cases, on="class_id").assign(sample=name))
    return pd.concat(frames, ignore_index=True)


def first_commit(sample, project, idx):
    ordered = pd.read_csv(zenodo(sample, project) / "ordered_refactorings.csv")
    first = ordered[ordered["id"] == idx].iloc[0]
    return first["hash"], first["filepath"].replace("\\", "/")


def recorded_paths(sample, project, idx):
    """The path the authors recorded at each commit, read as check2.py reads it."""
    base = zenodo(sample, project)
    proneness = pd.read_csv(base / "proneness_results.csv")
    rows = proneness[proneness["refactoring_id"].str.startswith(f"{idx}_")]
    history = pd.read_csv(base / "class_change_history" / rows["refactoring_id"].tolist()[-1])
    return dict(zip(history["hash"], history["full-path"].str.replace("\\", "/")))


def lines_at(project, commit, path):
    """File content at a commit, read directly from git. This also works for a pure rename."""
    result = subprocess.run(["git", "-C", str(REPOS / project), "show", f"{commit}:{path}"],
                            capture_output=True)
    if result.returncode != 0:
        return None
    return result.stdout.decode("utf-8", "ignore").splitlines()
