import re
import json
from anki_patcher.util import parse_config

def execute(card_id, fields, config):
    source_field, target_field = parse_config(["source_field", "target_field"], config)

    if source_field not in fields:
        print(f"Source field {source_field} does not exist on card {card_id}")
        return
    
    if target_field not in fields:
        print(f"Target field {target_field} does not exist on card {card_id}")
        return
    
    print(f"Swapping content of fields {source_field} and {target_field} on card {card_id}")

    source_content = fields[source_field].get("value")
    target_content = fields[target_field].get("value")

    if source_content is None or target_content is None:
        print(f"Skipping card {card_id} as one of the fields does not have a 'value' key")
        return

    updated_fields = {
        source_field: target_content,
        target_field: source_content
    }

    from anki_patcher.patcher.anki import invoke
    params = {
        "note": {
            "id": card_id,
            "fields": updated_fields
        }
    }
    invoke("updateNoteFields", params)
    print(f"Swapped fields for card {card_id}: {source_field} ↔ {target_field}")

def replace_content(content, replacements):
    for replacement in replacements:
        match_regex = list(replacement.keys())[0]
        replacement_value = replacement[match_regex]
        content = re.sub(match_regex, replacement_value, content)

    return content
