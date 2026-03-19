import sys, os, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.OCR.ocr_extractor import extract_text_from_files
from src.OCR.text_cleaning import process_chunks_dict
from src.OCR.text_deduping import build_merged_dict_from_cleaned
from src.pipeline.ocr_pipeline import run_ocr_pipeline
from src.decoding.agent import DecodingAgent


if __name__ == "__main__":
    # === 1️⃣ Choose a few sample screenshots ===
    # These should already live under data/raw_images/<user>
    user = "Stefan"
    test_files = [
        f"data/raw_images/{user}/image01.jpg",
        f"data/raw_images/{user}/image02.jpg"
    ]

    # === 2️⃣ Step-by-step test (optional, for understanding) ===
    print("\n--- STEP 1: OCR extraction ---")
    chunks = extract_text_from_files(test_files, user)
    print(json.dumps(chunks[:1], indent=2))  # show first chunk only

    print("\n--- STEP 2: Cleaning ---")
    cleaned = process_chunks_dict({user: chunks})
    print(json.dumps(cleaned[user][:1], indent=2))

    print("\n--- STEP 3: Deduping ---")
    merged = build_merged_dict_from_cleaned(cleaned)
    print(json.dumps(merged, indent=2))

    # === 3️⃣ Full pipeline in one call (compare results) ===
    print("\n--- FULL PIPELINE ---")
    merged_pipeline = run_ocr_pipeline(file_paths=test_files, save_outputs=False)
    print(json.dumps(merged_pipeline, indent=2))

    # === 4️⃣ Run the decoding agent ===
    print("\n--- DECODING (Basic Mode) ---")
    agent = DecodingAgent(copilot_mode=False, web_mode=True)
    decoded = agent.run(
        bio_dict=merged_pipeline["uploaded_user"],
        username="uploaded_user"
    )
    print(json.dumps(decoded, indent=2, ensure_ascii=False))

    print("\n--- DECODING (Copilot Mode) ---")
    agent_copilot = DecodingAgent(copilot_mode=True, web_mode=True)
    decoded_copilot = agent_copilot.run(
        bio_dict=merged_pipeline["uploaded_user"],
        username="uploaded_user"
    )
    print(json.dumps(decoded_copilot, indent=2, ensure_ascii=False))
