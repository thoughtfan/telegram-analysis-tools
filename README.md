# Telegram Analysis Tools
A toolkit for processing Telegram chat exports to prepare them for analysis with Large Language Models (LLMs).
## Features
- Convert JSON Telegram exports to simplified formats
- Consolidate sequential messages from the same user
- Filter out noise and bot messages
- Transform URLs to reduce clutter
- Generate human-readable markdown for easy reference
- Split large conversations into analysis-ready chunks
- Filter by date or message ID ranges

## Installation

1. Clone this repository (or you could simply download the .py scripts you need, given they have no dependencies not included in Python 3.6). If cloning:
   ```
    git clone https://github.com/thoughtfan/telegram-analysis-tools.git
   cd telegram-analysis-tools
   ```

2. Ensure you have Python 3.6 or newer installed. All scripts use only standard Python libraries (no additional packages required).

3. Make the scripts executable (Linux/Mac):
   ```
   chmod +x scripts/*.py
   ```
   
   **Note:** If you choose not to make the scripts executable, you'll need to prefix all commands in this documentation with `python3`. For example: `python3 scripts/telegram_simplifier_plus.py` instead of `./scripts/telegram_simplifier_plus.py`.

4. Make scripts accessible from anywhere (optional but recommended):
   ```
   # Create a bin directory in your home if it doesn't exist
   mkdir -p ~/bin
   
   # Create symlinks to scripts
   ln -s "$PWD/scripts/"*.py ~/bin/
   
   # Make sure ~/bin is in your PATH (add to your .bashrc or .zshrc if it's not)
   echo 'export PATH=$PATH:~/bin' >> ~/.bashrc
   source ~/.bashrc
   ```
   
   **Note:** If you skip this step, you'll need to use the full path to the scripts or run them from the project directory.


## Quick Start
1. Export your Telegram chat as JSON (using Telegram Desktop)

2. Process the JSON file:
   ```
   telegram_simplifier_plus.py result.json clean_consolidated.txt
   ```
3. Filter out noise (optional):
   ```
   telegram_filter_noise.py clean_consolidated.txt clean_low_noise.txt
   ```
4. Split into chunks for analysis:
   ```
   chunk_splitter_with_dates.py clean_low_noise.txt chunk_
   ```   
5. Start a new LLM conversation, instructing it on what you'd like it to do with the chunks to follow.

6. Copy your chunk output files, submitting one at a time to your LLM interface (default chunk-size is 50,000 chars because that's the max the nano-gpt.com web interface will handle).

## More Information
See the [Usage Guide](docs/usage-guide.md) for detailed options and advanced scenarios./n
There are two output examples of telegram_simplifier_plus.py: the llm-optimised [sample_output.txt](examples/sample_output.txt) and the optional (`--markdown=FILE`) human-readable [sample_output.md](examples/sample_output.md) *with message ID's to refer to them from LLM summaries*. (For comparison purposes, also included is a file with the same three example messages in the raw form in which it was exported from Telegram: [sample-input_telegram-export.json](examples/sample-input_telegram-export.json))./n
If you are interested in contributiong to this project, please see the [Contributing page](docs/CONTRIBUTING.md).

## License
This project is released under the [MIT License](LICENSE).