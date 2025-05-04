# Usage Guide
## Script Options
### `telegram_simplifier_plus.py`
Converts JSON Telegram exports to simplified formats with several preprocessing options.
```bash
python scripts/telegram_simplifier_plus.py input.json output.txt [options]
```
**Parameters:**
-   `input.json`: The path to your exported Telegram JSON file.
-   `output.txt`: The path for the main text output file (consolidated messages).
**Options:**
-   `--markdown=FILE`: Create a human-readable markdown output file at the specified path.
-   `--no-consolidate`: Prevent the script from consolidating sequential messages from the same user.
-   `--no-bot-filter`: Prevent the script from filtering out messages likely sent by bots or machines.
-   `--window=SECONDS`: Set the time window (in seconds) for consolidating sequential messages (default: 180 seconds).
-   `--max-length=CHARS`: Set the maximum character length for messages to be considered for consolidation (default: 300 characters).
-   `--url-mode=MODE`: How to handle URLs in the output. `MODE` can be:
    -   `preserve`: Keep the original URL.
    -   `replace`: Replace the URL with a placeholder like `[URL]`.
    -   `domain` (default): Replace the URL with just the domain name (e.g., `[github.com]`).
### `telegram_filter_noise.py`
Filters out low-value messages ("noise") from the consolidated output based on criteria like length or message ID/date.
```bash
python scripts/telegram_filter_noise.py input.txt output.txt [options]
```
**Parameters:**
-   `input.txt`: The path to the input consolidated text file (e.g., from `telegram_simplifier_plus.py`).
-   `output.txt`: The path for the filtered output text file.
**Options:**
-   `--min-length=N`: Include only messages with a character length greater than or equal to `N` (default: 0, which disables this filter).
-   `--start-msg=ID`: Include only messages with a Telegram message ID greater than or equal to this value.
-   `--start-date=DATE`: Include only messages with a date greater than or equal to this value. `DATE` can be in `YYYY-MM-DD` format or a Unix timestamp (number of seconds since the epoch).
### `chunk_splitter_with_dates.py`
Splits a large text file into smaller chunks of a specified size, reporting the date range covered by each chunk.
```bash
python scripts/chunk_splitter_with_dates.py input.txt chunk_prefix [max_chars]
```
**Parameters:**
-   `input.txt`: The path to the input text file to be split.
-   `chunk_prefix`: A prefix for the output files. Chunks will be named like `chunk_prefix001.txt`, `chunk_prefix002.txt`, etc.
-   `max_chars`: (Optional) The maximum number of characters per chunk (default: 50000).
## Workflow Examples
### Basic Cleanup for Reading
```bash
# Convert JSON export to a human-readable markdown file
python scripts/telegram_simplifier_plus.py telegram_export.json readable_chat.md --markdown=readable_chat.md
# Read the markdown version
less readable_chat.md # Or use your preferred text editor/viewer
```
### Preparing for LLM Analysis
```bash
# Process and consolidate messages from JSON export
python scripts/telegram_simplifier_plus.py telegram_export.json consolidated.txt --markdown=consolidated.md
# Filter out noise and short messages (e.g., less than 20 chars)
python scripts/telegram_filter_noise.py consolidated.txt filtered.txt --min-length=20
# Split the filtered file into chunks of 50,000 characters
python scripts/chunk_splitter_with_dates.py filtered.txt chunk_ 50000
```
### Analyzing Specific Time Periods or Message Ranges
```bash
# Process and filter messages starting from a specific date (YYYY-MM-DD)
python scripts/telegram_simplifier_plus.py telegram_export.json consolidated_recent.txt
python scripts/telegram_filter_noise.py consolidated_recent.txt filtered_recent.txt --start-date=2023-10-26
# Process and filter messages starting from a specific message ID
python scripts/telegram_simplifier_plus.py telegram_export.json consolidated_subset.txt
python scripts/telegram_filter_noise.py consolidated_subset.txt filtered_subset.txt --start-msg=150000
```
This guide provides more detail on the script parameters and shows practical examples of how to chain the scripts together for different use cases. Remember to replace `telegram_export.json`, `consolidated.txt`, `filtered.txt`, etc., with your actual filenames.