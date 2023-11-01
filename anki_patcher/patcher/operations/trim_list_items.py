import re
import json
from anki_patcher.util import parse_config, parse_fields, trim_list_points

def execute(card_id, fields, config):
    print("exec")
    print(config)
    [max_root_items, max_nested_items] = parse_config(["max_root_items", "max_nested_items"], config)
    print(config)
    field_names = config.get("field_names")

    updated_fields = {}
    target_fields = fields.keys() if field_names is None else field_names

    for field_name in target_fields:
        try:
            print(f"Looking for field {field_name}")
            field = fields.get(field_name)

            if field is None:
                print(f"Field {field_name} does not exist on card {card_id}")
                continue

            print(f"Found field {field_name} on card {card_id}")
            field_content = field.get("value")

            if field_content is None:
                print(f"Skipping card {card_id} field {field_name} as it does not have a 'value' key")
                continue

            print(f"Replacing content for field {field_name}")
            updated_field_content = trim_list_points(field_content, max_root_items, max_nested_items)
            if updated_field_content != field_content:
                updated_fields[field_name] = updated_field_content
        except Exception as e:
            print(f"Error trimming list items for field {field_name} on card {card_id}: {e}")

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

