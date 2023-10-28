import re
import json

from anki_patcher.util import parse_config, parse_fields

def execute(card_id, fields, config):
    [field_names, replacements] = parse_config(["field_names","replacements"], config)

    print(field_names)
    updated_fields = {}
    for field_name in field_names:
        try:
            print(f"Looking for field {field_name}")
            field = fields[field_name]

            print(f"Found field {field_name} on card {card_id}")
            field_content = field.get("value")

            if field_content is None:
                print(f"Skipping card {card_id} field {field_name} as it does not exist")
                continue

            print(f"Replacing content for field {field_name}")
            updated_field_content = replace_content(field_content, replacements)
            if updated_field_content != field_content:
                updated_fields[field_name] = updated_field_content
        except Exception as e:
            print(f"Error replacing content for field {field_name} on card {card_id}: {e}")

    if updated_fields:
        from anki_patcher.patcher.anki import invoke
        params = {
            "note": {
                "id": card_id,
                "fields": updated_fields
            }
        }
        invoke("updateNoteFields", params)
        print(f"Updated fields for card {card_id}: {', '.join(updated_fields.keys())}")

def replace_content(content, replacements):
    for replacement in replacements:
        match_regex = list(replacement.keys())[0]
        replacement_value = replacement[match_regex]
        content = re.sub(match_regex, replacement_value, content)

    return content