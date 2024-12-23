# 🩹 Anki Patcher

= modular python script launcher to patch anki cards en masse

## Basic Idea

Anki patcher is a script launcher to manipulate anki cards via patch `operations` defined as python functions.

An operation is a python file with an `execute (card_id, fields, config)` function. This function gets called for each card of a specified deck and can execute arbitrary code on the card. The `card_id` and `fields` are provided by anki pacher and the `config` is a parsed .yml file provided by the user.

## Setup

- run `poetry install`
- run `poetry shell` and `python -m unidic download` to download the unidic dictionary
- add an .env file to the root of the project (based on .env.example)
- install anki-connect add-on in your anki desktop app

## Available commands

To execute an operation, run `poetry run anki-patcher <--flags> <command>`

- `poetry run anki-patcher list`: lists all available patch operations
- `poetry run anki-patcher patch -o <operation> -d <deck-name> -c <path-to-config.yml> `: executes the specified operation on all cards of the deck 

### Stock operations:

- `add_image`: for each card of a deck, adds an image retrieved from google, based on another card field value ([example config](./example_configs/add_image_example.yml))
  - use-case: add images to cards for language learning
  - example-use: `poetry run anki-patcher patch -o add_image -d "German::A1" -c example_configs/add_image_example.yml`
- `add_tts`: for each card of a deck, adds a text-to-speech audio file retrieved from google tts, based on another card field value ([example config](./example_configs/add_tts_example.yml))
  - use-case: add tts to cards for language learning
  - example-use: `poetry run anki-patcher patch -o add_tts -d "German::A1" -c example_configs/add_tts_example.yml`
- `gpt`: for each card of a deck, adds a text generated by OpenAI GPT Api (e.g. gpt-4), based on another card field value ([example config](./example_configs/gpt_example.yml))
  - use-case: add example sentences to cards
  - example-use: `poetry run anki-patcher patch -o gpt -d "German::A1" -c example_configs/gpt_example.yml`
- `replace`: for each card of a deck, replaces a substring of a field value with another string ([example config](./example_configs/replace_example.yml))
  - use-case: replace a substring of a field value with another string
  - example-use: `poetry run anki-patcher patch -o replace -d "German::A1" -c example_configs/replace_example.yml`
- ... building more, contributions welcome!

## Building your own operations

It's easy! 
Just create a new file in [operations](anki_patcher/patcher/operations/) with a `execute(card_id, fields, config)` function (see [add_image](anki_patcher/patcher/operations/add_image.py) for an example). Afterwards, the operation will be available to be executed via `poetry run anki-patcher patch -o <operation> -d <deck-name> -c <path-to-config.yml> `. To check if your operation is available, run `poetry run anki-patcher list`.