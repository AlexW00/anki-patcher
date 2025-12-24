#! /bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

(
  cd "$SCRIPT_DIR/.."
  docker compose build anki-patcher
)
export ANKI_PATCHER_DOCKER_BUILT=1

"$SCRIPT_DIR/process_vocab_inbox.sh" &
pid1=$!
"$SCRIPT_DIR/process_sentence_inbox.sh" &
pid2=$!

wait $pid1 $pid2
