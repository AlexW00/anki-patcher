import os

from .anki import invoke
import importlib.util
import multiprocessing

ANKI_MEDIA_FOLDER = os.getenv("ANKI_MEDIA_FOLDER")  # Path to Anki media folder
operations = {}


def get_operations_dir():
    return os.path.join(os.path.dirname(__file__), "operations")


def get_operations():
    operations = []
    for filename in os.listdir(get_operations_dir()):
        filename = os.path.join(get_operations_dir(), filename)
        if filename.endswith(".py") and filename.endswith("__init__.py") == False:
            operation = filename.split("/")[-1][:-3]
            operations.append([operation, filename])
    return operations


def import_operation(operation):
    operation_name, operation_file = operation
    spec = importlib.util.spec_from_file_location(operation_name, operation_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    execute_function = getattr(module, "execute", None)
    if execute_function:
        return {operation_name: execute_function}
    else:
        raise Exception(f"Operation {operation_name} does not have an execute function")


def import_operations():
    global operations
    operations_dirs = get_operations()
    for operation in operations_dirs:
        imported_operation = import_operation(operation)
        if imported_operation:
            operations.update(imported_operation)


def get_note_infos(deck_name):
    query = f'deck:"{deck_name}"'
    params = {"query": query}
    response = invoke("findNotes", params)
    card_ids = response.get("result")

    if card_ids is None:
        print(f"Error: Could not retrieve cards for query: {query}")
        return []

    params = {"notes": card_ids}
    response = invoke("notesInfo", params)
    note_infos = response.get("result", [])
    return note_infos


def execute_operation(note_info, config, operation_name):
    card_id = note_info.get("noteId")
    fields = note_info.get("fields", {})

    operation = operations.get(operation_name)
    try:
        operation(card_id, fields, config)
    except Exception as e:
        print(f"Error executing operation {operation_name} on card {card_id}: {e}")


def patch(operation_name, deck_name, config):
    note_infos = get_note_infos(deck_name)
    if note_infos == []:
        print(f"No cards found for deck: {deck_name}")
        return

    print(f"Patching {len(note_infos)} cards in deck: {deck_name}")
    for note_info in note_infos:
        execute_operation(note_info, config, operation_name)


def patch_async(operation_name, deck_name, config):
    note_infos = get_note_infos(deck_name)
    if note_infos == []:
        print(f"No cards found for deck: {deck_name}")
        return

    print(f"Patching {len(note_infos)} cards in deck: {deck_name}")
    results = []

    pool = multiprocessing.Pool(100)
    for note_info in note_infos:
        result = pool.apply_async(
            execute_operation, (note_info, config, operation_name)
        )
        print(f"Started patching card {note_info.get('noteId')}")
        results.append(result)

    for result in results:
        try:
            result.get()
        except Exception as e:
            print(f"Error executing operation {operation_name}: {e}")

    print(f"Finished patching {len(note_infos)} cards in deck: {deck_name}")


def get_available_operations():
    operations = get_operations()
    available_operations = []
    for operation in operations:
        available_operations.append(operation[0].split("/")[-1])
    return available_operations


import_operations()
