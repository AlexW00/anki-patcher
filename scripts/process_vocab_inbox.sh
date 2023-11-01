#! /bin/bash

VOCAB_INBOX="00 - inbox::01 - vocab"

echo "Processing $VOCAB_INBOX"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Run commands in parallel
poetry run anki-patcher -o trim_list_items -c "$SCRIPT_DIR/../configs/trim_list_items_default.yml" -d "$VOCAB_INBOX" patch &
pid0=$!
poetry run anki-patcher -o add_tts -c "$SCRIPT_DIR/../configs/add_tts_default.yml" -d "$VOCAB_INBOX" patch &
pid1=$!
poetry run anki-patcher -o add_image -c "$SCRIPT_DIR/../configs/add_image_vocab.yml" -d "$VOCAB_INBOX" patch &
pid2=$!
poetry run anki-patcher -o gpt -c "$SCRIPT_DIR/../configs/gpt_sentence_vocab.yml" -d "$VOCAB_INBOX" patch &
pid3=$!
poetry run anki-patcher -o gpt -c "$SCRIPT_DIR/../configs/gpt_constituents_vocab.yml" -d "$VOCAB_INBOX" patch &
pid4=$!


wait $pid0 $pid1 $pid2 $pid3 $pid4

echo "Done processing $VOCAB_INBOX"