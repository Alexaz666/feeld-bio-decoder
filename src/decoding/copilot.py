from openai import OpenAI
from jinja2 import Template
from src.decoding.llm_config import MODEL_NAME, TEMPERATURE_COPILOT, COPILOT_PROMPT_TEMPLATE

client = OpenAI()

def generate_copilot_comment_llm(decoded_bio, user_bio=None, user_reflection=None):
    with open(COPILOT_PROMPT_TEMPLATE, "r") as f:
        template = Template(f.read())

    prompt = template.render(
        decoded_bio=decoded_bio,
        user_bio=user_bio,
        user_reflection=user_reflection
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=TEMPERATURE_COPILOT,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()