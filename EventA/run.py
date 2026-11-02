#!/usr/bin/env python3
"""Event A runner for the frozen CS4928 M2 code, without changing M2 files.

Copy this file to repo-root/EventA/run_step3.py. Run from repo root:
    python EventA/run_step3.py prepare
    python EventA/run_step3.py check1
    python EventA/run_step3.py sensitivity
    python EventA/run_step3.py fetch
    python EventA/run_step3.py clone
    python EventA/run_step3.py check2

The copies of M2/check1, M2/check2, M2/fetch_inputs get ONE fixed substitution:
'M2/' -> 'EventA/' in file paths; algorithm/threshold source is otherwise identical.
"""
import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
EA = ROOT / 'EventA'
M2 = ROOT / 'M2'
PROJECTS_M2 = {'sling-whiteboard', 'incubator-tamaya-sandbox', 'ofbiz-framework', 'any23'}
SCRIPT_NAMES = {'check1': 'check1.py', 'check2': 'check2.py', 'fetch': 'fetch_inputs.py'}


def ensure(condition, problem):
    if not condition:
        raise SystemExit('STOP: ' + problem)


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def selection():
    manifest = EA / 'inputs' / 'heldout_cases.csv'
    old = M2 / 'inputs' / 'sample_cases.csv'
    ensure(manifest.is_file(), f'Missing frozen sample: {manifest}')
    ensure(old.is_file(), f'Missing M2 sample: {old}')
    df = pd.read_csv(manifest, dtype={'class_id': str})
    ensure(all(x in df.columns for x in ['project', 'family', 'class_id']), 'Invalid Event A sample columns')
    ensure(len(df) == 24 and df.class_id.nunique() == 24, 'Expected exactly 24 unique cases')
    ensure(set(df['family']) == {'Move', 'Rename'}, 'Must have Move and Rename')
    ensure((df.groupby('family').size() == 12).all(), 'Must have 12 cases per family')
    ensure(df.project.nunique() == 1, 'Must select exactly one new project')
    project = df['project'].iloc[0]
    ensure(project not in PROJECTS_M2, 'The held-out project was already used in M2')
    old_ids = set(pd.read_csv(old, usecols=['class_id'], dtype={'class_id': str}).class_id)
    ensure(not (set(df.class_id) & old_ids), 'Overlapping M2 case IDs')
    source = ROOT / 'Results' / 'cross_project_raw_results.csv'
    ensure(source.is_file(), 'Missing Results/cross_project_raw_results.csv')
    if 'source_csv_sha256' in df.columns:
        expected = set(df.source_csv_sha256.dropna().astype(str))
        ensure(len(expected) == 1 and sha256(source) in expected, 'Published source CSV has changed since Step 1')
    return df, project


