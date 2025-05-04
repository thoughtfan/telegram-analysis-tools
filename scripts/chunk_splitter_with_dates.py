#!/usr/bin/env python3
"""
Splits a large text file into chunks based on character count limits.
Designed for pipe-separated Telegram export data.
Outputs timestamp ranges for each chunk to help identify era boundaries.
"""

import sys
import os
import re
import time
from datetime import datetime

# Default settings
DEFAULT_INPUT = "2ndpass_filtered.txt"
DEFAULT_OUTPUT_PREFIX = "chunk_"
DEFAULT_MAX_CHARS = 50000  # Target character limit per chunk

def extract_unixtime(line):
    """Extract the unixtime from a pipe-separated telegram message line."""
    try:
        parts = line.split('|')
        if len(parts) >= 2:
            # Unixtime is the second field in pipe-separated format
            return int(parts[1])
    except (IndexError, ValueError):
        pass
    return None

def format_unixtime(unixtime):
    """Convert unixtime to a human-readable date string."""
    if unixtime is None:
        return "Unknown"
    try:
        dt = datetime.fromtimestamp(unixtime)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError, OverflowError):
        return "Invalid timestamp"

def split_file_by_char_count(input_file, output_prefix, max_chars):
    """
    Splits the input file into multiple chunks, each with approximately max_chars characters.
    Preserves whole lines (doesn't split in the middle of a line).
    Reports timestamp ranges for each chunk.
    """
    # Read the input file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return False

    # Check if the first line is a header
    header = None
    lines = content.split('\n')
    if lines and lines[0].startswith('# Format:'):
        header = lines[0]
        content = '\n'.join(lines[1:])  # Remove header from content

    # Split the content into lines (preserving empty lines)
    lines = content.split('\n')

    if not lines or (len(lines) == 1 and not lines[0]):
        print("Error: No content to split.")
        return False

    print(f"Read {len(lines)} lines from '{input_file}'")
    print(f"Total characters: {len(content)}")

    chunk_num = 1
    chunk_files = []
    chunk_timestamps = []
    current_chunk = []
    current_chars = 0

    # Process each line
    for line in lines:
        line_chars = len(line) + 1  # +1 for the newline character

        # Check if adding this line would exceed the limit
        if current_chars + line_chars > max_chars and current_chunk:
            # Extract timestamps from first and last message in the chunk
            first_msg = current_chunk[0]
            last_msg = current_chunk[-1]
            first_time = extract_unixtime(first_msg)
            last_time = extract_unixtime(last_msg)

            # Write the current chunk to a file
            chunk_file = f"{output_prefix}{chunk_num:03d}.txt"
            try:
                with open(chunk_file, 'w', encoding='utf-8') as f:
                    if header and chunk_num == 1:  # Only include header in first chunk
                        f.write(header + '\n')
                    f.write('\n'.join(current_chunk))
            except Exception as e:
                print(f"Error writing chunk {chunk_num}: {e}")
                return False

            # Store chunk info for reporting
            chunk_files.append(chunk_file)
            chunk_timestamps.append((first_time, last_time))

            print(f"Created {chunk_file} ({current_chars} characters, {len(current_chunk)} lines)")
            print(f"  - Time range: {format_unixtime(first_time)} to {format_unixtime(last_time)}")
            print(f"  - Unix range: {first_time} to {last_time}")

            # Reset for next chunk
            chunk_num += 1
            current_chunk = []
            current_chars = 0

        # Add the line to the current chunk
        current_chunk.append(line)
        current_chars += line_chars

    # Write the last chunk if there's anything left
    if current_chunk:
        # Extract timestamps from first and last message in the chunk
        first_msg = current_chunk[0]
        last_msg = current_chunk[-1]
        first_time = extract_unixtime(first_msg)
        last_time = extract_unixtime(last_msg)

        chunk_file = f"{output_prefix}{chunk_num:03d}.txt"
        try:
            with open(chunk_file, 'w', encoding='utf-8') as f:
                if header and chunk_num == 1:  # Only include header in first chunk
                    f.write(header + '\n')
                f.write('\n'.join(current_chunk))
        except Exception as e:
            print(f"Error writing last chunk: {e}")
            return False

        # Store chunk info for reporting
        chunk_files.append(chunk_file)
        chunk_timestamps.append((first_time, last_time))

        print(f"Created {chunk_file} ({current_chars} characters, {len(current_chunk)} lines)")
        print(f"  - Time range: {format_unixtime(first_time)} to {format_unixtime(last_time)}")
        print(f"  - Unix range: {first_time} to {last_time}")

    print(f"\nSuccessfully split into {len(chunk_files)} chunks:")
    print("\nSummary of chunks and their time ranges:")
    print("----------------------------------------")
    print("Chunk File            | Date Range                               | Unix Range")
    print("--------------------- | ---------------------------------------- | --------------------")

    for i, (chunk_file, (first_time, last_time)) in enumerate(zip(chunk_files, chunk_timestamps)):
        first_date = format_unixtime(first_time)
        last_date = format_unixtime(last_time)
        date_range = f"{first_date} to {last_date}"
        unix_range = f"{first_time} to {last_time}"
        print(f"{chunk_file:<21} | {date_range:<40} | {unix_range}")

    # Create a CSV summary file for easy reference
    summary_file = "chunk_summary.csv"
    try:
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("Chunk,Start Date,End Date,Start Unixtime,End Unixtime\n")
            for i, (chunk_file, (first_time, last_time)) in enumerate(zip(chunk_files, chunk_timestamps)):
                first_date = format_unixtime(first_time)
                last_date = format_unixtime(last_time)
                f.write(f"{chunk_file},{first_date},{last_date},{first_time},{last_time}\n")
        print(f"\nChunk summary saved to {summary_file}")
    except Exception as e:
        print(f"Error writing summary file: {e}")

    return True

def main():
    """Main function to parse arguments and run the splitter."""
    # Parse command line arguments
    input_file = DEFAULT_INPUT
    output_prefix = DEFAULT_OUTPUT_PREFIX
    max_chars = DEFAULT_MAX_CHARS

    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_prefix = sys.argv[2]
    if len(sys.argv) > 3:
        try:
            max_chars = int(sys.argv[3])
        except ValueError:
            print(f"Error: Maximum characters must be an integer. Using default: {DEFAULT_MAX_CHARS}")
            max_chars = DEFAULT_MAX_CHARS

    print(f"Splitting '{input_file}' into chunks of approximately {max_chars} characters each.")
    print(f"Will also report timestamp ranges for each chunk.")

    success = split_file_by_char_count(input_file, output_prefix, max_chars)

    if success:
        print("\nNext step: Review the chunk_summary.csv file to identify era boundaries.")
        print("Then you can proceed with the multi-era analysis strategy.")

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())