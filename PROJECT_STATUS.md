**Change Requirement**
1. Mode selection should appear before any mode-specific inputs.

2. Basic mode flow should be:
   - screenshot upload
   - OCR
   - shared profile decode
   - structured decoded output only
   - no user bio input
   - no advisory layer

3. Bestie mode should use a progressive two-stage flow:

   Stage 1 (same as Basic plus red-flag detection):
   - screenshot upload
   - OCR
   - shared profile decode
   - red-flag detection with override
   - display decoded profile

   Stage 2 (Bestie advisory step):
   - AFTER the decoded profile is shown, prompt the user for their own context (pasting their own bio, or describing their dating intentions, relationship style, communication style, etc. in the provided text box)
   - This input should be required before generating advisory output
   - After user context is provided, generate a separate advisory section containing:
     - match_score
     - match_reasoning
     - commentary / "honest take"

4. The base decoding prompt should be shared by both modes and should focus only on interpreting the target profile, and no longer include match_score or match_reasoning as output. 

5. Bestie advisory should be generated in a second step from:
   - decoded profile (from Stage 1)
   - user context (from Stage 2)

6. The UI should reflect this separation clearly:
   - Basic shows only decoded profile.
   - Bestie shows decoded profile first, then an optional advisory section generated after user input.

Given these decisions, create a safe incremental implementation plan.

For each step, specify:
- goal
- files to change
- files that should remain untouched
- risks
- how to manually test before moving on

Important constraints:
- Do not redesign the OCR pipeline.
- Keep the base decode pipeline shared.
- Prefer small, incremental changes over large rewrites.
- Do not modify files yet.


**Change Implementation Plan**

**Step 1**
Status: Done.
Goal: make the base decode contract shared and profile-only by removing `match_score` and `match_reasoning` from the base decode prompt.

Files to change:
- [src/decoding/prompts/bio_decoder_prompt.j2](/Users/alexis/Desktop/Learning/Projects/202508_bio_decoder/src/decoding/prompts/bio_decoder_prompt.j2)

Files that should remain untouched:
- [src/decoding/decoding_prompt.py](/Users/alexis/Desktop/Learning/Projects/202508_bio_decoder/src/decoding/decoding_prompt.py)
- [src/decoding/agent.py](/Users/alexis/Desktop/Learning/Projects/202508_bio_decoder/src/decoding/agent.py)
- [streamlit_app.py](/Users/alexis/Desktop/Learning/Projects/202508_bio_decoder/streamlit_app.py)
- OCR pipeline files

Risks:
- Existing sample expectations may still assume compatibility fields are in the decoded JSON.
- Later Bestie work must provide compatibility separately.

How to manually test before moving on:
- Run Basic mode on one sample.
- Confirm decode succeeds and no longer includes `match_score` or `match_reasoning`.
- Confirm no code path crashes because those keys are absent.

**Step 2**
Stauts: Done.
Goal: move mode selection to the top and make mode-specific UI conditional from the start.

Files to change:
- [streamlit_app.py](/Users/alexis/Desktop/Learning/Projects/202508_bio_decoder/streamlit_app.py)

Files that should remain untouched:
- [src/decoding/agent.py](/Users/alexis/Desktop/Learning/Projects/202508_bio_decoder/src/decoding/agent.py)
- OCR pipeline files
- prompt files

Risks:
- Session-state leakage when switching modes.
- Old Stage 2 UI remnants appearing in Basic mode.

Session-state requirements:
- Introduce or formalize `selected_mode`.
- On mode change, clear:
  `flagged_reason`, `allow_decode`, `decode_done`, `decoded_profile`, `bestie_user_context`, `advisory_result`.

How to manually test before moving on:
- Toggle between Basic and Bestie before upload.
- Confirm only mode-appropriate inputs appear.
- Confirm switching modes clears stale Bestie outputs.

**Step 3**
Status: Done.
Goal: implement Bestie Stage 1 as “Basic plus red-flag detection and override,” ending with decoded profile display only.

Files to change:
- [streamlit_app.py](/Users/alexis/Desktop/Learning/Projects/202508_bio_decoder/streamlit_app.py)

Files that should remain untouched:
- OCR pipeline files
- [src/decoding/prompts/bio_decoder_prompt.j2](/Users/alexis/Desktop/Learning/Projects/202508_bio_decoder/src/decoding/prompts/bio_decoder_prompt.j2)
- [src/decoding/copilot.py](/Users/alexis/Desktop/Learning/Projects/202508_bio_decoder/src/decoding/copilot.py)
- [src/decoding/prompts/copilot_comment_prompt.j2](/Users/alexis/Desktop/Learning/Projects/202508_bio_decoder/src/decoding/prompts/copilot_comment_prompt.j2)

Files that may need later adjustment but should ideally stay untouched in this step:
- [src/decoding/agent.py](/Users/alexis/Desktop/Learning/Projects/202508_bio_decoder/src/decoding/agent.py)

Risks:
- Current agent web behavior may still try to attach commentary until later cleanup.
- Decode/advisory separation may be temporarily messy if not staged carefully.

Session-state requirements:
- Persist `merged_bio`, `flagged_reason`, `allow_decode`, `decoded_profile`, `decode_done`.
- On any new OCR run, clear:
  `decoded_profile`, `decode_done`, `bestie_user_context`, `advisory_result`.

