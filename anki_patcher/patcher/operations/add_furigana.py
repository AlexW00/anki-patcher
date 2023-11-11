from anki_patcher.patcher.anki import invoke

from anki_patcher.util import (
    parse_env,
    remove_furiganas,
)

import MeCab
import pykakasi
from jamdict import Jamdict
import furiganamaker
import regex


kakasi = pykakasi.kakasi()
mecab = MeCab.Tagger()
jam = Jamdict()
maker = furiganamaker.Instance("[", "]", kakasi, mecab, jam)


def add_furigana(text):
    problems = []
    hasfurigana, newtext = maker.process(text, problems)
    return newtext


def execute(card_id, fields, config):
    env = parse_env(["ANKI_MEDIA_FOLDER"])
    if config is None:
        config = {}

    field_names = config.get("field_names", fields.keys())

    new_fields = {}

    for field_name in field_names:
        field = fields[field_name]
        if field is None:
            continue

        value = field.get("value")
        if value is None:
            continue

        value = remove_furiganas(value)
        # replace all text (inside html tags) with furigana

        # re anyything thats not a tag
        re = r"(?<=^|>)[^><]+?(?=<|$)"
        # replace with furigana
        new_value = regex.sub(re, lambda m: add_furigana(m.group(0)), value)

        new_fields[field_name] = new_value

    params = {"note": {"id": card_id, "fields": new_fields}}
    invoke("updateNoteFields", params)
