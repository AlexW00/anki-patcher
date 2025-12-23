import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import re
from anki_patcher.patcher.anki import invoke

from anki_patcher.util import (
    parse_config,
    remove_furiganas,
    remove_html_tags_bs,
)


def fetch_example_sentences(japanese_word, num_example_sentences):
    # URL encode the Japanese word
    encoded_word = quote(japanese_word)

    # Construct the URL
    url = f"https://massif.la/ja/search?q={encoded_word}"

    # Make the HTTP request
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code != 200:
        return ["Error: Unable to fetch data from Massif"]

    # Parse the HTML content
    soup = BeautifulSoup(response.text, "html.parser")

    # Define the regex pattern to find the Japanese word
    pattern = re.compile(re.escape(japanese_word))

    # Extract example sentences
    sentences = []
    for li in soup.find_all("li", class_="text-japanese"):
        # Find the first div in each li element, which contains the sentence
        sentence_div = li.find("div")
        if sentence_div:
            # Remove furigana (if any)
            for furigana in sentence_div.find_all(["span", "em"]):
                furigana.unwrap()

            # Get the sentence text
            sentence = sentence_div.get_text()

            # Highlight the Japanese word using regex replace
            highlighted_sentence = pattern.sub(
                f"<span style='background-color: #897099'>{japanese_word}</span>",
                sentence,
            )

            sentences.append(highlighted_sentence)
            if len(sentences) == num_example_sentences:
                break

    return sentences


def execute(card_id, fields, config):
    [source_field_name, out_field_name] = parse_config(
        ["source_field_name", "out_field_name"], config
    )
    num_example_sentences = config.get("num_example_sentences", 3)
    do_overwrite = config.get("do_overwrite", False)

    source_field = fields[source_field_name]
    if source_field is None:
        print(f"Field {source_field_name} doesn't exist, skipping card {card_id}")
        return

    source_value = source_field.get("value")
    if source_value is None:
        print(
            f"Field {source_field_name} doesn't have a value, skipping card {card_id}"
        )
        return

    source_value = remove_html_tags_bs(source_value)
    source_value = remove_furiganas(source_value)
    source_value = source_value.strip()

    if source_value == "":
        print(f"Field {source_field_name} is empty, skipping card {card_id}")
        return

    out_field = fields[out_field_name]
    if out_field is None:
        print(f"Field {out_field_name} doesn't exist, skipping card {card_id}")
        return

    out_value = out_field.get("value")
    if out_value is not None and out_value != "" and not do_overwrite:
        print(
            f"Field {out_field_name} already has a value, skipping card {card_id} (value: {out_value})"
        )
        return

    example_sentences = fetch_example_sentences(source_value, num_example_sentences)
    if len(example_sentences) == 0:
        print(
            f"Unable to find example sentences for {source_value}, skipping card {card_id}"
        )
        return

    # place inside ul
    example_sentences_html = "<ul>"
    for sentence in example_sentences:
        example_sentences_html += f"<li>{sentence}</li>"
    example_sentences_html += "</ul>"
    out_value = example_sentences_html.strip()

    params = {"note": {"id": card_id, "fields": {out_field_name: out_value}}}
    invoke("updateNoteFields", params)

    print(f"Added example sentences to {out_field_name}")
