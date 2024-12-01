import os
import openai

from anki_patcher.util import parse_config
from anki_patcher.patcher.anki import invoke
import timeout_decorator
import re


# exports all cards of a specified deck to markdown files
# by filling out the user provided template with the card's fields
@timeout_decorator.timeout(10)
def execute(note_id, fields, config):
    # Parse configurations
    [
        template,
        input_field_names,
        out_dir,
        filename_template,
        do_remove_html_from_fields,
        filename_template_regex,
    ] = parse_config(
        [
            "template",
            "input_field_names",
            "out_dir",
            "filename_template",
            "do_remove_html_from_fields",
            "filename_template_regex",
        ],
        config,
    )
    # check that out dir exists
    if not os.path.exists(out_dir):
        # ask if it should be created
        if (
            not input(f"Directory {out_dir} does not exist. Create it? (y/n): ").lower()
            == "y"
        ):
            # throw an exception if the user doesn't want to create the directory
            raise Exception(f"Directory {out_dir} does not exist")

    # Parse input fields to a dictionary
    input_field_values = {}
    for input_field_name in input_field_names:
        if not input_field_name in fields:
            raise Exception(f"Field {input_field_name} must be set")

        value = fields[input_field_name].get("value")
        # remove all html tags from the value
        value_stripped = re.sub(r"<.*?>", " ", value)

        if do_remove_html_from_fields:
            input_field_values[input_field_name] = value_stripped
        else:
            input_field_values[input_field_name] = value

    # fill out the template with the card's fields
    output = template.format(**input_field_values)

    # get the cards deck name by its id via anki connect
    card_id = invoke("notesInfo", {"notes": [note_id]})["result"][0]["cards"][0]
    deck_name = invoke("cardsInfo", {"cards": [card_id]})["result"][0]["deckName"]

    # write the output to a file
    # file location is out_dir/deck_name/card_id.md
    # important: split the deck name by :: and re join with /
    filename = filename_template.format(**input_field_values)
    if filename_template_regex and filename_template_regex != "":
        filename = re.sub(filename_template_regex, "", filename)
    out_file = os.path.join(out_dir, "/".join(deck_name.split("::")), filename + ".md")

    out_file_dir = out_file[: out_file.rfind("/")]
    os.makedirs(out_file_dir, exist_ok=True)

    last_edit = invoke("notesInfo", {"notes": [note_id]})["result"][0]["mod"]
    file_last_edit = 0
    if os.path.exists(out_file):
        file_last_edit = os.path.getmtime(out_file)

    if last_edit > file_last_edit:
        with open(out_file, "w") as f:
            print(f"Writing card {note_id} to {out_file}")
            f.write(output)
    else:
        print(f"Skipping card {note_id} as the file is up to date")
