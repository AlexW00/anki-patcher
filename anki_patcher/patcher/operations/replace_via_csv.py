from anki_patcher.util import parse_config
import csv
from anki_patcher.patcher.anki import invoke


def execute(card_id, fields, config):
    [source_field, target_field, csv_file, csv_source_column, csv_target_column] = (
        parse_config(
            [
                "source_field",
                "target_field",
                "csv_file",
                "csv_source_column",
                "csv_target_column",
            ],
            config,
        )
    )
    # 1. get source field value
    source_content = fields[source_field].get("value")
    print(f"Looking for source field value '{source_content}' in csv file {csv_file}")

    # 2. read csv file
    new_target_value = None
    with open(csv_file, "r") as f:
        # delimiter = ,
        csv_data = list(csv.reader(f))

        # 3. find the value in the csv
        for row in csv_data:
            if row[csv_source_column] == source_content:
                new_target_value = row[csv_target_column]
                break
    if new_target_value is None:
        print(
            f"Could not find a match for source field value '{source_content}' in csv file {csv_file}"
        )
        return

    current_target_value = fields[target_field].get("value")
    if current_target_value == new_target_value:
        print(
            f"Skipping card {card_id} as target field value '{new_target_value}' is already set"
        )
        return

    # 4. update target field
    updated_fields = {target_field: new_target_value}

    params = {"note": {"id": card_id, "fields": updated_fields}}
    invoke("updateNoteFields", params)
    print(f"Updated fields for card {card_id}: {', '.join(updated_fields.keys())}")
