import os
import re
import regex
from bs4 import BeautifulSoup

def parse_env(vars):
    env_values = []
    for var in vars:
        value = os.getenv(var)
        if value == None:
            raise Exception(f"Environment variable {var} must be set")
        env_values.append(value)
    return env_values

def parse_config(props, config):
    config_values = []
    for prop in props:
        value = config.get(prop)
        if value == None:
            raise Exception(f"Config must specify {prop}")
        config_values.append(value)
    return config_values

def parse_fields(field_names, fields):
    field_values = []
    for field_name in field_names:
        field_value = fields[field_name].get("value")
        if field_name == None:
            raise Exception(f"Field {field_name} must be set")
        
        field_values.append(field_value)
    return field_values

def remove_html_tags_bs(input_text):
    soup = BeautifulSoup(input_text, "html.parser")
    return soup.get_text()

def remove_furiganas(string):
    # removes all furigana written with square or round brackets
    # e.g. 家族[かぞく] -> 家族
    return re.sub(r'(\[.*?\])|(\(.*?\))', '', string)
import regex

def clean_text_for_tts(input_text):
    # Keeping letters (both Latin and Japanese), Japanese characters, and spaces
    # Removing numbers and special characters
    cleaned_text = regex.sub(r'[^\p{L}\p{N}\p{Zs}\p{Script=Hiragana}\p{Script=Katakana}\p{Script=Han}]', '', input_text)
    return cleaned_text


def trim_list_points(string, max_root_items, max_nested_items):
    soup = BeautifulSoup(string, 'html.parser')

    def trim_list(list_element, max_items):
        for i, li in enumerate(list_element.find_all('li', recursive=False)):
            # Trim nested lists first
            for nested_list in li.find_all(['ul', 'ol'], recursive=False):
                trim_list(nested_list, max_nested_items)

            # Remove list items beyond the limit
            if i >= max_items:
                li.decompose()

    lists = soup.find_all(['ul', 'ol'])
    for list_element in lists:
        trim_list(list_element, max_root_items)

    return str(soup)
