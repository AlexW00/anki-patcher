import requests
import re
import os

ANKI_CONNECT_URL = os.getenv("ANKI_CONNECT_URL", "http://localhost:8765")

def invoke(action, params):
    request = {
        "action": action,
        "params": params,
        "version": 6
    }
    response = requests.post(ANKI_CONNECT_URL, json=request)
    if response.status_code != 200:
        raise Exception(f"Received non-200 response from AnkiConnect: {response.status_code}")
    return response.json()

# cleans a string of html tags such as li, div, etc
def clean_string_of_html_tags(string):
    no_opening = re.sub(r'<[^<]+?>', ';', string)
    clean = re.sub(r';+', ',', no_opening)
    # remove affix and suffix if = ","
    if clean[0] == ",":
        clean = clean[1:]
    if clean[-1] == ",":
        clean = clean[:-1]
    # take MAX first 3 words
    length = len(clean.split(","))
    if length > 2:
        clean = ','.join(clean.split(",")[:2])
    return clean
