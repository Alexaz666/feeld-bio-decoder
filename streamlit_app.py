import streamlit as st
import os
import tempfile
from src.pipeline.ocr_pipeline import run_ocr_pipeline
from src.decoding.agent import DecodingAgent
from src.decoding.red_flags import flag_red_phrases

st.title("📖 Dating App Bio Decoder")
st.markdown("Upload a screenshot of a dating profile to decode it.")

# === Choose mode ===
mode = st.radio(
    "Choose decoding mode:",
    ["Basic", "Bestie"],
    help="Basic: Just decode the profile.\nBestie: Check for red flags before decoding and give advice."
)
copilot_mode = (mode == "Bestie")

# === State containers ===
if "selected_mode" not in st.session_state:
    st.session_state.selected_mode = mode
if "ocr_done" not in st.session_state:
    st.session_state.ocr_done = False
if "merged_bio" not in st.session_state:
    st.session_state.merged_bio = None
if "decoded_profile" not in st.session_state:
    st.session_state.decoded_profile = None
if "decode_done" not in st.session_state:
    st.session_state.decode_done = False
if "flagged_reason" not in st.session_state:
    st.session_state.flagged_reason = None
if "allow_decode" not in st.session_state:
    st.session_state.allow_decode = True
if "bestie_user_context" not in st.session_state:
    st.session_state.bestie_user_context = ""
if "advisory_result" not in st.session_state:
    st.session_state.advisory_result = None

if st.session_state.selected_mode != mode:
    st.session_state.selected_mode = mode
    st.session_state.flagged_reason = None
    st.session_state.allow_decode = True
    st.session_state.decoded_profile = None
    st.session_state.decode_done = False
    st.session_state.bestie_user_context = ""
    st.session_state.advisory_result = None
    st.session_state.pop("override_choice", None)

# === Upload screenshots ===
uploaded_images = st.file_uploader(
    "Upload profile screenshot(s)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

# === Step 1: Run OCR when user uploads ===
if uploaded_images and st.button("Run OCR"):
    temp_paths = []
    for uploaded_file in uploaded_images:
        suffix = os.path.splitext(uploaded_file.name)[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(uploaded_file.read())
            temp_paths.append(temp_file.name)

    with st.spinner("Running OCR..."):
        merged = run_ocr_pipeline(file_paths=temp_paths, save_outputs=False)
        st.session_state.merged_bio = merged
        st.session_state.ocr_done = True
        st.session_state.decoded_profile = None
        st.session_state.decode_done = False
        st.session_state.bestie_user_context = ""
        st.session_state.advisory_result = None

# === Step 2: Worthiness check (Co-Pilot only) ===
if st.session_state.ocr_done and st.session_state.merged_bio:
    bio_dict = st.session_state.merged_bio["uploaded_user"]
    bio_text = bio_dict.get("merged_text", "").strip()

    st.session_state.flagged_reason = None
    st.session_state.allow_decode = True

    if copilot_mode:
        flagged = flag_red_phrases(bio_text)
        if not bio_text or len(bio_text) < 30:
            st.session_state.flagged_reason = "Bio too short or empty."
        elif flagged:
            phrase = flagged[0]
            st.session_state.flagged_reason = f"Red flag ({phrase['type']}): '{phrase['phrase']}' found in bio."

        if st.session_state.flagged_reason:
            st.warning(f"🚩 {st.session_state.flagged_reason}")

            st.session_state.override_choice = st.radio(
                "Do you want to decode this bio anyway?",
                ["Yes", "No"],
                index=1 if "override_choice" not in st.session_state else ["Yes", "No"].index(st.session_state.get("override_choice", "No"))
            )
            st.session_state.allow_decode = (st.session_state.override_choice == "Yes")

# === Step 3: Decode if allowed ===
if st.session_state.ocr_done:
    if st.session_state.flagged_reason and not st.session_state.allow_decode:
        st.info("Decoding skipped.")
    else:
        if st.button("Continue to Decode"):
            with st.spinner("Decoding profile..."):
                agent = DecodingAgent(
                    copilot_mode=copilot_mode,
                    web_mode=True
                )
                result = agent.run(
                    bio_dict=st.session_state.merged_bio["uploaded_user"],
                    username="uploaded_user"
                )
                st.session_state.decoded_profile = result
                st.session_state.decode_done = True
                st.session_state.advisory_result = None

if st.session_state.decode_done and st.session_state.decoded_profile:
    st.subheader("🧠 Decoded Profile")
    st.json(st.session_state.decoded_profile)

    if copilot_mode:
        st.subheader("💬 Bestie Stage 2")
        st.markdown("Add your own context below before generating any advisory output.")
        st.text_area(
            "Your context",
            key="bestie_user_context",
            placeholder="Paste your bio or describe your dating intentions, relationship style, communication style, and what you're looking for."
        )
        if not st.session_state.bestie_user_context.strip():
            st.info("Your context will be required before Bestie advice can be generated.")
