#!/usr/bin/env python3
"""
Enhanced Telegram JSON export processor that:
1. Converts JSON to pipe-separated format
2. Filters out machine and bot messages
3. Consolidates rapid sequential messages from the same user
4. Transforms URLs (by default to domain-only format)
5. Creates a human-readable markdown version for easy reference
"""

import json
import sys
import re
import os
from datetime import datetime
from urllib.parse import urlparse

def flatten_text(text_field):
    """Convert any text field (string or array) to a single string."""
    if isinstance(text_field, str):
        return text_field
    elif isinstance(text_field, list):
        result = ""
        for item in text_field:
            if isinstance(item, str):
                result += item
            elif isinstance(item, dict) and 'text' in item:
                result += item['text']
        return result
    return ""

def is_bot_or_machine_message(msg):
    """
    Determine if a message is from a bot or is a machine-generated message.

    Args:
        msg: Dictionary containing message data

    Returns:
        bool: True if message is from a bot or machine-generated
    """
    # Check if message is service message (joining, leaving, etc.)
    if msg.get('type') != 'message':
        return True

    # Check for known bot usernames/IDs
    known_bots = ['Rose', 'user609517172']  # Add more bot identifiers as needed
    if msg.get('from') in known_bots or msg.get('from_id') in known_bots:
        return True

    # Check for common bot message patterns
    text = flatten_text(msg.get('text', ''))
    bot_patterns = [
        r'Hey there .+, and welcome to',  # Welcome messages
        r'Please remember to follow the rules',
        r'This group has rules that you agreed to',
        r'has joined the group',
        r'has left the group',
        r'has been banned', 
        r'has been removed'
    ]

    for pattern in bot_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False

def transform_urls(text, mode="domain"):
    """
    Transform URLs in text based on the specified mode.

    Args:
        text: The text to process
        mode: How to handle URLs:
              "preserve" - leave URLs intact
              "replace" - replace with [URL]
              "domain" - keep only the domain name

    Returns:
        Processed text
    """
    if mode == "preserve":
        return text

    # Find all URLs
    url_pattern = r'https?://\S+'

    if mode == "replace":
        # Replace URLs with [URL]
        return re.sub(url_pattern, "[URL]", text)

    elif mode == "domain":
        # Extract and keep only domain names
        def domain_only(match):
            url = match.group(0)
            try:
                domain = urlparse(url).netloc
                return f"[{domain}]"
            except:
                return "[URL]"

        return re.sub(url_pattern, domain_only, text)

    # Default: preserve
    return text

def consolidate_messages(messages, time_window=180, max_length=300):
    """
    Consolidate sequential messages from the same user if they occur within
    the specified time window and don't exceed the max length.

    Args:
        messages: List of message dictionaries with simplified format
        time_window: Maximum seconds between messages to consolidate (default: 180)
        max_length: Maximum character length for individual messages to consolidate (default: 300)

    Returns:
        List of consolidated messages
    """
    if not messages:
        return []

    consolidated = []
    current_group = [messages[0]]

    for i in range(1, len(messages)):
        current_msg = messages[i]
        last_msg = current_group[-1]

        # Check if this message is from the same user as the previous one
        if (current_msg['from_id'] == last_msg['from_id'] and 
            # Check if within time window
            int(current_msg['date_unixtime']) - int(last_msg['date_unixtime']) <= time_window and 
            # Check if current message isn't too long
            len(current_msg['text']) <= max_length and 
            # Check if accumulated text isn't too long
            len(last_msg['text']) <= max_length):

            # Add to current group
            current_group.append(current_msg)
        else:
            # Process the current group if it exists
            if len(current_group) > 1:
                # Combine messages in the group
                combined_msg = {
                    'id': current_group[0]['id'],  # Keep ID of first message
                    'date_unixtime': current_group[-1]['date_unixtime'],  # Use timestamp of LAST message
                    'from': current_group[0]['from'],
                    'from_id': current_group[0]['from_id'],
                    'text': '\n\n'.join(msg['text'] for msg in current_group)
                }
                consolidated.append(combined_msg)
            else:
                # Single message, no consolidation needed
                consolidated.append(current_group[0])

            # Start a new group with the current message
            current_group = [current_msg]

    # Process the last group
    if len(current_group) > 1:
        combined_msg = {
            'id': current_group[0]['id'],
            'date_unixtime': current_group[-1]['date_unixtime'],  # Use timestamp of LAST message
            'from': current_group[0]['from'],
            'from_id': current_group[0]['from_id'],
            'text': '\n\n'.join(msg['text'] for msg in current_group)
        }
        consolidated.append(combined_msg)
    else:
        consolidated.append(current_group[0])

    return consolidated

