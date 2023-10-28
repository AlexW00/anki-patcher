# 🩹 Anki Patcher

= modular python script launcher to patch anki cards en masse

## Basic Idea

Anki patcher is a script launcher to manipulate anki cards via patch `operations` defined as python functions.

An operation is a python file with an `execute (card_id, fields, config)` function. This function gets called for each card of a specified deck and can execute arbitrary code on the card. The `card_id` and `fields` are provided by anki pacher and the config is a parsed .yml file provided by the user.

## Setup

- run `poetry install`
- add an .env file to the root of the project (based on .env.example)

## Available commands

To execute an operation, run `poetry run anki-patcher <--flags> <command>`

- `poetry run anki-patcher list`: lists all available patch operations
- `poetry run anki-patcher patch -o <operation> -d <deck-name> -c <path-to-config.yml> `: executes the specified operation on all cards of the deck 

### Stock operations:

- `add_image`: for each card of a deck, adds an image retrieved from google, based on another card field value ([example config](./example_configs/add_image_example.yml))
  - use-case: add images of vocabulary words to your cards
- ... building more, contributions welcome!

## Building your own operations

It's easy! 
Just create a new file in [operations](anki_patcher/patcher/operations/) with a `execute(card_id, fields, config)` function (see [add_image](anki_patcher/patcher/operations/add_image.py) for an example). Afterwards, the operation will be available to be executed via `poetry run anki-patcher patch -o <operation> -d <deck-name> -c <path-to-config.yml> `. To check if your operation is available, run `poetry run anki-patcher list`.