import pydriller

repo_path = "/../refactoring_recommender/data/repos/jmeter"
commit1 = "69cb24419be822f605e56f0960d60eea57eb44aa"
commit2 = "b7799e1602f257ab491c836bd57f416c87c5c04e"
file_path = "src/core/org/apache/jmeter/gui/util/TextAreaCellRenderer.java"
total_lines = 0
changed_lines = 0
for commit in pydriller.Repository(repo_path, from_commit=commit1, to_commit=commit2).traverse_commits():
    for file in commit.modified_files:

        if commit.hash == commit2:
            if file.old_path == file_path or file.new_path == file_path:
                print(f"File changes found in commit {commit.hash}")
                print("nloc: ", file.nloc)
                print("Changed lines: ", int(file.added_lines + file.deleted_lines))
                print("Unchanged lines: ", int(file.nloc) - int(file.added_lines + file.deleted_lines))
                # changed_lines += file.added_lines + file.deleted_lines