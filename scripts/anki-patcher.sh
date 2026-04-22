#!/usr/bin/env bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
ANKI_MEDIA_FOLDER="$HOME/Library/Application Support/Anki2/User 1/collection.media"

cd "$SCRIPT_DIR/.."
docker compose run --rm -T \
  -e ANKI_MEDIA_FOLDER=/anki_media \
  -v "$ANKI_MEDIA_FOLDER:/anki_media:rw" \
  anki-patcher "$@"
