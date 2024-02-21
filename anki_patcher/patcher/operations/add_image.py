import requests
import os
from PIL import Image
import io
import timeout_decorator


from anki_patcher.util import parse_config, parse_env, parse_fields, remove_html_tags

MAX_IMAGE_RETRIES = 5


@timeout_decorator.timeout(10)
def execute(card_id, fields, config):
    # load env vars via helper function
    env = parse_env(["ANKI_MEDIA_FOLDER", "GOOGLE_API_KEY", "CX"])
    # load config vars via helper function
    [search_input_field_name, image_field_name] = parse_config(
        ["search_input_field_name", "image_field_name"], config
    )
    # load card field values via helper function
    [search_input, existing_image] = parse_fields(
        [search_input_field_name, image_field_name], fields
    )

    # clean search input of html tags
    clean_query = remove_html_tags(search_input)
    # split by " "
    clean_query = clean_query.split(", ")
    # remove empty strings
    clean_query = list(filter(None, clean_query))
    # take only the first word
    clean_query = clean_query[:1]
    # join back with " "
    clean_query = ", ".join(clean_query)
    # call the main operation function to add image to card
    add_image_to_card(card_id, clean_query, existing_image, image_field_name, env)


def is_valid_image(filepath):
    try:
        img = Image.open(filepath)
        img.verify()
        return True
    except:
        return False


def get_image_type(image_data):
    try:
        image = Image.open(io.BytesIO(image_data))
        return image.format.lower()
    except Exception as e:
        return None


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
        "num": 5,  # Number of images to return. Set to 1 to get the first image.
        "fileType": "jpg",
    }
    try:
        response = requests.get(
            "https://www.googleapis.com/customsearch/v1", params=params
        )
        if response.status_code != 200:
            raise Exception(
                f"Received non-200 response from Google Custom Search API: {response.status_code}"
            )
        data = response.json()

        if "items" not in data or not data["items"]:
            print(f"No images found for query: {query}")
            return

        for attempt in range(MAX_IMAGE_RETRIES):
            image_url = data["items"][attempt]["link"]
            image_data = requests.get(image_url).content
            image_type = get_image_type(image_data)

            valid_image_types = ["jpeg", "png", "jpg"]
            if image_type not in valid_image_types:
                print(f"Invalid image downloaded, retrying... ({attempt + 1}/3)")
                continue

            image_filename = f"{card_id}.{image_type}"
            filepath = os.path.join(media_folder, image_filename)

            with open(filepath, "wb") as f:
                f.write(image_data)

            if is_valid_image(filepath):
                # Update the Anki card to reference the image by its filename
                field_data = f'<img src="{image_filename}">'
                params = {
                    "note": {"id": card_id, "fields": {image_field_name: field_data}}
                }
                from anki_patcher.patcher.anki import invoke

                invoke("updateNoteFields", params)
                print(f"Added image to card {card_id}")
                break
            else:
                print(f"Invalid image downloaded, retrying... ({attempt + 1}/3)")
                if attempt == MAX_IMAGE_RETRIES - 1:
                    print("Failed to download a valid image after 3 attempts")
    except Exception as e:
        print(f"Error downloading image: {e}")
        return