How to manually test before moving on:
- Bestie non-flagged profile: decode and show profile only.
- Bestie flagged profile: warning, override, then decode and show profile only.
- Confirm Stage 1 does not require user context yet.

**Step 4**
Status: done.
Goal: introduce Stage 2 UI for Bestie after Stage 1 decode completes.

Files to change:
- [streamlit_app.py](/Users/alexis/Desktop/Learning/Projects/202508_bio_decoder/streamlit_app.py)

Files that should remain untouched:
- OCR pipeline files
- [src/decoding/agent.py](/Users/alexis/Desktop/Learning/Projects/202508_bio_decoder/src/decoding/agent.py)
- both prompt files
- [src/decoding/copilot.py](/Users/alexis/Desktop/Learning/Projects/202508_bio_decoder/src/decoding/copilot.py)

Risks:
- Showing Stage 2 too early.
- Letting users generate advisory without a finished decode.

Session-state requirements:
- Show Stage 2 controls only if `decode_done` is true and `decoded_profile` exists.
- Store text in `bestie_user_context`.
- Do not generate advisory unless `bestie_user_context.strip()` is non-empty.

How to manually test before moving on:
- Decode in Bestie mode and confirm the user-context box appears only afterward.
- Confirm advisory cannot be generated without entering context.
- Confirm Basic mode still never shows Stage 2 UI.

**Step 5**
Status: in progress. 
Goal: implement the dedicated Bestie advisory generation step using only the already computed decoded profile plus user context.

Files to change:
- [src/decoding/copilot.py](/Users/alexis/Desktop/Learning/Projects/202508_bio_decoder/src/decoding/copilot.py)
- [src/decoding/prompts/copilot_comment_prompt.j2](/Users/alexis/Desktop/Learning/Projects/202508_bio_decoder/src/decoding/prompts/copilot_comment_prompt.j2)
- possibly [streamlit_app.py](/Users/alexis/Desktop/Learning/Projects/202508_bio_decoder/streamlit_app.py) for wiring

Files that should remain untouched:
- OCR pipeline files
- [src/decoding/prompts/bio_decoder_prompt.j2](/Users/alexis/Desktop/Learning/Projects/202508_bio_decoder/src/decoding/prompts/bio_decoder_prompt.j2)
- [src/decoding/decoding_prompt.py](/Users/alexis/Desktop/Learning/Projects/202508_bio_decoder/src/decoding/decoding_prompt.py)

Critical rule:
- Stage 2 must reuse `decoded_profile` already in session state.
- It must not call OCR or base decoding again.

Risks:
- Advisory prompt may need to return structured data plus prose cleanly.
- If advisory output shape is inconsistent, UI rendering gets awkward.

Session-state requirements:
- Advisory generation reads:
  `decoded_profile`
  `bestie_user_context`
- Advisory generation writes:
  `advisory_result`
- If `decoded_profile` or `bestie_user_context` changes, invalidate `advisory_result`.

How to manually test before moving on:
- Generate advisory once.
- Change only the user-context text and regenerate.
- Confirm OCR and base decode are not rerun, and only advisory changes.

**Step 6**

Goal: clean up the agent so it owns shared decode behavior only and no longer auto-generates Bestie web commentary during Stage 1.

Files to change:
- [src/decoding/agent.py](/Users/alexis/Desktop/Learning/Projects/202508_bio_decoder/src/decoding/agent.py)

Files that should remain untouched:
- OCR pipeline files
- [src/decoding/prompts/bio_decoder_prompt.j2](/Users/alexis/Desktop/Learning/Projects/202508_bio_decoder/src/decoding/prompts/bio_decoder_prompt.j2)

Risks:
- CLI co-pilot behavior may diverge from web behavior if not handled carefully.
- Temporary duplication between UI logic and agent logic if this cleanup is delayed too long.

How to manually test before moving on:
- Bestie Stage 1 decode should produce only decoded profile.
- Bestie Stage 2 should still generate advisory separately.
- Basic mode should remain unchanged.

**Step 7**

Goal: finalize clean rendering and stale-state prevention in Streamlit.

Files to change:
- [streamlit_app.py](/Users/alexis/Desktop/Learning/Projects/202508_bio_decoder/streamlit_app.py)

Files that should remain untouched:
- OCR pipeline files
- shared prompt files unless a bug is found

Session-state rules to enforce here:
- On mode change, clear Bestie-only state.
- On new profile or OCR rerun, clear decode and advisory state.
- On decode rerun, clear advisory state.
- On advisory rerun, do not touch OCR or decode state.

Risks:
- Most likely issue is stale `advisory_result` hanging around after profile/mode change.

How to manually test before moving on:
- Bestie: decode profile A, generate advisory, then upload profile B.
- Confirm old advisory disappears.
- Switch to Basic and confirm no Bestie advisory remains.
- Return to Bestie and confirm Stage 2 starts fresh.

**Step 8**

Goal: full regression pass of the intended product behavior.

Files to change:
- none unless a small follow-up fix is needed

Files that should remain untouched:
- OCR pipeline files
- shared decode contract unless bugs are found

How to manually test before moving on:
- Basic happy path.
- Bestie non-flagged path.
- Bestie flagged-with-override path.
- Bestie with missing user context.
- Advisory regeneration with changed user context only.
- Confirm Stage 2 never reruns OCR or base decode.
- Confirm decoded profile never includes advisory fields.

If you want, I can next turn this into a concrete edit sequence for just the first 2 implementation steps, keeping the blast radius very small.