def check_freeze():
    for file in ['EventA/prediction.md', 'EventA/inputs/heldout_cases.csv',
                 'EventA/inputs/selection_record.md']:
        ensure((ROOT / file).is_file(), f'Missing frozen prerequisite {file}')
        git_file = subprocess.run(['git', 'cat-file', '-e', f'HEAD:{file}'],
                                  cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        ensure(git_file.returncode == 0, f'{file} is not committed in HEAD; commit your prediction first')
        changed = subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--', file], cwd=ROOT)
        ensure(changed.returncode == 0, f'{file} has uncommitted changes. Preserve freeze first')


def write_once(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        ensure(path.read_bytes() == content, f'{path} exists with different contents; refusing to overwrite')
    else:
        path.write_bytes(content)


def prepare():
    check_freeze()
    df, project = selection()
    new_sample = df[['family', 'class_id']].copy()
    new_sample.insert(0, 'rq', 'EA')
    new_sample.insert(3, 'plan_row', range(1, len(new_sample) + 1))
    write_once(EA / 'inputs' / 'sample_cases.csv', new_sample.to_csv(index=False).encode('utf-8'))
    for name in SCRIPT_NAMES.values():
        src = M2 / 'scripts' / name
        ensure(src.is_file(), f'Missing M2 method: {src}')
        original = src.read_text(encoding='utf-8')
        ensure('M2/' in original, f'Cannot find expected M2 paths in {src}')
        adapted = original.replace('M2/', 'EventA/')
        write_once(EA / 'scripts' / name, adapted.encode('utf-8'))
    (EA / 'raw').mkdir(exist_ok=True)
    (EA / 'derived').mkdir(exist_ok=True)
    (EA / 'repos').mkdir(exist_ok=True)
    (EA / 'inputs' / 'zenodo').mkdir(parents=True, exist_ok=True)
    print('Preparation complete. Held-out project:', project)
    print('24 cases / 12 per family; method copies only change output/input folder M2/ -> EventA/.')
    print('Source scripts:', ', '.join(SCRIPT_NAMES.values()))


def run_script(key, log_name):
    check_freeze()
    selection()
    script = EA / 'scripts' / SCRIPT_NAMES[key]
    ensure(script.is_file(), 'Run prepare first')
    log = EA / 'raw' / log_name
    if key == 'fetch':  # allow retry after rate limits; preserve every attempt's log
        attempt = 2
        while log.exists():
            log = EA / 'raw' / f'fetch_run_{attempt}.log'
            attempt += 1
    else:
        ensure(not log.exists(), f'First result/log already exists at {log}. Do not overwrite; preserve frozen first attempt.')
    print(f'Executing: {sys.executable} {script.relative_to(ROOT)}', flush=True)
    with log.open('w', encoding='utf-8') as out:
        run = subprocess.run([sys.executable, str(script.relative_to(ROOT))], cwd=ROOT,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             text=True, encoding='utf-8', errors='replace')
        out.write(run.stdout)
    print(run.stdout)
    print('Full execution log saved to', log.relative_to(ROOT))
    if run.returncode:
        raise SystemExit(f'{key} exited with error {run.returncode}. Preserve the log for audit.')


def clone():
    check_freeze()
    _, project = selection()
    dest = EA / 'repos' / project
    if dest.is_dir() and (dest / '.git').exists():
        print('Existing Git repository:', dest.relative_to(ROOT))
        return
    ensure(not dest.exists(), f'{dest} exists but is not a Git clone')
    url = f'https://github.com/apache/{project}.git'
    print('Cloning full Git history from', url, flush=True)
    subprocess.run(['git', 'clone', url, str(dest)], cwd=ROOT, check=True)
    print('Clone completed:', dest.relative_to(ROOT))


def sensitivity():
    """M2/pack_tasks.py algorithm, same < comparisons and 'first below' inclusive rule.
    Only differs in one-panel plotting omitted; outputs a CSV table instead.
    """
    check_freeze()
    cases_path = EA / 'derived' / 'check1_cases.csv'
    rows_path = EA / 'raw' / 'sample_rows.csv'
    ensure(cases_path.exists() and rows_path.exists(), 'Run check1 first')
    target = EA / 'derived' / 'sensitivity.csv'
    ensure(not target.exists(), 'Sensitivity output already exists; refusing to overwrite frozen first result')
    rows = pd.read_csv(rows_path)
    cases = pd.read_csv(cases_path)
    def duration_with_cutoff(case_rows, cutoff):
        case_rows = case_rows.sort_values('#refactorings')
        below = case_rows[case_rows['lcs_remaining_probs'] < cutoff]
        return below['#refactorings'].iloc[0] if len(below) else case_rows['#refactorings'].max()
    results = []
    for cutoff in [None, 0.01, 0.05, 0.10]:
        for (rq, family), group in cases.groupby(['rq', 'family']):
            if cutoff is None:
                durations = group['re_duration']
            else:
                durations = [duration_with_cutoff(rows[rows['class_id'] == cid], cutoff)
                             for cid in group['class_id']]
            durations = pd.Series(durations)
            results.append({'cutoff': 'none (as published)' if cutoff is None else f'{cutoff:.0%}',
                            'rq': rq, 'family': family,
                            'n_short': int((durations < 10).sum()),
                            'median_duration': durations.median()})
    sensitivity_df = pd.DataFrame(results)
    sensitivity_df.to_csv(target, index=False)
    print(sensitivity_df.to_string(index=False))
    print('Saved:', target.relative_to(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare','check1','sensitivity','fetch','clone','check2'])
    args = parser.parse_args()
    if args.action == 'prepare':
        prepare()
    elif args.action == 'sensitivity':
        sensitivity()
    elif args.action == 'clone':
        clone()
    else:
        ensure((EA / 'inputs' / 'sample_cases.csv').exists(), 'Run prepare first')
        if args.action == 'check2':
            _, project = selection()
            ensure((EA / 'repos' / project / '.git').is_dir(), 'Run clone first')
            ensure((EA / 'inputs' / 'zenodo' / 'Data' / 'change_proneness_data' / project).is_dir(), 'Run fetch first')
            ensure((EA / 'raw' / 'sample_rows.csv').is_file(), 'Run check1 first')
        run_script(args.action, f'{args.action}_run.log')

if __name__ == '__main__':
    main()
