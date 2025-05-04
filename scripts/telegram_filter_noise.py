#!/usr/bin/env python3
"""
Smart noise filter for consolidated Telegram messages.
Identifies and removes messages likely to be conversational noise.
"""

import sys
import re
import os
from datetime import datetime

# Low-value standalone phrases (case insensitive)
LOW_VALUE_PHRASES = [
    r"^(agreed|agree|this|that|yes|no|yep|nope|maybe|ok|okay|lol|haha|hmm|cool|nice|great|\+1|-1|same|\^|indeed|true|false|correct|wrong|right|exactly|precisely|ofc|of course|def|definitely|absolutely)$",
    r"^(thanks|thank you|ty|thx|tnx|thanks!|ty!)$",
    r"^([hm]+|[ha]+|[lo]+|[eh]+)$",  # Variations like "hmm", "haha", "lol", "ehh"
    r"^([kw]{1,3})$",  # Just "k" or "kk" or "w" or "ww"
    r"^[.!?…,:;]+$",  # Just punctuation
]

# Off-topic redirections and moderation phrases
OFF_TOPIC_PATTERNS = [
    r"^(\/off|\/price)\b",  # Rose commands
    r"please (take|move|continue) this (discussion|conversation|topic) to",
    r"this (discussion|conversation|topic) belongs in",
    r"there('s| is) a (channel|group|chat) for (this|that|price)",
    r"let's (keep|stay) on topic",
    r"this is (off|getting off) topic",
]

# Emoji-heavy pattern
EMOJI_PATTERN = r"^[\W\s]*[\U0001F300-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U000024C2-\U0001F251\U0001f926-\U0001f937]+[\W\s]*$"

# URL-only pattern (message consists solely of a URL with optional whitespace)
URL_ONLY_PATTERN = r"^\s*(\[[\w\.]+\])\s*$"  # Matches domain-only links like [example.com]

def unix_to_readable_date(timestamp):
    """Convert Unix timestamp to human-readable date."""
    try:
        return datetime.fromtimestamp(int(timestamp)).strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return None

def is_noise_message(msg_text, min_length=0):
    """
    Determine if a message is likely to be conversational noise.

    Args:
        msg_text: The text content of the message
        min_length: If > 0, messages longer than this bypass noise checks

    Returns:
        bool: True if message is likely noise, False otherwise
    """
    # Quick check on length - longer messages bypass noise check if min_length is set
    if min_length > 0 and len(msg_text) > min_length and not msg_text.count('\n\n'):  # Not consolidated (no \n\n)
        return False

    # Normalize text for pattern matching
    normalized_text = msg_text.strip().lower()

    # Skip if empty after normalization
    if not normalized_text:
        return True

    # Check against low-value phrases
    for pattern in LOW_VALUE_PHRASES:
        if re.match(pattern, normalized_text, re.IGNORECASE):
            return True

    # Check for off-topic/moderation messages
    for pattern in OFF_TOPIC_PATTERNS:
        if re.search(pattern, normalized_text, re.IGNORECASE):
            return True

    # Check if it's just emoji(s)
    if re.match(EMOJI_PATTERN, normalized_text):
        return True

    # Check if it's just a URL (possibly in domain-only format from first pass)
    if re.match(URL_ONLY_PATTERN, normalized_text):
        return True

    # Not identified as noise
    return False

