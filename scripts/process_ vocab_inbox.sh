#! /bin/bash

VOCAB_INBOX="00 - inbox::01 - vocab"

echo "Processing $VOCAB_INBOX"

# Run commands in parallel
poetry run anki-patcher -o add_tts -c ../configs/add_tts_default.yml -d "$VOCAB_INBOX" &
pid1=$!
poetry run anki-patcher -o add_image -c ../configs/add_image_default.yml -d "$VOCAB_INBOX" &
pid2=$!
poetry run anki-patcher -o gpt -c ../configs/gpt_sentence_vocab.yml -d "$VOCAB_INBOX" &
pid3=$!

wait $pid1 $pid2 $pid3

echo "Done processing $VOCAB_INBOX"