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
1. Clone this repository:

   git clone https://github.com/thoughtfan/telegram-analysis-tools.git
   cd telegram-analysis-tools

2. Ensure you have Python 3.6 or newer installed. All scripts use only standard Python libraries (no additional packages required).

3. Make the scripts executable (Linux/Mac):

   chmod +x scripts/*.py

## Quick Start
1. Export your Telegram chat as JSON (using Telegram Desktop)

2. Process the JSON file:

   python scripts/telegram_simplifier_plus.py result.json clean_consolidated.txt

3. Filter out noise (optional):

   python scripts/telegram_filter_noise.py clean_consolidated.txt clean_low_noise.txt

4. Split into chunks for analysis:

   python scripts/chunk_splitter_with_dates.py clean_low_noise.txt chunk_
   
5. Start a new LLM conversation, instructing it on what you'd like it to do with the chunks to follow.

6. Copy your chunk output files, submitting one at a time to your LLM interface (default chunk-size is 50,000 chars because that's the max the nano-gpt.com web interface will handle).

## More Information
See the [Usage Guide](docs/usage-guide.md) for detailed options and advanced scenarios. 
Refer to two examples in the [examples folder](examples/) to see llm-optimised (.txt) and human-readable (.md.) outputs of telegram_simplifier_plus.py.
If you are interested in contributiong to this project, please see the [Contributing page](docs/CONTRIBUTING.md).

## License
This project is released under the [MIT License](LICENSE).