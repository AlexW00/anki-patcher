import os
import openai

from anki_patcher.util import parse_config
from anki_patcher.patcher.anki import invoke
import timeout_decorator


@timeout_decorator.timeout(10)
def execute(card_id, fields, config):
    # Configure OpenAI-compatible client to use OpenRouter by default
    # Env precedence: OPENROUTER_API_KEY > OPENAI_API_KEY (for backward compatibility)
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise Exception(
            "Missing API key. Set OPENROUTER_API_KEY (preferred) or OPENAI_API_KEY."
        )

    # Allow override via env; default to OpenRouter's OpenAI-compatible endpoint
    openai.api_base = os.getenv("OPENAI_API_BASE", "https://openrouter.ai/api/v1")
    openai.api_key = api_key

    # Parse configurations
    model_type = config.get("model_type", "gpt-4o")
    max_tokens = config.get("max_tokens", 500)
    temperature = config.get("temperature", 0.7)
    top_p = config.get("top_p", 1)
    frequency_penalty = config.get("frequency_penalty", 0)
    presence_penalty = config.get("presence_penalty", 0)
    stop = config.get("stop", "")

    [prompt_template, input_field_names, output_field_name, do_overwrite_output] = (
        parse_config(
            [
                "prompt_template",
                "input_field_names",
                "output_field_name",
                "do_overwrite_output",
            ],
            config,
        )
    )

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
    initial_message = {"role": "user", "content": prompt}
    messages.append(initial_message)

    # Map model name to OpenRouter format if needed (prefix vendor when missing)
    def _to_openrouter_model(name: str) -> str:
        if "/" in name:
            return name
        # Heuristic: OpenAI family models (gpt-*, o3, o4-*)
        lower = name.lower()
        if lower.startswith("gpt") or lower.startswith("o"):
            return f"openai/{name}"
        return name

    options = {
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "frequency_penalty": frequency_penalty,
        "presence_penalty": presence_penalty,
        "stop": stop,
        "stream": False,
        "messages": messages,
        "model": _to_openrouter_model(model_type),
    }
    try:
        response = openai.ChatCompletion.create(**options)
        text = response["choices"][0]["message"]["content"]

        params = {"note": {"id": card_id, "fields": {output_field_name: text}}}
        invoke("updateNoteFields", params)
        print(f"Added generated text to card {card_id}")
    except Exception as e:
        print(f"Failed to generate text: {e}")
