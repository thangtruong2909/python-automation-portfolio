"""
Batch File Renamer
-------------------
Renames all files in a chosen folder using a pattern you define.
Supports adding: sequence numbers, current date, and a custom prefix/suffix.

HOW TO RUN:
1. Install Python (if not already installed): https://www.python.org/downloads/
2. Open a terminal / command prompt in this script's folder.
3. Run:  python batch_file_renamer.py
4. Follow the on-screen prompts.

This script does a DRY RUN first (shows you the new names WITHOUT
renaming anything) and asks for confirmation before actually renaming.
"""

import os
from datetime import datetime


def get_new_filename(original_name, index, prefix, suffix, use_date, date_str):
    """
    Build the new filename based on user-chosen pattern.
    original_name: the current file name including extension
    index: sequence number for this file (1, 2, 3, ...)
    prefix: text to add at the start (optional)
    suffix: text to add before the extension (optional)
    use_date: True/False whether to include today's date
    date_str: pre-formatted date string, e.g. "2026-07-24"
    """
    name, ext = os.path.splitext(original_name)

    parts = []
    if prefix:
        parts.append(prefix)
    if use_date:
        parts.append(date_str)
    parts.append(f"{index:03d}")  # 3-digit sequence number: 001, 002, 003...
    if suffix:
        parts.append(suffix)

    new_name = "_".join(parts) + ext
    return new_name


def main():
    print("=== Batch File Renamer ===\n")

    # 1. Ask for the target folder
    folder = input("Enter the full path of the folder containing files to rename: ").strip()
    if not os.path.isdir(folder):
        print("Error: that folder does not exist. Please check the path and try again.")
        return

    # 2. Get all files (skip subfolders)
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    files.sort()  # alphabetical order before numbering

    if not files:
        print("No files found in that folder.")
        return

    print(f"\nFound {len(files)} file(s) in the folder.")

    # 3. Ask user for pattern options
    prefix = input("Enter a prefix to add (or press Enter to skip): ").strip()
    suffix = input("Enter a suffix to add before file extension (or press Enter to skip): ").strip()
    use_date_input = input("Include today's date in the filename? (y/n): ").strip().lower()
    use_date = use_date_input == "y"
    date_str = datetime.now().strftime("%Y-%m-%d")

    # 4. Build the rename plan (dry run)
    rename_plan = []
    for i, filename in enumerate(files, start=1):
        new_name = get_new_filename(filename, i, prefix, suffix, use_date, date_str)
        rename_plan.append((filename, new_name))

    # 5. Show preview
    print("\n--- PREVIEW (nothing has been renamed yet) ---")
    for old_name, new_name in rename_plan:
        print(f"  {old_name}  -->  {new_name}")

    # 6. Confirm before applying
    confirm = input("\nApply these renames? (y/n): ").strip().lower()
    if confirm != "y":
        print("Cancelled. No files were renamed.")
        return

    # 7. Apply renames
    renamed_count = 0
    for old_name, new_name in rename_plan:
        old_path = os.path.join(folder, old_name)
        new_path = os.path.join(folder, new_name)

        # Avoid overwriting an existing file with the same new name
        if os.path.exists(new_path):
            print(f"  Skipped '{old_name}' -> '{new_name}' (a file with that name already exists)")
            continue

        os.rename(old_path, new_path)
        renamed_count += 1

    print(f"\nDone. {renamed_count} file(s) renamed successfully.")


if __name__ == "__main__":
    main()
