import os
import json
import logging
from datetime import datetime

def setup_logging(debug=False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level,
                        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

def format_user_input(user_name, user_input):
    """
    Formats the user input along with a timestamp and username.
    """
    datetime_iso = iso_datetime_day()
    return f"{datetime_iso}{user_name}: {user_input}"

def iso_datetime_day():
    """
    Generates an ISO datetime string along with the day of the week.
    """
    datetime_utc = datetime.now()
    datetime_local = datetime_utc.astimezone()
    current_time_iso8601 = datetime_local.replace(microsecond=0).isoformat()
    day_of_week = datetime_local.strftime('%A')
    return (f"{current_time_iso8601}, {day_of_week} - ")

def iso_datetime():
    """
    Generates an ISO datetime string.
    """
    datetime_utc = datetime.now()
    datetime_local = datetime_utc.astimezone()
    return datetime_local.strftime('%Y%m%d%H%M%S')

def save_to_file(file_path, data):
    """
    Writes the provided data to a file specified by file_path.
    """
    os.makedirs(file_path, exist_ok=True)
    with open(file_path, 'w') as file:
        json.dump(data, file)

def load_json(file_path):
    """
    Loads and returns a JSON object from the file specified by file_path.
    """
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        logging.info(f"JSON file not found at {file_path}, creating a new one.")
        return {}
    
def load_character_sheet(sub_dir, sheet = None):
    sub_dir = str(sub_dir).lower()
    sheet = str(sheet).lower() if sheet is not None else sub_dir

    file_path = f"./instructions/{sub_dir}/{sheet.lower()}.txt"
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        logging.error(f"Character sheet {sheet} not found.")
        return ""
    
def load_template(template_name):
    file_path = file_path = f"./instructions/templates/{template_name}.txt"
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        logging.error(f"template {template_name} not found.")
        return ""