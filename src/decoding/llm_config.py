import os

# Model config
MODEL_NAME = "gpt-4"
TEMPERATURE_DECODE = 0.5
TEMPERATURE_COPILOT = 0.7

# Decoding prompt file path 
DECODING_PROMPT_TEMPLATE = os.path.join("src", "decoding", "prompts", "bio_decoder_prompt.j2")
USER_BIO_PATH = os.path.join("data", "user_bio", "my_bio.txt")

# Co-pilot prompt
COPILOT_PROMPT_TEMPLATE = os.path.join("src", "decoding", "prompts", "copilot_comment_prompt.j2")

# Safety
MAX_RETRIES = 2
DEBUG_MODE = True
