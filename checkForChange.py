import hashlib
import json
import logging
import notify2
import os
import re
import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pathlib import Path

base_dir = Path(__file__).resolve().parent
#os.path.dirname(os.path.abspath(__file__))

# Set up logging
current_date=datetime.now().strftime("%Y-%m-%d-%H%M")
LOG_FILE = f"{base_dir}/debug-{current_date}.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,  # Set logging level to DEBUG to capture detailed information
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def delete_old_logs(base_dir):
    """
    Deletes log files with a date in the filename that is older than today's date.
    """
    filename_pattern = r"debug-(\d{4}-\d{2}-\d{2}-\d{4})\.log"
    current_date = datetime.now().date()
    try:
        for filename in os.listdir(base_dir):
            match = re.match(filename_pattern, filename)
            if match:
                file_date_str = match.group(1)  # Extract the YYYY-mm-dd-HHMM part from the filename
                file_date = datetime.strptime(file_date_str, "%Y-%m-%d-%H%M").date()  # Convert to date

                file_path = os.path.join(base_dir, filename)
                if file_date < current_date - timedelta(days=56):
                    os.remove(file_path)
                    logging.info(f"Deleted old log file: {file_path}")
                else:
                    logging.debug(f"File is not old enough: {file_path}")
    except Exception as e:
        logging.error(f"Error while deleting old log files: {e}")


def get_page_content(url, tag_name):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error if the request fails
        logging.debug(f"Successfully fetched content from {url}")

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the first occurrence of the tag
        tag_content = soup.find(id=tag_name)

        if tag_content:
            start = tag_content.text.strip()[:300].strip()[:30].strip()
            end = tag_content.text.strip()[-300:].strip()[-30:].strip()
            logging.debug(f"First chunk: {start}")
            logging.debug(f"Last chunk: {end}")

            return str(tag_content).strip()
        else:
            logging.warning(f"Tag <{tag_name}> not found in the content.")
            return None
    except requests.RequestException as e:
        logging.error(f"Error fetching content from {url}: {e}")
        show_notification("checkForChange Alert", f"Unable to fetch content from {page_name}: will try again later")
        return None


def get_page_hash(content):
    page_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
    logging.debug(f"Generated hash: {page_hash}")
    return page_hash


def load_previous_hash(hash_file):
    if os.path.exists(hash_file):
        with open(hash_file, 'r') as f:
            previous_hash = f.read().strip()
            logging.debug(f"Loaded previous hash from {hash_file}: {previous_hash}")
            return previous_hash
    logging.debug(f"No previous hash found at {hash_file}")
    return None


def save_hash(hash_file, page_hash):
    with open(hash_file, 'w') as f:
        f.write(page_hash)
    logging.debug(f"Saved new hash to {hash_file}: {page_hash}")


def save_page_contents(contents_file, contents):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    with open(contents_file + timestamp, 'w') as f:
        f.write(contents)
    logging.debug(f"Saved new contents to {contents_file}_{timestamp}")


def show_notification(title, message):
    try:
        notify2.init("Notification")
        notification = notify2.Notification(title, message)
        notification.urgency=notify2.URGENCY_CRITICAL
        notification.category="Intranet"
        notification.timeout=notify2.EXPIRES_NEVER
        notification.show()
        logging.info(f"Notification shown: {title} - {message}")
    except Exception as e:
        logging.debug(f"Notification failed: {e}")

def check_for_change(url, hash_file, page_name, contents_file):
    content = get_page_content(url, 'content')
    if content is None:
        logging.error(f"Could not retrieve content from {url}, skipping check.")
        show_notification("checkForChange Alert", f"Unable to connect to {page_name}: will try again later")
        return

    current_hash = get_page_hash(content)
    previous_hash = load_previous_hash(hash_file)

    if previous_hash == None:
        show_notification("checkForChange Alert", f"No previous hash for {page_name}: storing hash for next use")
        save_hash(hash_file, current_hash)
        logging.info(f"No previous hash for {page_name}, hash stored.")
        save_page_contents(contents_file, content)
        logging.info(f"No previous contents for {page_name}, contents stored.")
    elif previous_hash != current_hash:
        # If different, show a notification and update the hash file
        show_notification("checkForChange Alert", f"Change detected on {page_name}")
        save_hash(hash_file, current_hash)
        save_page_contents(contents_file, content)
        logging.info(f"Change detected on {page_name}, hash updated.")
    else:
        logging.debug(f"No change detected on {page_name}.")

def main(config):
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    logging.info(f"\n\nStarting web page monitoring at {current_datetime}")
    # Check each web page for changes
    for target in config:
        logging.info("####")
        name = target.get('name')
        short_name = target.get('short_name')
        url = target.get('url')
        check_for_change(url, f"hash_{short_name}", name, f"contents_{short_name}")
    logging.info("Completed one cycle of web page checks.")

if __name__ == "__main__":
    logging.info("-=-=-=-=-=-=-=-=-")
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    logging.info(f"Script execution started at {current_datetime}")
    delete_old_logs(base_dir)

    # allow local config override if it exists
    standard_config_path = base_dir / 'config.json'
    local_config_path = base_dir / 'config.json.local'
    config_path = local_config_path if local_config_path.exists() else standard_config_path

    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
    while True:
        main(config)
        # Check every 5 minutes (300 seconds)
        logging.debug("Sleeping for 5 minutes...")
        time.sleep(300)

