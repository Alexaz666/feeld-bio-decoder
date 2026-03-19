import os
import json
from PIL import Image
import pytesseract

def extract_text_from_files(file_paths, user: str = "uploaded_user"):
    """
    Unified OCR extractor for one or more image files.
    - file_paths: string or list of image paths (local or temporary uploads)
    - user: optional user/session name
    Returns: list of {chunk_id, text} dicts
    """
    if isinstance(file_paths, str):
        file_paths = [file_paths]  # normalize single input

    bio_chunks = []
    for i, path in enumerate(sorted(file_paths)):
        if not path.lower().endswith((".png", ".jpg", ".jpeg")):
            continue
        try:
            with Image.open(path) as image:
                text = pytesseract.image_to_string(image).strip()
        except Exception as e:
            print(f"[!] Could not process {path}: {e}")
            continue

        if text:
            chunk_id = f"{user}_img_{str(i).zfill(2)}"
            bio_chunks.append({"chunk_id": chunk_id, "text": text})

    return bio_chunks


def extract_text_from_folder(user, folder_path):
    image_paths = [
        os.path.join(folder_path, f)
        for f in sorted(os.listdir(folder_path))
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]
    return extract_text_from_files(image_paths, user)


def save_chunks_to_json(chunks, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)


# Example usage
if __name__ == "__main__":
    user = "Brady"
    folder = f"data/raw_images/{user}/"
    output = f"data/extracted_text/{user}.json"

    os.makedirs(os.path.dirname(output), exist_ok=True)
    text_chunks = extract_text_from_folder(user, folder)
    save_chunks_to_json({user: text_chunks}, output)
    print(f"Extracted {len(text_chunks)} chunks for {user}")
