import os
import pandas as pd
from components.utility import DATA_PATH


def merge_project_csvs(project_dir, output_file, project_name):

    # If the project didn't have BCP history we don't consider it
    if not os.path.exists(os.path.join(project_dir, "bcp_proneness_results.csv")):
        return None

    # Development effort data
    dev_effort_path = DATA_PATH / "dev_effort_data" / f"{project_name}.csv"
    dev_effort_df = pd.read_csv(dev_effort_path)
    tloc = dev_effort_df["tloc"]
    raw_tloc = dev_effort_df["raw_tloc"]

    # BCP + proneness data
    bcp_proneness_df = pd.read_csv(os.path.join(project_dir, "bcp_proneness_results.csv"))
    dev_effort_df = dev_effort_df[["tloc", "raw_tloc"]]  # Only keep required columns
    bcp_proneness_df = pd.concat([bcp_proneness_df, dev_effort_df.reset_index(drop=True)], axis=1)

    # Save merged file
    bcp_proneness_df.to_csv(output_file, index=False)
    return output_file

def create_cross_project_csv(projects_dir, output_file):
    """
    Stacks all merged project CSVs (row-wise) into a final cross-project CSV.
    """
    merged_files = []
    project_dirs = sorted(os.listdir(projects_dir))  # List of project folders
    results_per_project_path = DATA_PATH / "merged_results"
    os.makedirs(results_per_project_path, exist_ok=True)

    for project in project_dirs:
        project_path = os.path.join(projects_dir, project)
        dev_effort_path = DATA_PATH / "dev_effort_data" / f"{project}.csv"
        if os.path.isdir(project_path) and os.path.exists(dev_effort_path):  # Ensure it's a directory
            merged_file = os.path.join(results_per_project_path, f"{project}_merged.csv")
            merged_csv = merge_project_csvs(project_path, merged_file, project)
            if merged_csv:
                merged_files.append(merged_csv)

    with open(output_file, "w", encoding="utf-8", newline="") as f_out:
        first_file = True
        for merged_csv in merged_files:
            chunk_iter = pd.read_csv(merged_csv, chunksize=10000)  # Process in 10k-row chunks
            for chunk in chunk_iter:
                chunk.to_csv(f_out, mode="a", index=False, header=first_file, lineterminator="\n")
                first_file = False  # Write header only once
    print(f"✅ Cross-project CSV saved at {output_file}")

# Run the process
bcp_proneness_path = DATA_PATH / "change_proneness_data"
cross_project_csv_path = DATA_PATH / "cross_project_raw_results.csv"

if os.path.exists(cross_project_csv_path):
    os.remove(cross_project_csv_path)
create_cross_project_csv(str(bcp_proneness_path), str(cross_project_csv_path))