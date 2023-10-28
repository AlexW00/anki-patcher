import requests
import os

from anki_patcher.patcher.anki import clean_string_of_html_tags
from anki_patcher.util import parse_config, parse_env, parse_fields

def execute (card_id, fields, config):
    # load env vars via helper function
    env = parse_env(["ANKI_MEDIA_FOLDER", "GOOGLE_API_KEY", "CX"])
    # load config vars via helper function
    [search_input_field_name, image_field_name] = parse_config(["search_input_field_name", "image_field_name"], config)
    # load card field values via helper function
    [search_input, existing_image] = parse_fields([search_input_field_name, image_field_name,], fields)

    # clean search input of html tags
    clean_query = clean_string_of_html_tags(search_input)
    # call the main operation function to add image to card
    add_image_to_card(card_id, clean_query, existing_image, image_field_name, env)


def add_image_to_card(card_id, query, existing_image, image_field_name, env):
    if existing_image != "":
        print(f"Skipping card {card_id} as it already has an image")
        return

    [media_folder, google_api_key, cx] = env

    print(f"Searching for image: {query}")
    params = {
        "q": query,
        "searchType": "image",
        "key": google_api_key,
        "cx": cx,
        "num": 1,  # Number of images to return. Set to 1 to get the first image.
        "fileType": "jpg"
    }
    try:
        response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
        if response.status_code != 200:
            raise Exception(f"Received non-200 response from Google Custom Search API: {response.status_code}")
        data = response.json()
        if "items" not in data or not data["items"]:
            print(f"No images found for query: {query}")
            return
        
        image_url = data["items"][0]["link"]

        # Download the image
        image_data = requests.get(image_url).content
        image_filename = f"{card_id}.jpg"
        
        # Save the image to the Anki media folder
        filepath = os.path.join(media_folder, image_filename)

        # override existing file:
        with open(filepath, 'wb') as f:
            f.write(image_data)

        # Update the Anki card to reference the image by its filename
        field_data = f'<img src="{image_filename}">'
        params = {
            "note": {
                "id": card_id,
                "fields": {image_field_name: field_data}
            }
        }
        from anki_patcher.patcher.anki import invoke
        invoke("updateNoteFields", params)
        print(f"Added image to card {card_id}")
    except Exception as e:
        print(f"Error downloading image: {e}")
        return
