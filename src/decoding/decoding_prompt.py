import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from jinja2 import Template
from collections import OrderedDict
from src.decoding.llm_config import MODEL_NAME, TEMPERATURE_DECODE, USER_BIO_PATH, DECODING_PROMPT_TEMPLATE

load_dotenv()
client = OpenAI()


def load_user_bio(custom_bio: str = None) -> str:
    """
    Loads the user's own bio for compatibility scoring.
    - If `custom_bio` is provided (from web upload or text input), use that.
    - Otherwise, fall back to loading from USER_BIO_PATH.
    """
    if custom_bio and custom_bio.strip():
        return custom_bio.strip()

    try:
        with open(USER_BIO_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"[!] User bio file not found at {USER_BIO_PATH}. Returning empty string.")
        return ""



def extract_bio_fields(bio_dict: dict) -> dict:
    """
    Extracts and cleans key fields from a bio dictionary.
    Returns a dict with keys: merged_text, desires_raw, interests_raw, num_shared_desires
    """
    return {
        "merged_text": bio_dict.get("merged_text", "").strip(),
        "desires_raw": bio_dict.get("desires_raw", "").strip(),
        "interests_raw": bio_dict.get("interests_raw", "").strip(),
        "num_shared_desires": bio_dict.get("num_shared_desires", "").strip()
    }


def call_full_prompt(bio_dict, user_bio=None):
    """
    Renders the decoding prompt and sends it to the LLM.
    bio_dict: single bio entry (dict)
    user_bio: optional string
    """
    fields = extract_bio_fields(bio_dict)

    with open(DECODING_PROMPT_TEMPLATE, "r") as f:
        template = Template(f.read())

    prompt = template.render(
        **fields,
        user_bio=user_bio
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=TEMPERATURE_DECODE,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    content = response.choices[0].message.content
    try:
        return json.loads(content, object_pairs_hook=OrderedDict)
    except json.JSONDecodeError:
        return {"error": "Could not parse JSON", "raw_output": content}