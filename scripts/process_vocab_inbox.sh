#! /bin/bash

VOCAB_INBOX="00 - inbox::01 - vocab"

echo "Processing $VOCAB_INBOX"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Run commands in parallel
poetry run anki-patcher -o trim_list_items -c "$SCRIPT_DIR/../configs/trim_list_items_default.yml" -d "$VOCAB_INBOX" patch-async &
pid0=$!
poetry run anki-patcher -o add_tts -c "$SCRIPT_DIR/../configs/add_tts_default.yml" -d "$VOCAB_INBOX" patch-async &
pid1=$!
poetry run anki-patcher -o add_image -c "$SCRIPT_DIR/../configs/add_image_vocab.yml" -d "$VOCAB_INBOX" patch-async &
pid2=$!
poetry run anki-patcher -o add_example -c "$SCRIPT_DIR/../configs/add_example.yml" -d "$VOCAB_INBOX" patch-async &
pid3=$!
poetry run anki-patcher -o gpt -c "$SCRIPT_DIR/../configs/gpt_constituents_vocab.yml" -d "$VOCAB_INBOX" patch-async &
pid4=$!
poetry run anki-patcher -o gpt -c "$SCRIPT_DIR/../configs/gpt_translate_to_eng.yml" -d "$VOCAB_INBOX" patch-async &
pid5=$!
poetry run anki-patcher -o replace -c "$SCRIPT_DIR/../configs/replace_no_pitch.yml" -d "$VOCAB_INBOX" patch-async &
pid6=$!

wait $pid0 $pid1 $pid2 $pid3 $pid4 $pid5 $pid6

poetry run anki-patcher -o replace -c "$SCRIPT_DIR/../configs/replace_english_empty_line.yml" -d "$VOCAB_INBOX" patch-async
poetry run anki-patcher -o add_furigana -c "$SCRIPT_DIR/../configs/add_furigana_vocab_sentence.yml" -d "$VOCAB_INBOX" patch-async 

echo "Done processing $VOCAB_INBOX"