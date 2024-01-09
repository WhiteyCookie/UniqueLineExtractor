#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  5 23:18:40 2024

@author: root
"""

import os
import argparse
import tempfile
import time
import re
import psutil
from tqdm import tqdm
import send2trash

# ANSI Color Codes
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"


def find_text_files(start_folder):
    """Find all text files in the given start folder and its subfolders."""
    text_files = {}
    for foldername, _, filenames in os.walk(start_folder):
        txt_files = [os.path.join(foldername, file)
                     for file in filenames if file.endswith('.txt')]
        if txt_files:
            text_files[foldername] = txt_files
    return text_files


def is_line_duplicate(line, unique_lines_file):
    unique_lines_file.seek(0)
    for existing_line in unique_lines_file:
        if line.strip() == existing_line.strip():
            return True
    return False


def is_valid_line(line):
    """Check if the line is in the desired format and not a Gmail address."""
    pattern = r'^[\w\.-]+@[\w\.-]+:\w+$'
    is_valid_format = bool(re.match(pattern, line.strip()))
    is_gmail = "@gmail.com" in line
    return is_valid_format and not is_gmail


def process_file(file_path, temp_dir, max_memory):
    unique_lines_set = set()
    unique_lines_file = tempfile.NamedTemporaryFile(
        mode='w+', dir=temp_dir, delete=False)
    lines_read = 0
    duplicates = 0
    gmail_accounts_removed = 0
    batch_size = 2000  # You can adjust this based on performance testing
    batch = []
    process = psutil.Process(os.getpid())

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            file_size = os.path.getsize(file_path)
            with tqdm(total=file_size, unit='B', unit_scale=True, desc=os.path.basename(file_path)) as pbar:
                for line in file:
                    lines_read += 1
                    pbar.update(len(line.encode('utf-8')))

                    if process.memory_info().rss > max_memory:
                        print(
                            RED + "Approaching memory limit. Flushing to disk." + RESET)
                        batch_to_disk(batch, unique_lines_file)
                        batch.clear()
                        unique_lines_set.clear()

                    if line not in unique_lines_set and is_valid_line(line):
                        unique_lines_set.add(line)
                        batch.append(line)
                        if len(batch) >= batch_size:
                            batch_to_disk(batch, unique_lines_file)
                            batch.clear()
                    elif "@gmail.com" in line:
                        gmail_accounts_removed += 1

        if batch:  # Write any remaining lines in the batch
            batch_to_disk(batch, unique_lines_file)

    except Exception as error:
        print(RED + f"Error processing {file_path}: {error}" + RESET)
        unique_lines_file.close()
        return None, lines_read, duplicates

    unique_lines_file.close()
    return unique_lines_file.name, lines_read, duplicates, gmail_accounts_removed


def batch_to_disk(batch, unique_lines_file):
    for line in batch:
        unique_lines_file.write(line)


def merge_temp_files(temp_files, output_file):
    unique_lines = set()
    for temp_file in temp_files:
        with open(temp_file, 'r', encoding='utf-8') as file:
            for line in file:
                unique_lines.add(line.strip())

    with open(output_file, 'w', encoding='utf-8') as file:
        for line in sorted(unique_lines):
            file.write(f"{line}\n")

    return len(unique_lines)


def delete_temp_files_with_retry(file_paths, retries=3, delay=2):
    for file_path in file_paths:
        attempt = 0
        while attempt < retries:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                break
            except Exception as error:
                print(
                    RED + f"Error deleting {file_path}: {error}. Retrying..." + RESET)
                time.sleep(delay)
                attempt += 1


def main():
    start_time = time.time()  # Start the timer
    parser = argparse.ArgumentParser(
        description="This script recursively crawls through directories and subdirectories from a specified start point, finds .txt files, processes them to extract unique lines, and creates a summary output file in each directory containing .txt files without exceeding memory limits.")
    parser.add_argument("-s", "--start", required=False, default=os.path.dirname(os.path.realpath(__file__)),
                        help="Start folder for crawling text files. Defaults to the script's directory if not specified.")
    parser.add_argument("-o", "--output", required=False, default="merged_summary",
                        help="Base name for output files. Defaults to 'merged_summary' if not specified.")
    parser.add_argument("-m", "--max-memory", required=False, type=float, default=4.0,
                        help="Maximum memory usage in GB. Defaults to 3.5 GB if not specified.")

    args = parser.parse_args()
    text_files_by_folder = find_text_files(args.start)
    max_memory_bytes = args.max_memory * 1024 * 1024 * 1024

    total_files_processed = 0
    total_duplicates = 0
    total_gmail_accounts_removed = 0
    total_unique_lines_across_all_folders = 0
    total_files_moved_to_trash = []

    for folder, txt_files in text_files_by_folder.items():
        temp_files = []
        for file_path in txt_files:
            try:
                temp_file_path, lines_read, duplicates, gmail_accounts_removed = process_file(
                    file_path, folder, max_memory_bytes)
                if temp_file_path:
                    temp_files.append(temp_file_path)
                    total_files_processed += 1
                    total_duplicates += duplicates
                    total_gmail_accounts_removed += gmail_accounts_removed
                    print(
                        YELLOW + f"Processed {file_path}. Temporary file: {temp_file_path}" + RESET)
            except Exception as error:
                print(RED + f"Error processing {file_path}: {error}" + RESET)

        # Merge temp files for the current folder
        try:
            folder_name = os.path.basename(folder)
            output_file = os.path.join(folder, f"{folder_name}_summary.txt")
            folder_unique_lines = merge_temp_files(temp_files, output_file)
            total_unique_lines_across_all_folders += folder_unique_lines
            print(
                GREEN + f"Merged summary file created: {output_file}" + RESET)
        except Exception as error:
            print(RED + f"Error merging files in {folder}: {error}" + RESET)

        # Clean up temporary files with retry
        delete_temp_files_with_retry(temp_files)

        # Move processed files to trash
        for file_path in txt_files:
            if file_path != output_file:
                try:
                    send2trash.send2trash(file_path)
                    total_files_moved_to_trash.append(file_path)
                except Exception as error:
                    print(
                        RED + f"Error moving {file_path} to trash: {error}" + RESET)

    print(GREEN + "\n--- Statistics ---" + RESET)
    print(
        YELLOW + f"Total Directories Processed: {len(text_files_by_folder)}" + RESET)
    print(YELLOW + f"Total Files Processed: {total_files_processed}" + RESET)
    print(
        YELLOW + f"Total Unique Lines Across All Folders: {total_unique_lines_across_all_folders}" + RESET)
    print(YELLOW + f"Total Duplicates Found: {total_duplicates}" + RESET)
    print(
        YELLOW + f"Total Gmail Accounts Removed: {total_gmail_accounts_removed}" + RESET)
    print(
        YELLOW + f"Total Files Moved to Trash: {len(total_files_moved_to_trash)}" + RESET)
    # Uncomment the next line if you want to list the files moved to trash
    # for file in total_files_moved_to_trash: print(YELLOW + f"Moved to Trash: {file}" + RESET)


    end_time = time.time()  # End the timer
    elapsed_time = end_time - start_time  # Calculate elapsed time in seconds

    # Convert elapsed time to hours, minutes, and seconds
    hours = int(elapsed_time // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    seconds = int(elapsed_time % 60)

    # Format the time in HH:MM:SS
    formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    print(GREEN + f"\nTotal Execution Time: {formatted_time}" + RESET)

if __name__ == "__main__":
    main()
    