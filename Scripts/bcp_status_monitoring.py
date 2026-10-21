import os
import time
import pickle
import pandas as pd
from datetime import datetime

from codes.components.utility import DATA_PATH
# Path to the directory containing the pkl files
BCP_STATUS_PATH = str(DATA_PATH / 'bcp_status_monitoring')
PRONENESS_DATA_PATH = str(DATA_PATH / 'change_proneness_data')
os.makedirs(BCP_STATUS_PATH, exist_ok=True)
OUTPUT_CSV_PATH = os.path.join(BCP_STATUS_PATH, "refactoring_progress.csv")
OUTPUT_TXT_PATH = os.path.join(BCP_STATUS_PATH, "refactoring_summary.txt")

# Interval to update the reports (15 minutes)
UPDATE_INTERVAL = 15 * 60  # 15 minutes in seconds

def get_refactoring_progress():
    """Scans the repository directories and retrieves processed and remaining refactorings."""
    projects = os.listdir(PRONENESS_DATA_PATH)
    progress_data = []

    total_processed = 0
    total_remaining = 0

    for project in projects:
        project_path = os.path.join(PRONENESS_DATA_PATH, project)
        pickle_path = os.path.join(project_path, "bcp_results.pkl")
        csv_path = os.path.join(project_path, "bcp_proneness_results.csv")

        # Skip if the necessary files do not exist
        if not os.path.exists(pickle_path) or not os.path.exists(csv_path):
            continue

        # Load processed refactorings
        try:
            with open(pickle_path, "rb") as f:
                bcp_results_dict = pickle.load(f)
            processed_count = len(bcp_results_dict["refactoring_id"])
        except Exception as e:
            print(f"Error loading {pickle_path}: {e}")
            continue

        # Load total refactorings from CSV
        try:
            proneness_df = pd.read_csv(csv_path)
            total_refactorings = len(proneness_df["refactoring_id"].unique())
        except Exception as e:
            print(f"Error reading {csv_path}: {e}")
            continue

        # Calculate remaining refactorings
        remaining_count = total_refactorings - processed_count
        progress_data.append([project, processed_count, remaining_count, total_refactorings])

        # Update global counters
        total_processed += processed_count
        total_remaining += remaining_count

    return progress_data, total_processed, total_remaining


def update_reports():
    """Updates the CSV and TXT files with progress information every 15 minutes."""
    while True:
        # Get current progress data
        progress_data, total_processed, total_remaining = get_refactoring_progress()

        # Convert to DataFrame and save as CSV
        df = pd.DataFrame(progress_data, columns=["Project", "Processed", "Remaining", "Total"])
        df.to_csv(OUTPUT_CSV_PATH, index=False)

        # Compute the percentage of remaining refactorings
        if total_processed + total_remaining > 0:
            remaining_percentage = (total_remaining / (total_processed + total_remaining)) * 100
        else:
            remaining_percentage = 0.0

        # Write summary to TXT file
        with open(OUTPUT_TXT_PATH, "a") as txt_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            txt_file.write(f"{timestamp} - Total Processed: {total_processed}, Total Remaining: {total_remaining}, Remaining: {remaining_percentage:.2f}%\n")

        print(f"Updated reports at {datetime.now()}")

        # Sleep for the defined interval (15 minutes)
        time.sleep(UPDATE_INTERVAL)


if __name__ == "__main__":
    update_reports()