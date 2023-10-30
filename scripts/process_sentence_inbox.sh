#! /bin/bash

SENTENCE_INBOX="00 - inbox::04 - sentences"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo "Processing $SENTENCE_INBOX"

# Run commands in parallel
poetry run anki-patcher -o add_tts -c "$SCRIPT_DIR/../configs/add_tts_default.yml" -d "$SENTENCE_INBOX" patch

echo "Done processing $SENTENCE_INBOX"