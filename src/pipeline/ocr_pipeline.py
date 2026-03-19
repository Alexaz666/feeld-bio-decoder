import os
import json
from src.OCR.ocr_extractor import extract_text_from_files, extract_text_from_folder, save_chunks_to_json
from src.OCR.text_cleaning import process_chunks_dict
from src.OCR.text_deduping import build_merged_dict_from_cleaned

def run_ocr_pipeline(user: str = None, file_paths=None, save_outputs: bool = True):
    """
    Runs the full OCR → cleaning → deduping pipeline.
    Supports both batch mode (from folders) and in-memory mode (from uploads).

    Args:
        user (str): Username or session identifier. Optional for web uploads.
        file_paths (str | list): Image path(s). Optional for batch mode.
        save_outputs (bool): Whether to save intermediate JSONs to disk.
    
    Returns:
        dict: Merged bio JSON (in memory).
    """

    # === Step 1: OCR Extraction ===
    if file_paths:
        chunks = extract_text_from_files(file_paths, user or "uploaded_user")
    else:
        raw_image_folder = f"data/raw_images/{user}"
        chunks = extract_text_from_folder(user, raw_image_folder)

    ocr_data = {user or "uploaded_user": chunks}

    if save_outputs and user:
        ocr_output_path = f"data/extracted_text/{user}.json"
        save_chunks_to_json(ocr_data, ocr_output_path)

    # === Step 2: Text Cleaning ===
    cleaned_data = process_chunks_dict(ocr_data)

    if save_outputs and user:
        cleaned_output_path = f"data/cleaned_text/{user}_cleaned.json"
        os.makedirs(os.path.dirname(cleaned_output_path), exist_ok=True)
        with open(cleaned_output_path, "w", encoding="utf-8") as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

    # === Step 3: De-duplication & Merging ===
    merged_json = build_merged_dict_from_cleaned(cleaned_data)

    if save_outputs and user:
        merged_output_path = f"data/merged_bios/{user}_merged.json"
        os.makedirs(os.path.dirname(merged_output_path), exist_ok=True)
        with open(merged_output_path, "w", encoding="utf-8") as f:
            json.dump(merged_json, f, ensure_ascii=False, indent=2)
        print(f"[✓] Merged bio saved to: {merged_output_path}")

    return merged_json
