from src.decoding.red_flags import flag_red_phrases
from src.decoding.decoding_prompt import load_user_bio, call_full_prompt
from src.decoding.decoding_utils import save_decoded_bio
from src.decoding.copilot import generate_copilot_comment_llm


class DecodingAgent:
    """
    Runs the decoding pipeline in two modes:
      - Basic mode (“Decoder”): straight interpretation, no coaching.
      - Co-Pilot mode (“Dating Coach”): includes worthiness check and commentary.
    """

    def __init__(self, copilot_mode: bool = False, user_bio: str | None = None, web_mode: bool = False):
        self.copilot_mode = copilot_mode
        self.web_mode = web_mode
        self.user_bio = load_user_bio(custom_bio=user_bio)

    # === Main entry ===
    def run(self, bio_dict: dict, username: str) -> dict:
        """
        Processes a single candidate bio based on selected mode.
        """
        bio_text = bio_dict.get("merged_text", "").strip()

        # --- BASIC MODE: straight decoding ---
        if not self.copilot_mode:
            decoded = self.decode_bio(bio_dict)
            saved_output = save_decoded_bio(
                username=username,
                decoded_bio=decoded,
                save_to_disk=not self.web_mode
            )
            if isinstance(saved_output, str):
                decoded["saved_to"] = saved_output
            return decoded

        # --- CO-PILOT MODE: worthiness + optional reflection ---
        is_worthy, reason = self.assess_worthiness(bio_text)
        if not is_worthy:
            if not self.confirm_proceed(reason):
                return {"status": "skipped", "reason": reason}

        decoded = self.decode_bio(bio_dict)
        saved_output = save_decoded_bio(
            username=username,
            decoded_bio=decoded,
            save_to_disk=not self.web_mode
        )
        if isinstance(saved_output, str):
            decoded["saved_to"] = saved_output

        if not self.web_mode:
            wants_input = input("\n🧠 Want my honest take before you act? (y/n): ").strip().lower()
            if wants_input == "y":
                reflection = input("What are you feeling about this match? (optional): ").strip()
                decoded["commentary"] = generate_copilot_comment_llm(
                    decoded_bio=decoded,
                    user_bio=self.user_bio,
                    user_reflection=reflection
                )

        return decoded


    # === Support methods ===
    def assess_worthiness(self, text: str) -> tuple[bool, str]:
        if not text or len(text.strip()) < 30:
            return False, "Bio too short or empty."

        red_phrases = flag_red_phrases(text)
        if red_phrases:
            flag = red_phrases[0]
            reason = f"Red flag ({flag['type']}): '{flag['phrase']}' found in bio."
            return False, reason

        return True, ""

    def confirm_proceed(self, reason: str) -> bool:
        if self.web_mode:
            # Skip interactive prompt in Streamlit; it’s handled in the UI
            return True
        print(f"\n⚠️ Worthiness check failed: {reason}")
        choice = input("Do you still want to decode this bio? (y/n): ").strip().lower()
        return choice == "y"

    def decode_bio(self, bio_dict: dict) -> dict:
        return call_full_prompt(bio_dict, user_bio=self.user_bio)