from src.decoding.decoding_prompt import call_full_prompt
from src.decoding.decoding_utils import save_decoded_bio


class DecodingAgent:
    """
    Runs the shared profile decoding step.
    """

    def __init__(self, copilot_mode: bool = False, user_bio: str | None = None, web_mode: bool = False):
        self.copilot_mode = copilot_mode
        self.web_mode = web_mode

    # === Main entry ===
    def run(self, bio_dict: dict, username: str) -> dict:
        """
        Processes a single candidate bio through the shared decode step.
        """
        decoded = self.decode_bio(bio_dict)
        saved_output = save_decoded_bio(
            username=username,
            decoded_bio=decoded,
            save_to_disk=not self.web_mode
        )
        if isinstance(saved_output, str):
            decoded["saved_to"] = saved_output

        return decoded

    def decode_bio(self, bio_dict: dict) -> dict:
        return call_full_prompt(bio_dict)
