import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pipeline.ocr_pipeline import run_ocr_pipeline

if __name__ == "__main__":
    # Replace "Kris" with any test folder name under data/raw_images/
    user = "Kris"
    result = run_ocr_pipeline(user)
    print("[✓] OCR pipeline completed.")
    print(result)
