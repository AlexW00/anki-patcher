#! /bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

"$SCRIPT_DIR/process_vocab_inbox.sh" &
pid1=$!
"$SCRIPT_DIR/process_sentence_inbox.sh" &
pid2=$!

wait $pid1 $pid2