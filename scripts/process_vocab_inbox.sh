#! /bin/bash

VOCAB_INBOX="00 - inbox::01 - vocab"

echo "Processing $VOCAB_INBOX"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
DOCKER_CONFIG_DIR="/work/configs"
RUN_COMMAND="${SCRIPT_DIR}/anki-patcher.sh"

# Run commands in parallel
$RUN_COMMAND -o trim_list_items -c "$DOCKER_CONFIG_DIR/trim_list_items_default.yml" -d "$VOCAB_INBOX" patch-async &
pid0=$!
$RUN_COMMAND -o add_tts -c "$DOCKER_CONFIG_DIR/add_tts_default.yml" -d "$VOCAB_INBOX" patch-async &
pid1=$!
$RUN_COMMAND -o add_image -c "$DOCKER_CONFIG_DIR/add_image_vocab.yml" -d "$VOCAB_INBOX" patch-async &
pid2=$!
$RUN_COMMAND -o add_example -c "$DOCKER_CONFIG_DIR/add_example.yml" -d "$VOCAB_INBOX" patch-async &
pid3=$!
$RUN_COMMAND -o gpt -c "$DOCKER_CONFIG_DIR/gpt_constituents_vocab.yml" -d "$VOCAB_INBOX" patch-async &
pid4=$!
$RUN_COMMAND -o gpt -c "$DOCKER_CONFIG_DIR/gpt_translate_to_eng.yml" -d "$VOCAB_INBOX" patch-async &
pid5=$!
$RUN_COMMAND -o replace -c "$DOCKER_CONFIG_DIR/replace_no_pitch.yml" -d "$VOCAB_INBOX" patch-async &
pid6=$!

wait $pid0 $pid1 $pid2 $pid3 $pid4 $pid5 $pid6

$RUN_COMMAND -o replace -c "$DOCKER_CONFIG_DIR/replace_english_empty_line.yml" -d "$VOCAB_INBOX" patch-async
$RUN_COMMAND -o add_furigana -c "$DOCKER_CONFIG_DIR/add_furigana_vocab_sentence.yml" -d "$VOCAB_INBOX" patch-async

echo "Done processing $VOCAB_INBOX"