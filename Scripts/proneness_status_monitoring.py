import os
import csv
import json
from pathlib import Path
import pandas as pd
from tqdm import tqdm
import time
from datetime import datetime
from collections import deque
import pickle

DATA_PATH = Path(r"C:\Users\Mikel\projects\2025\refactoring-ripple-effects\data")
TOTAL_REPOS = 354

def inspect_project(change_proneness_res_path, project):

    processed_refactorings_txt = change_proneness_res_path / project / "processed_refactorings.txt"
    total_refactorings_csv = change_proneness_res_path / project / "ordered_refactorings.csv"
    collected_real_refactorings = change_proneness_res_path / project / "proneness_results.pkl"

    if os.path.exists(processed_refactorings_txt):
        # Get last line from the text file
        with open(str(processed_refactorings_txt), "r", encoding="utf-8") as f:
            lines = f.readlines()
            last_processed_refactoring = int(lines[-1].strip().split(",")[0])
    else:
        last_processed_refactoring = 0

    if os.path.exists(total_refactorings_csv):
        try:
            # Get last line from the csv file
            with open(total_refactorings_csv, 'r', encoding="utf-8") as file:
                reader = reversed(list(csv.reader(file)))
                last_row = next(reader)
                total_refactorings_num = int(last_row[0])
        except Exception as e:
            total_refactorings_num = 0
    else:
        total_refactorings_num = 0

    # Really collected ones:
    if os.path.exists(collected_real_refactorings):
        try:
            with open(collected_real_refactorings, "rb") as f:
                retreived_dict = pickle.load(f)
                ref_id_list = retreived_dict["refactoring_id"]
                ref_id_set = set(ref_id_list)
                total_really_collected_ref_cases = len(ref_id_set)
        except:
            total_really_collected_ref_cases = 0
    else:
        total_really_collected_ref_cases = 0

    return last_processed_refactoring, total_refactorings_num, total_really_collected_ref_cases


def get_totals(res_dict):

    res_dict["project"].append("TOTALS")
    sum_total_refactorings = sum(res_dict["total_refactorings"])
    sum_processed_refactoings = sum(res_dict["processed_refactorings"])
    sum_collected_refactorings = sum(res_dict["num_collected_cases"])
    res_dict["total_refactorings"].append(sum_total_refactorings)
    res_dict["processed_refactorings"].append(sum_processed_refactoings)
    res_dict["remaining_refactorings"].append(sum_total_refactorings - sum_processed_refactoings)
    res_dict["% processed"].append(round((sum_processed_refactoings / sum_total_refactorings) * 100, 2))
    res_dict["% remaining"].append(round(((sum_total_refactorings - sum_processed_refactoings) / sum_total_refactorings) * 100, 2))
    res_dict["num_collected_cases"].append(sum_collected_refactorings)
    res_dict["% collected"].append(round((sum_collected_refactorings / sum_total_refactorings) * 100, 2))
    res_dict["FULLY PROCESSED"].append(sum(res_dict["FULLY PROCESSED"]))
    res_dict["PROCESSED AND WITH COLLECTED DATA"].append(sum(res_dict["PROCESSED AND WITH COLLECTED DATA"]))
    res_dict["non_processed_but_with_history_data"].append(sum(res_dict["non_processed_but_with_history_data"]))
    res_dict["processed_but_without_collected_data"].append(sum(res_dict["processed_but_without_collected_data"]))
    return res_dict

