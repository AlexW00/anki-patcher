#!/usr/bin/env bash

ANKI_MEDIA_FOLDER="$HOME/Library/Application\\ Support/Anki2/User\\ 1/collection.media"

docker compose run --rm -T \
  -e ANKI_MEDIA_FOLDER=/anki_media \
  -v "$ANKI_MEDIA_FOLDER:/anki_media:rw" \
  anki-patcher "$@"