def filter_noise(input_file, output_file, min_length=0, start_msg_id=None, start_date=None):
    """
    Filter out messages that are likely just conversational noise.

    Args:
        input_file: Path to the consolidated pipe-separated messages file
        output_file: Path to save the noise-filtered output
        min_length: If > 0, messages longer than this bypass noise checks
        start_msg_id: If provided, filter only messages with ID >= this value
        start_date: If provided, filter only messages with date >= this value (yyyy-mm-dd or unixtime)
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return False

    # Check if the first line is a header
    header = None
    if lines and lines[0].startswith('# Format:'):
        header = lines[0]
        lines = lines[1:]

    print(f"Read {len(lines):,} lines from '{input_file}'")

    # Convert string date to unixtime if needed
    start_timestamp = None
    if start_date:
        if start_date.isdigit():  # Already a unixtime
            start_timestamp = int(start_date)
        else:  # Try to parse as yyyy-mm-dd
            try:
                dt = datetime.strptime(start_date, "%Y-%m-%d")
                start_timestamp = int(dt.timestamp())
            except ValueError:
                print(f"Warning: Couldn't parse date '{start_date}'. Using all messages.")

    # Filter by start ID or date if specified
    if start_msg_id is not None or start_timestamp is not None:
        filtered_by_id_or_date = []
        excluded_count = 0

        for line in lines:
            parts = line.split('|')
            if len(parts) < 5:
                filtered_by_id_or_date.append(line)  # Keep header or malformed lines
                continue

            msg_id = int(parts[0]) if parts[0].isdigit() else 0
            date_unixtime = int(parts[1]) if parts[1].isdigit() else 0

            # Check if this message should be included based on ID and/or date
            include = True
            if start_msg_id is not None and msg_id < start_msg_id:
                include = False
            if start_timestamp is not None and date_unixtime < start_timestamp:
                include = False

            if include:
                filtered_by_id_or_date.append(line)
            else:
                excluded_count += 1

        lines = filtered_by_id_or_date
        if excluded_count > 0:
            if start_msg_id is not None and start_timestamp is not None:
                print(f"Excluded {excluded_count:,} messages before ID {start_msg_id} or date {start_date}")
            elif start_msg_id is not None:
                print(f"Excluded {excluded_count:,} messages before ID {start_msg_id}")
            else:
                print(f"Excluded {excluded_count:,} messages before date {start_date}")

    # Filter out noise messages
    filtered_lines = []
    noise_count = 0
    noise_categories = {
        "low_value": 0,
        "off_topic": 0,
        "emoji_only": 0,
        "url_only": 0,
        "empty": 0
    }

    for line in lines:
        parts = line.split('|')
        if len(parts) < 5:  # Verify line has expected format
            # Keep malformed lines
            filtered_lines.append(line)
            continue

        text = parts[4].strip()

        # Check if this is a noise message
        if not text:
            noise_count += 1
            noise_categories["empty"] += 1
            continue

        # Check against different noise patterns for stats
        normalized_text = text.strip().lower()
        is_noise = False

        # Empty after normalization
        if not normalized_text:
            noise_count += 1
            noise_categories["empty"] += 1
            is_noise = True

        # Low-value phrases
        elif any(re.match(pattern, normalized_text, re.IGNORECASE) for pattern in LOW_VALUE_PHRASES):
            noise_count += 1
            noise_categories["low_value"] += 1
            is_noise = True

        # Off-topic/moderation
        elif any(re.search(pattern, normalized_text, re.IGNORECASE) for pattern in OFF_TOPIC_PATTERNS):
            noise_count += 1
            noise_categories["off_topic"] += 1
            is_noise = True

        # Emoji-only
        elif re.match(EMOJI_PATTERN, normalized_text):
            noise_count += 1
            noise_categories["emoji_only"] += 1
            is_noise = True

        # URL-only
        elif re.match(URL_ONLY_PATTERN, normalized_text):
            noise_count += 1
            noise_categories["url_only"] += 1
            is_noise = True

        # Minimum length check (if enabled)
        elif min_length > 0 and len(text) <= min_length and not text.count('\n\n'):
            noise_count += 1
            noise_categories["low_value"] += 1
            is_noise = True

        # Keep the message if it's not noise
        if not is_noise:
            filtered_lines.append(line)

    # Calculate statistics
    if lines:
        noise_percentage = (noise_count / len(lines)) * 100
    else:
        noise_percentage = 0

    print(f"\nNoise filtering statistics:")
    print(f"- Total noise messages removed: {noise_count:,} ({noise_percentage:.1f}% of input)")
    print(f"  - Low-value phrases: {noise_categories['low_value']:,}")
    print(f"  - Off-topic/moderation: {noise_categories['off_topic']:,}")
    print(f"  - Emoji-only: {noise_categories['emoji_only']:,}")
    print(f"  - URL-only: {noise_categories['url_only']:,}")
    print(f"  - Empty: {noise_categories['empty']:,}")
    print(f"- Messages kept: {len(filtered_lines):,}")

    # Write output file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            if header:
                f.write(header)
            for line in filtered_lines:
                f.write(line)

        # Calculate file size reduction
        input_size = os.path.getsize(input_file)
        output_size = os.path.getsize(output_file)
        size_reduction = input_size - output_size
        size_reduction_pct = (size_reduction / input_size) * 100

        print(f"\nFile size comparison:")
        print(f"- Input: {input_size:,} bytes")
        print(f"- Output: {output_size:,} bytes")
        print(f"- Reduction: {size_reduction:,} bytes ({size_reduction_pct:.1f}%)")

        print(f"\nNoise-filtered data saved to '{output_file}'")
        return True
    except Exception as e:
        print(f"Error writing output file: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python telegram_filter_noise.py input.txt output.txt [options]")
        print("Options:")
        print("  --min-length=N        Minimum character length below which messages are examined (default: 0, disabled)")
        print("  --start-msg=ID        Process only messages with ID >= this value")
        print("  --start-date=DATE     Process only messages with date >= this value (YYYY-MM-DD or unixtime)")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Parse optional arguments
    min_length = 0  # Default: disabled (as you requested)
    start_msg_id = None
    start_date = None

    for arg in sys.argv[3:]:
        if arg.startswith('--min-length='):
            try:
                min_length = int(arg.split('=')[1])
            except (ValueError, IndexError):
                print(f"Invalid min-length value: {arg}")
                sys.exit(1)
        elif arg.startswith('--start-msg='):
            try:
                start_msg_id = int(arg.split('=')[1])
            except (ValueError, IndexError):
                print(f"Invalid start-msg value: {arg}")
                sys.exit(1)
        elif arg.startswith('--start-date='):
            start_date = arg.split('=')[1]

    print(f"Filtering noise from {input_file}")
    if min_length > 0:
        print(f"Using minimum length threshold: {min_length} characters")
    else:
        print("Minimum length filtering: disabled")

    if start_msg_id is not None:
        print(f"Starting from message ID: {start_msg_id}")
    if start_date is not None:
        print(f"Starting from date: {start_date}")

    filter_noise(input_file, output_file, min_length, start_msg_id, start_date)