def count_results(results_dict, change_proneness_res_path):

    empty_projects = 0
    if results_dict == {}:
        res_dict = {"project": [], "total_refactorings": [], "processed_refactorings": [], "remaining_refactorings": [],
                    "num_collected_cases": [], "% processed": [], "% remaining": [], "% collected": [], "FULLY PROCESSED": [],
                    "PROCESSED AND WITH COLLECTED DATA": [], "non_processed_but_with_history_data": [], "processed_but_without_collected_data": []}

        projects = os.listdir(str(change_proneness_res_path))
        for project in projects:

            last_processed_refactoring, total_refactorings_num, total_really_collected_ref_cases = inspect_project(change_proneness_res_path, project)
            if total_refactorings_num == 0:
                empty_projects += 1
                continue

            res_dict["project"].append(project)
            res_dict["total_refactorings"].append(total_refactorings_num)
            res_dict["processed_refactorings"].append(last_processed_refactoring)
            res_dict["remaining_refactorings"].append(total_refactorings_num - last_processed_refactoring)
            res_dict["num_collected_cases"].append(total_really_collected_ref_cases)

            try:
                res_dict["% processed"].append(round((last_processed_refactoring / total_refactorings_num) * 100, 2))

            except ZeroDivisionError:
                res_dict["% processed"].append(0)
            try:
                res_dict["% remaining"].append(round(((total_refactorings_num - last_processed_refactoring) / total_refactorings_num) * 100, 2))
            except ZeroDivisionError:
                res_dict["% remaining"].append(0)

            if last_processed_refactoring == total_refactorings_num:
                res_dict["FULLY PROCESSED"].append(1)
                res_dict["non_processed_but_with_history_data"].append(0)
                if total_really_collected_ref_cases != 0:
                    res_dict["PROCESSED AND WITH COLLECTED DATA"].append(1)
                    res_dict["processed_but_without_collected_data"].append(0)
                else:
                    res_dict["PROCESSED AND WITH COLLECTED DATA"].append(0)
                    res_dict["processed_but_without_collected_data"].append(1)
            else:
                res_dict["FULLY PROCESSED"].append(0)
                res_dict["PROCESSED AND WITH COLLECTED DATA"].append(0)
                res_dict["processed_but_without_collected_data"].append(0)
                if total_really_collected_ref_cases != 0:
                    res_dict["non_processed_but_with_history_data"].append(1)
                else:
                    res_dict["non_processed_but_with_history_data"].append(0)


            try:
                res_dict["% collected"].append(round((total_really_collected_ref_cases / total_refactorings_num) * 100, 2))
            except ZeroDivisionError:
                res_dict["% collected"].append(0)

        res_dict = get_totals(res_dict)
        return res_dict, empty_projects

    else:

        res_dict_2 = {"project": [], "total_refactorings": [], "processed_refactorings": [], "remaining_refactorings": [],
                      "num_collected_cases": [], "% processed": [], "% remaining": [], "% collected": [], "FULLY PROCESSED": [],
                      "PROCESSED AND WITH COLLECTED DATA": [], "non_processed_but_with_history_data": [], "processed_but_without_collected_data": []}
        for i in range(0, len(results_dict["project"])-1):

            if results_dict["FULLY PROCESSED"][i] == 1:
                res_dict_2["project"].append(results_dict["project"][i])
                res_dict_2["total_refactorings"].append(results_dict["total_refactorings"][i])
                res_dict_2["processed_refactorings"].append(results_dict["processed_refactorings"][i])
                res_dict_2["remaining_refactorings"].append(results_dict["remaining_refactorings"][i])
                res_dict_2["% processed"].append(results_dict["% processed"][i])
                res_dict_2["% remaining"].append(results_dict["% remaining"][i])
                res_dict_2["FULLY PROCESSED"].append(results_dict["FULLY PROCESSED"][i])
                res_dict_2["num_collected_cases"].append(results_dict["num_collected_cases"][i])
                res_dict_2["% collected"].append(results_dict["% collected"][i])
            else:
                last_processed_refactoring, total_refactorings_num, total_really_collected_ref_cases = inspect_project(change_proneness_res_path, results_dict["project"][i])
                res_dict_2["project"].append(results_dict["project"][i])
                res_dict_2["total_refactorings"].append(total_refactorings_num)
                res_dict_2["processed_refactorings"].append(last_processed_refactoring)
                res_dict_2["remaining_refactorings"].append(total_refactorings_num - last_processed_refactoring)
                try:
                    res_dict_2["% processed"].append(round((last_processed_refactoring / total_refactorings_num) * 100, 2))
                except ZeroDivisionError:
                    res_dict_2["% processed"].append(0)
                try:
                    res_dict_2["% remaining"].append(
                        round(((total_refactorings_num - last_processed_refactoring) / total_refactorings_num) * 100, 2))
                except ZeroDivisionError:
                    res_dict_2["% remaining"].append(0)
                if last_processed_refactoring == total_refactorings_num:
                    res_dict_2["FULLY PROCESSED"].append(1)
                    if total_really_collected_ref_cases != 0:
                        res_dict_2["PROCESSED AND WITH COLLECTED DATA"].append(1)
                        res_dict_2["processed_but_without_collected_data"].append(0)
                    else:
                        res_dict_2["PROCESSED AND WITH COLLECTED DATA"].append(0)
                        res_dict_2["processed_but_without_collected_data"].append(1)

                else:
                    res_dict_2["FULLY PROCESSED"].append(0)
                    res_dict_2["PROCESSED AND WITH COLLECTED DATA"].append(0)
                    if total_really_collected_ref_cases != 0:
                        res_dict_2["non_processed_but_with_history_data"].append(1)
                    else:
                        res_dict_2["non_processed_but_with_history_data"].append(0)

                res_dict_2["num_collected_cases"].append(total_really_collected_ref_cases)
                try:
                    res_dict_2["% collected"].append(round((total_really_collected_ref_cases / total_refactorings_num) * 100, 2))
                except ZeroDivisionError:
                    res_dict_2["% collected"].append(0)
                    res_dict_2["PROCESSED AND WITH COLLECTED DATA"].append(0)

        res_dict_2 = get_totals(res_dict_2)
        return res_dict_2, int(TOTAL_REPOS - len(results_dict["project"]))


