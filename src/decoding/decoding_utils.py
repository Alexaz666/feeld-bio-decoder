import os
import json

def save_decoded_bio(
    username: str,
    decoded_bio: dict,
    output_dir: str = "data/decoded_bios",
    save_to_disk: bool = True
) -> str | dict:
    """
    Saves decoded bio to a JSON file (for CLI/dev) or returns it in-memory (for web).
    
    Args:
        username (str): Name or ID of the profile.
        decoded_bio (dict): Decoded output from the LLM.
        output_dir (str): Directory to save the file.
        save_to_disk (bool): If False, skip saving and return decoded_bio directly.
    
    Returns:
        str | dict: File path if saved, or the decoded_bio itself if in-memory.
    """
    if not save_to_disk:
        # In-memory mode (web app)
        return decoded_bio

    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"{username}_decoded.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(decoded_bio, f, indent=2, ensure_ascii=False)
    return filepath
