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