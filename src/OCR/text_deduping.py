import os
import json
from typing import List

# === Core deduplication logic ===

def find_token_overlap(tokens_a: List[str], tokens_b: List[str], max_n: int = 25) -> int:
    """
    Returns the length of the longest overlap between two text chunks
    """
    max_overlap = 0
    for i in range(1, max_n + 1):
        if tokens_a[-i:] == tokens_b[:i]:
            max_overlap = i
    return max_overlap


def dedupe_tokens_by_overlap(text_chunks: List[str], max_token_window: int = 25) -> List[str]:
    """
    Given a list of cleaned_text chunks, deduplicate them based on the length of token overlap.
    Returns a single merged token list.
    """
    merged_tokens = []
    for idx, text in enumerate(text_chunks):
        tokens = text.strip().split() # tokenise cleand_text chunks
        if idx == 0: #idx 0 => first chunk, take as is
            merged_tokens.extend(tokens)
        else:
            prev_tail = merged_tokens[-max_token_window:] # last 25 tokens of prev chunk
            curr_head = tokens[:max_token_window]         # first 25 tokens of the current chunk
            overlap = find_token_overlap(prev_tail, curr_head, max_n=max_token_window) # identify overlap
            merged_tokens.extend(tokens[overlap:])        # append current text to prev. after removing overlap
    return merged_tokens


# === Wrapper to handle I/O and structure ===
def build_merged_dict_from_cleaned(data: dict, max_token_window: int = 25) -> dict:
    """
    Deduplicates and merges cleaned text chunks held in memory.
    - data: {username: [ {cleaned_text, desires_raw, ...}, ... ] }
    Returns: {username: {merged_text, desires_raw, interests_raw, num_shared_desires}}
    """
    username = next(iter(data))
    chunks = data[username]
    cleaned_texts = [chunk["cleaned_text"].strip() for chunk in chunks]

    merged_tokens = dedupe_tokens_by_overlap(cleaned_texts, max_token_window)
    last_chunk = chunks[-1]

    merged_json = {
        username: {
            "merged_text": " ".join(merged_tokens),
            "desires_raw": last_chunk.get("desires_raw", ""),
            "interests_raw": last_chunk.get("interests_raw", ""),
            "num_shared_desires": last_chunk.get("num_shared_desires", "")
        }
    }
    return merged_json


def build_merged_json_from_cleaned(json_path: str, output_path: str, max_token_window: int = 25):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    merged_json = build_merged_dict_from_cleaned(data, max_token_window)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged_json, f, ensure_ascii=False, indent=2)

    print(f"[✓] Merged file saved to {output_path}")
    return merged_json


# === CLI execution ===
if __name__ == "__main__":
    user = "Brady"
    input_file = f"data/cleaned_text/{user}_cleaned.json"
    output_file = f"data/merged_bios/{user}_merged.json"
    build_merged_json_from_cleaned(input_file, output_file)

