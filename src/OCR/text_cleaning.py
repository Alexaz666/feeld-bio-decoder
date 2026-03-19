import os
import json
import re

# === Basic cleaning functions ===

def fix_line_breaks(text):
    return re.sub(r'(?<![\.\?!])\n(?=[a-z])', ' ', text)

def normalise_anchors(text):
    literal_anchors = [
        "LAST SEEN", "Desires", "Interests", "Block or report"
    ]
    
    for anchor in literal_anchors:
        pattern = re.compile(re.escape(anchor), re.IGNORECASE)
        text = pattern.sub(anchor.upper(), text)

    regex_anchors = {
        r"desires\s*@\s*(\d+)\s*shared": r"DESIRES SHARED (\1)", # Keep the number 
        r"@\s*(\d)\s*shared desire": " ", # Only keep once (1 desire)
        r"@\s*(\d+)\s*shared desires": " ", # Only keep once (multiple desires)
        r"\d+\s*km away": "BIO START" 
    }

    for pattern, replacement in regex_anchors.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return text

def basic_clean(text):
    text = re.sub(r'^\d{1,2}:\d{2}$', '', text, flags=re.MULTILINE) # remove timestamp
    text = text.replace('|', 'I') # correct misread letter I 
    text = text.replace('#', '').replace('$', '').replace('¢', '').replace('©', '')
    text = text.replace('GG', '').replace('44', '').replace('4G', '').replace('wt)', '').replace('rm)', '')
    text = text.replace('BLOCK OR REPORT', '')
    text = fix_line_breaks(text) 
    text = normalise_anchors(text)
    text = re.sub(r'\s+', ' ', text) # Normalise whitespace
    return text.strip()

# === Tag extraction ===

def extract_tag_blocks(text):
    desires_block = ""
    interests_block = ""
    num_shared = ""

    desires_index = text.find("DESIRES")
    shared_index = text.find("SHARED")
    interests_index = text.find("INTERESTS")

    shared_pattern = r"SHARED \((\d+)\)"

    if desires_index != -1:
        start = desires_index + len("DESIRES")
        end = interests_index if interests_index != -1 else len(text)
        desires_raw = text[start:end]
        desires_block = re.sub(shared_pattern, "", desires_raw, flags=re.IGNORECASE).strip()

    if shared_index != -1:
        match = re.search(shared_pattern, text)
        if match:
            num_shared = match.group(1)

    if interests_index != -1:
        start = interests_index + len("INTERESTS")
        interests_block = text[start:].strip()

    return desires_block, num_shared, interests_block

# === Main pipeline for one chunk ===

def clean_and_extract_tags(chunk):
    raw_text = chunk.get("text", "")
    chunk_id = chunk.get("chunk_id", "")

    cleaned_text = basic_clean(raw_text)
    desires_block, num_shared, interests_block = extract_tag_blocks(cleaned_text)

    # Remove tag blocks from main cleaned text
    if num_shared:
        cleaned_text = re.sub(r"SHARED \(\d+\)", "", cleaned_text)
    if desires_block:
        cleaned_text = cleaned_text.replace("DESIRES  " + desires_block, "")
    if interests_block:
        cleaned_text = cleaned_text.replace("INTERESTS " + interests_block, "")

    return {
        "chunk_id": chunk_id,
        "cleaned_text": cleaned_text.strip(),
        "desires_raw": desires_block,
        "interests_raw": interests_block,
        "num_shared_desires": num_shared
    }

# === Script entry point ===
def process_chunks_dict(data: dict) -> dict:
    """
    Cleans OCR chunks in-memory.
    - data: {username: [ {chunk_id, text}, ... ] }
    Returns: {username: [ cleaned_chunk_dicts ... ] }
    """
    cleaned_data = {}
    for username, chunks in data.items():
        cleaned_chunks = [clean_and_extract_tags(chunk) for chunk in chunks]
        cleaned_data[username] = cleaned_chunks
    return cleaned_data


def process_json_file(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned_data = process_chunks_dict(data)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

    print(f"[✓] Cleaned data saved to {output_path}")


# === CLI execution ===
if __name__ == "__main__":
    user = "Brady"
    input_file = f"data/extracted_text/{user}.json"
    output_file = f"data/cleaned_text/{user}_cleaned.json"
    process_json_file(input_file, output_file)
