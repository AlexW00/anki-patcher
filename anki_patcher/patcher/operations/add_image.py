import requests
import base64
from PIL import Image
import io
import timeout_decorator


from anki_patcher.util import parse_config, parse_env, parse_fields, remove_html_tags

MAX_IMAGE_RETRIES = 5


@timeout_decorator.timeout(10)
def execute(card_id, fields, config):
    # load env vars via helper function
    # We store images via AnkiConnect; no need for ANKI_MEDIA_FOLDER
    env = parse_env(["GOOGLE_API_KEY", "CX"])
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


def is_valid_image_bytes(image_data):
    try:
        img = Image.open(io.BytesIO(image_data))
        img.verify()
        return True
    except Exception:
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

    # env: [GOOGLE_API_KEY, CX]
    [google_api_key, cx] = env
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

        items = data["items"]
        total_attempts = min(len(items), MAX_IMAGE_RETRIES)
        for attempt in range(total_attempts):
            image_url = items[attempt]["link"]
            image_resp = requests.get(image_url, timeout=10)
            if image_resp.status_code != 200:
                print(
                    f"Failed to fetch image URL (status {image_resp.status_code}), retrying... ({attempt + 1}/{total_attempts})"
                )
                continue
            image_data = image_resp.content
            image_type = get_image_type(image_data)

            valid_image_types = ["jpeg", "png", "jpg"]
            if image_type not in valid_image_types:
                print(
                    f"Invalid image type, retrying... ({attempt + 1}/{total_attempts})"
                )
                continue

            image_filename = f"{card_id}.{image_type}"
            if is_valid_image_bytes(image_data):
                # Store media in Anki via AnkiConnect to avoid host/container path issues
                from anki_patcher.patcher.anki import invoke

                b64 = base64.b64encode(image_data).decode("utf-8")
                store_params = {"filename": image_filename, "data": b64}
                store_result = invoke("storeMediaFile", store_params)
                if store_result.get("error"):
                    print(f"AnkiConnect error storing media: {store_result['error']}")
                    continue

                # Update the Anki card to reference the image by its filename
                field_data = f'<img src="{image_filename}">'
                update_params = {
                    "note": {"id": card_id, "fields": {image_field_name: field_data}}
                }
                update_result = invoke("updateNoteFields", update_params)
                if update_result.get("error"):
                    print(f"AnkiConnect error updating field: {update_result['error']}")
                    continue
                print(f"Added image to card {card_id}")
                break
            else:
                print(
                    f"Invalid image content, retrying... ({attempt + 1}/{total_attempts})"
                )
                if attempt == total_attempts - 1:
                    print(
                        f"Failed to download a valid image after {total_attempts} attempts"
                    )
    except Exception as e:
        print(f"Error downloading image: {e}")
        return
