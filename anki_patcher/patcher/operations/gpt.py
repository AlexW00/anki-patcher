import os
import openai

from anki_patcher.util import parse_config
from anki_patcher.patcher.anki import invoke


def execute(card_id, fields, config):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    # Parse configurations
    model_type = config.get('model_type', 'gpt-3.5-turbo')
    max_tokens = config.get('max_tokens', 150)
    temperature = config.get('temperature', 0.7)
    top_p = config.get('top_p', 1)
    frequency_penalty = config.get('frequency_penalty', 0)
    presence_penalty = config.get('presence_penalty', 0)
    stop = config.get('stop', '')

    [prompt_template, input_field_names, output_field_name, do_overwrite_output] = parse_config(["prompt_template", "input_field_names", "output_field_name", "do_overwrite_output"], config)
    
    # check if it already has an output
    if not do_overwrite_output:
        existing_output = fields[output_field_name].get("value")
        if existing_output:
            print(f"Skipping card {card_id} as it already has an output")
            return

    # Parse input fields to a dictionary
    input_field_values = {}
    for input_field_name in input_field_names:
        if not input_field_name in fields:
            raise Exception(f"Field {input_field_name} must be set")
        
        input_field_values[input_field_name] = fields[input_field_name].get("value")

    prompt = prompt_template.format(**input_field_values)


    # via chat
    messages = []
    initial_message = {
        "role": "user",
        "content": prompt
    }
    messages.append(initial_message)
    
    options = {
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "frequency_penalty": frequency_penalty,
        "presence_penalty": presence_penalty,
        "stop": stop,
        "stream": False,
        "messages": messages,
        "model": model_type,
    }
    try:
        response = openai.ChatCompletion.create(**options)
        text = response['choices'][0]['message']['content']

        params = {
            "note": {
                "id": card_id,
                "fields": {output_field_name: text}
            }
        }
        invoke("updateNoteFields", params)
        print(f"Added generated text to card {card_id}")
    except Exception as e:
        print(f"Failed to generate text: {e}")