def unix_to_human_date(timestamp):
    """Convert Unix timestamp to human-readable date."""
    try:
        dt = datetime.fromtimestamp(int(timestamp))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return "Unknown date"

def create_markdown_output(messages, group_name):
    """
    Create a human-readable markdown version of the messages.

    Args:
        messages: List of message dictionaries with simplified format
        group_name: Name of the Telegram group

    Returns:
        String containing markdown formatted messages
    """
    md_lines = [
        f"# Telegram Messages from \"{group_name}\"",
        "",
        "_This markdown file was automatically generated for easy reading and reference._",
        "",
        "---",
        ""
    ]

    for msg in messages:
        # Convert Unix timestamp to human-readable date
        human_date = unix_to_human_date(msg['date_unixtime'])

        # Format the message in markdown
        md_lines.append(f"### Message ID: {msg['id']}")
        md_lines.append(f"**From:** {msg['from'] or 'Unknown'} ({msg['from_id'] or 'Unknown'})")
        md_lines.append(f"**Date:** {human_date}")
        md_lines.append("")

        # Add the message text, preserving newlines
        text = msg['text'].replace('\n\n', '\n\n> ')
        md_lines.append(f"> {text}")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")

    return "\n".join(md_lines)

def simplify_messages(input_file, output_file=None, markdown_output=None, consolidate=True, 
                      time_window=180, max_length=300, filter_bots=True, url_mode="domain"):
    """
    Simplify and optionally consolidate messages from a Telegram JSON export.

    Args:
        input_file: Path to the Telegram JSON export file
        output_file: Path to save the simplified output (None for stdout)
        markdown_output: Path to save a human-readable markdown version (None to skip)
        consolidate: Whether to consolidate sequential messages from the same user
        time_window: Maximum seconds between messages to consolidate
        max_length: Maximum character length for individual messages to consolidate
        filter_bots: Whether to filter out bot/machine messages
        url_mode: How to handle URLs: "preserve", "replace", or "domain"
    """
    # Calculate input file size for comparison
    input_file_size = os.path.getsize(input_file)

    # Read the JSON data
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract group name
    group_name = data.get('name', 'Telegram Group')

    # Extract messages
    messages = data.get('messages', [])
    total_messages = len(messages)

    # Filter out bot/machine messages if requested
    bot_count = 0
    if filter_bots:
        filtered_messages = []
        for msg in messages:
            if not is_bot_or_machine_message(msg):
                filtered_messages.append(msg)
            else:
                bot_count += 1

        print(f"Removed {bot_count} bot/machine messages ({bot_count/total_messages*100:.1f}% of total)")
        messages = filtered_messages

    # Simplify each message
    simplified = []
    url_transform_count = 0

    for msg in messages:
        if msg.get('type') == 'message':
            text = flatten_text(msg.get('text', ''))
            if text:  # Only include messages with text content
                # Transform URLs if requested
                original_text = text
                if url_mode != "preserve":
                    text = transform_urls(text, url_mode)
                    if text != original_text:
                        url_transform_count += 1

                simplified.append({
                    'id': msg.get('id', ''),
                    'date_unixtime': msg.get('date_unixtime', ''),
                    'from': msg.get('from', ''),
                    'from_id': msg.get('from_id', ''),
                    'text': text
                })

    print(f"Extracted {len(simplified):,} messages with text content")

    if url_mode != "preserve" and url_transform_count > 0:
        print(f"Transformed URLs in {url_transform_count:,} messages")

    original_count = len(simplified)

    # Optionally consolidate messages
    if consolidate:
        simplified = consolidate_messages(simplified, time_window, max_length)

        # Print message reduction statistics
        print(f"\nConsolidation statistics:")
        print(f"- Messages: {original_count:,} → {len(simplified):,}")
        print(f"  ({(original_count-len(simplified))/original_count*100:.1f}% reduction, {original_count-len(simplified):,} messages consolidated)")

    # Create the pipe-separated output format
    if output_file:
        output_lines = ["# Format: id|date_unixtime|from|from_id|text"]
        for msg in simplified:
            # Replace any pipe characters in text with escaped version to maintain format
            # Also replace newlines with space to maintain single-line format
            safe_text = msg['text'].replace('|', '\\|').replace('\n', ' ')

            # Safely handle None values
            msg_id = str(msg['id'] or "")
            date_unixtime = str(msg['date_unixtime'] or "")
            from_name = str(msg['from'] or "")
            from_id = str(msg['from_id'] or "")

            line = f"{msg_id}|{date_unixtime}|{from_name}|{from_id}|{safe_text}"
            output_lines.append(line)

        # Write output file
        with open(output_file, 'w', encoding='utf-8') as f:
            for line in output_lines:
                f.write(line + '\n')

        # Calculate output file size and reduction
        output_file_size = os.path.getsize(output_file)
        size_reduction = input_file_size - output_file_size
        size_reduction_pct = (size_reduction / input_file_size) * 100

        print(f"\nFile size comparison:")
        print(f"- Input: {input_file_size:,} bytes")
        print(f"- Output: {output_file_size:,} bytes")
        print(f"- Reduction: {size_reduction:,} bytes ({size_reduction_pct:.1f}%)")

        print(f"\nProcessed {total_messages:,} input messages → {len(simplified):,} output messages")
        print(f"Overall reduction: {(1 - len(simplified)/total_messages)*100:.1f}% fewer messages")

    # Create the markdown output if requested
    if markdown_output:
        md_content = create_markdown_output(simplified, group_name)

        with open(markdown_output, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"Human-readable markdown version saved to {markdown_output}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python telegram_simplifier_plus.py input.json [output.txt] [options]")
        print("Options:")
        print("  --markdown=FILE          Create a human-readable markdown output file")
        print("  --no-consolidate         Don't consolidate sequential messages")
        print("  --no-bot-filter          Don't filter out bot/machine messages")
        print("  --window=SECONDS         Set time window for consolidation (default: 180)")
        print("  --max-length=CHARS       Set max message length for consolidation (default: 300)")
        print("  --url-mode=MODE          How to handle URLs: preserve, replace, domain (default: domain)")
        sys.exit(1)

    input_file = sys.argv[1]

    # Determine output file
    output_file = None
    for arg in sys.argv[2:]:
        if not arg.startswith('--'):
            output_file = arg
            break

    # Parse optional arguments
    consolidate = True
    filter_bots = True
    time_window = 180
    max_length = 300
    markdown_output = None
    url_mode = "domain"  # Default is domain-only URLs

    for arg in sys.argv[2:]:
        if arg == '--no-consolidate':
            consolidate = False
        elif arg == '--no-bot-filter':
            filter_bots = False
        elif arg.startswith('--window='):
            try:
                time_window = int(arg.split('=')[1])
            except (ValueError, IndexError):
                print(f"Invalid window value: {arg}")
                sys.exit(1)
        elif arg.startswith('--max-length='):
            try:
                max_length = int(arg.split('=')[1])
            except (ValueError, IndexError):
                print(f"Invalid max-length value: {arg}")
                sys.exit(1)
        elif arg.startswith('--markdown='):
            markdown_output = arg.split('=')[1]
        elif arg.startswith('--url-mode='):
            url_mode = arg.split('=')[1]
            if url_mode not in ["preserve", "replace", "domain"]:
                print(f"Invalid URL mode: {url_mode}")
                print("Available modes: preserve, replace, domain")
                sys.exit(1)

    # If markdown output not explicitly specified but pipe-separated output is,
    # generate a default markdown filename based on the output filename
    if output_file and not markdown_output:
        base_name = os.path.splitext(output_file)[0]
        markdown_output = f"{base_name}.md"

    simplify_messages(input_file, output_file, markdown_output, consolidate, time_window, max_length, filter_bots, url_mode)