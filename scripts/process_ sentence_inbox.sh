#! /bin/bash

SENTENCE_INBOX="00 - inbox::04 - sentences"

echo "Processing $SENTENCE_INBOX"

# Run commands in parallel
poetry run anki-patcher -o add_tts -c ../configs/add_tts_default.yml -d "$SENTENCE_INBOX"

echo "Done processing $SENTENCE_INBOX"