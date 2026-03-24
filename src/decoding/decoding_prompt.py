import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from jinja2 import Template
from collections import OrderedDict
from src.decoding.llm_config import MODEL_NAME, TEMPERATURE_DECODE, DECODING_PROMPT_TEMPLATE

load_dotenv()
client = OpenAI()

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


def call_full_prompt(bio_dict):
    """
    Renders the decoding prompt and sends it to the LLM.
    bio_dict: single bio entry (dict)
    """
    fields = extract_bio_fields(bio_dict)

    with open(DECODING_PROMPT_TEMPLATE, "r") as f:
        template = Template(f.read())

    prompt = template.render(**fields)

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
