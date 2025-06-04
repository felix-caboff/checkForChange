# Web Page Change Monitor

This Python script monitors specific HTML page sections for content changes, logs activity, and issues desktop notifications upon detection of differences. It is designed for long-term unattended operation with detailed logging and automatic log rotation.

Pull requests welcome.

## Features

- Periodic monitoring of defined web pages and `<div id="content">` tags
- Content change detection via SHA-256 hash comparison
- Historical snapshot saving of changed content
- Desktop notifications using `notify2`
- Log rotation with automatic pruning of logs older than 56 days
- Has a local config override (`config.json.local`) for easy updates in the future
- SystemD service definition

## Installation

Linux desktop notifications use notify2. You must have a notification daemon running (e.g., notify-osd, dunst, xfce4-notifyd).

This can be run manually within a pipenv, but it is designed for use with a SystemD service.  See INSTALL file.

## Configuration

You will need to copy the `config.json` file to `config.json.local` and update the values.  Basic format is:

```
[
  {
    "name": "Example Site",
    "short_name": "example",
    "url": "https://example.com/somepage",
    "html_tag_id": "main_tag"
  },
  {
    "name": "Another Page",
    "short_name": "another",
    "url": "https://anotherdomain.com",
    "html_tag_id": "contents_tag"
  }
]
```

## What does it do

The script will:

- Monitor each configured page's <div id="{{{html_tag_id}}}">
- Compare its current hash with the previously stored one
- Save and log any content changes
- Alert via desktop notification
- Sleep for 5 minutes between checks

## Files Created

- debug-YYYY-MM-DD-HHMM.log — Rotating logs with DEBUG-level detail
- hash_<short_name> — Stores the last known hash for comparison
- contents_<short_name>YYYY-MM-DD_HHMMSS — Snapshot of HTML on content change

## Log Management

Old logs older than 56 days are automatically deleted. All script activity is logged in timestamped files in the same directory
