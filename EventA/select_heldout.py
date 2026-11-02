"""Event A, Step 1: freeze a *metadata-only* held-out sample.

Run from the repository root:
    python EventA/select_heldout.py

Reads only columns necessary for eligibility and identity. Does NOT inspect
#refactorings, lcs_remaining_probs, BCP, or any analysis outcomes.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

M2_PROJECTS = {
    'sling-whiteboard',
    'incubator-tamaya-sandbox',
    'ofbiz-framework',
    'any23',
}
DUPLICATE_PROJECTS = {'hop', 'incubator-hop'}
FAMILIES = ('Move', 'Rename')
N_PER_FAMILY = 12


def main():
    # This script is placed at repository-root/EventA/select_heldout.py.
    repo = Path(__file__).resolve().parent.parent
    source = repo / 'Results' / 'cross_project_raw_results.csv'
    previous = repo / 'M2' / 'inputs' / 'sample_cases.csv'
    out = repo / 'EventA' / 'inputs'
    manifest_path = out / 'heldout_cases.csv'
    note_path = out / 'selection_record.md'
    if not source.is_file():
        raise SystemExit(f'Missing original dataset: {source}')
    if not previous.is_file():
        raise SystemExit(f'Missing frozen M2 case list: {previous}')
    if manifest_path.exists() or note_path.exists():
        raise SystemExit('Event A selection already saved. Refusing to overwrite frozen selection files.')

    # IMPORTANT: no duration / similarity / result columns are loaded.
    wanted = ['project_id', 'refactoring_type', 'class_id', 'time_stamp', 'hash']
    df = pd.read_csv(source, usecols=wanted, dtype={'class_id': 'string'})
    df['family'] = df['refactoring_type'].astype('string').str.split().str[0]
    df = df[df['family'].isin(FAMILIES)].copy()

    case_metadata = (df.groupby('class_id', as_index=False)
        .agg(project=('project_id', 'first'), family=('family', 'first'),
             first_date=('time_stamp', 'min')))
    case_metadata['case_no'] = case_metadata['class_id'].str.split('_').str[0].astype(int)
    counts = (case_metadata.groupby(['project', 'family']).size()
              .unstack(fill_value=0))
    for family in FAMILIES:
        if family not in counts.columns:
            counts[family] = 0
    eligible = sorted(
        name for name, row in counts.iterrows()
        if row['Move'] >= N_PER_FAMILY
        and row['Rename'] >= N_PER_FAMILY
        and name not in M2_PROJECTS
        and name not in DUPLICATE_PROJECTS
    )
    if not eligible:
        raise SystemExit('No eligible unused projects. Do not loosen the rules after inspecting outcomes.')
    project = eligible[0]
    sample_parts = []
    for family in FAMILIES:
        part = (case_metadata[(case_metadata['project'] == project)
                              & (case_metadata['family'] == family)]
                .sort_values(['case_no', 'class_id', 'first_date'])
                .head(N_PER_FAMILY).copy())
        if len(part) != N_PER_FAMILY:
            raise AssertionError(f'Unexpected sample count for {family}: {len(part)}')
        part.insert(0, 'sample_number', range(1, N_PER_FAMILY + 1))
        sample_parts.append(part)
    selected = pd.concat(sample_parts, ignore_index=True)
    old = set(pd.read_csv(previous, usecols=['class_id'])['class_id'].astype(str))
    overlap = old.intersection(set(selected['class_id'].astype(str)))
    if overlap:
        raise SystemExit(f'Overlap with M2 cases: {sorted(overlap)}')
    source_rows = df[df['class_id'].isin(selected['class_id'])].copy()
    # Source data's timestamps and hashes define the historical observation window.
    end_date = str(source_rows['time_stamp'].max())
    start_date = str(source_rows['time_stamp'].min())
    selected['source_version'] = 'Zenodo 15209118 v1.0'
    selected['window_start_dataset'] = start_date
    selected['window_end_dataset'] = end_date

    # Hash the exact published results CSV, not a mutable latest URL.
    sha = hashlib.sha256()
    with source.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            sha.update(chunk)
    digest = sha.hexdigest()
    selected['source_csv_sha256'] = digest
    selected = selected[['project','family','sample_number','class_id','first_date',
                         'source_version','window_start_dataset',
                         'window_end_dataset','source_csv_sha256']]

    out.mkdir(parents=True, exist_ok=True)
    selected.to_csv(manifest_path, index=False)
    # Keep a row-level commit manifest for later audit; NO result columns.
    commit_path = out / 'heldout_commit_references.csv'
    source_rows[['class_id', 'time_stamp', 'hash']].to_csv(commit_path, index=False)
    note = f'''# Event A — held-out selection (BEFORE ANALYSIS)

- Source: Zenodo record 15209118, v1.0, `Results/cross_project_raw_results.csv`.
- Source file SHA-256: `{digest}`.
- Held-out project: `{project}` (not used in M2).
- Rule: first alphabetically named project with >=12 **distinct** Move cases and >=12 **distinct** Rename cases; exclude four M2 projects and duplicate hop/incubator-hop.
- Case rule: first 12 per family sorted by leading integer of `class_id`, then full `class_id`, then earliest `time_stamp`. Same M1 selection procedure.
- Dataset observation window (timestamps of the selected cases): {start_date} to {end_date}.
- Exact selected cases: `EventA/inputs/heldout_cases.csv` (24 rows, 12 per family).
- Historical commit hashes: `EventA/inputs/heldout_commit_references.csv`.
- Counts: Move = {int(counts.loc[project, 'Move'])}, Rename = {int(counts.loc[project, 'Rename'])} distinct available cases before sampling.
- Confirmed M2 case overlap: none.
- Results: NOT INSPECTED. No `#refactorings` or `lcs_remaining_probs` read.
- **Event A prediction: NOT YET RECORDED.** Freeze it in the tracker and repository before running the event checks.
'''
    note_path.write_text(note, encoding='utf-8')
    print(f'SELECTED HELD-OUT PROJECT: {project}')
    print(f'Eligible unused projects (by counts only): {len(eligible)}')
    print(f'Observation window: {start_date} through {end_date}')
    print('No overlap with M2 cases.')
    print(f'Manifest: {manifest_path.relative_to(repo)}')
    print(f'Commit refs: {commit_path.relative_to(repo)}')
    print(f'Selection note: {note_path.relative_to(repo)}')
    print('NEXT: record your Event A prediction and freeze it BEFORE running analysis.')


if __name__ == '__main__':
    main()
