import json
import pprint
from src.decoding.agent import DecodingAgent

# Load a test bio
with open("data/merged_bios/Mill_merged.json") as f:
    bio_data = json.load(f)

# Extract the user's bio dict
target_bio = bio_data["Mill"]

# Run agent
agent = DecodingAgent(copilot_mode=True)
result = agent.run(target_bio, username="Mill")
if "saved_to" in result:
    print(f"\n✅ Decoded bio saved to: {result['saved_to']}")


print("\n🔍 Agent Output:\n")
pprint.pprint(result, sort_dicts=False)
