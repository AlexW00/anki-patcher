#! /bin/bash

SENTENCE_INBOX="00 - inbox::04 - sentences"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
DOCKER_CONFIG_DIR="/work/configs"
RUN_COMMAND="${SCRIPT_DIR}/anki-patcher.sh"

echo "Processing $SENTENCE_INBOX"

# Run commands in parallel
$RUN_COMMAND -o add_tts -c "$DOCKER_CONFIG_DIR/add_tts_default.yml" -d "$SENTENCE_INBOX" patch &
pid1=$!

wait $pid1

echo "Done processing $SENTENCE_INBOX"