def store_status(results_df, empty_projects_num):

    # First store the df in a csv
    projects_status_path = DATA_PATH / "projects_status" / "totals_csv"
    projects_status_path_txt = DATA_PATH / "projects_status" / "2_status_per_project_totals.txt"
    os.makedirs(str(projects_status_path), exist_ok=True)
    results_df.to_csv(str(projects_status_path / f"2_status_per_project_{datetime.now().date()}.csv"), index=False)

    # Then txt with the totals
    totals_rowlist = deque(results_df.tail(1).values.tolist()[0])
    totals_rowlist.appendleft(datetime.now())
    totals_rowlist.append(empty_projects_num)
    totals_rowlist = [str(item) for item in totals_rowlist]
    delimiter = ","
    log_string = delimiter.join(totals_rowlist)
    if not os.path.exists(str(projects_status_path_txt)):
        with open(str(projects_status_path_txt), 'w') as file:
            file.write('LOG TIMESTAMP,TOTAL REFACTORINGS,PROCESSED,REMAINING, WITH COLLECTED HISTORY,(%)PROCESSED,(%)REMAINING, (%) WITH COLLECTED HISTORY,#PROCESSEDREPOS, PROCESSED_AND_WITH_COLLECTED_DATA, NON_PROCESSSED_BUT_WITH_HISTORY_DATA, PROCESSED_BUT_WITHOUT_COLLECTED_DATA, EMPTY' + '\n')
            file.write(log_string + '\n')
    else:
        with open(str(projects_status_path_txt), 'a') as file:
            file.write(log_string + '\n')


def main():

    wait_time = 1 * 60 * 60
    results_dict = {}
    while 1==1:
        change_proneness_res_path = DATA_PATH / "change_proneness_data"
        results_dict, empty_projects_num = count_results(results_dict, change_proneness_res_path)
        dict_keys = results_dict.keys()
        print("EMPTY PROJCEST", empty_projects_num)
        for key in dict_keys:
            print("KEY", key, "LEN", len(results_dict[key]))


        results_df = pd.DataFrame.from_dict(results_dict)

        store_status(results_df, empty_projects_num)

        print(f"> {datetime.now()} Next status-per-project log for 1 hour")
        # Show a progress bar while sleeping
        for _ in tqdm(range(wait_time), desc="Next execution in", unit="s"):
            time.sleep(1)  # Sleep for 1 second at a time

if __name__ == "__main__":
    main()