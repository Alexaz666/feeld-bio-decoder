import json
from src.decoding.decoding_prompt import call_full_prompt
from src.decoding.decoding_prompt import load_user_bio 

# Load a cleaned/merged bio JSON
with open("data/merged_bios/Kris_merged.json") as f:
    bio_data = json.load(f)

target_bio = bio_data["Kris"]
user_bio = load_user_bio()

# Run decoder
result = call_full_prompt(target_bio, user_bio)

# Show result
print(json.dumps(result, indent=2))
