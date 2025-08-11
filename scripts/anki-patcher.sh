#!/usr/bin/env bash

docker compose run --rm -T \
  -e ANKI_MEDIA_FOLDER=/anki_media \
  -v "$HOME/Library/Application\ Support/Anki2/User\ 1/collection.media":/anki_media:rw \
  anki-patcher "$@"