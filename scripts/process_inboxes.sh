#! /bin/bash

./process_vocab_inbox.sh &
pid1=$!
./process_sentence_inbox.sh &
pid2=$!

wait $pid1 $pid2