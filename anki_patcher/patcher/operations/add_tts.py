import os
import requests
import json
import base64

from anki_patcher.util import parse_config, parse_env, parse_fields, remove_html_tags_bs
from anki_patcher.util import remove_furiganas
from anki_patcher.util import clean_text_for_tts

def execute(card_id, fields, config):
    env = parse_env(["ANKI_MEDIA_FOLDER", "GOOGLE_API_KEY"])
    [text_input_field_name, audio_field_name, lang, voice_name] = parse_config(["text_input_field_name", "audio_field_name", "language", "voice_name"], config)
    do_override_audio = config.get("do_override_audio", False)
    [search_input, existing_audio] = parse_fields([text_input_field_name, audio_field_name], fields)

    # Clean search input of HTML tags
    no_html_query = remove_html_tags_bs(search_input)
    no_furigana_query = remove_furiganas(no_html_query)
    clean_query = clean_text_for_tts(no_furigana_query)

    add_audio_to_card(card_id, clean_query, lang, voice_name, do_override_audio, existing_audio, audio_field_name, env)

def add_audio_to_card(card_id, query, lang, voice_name, do_override_audio, existing_audio, audio_field_name, env):
    if existing_audio != "" and do_override_audio == False:
        print(f"Skipping card {card_id} as it already has an audio file")
        return

    [media_folder, google_api_key] = env
    print(f"Generating TTS audio for: {query}")

    url = "https://texttospeech.googleapis.com/v1/text:synthesize"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": google_api_key
    }
    data = {
        "input": {"text": query},
        "voice": {"languageCode": lang, "name": voice_name},
        "audioConfig": {"audioEncoding": "MP3"}
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            print(f"Failed to generate TTS audio: {response.text}")
            return

        body = response.json()
        audio_content = base64.b64decode(body['audioContent'])
        audio_filename = f"{card_id}.mp3"
        filepath = os.path.join(media_folder, audio_filename)
        
        with open(filepath, 'wb') as out:
            out.write(audio_content)
            print(f"Audio content written to file {audio_filename}")

        # Update the Anki card to reference the audio file
        field_data = f'[sound:{audio_filename}]'
        params = {
            "note": {
                "id": card_id,
                "fields": {audio_field_name: field_data}
            }
        }
        from anki_patcher.patcher.anki import invoke
        invoke("updateNoteFields", params)
        print(f"Added audio to card {card_id}")
    except Exception as e:
        print(f"Error generating TTS audio: {e}")
        return
