# Feeld Bio Decoder

An AI pipeline that extracts text from dating profile screenshots and uses LLM reasoning to infer relationship intent, personality signals, and potential compatibility indicators.

## Motivation

As someone who sometimes finds implicit social signals difficult to interpret, I built this tool to experiment with whether LLMs can help decode dating profiles into structured, interpretable information.

The goal is not to automate dating decisions, but to explore:

- How LLMs handle ambiguous social language
- How structured inference can be built on top of messy text data
- How agent-style control flows can improve reliability and cost efficiency

## Architecture
Pipeline:
1. Read screenshots of dating profiles
2. Extract text via OCR
3. Clean, merge and format extracted bio text
4. Send formatted bio text to an LLM for structured decoding
5. Save decoded output as JSON
6. (Optional Co-pilot Mode that gives user the honest opinion on the potential match)

## Key Features

### OCR Pipeline

- Extracts text from profile screenshots
- Modular design for reuse in other OCR projects

### Text Cleaning & Deduplication

- Removes UI artefacts
- Normalises formatting
- Removes duplicate lines commonly produced by OCR

### Early Filtering Stage (Efficiency + Safety Design)

Before running expensive LLM decoding, the pipeline performs a lightweight filtering stage to detect:

- Red flag language (racism, exclusionary preferences, aggressive sexual framing)
- Strong ideological incompatibility signals
- Extremely low-effort bios (<30 characters)

If triggered:

- Decoding is skipped
- A structured rejection reason is returned
- API cost is avoided

This acts as a control gate similar to decision engines used in risk systems.

### LLM Decoder

If the bio passes filtering, the LLM extracts:

- Dating intention
- Relationship structure
- Communication style
- Personality signals
- Lifestyle indicators
- Compatibility signals
- Green and red flags
- Inferred subtext

Outputs are structured into JSON for downstream processing.

### Co-pilot Mode (Optional Decision Support Layer)

After decoding, users can optionally enable Co-pilot mode.

This compares the target profile against the user's own profile.

Additional outputs include:

- Compatibility score estimate
- Honest interpretation
- Potential friction areas
- Suggested next step advice

This mode is designed as a lightweight decision-support layer rather than a recommendation engine.

## Project Structure

```
│
├── data
│   ├── cleaned_text
│   ├── decoded_bios
│   ├── extracted_text
│   ├── merged_bios
│   ├── model_outputs
│   ├── raw_images
│   └── user_bio
│
├── notebooks
│
├── src
│   ├── decoding
|       ├── prompts
│   ├── ocr
│   └── pipeline
│
├── test
│
├── venv
├── .gitignore
├── README.md
└── requirements.txt
```


## Example Output

Example decoder output:

```json
{
  "dating_intent": "Open to exploration and new experiences, with a focus on emotional intimacy",
  "relationship_structure": [
    "Non-monogamous",
    "Non-escalator"
  ],
  "partner_status": "Unpartnered",
  "kinks": [
    "Rope play",
    "Switch"
  ],
  "communication_style": "Humorous, open, and direct",
  "vibes": "Curious, adaptive, and emotionally available",
  "inferred_subtext": "Open to various experiences but values emotional intimacy and clear communication. Likely prefers meaningful connections over casual encounters.",
  "red_flags": [
    "None"
  ],
  "green_flags": [
    "Values clear communication",
    "Open to negotiation and aftercare",
    "Emphasizes emotional intimacy"
  ],
  "match_score": 8,
  "match_reasoning": "Shares similar values around communication, emotional intimacy, and non-traditional relationship structures. Compatibility may depend on comfort with non-vanilla experiences and willingness to explore."
}
```

### Tech Stack
* Python
* OpenAI API
* OCR (Tesseract / EasyOCR)
* Jinja2 prompt templating
* JSON structured outputs

## Design Decisions
Some notable design choices:
### Early filtering before LLM calls
Reduces cost and improves pipeline efficiency.

### Structured outputs instead of free text
Improves reliability and enables downstream evaluation.

### Modular pipeline design
Allows reuse of OCR and decoding components.

### Rule + LLM hybrid approach
Improves robustness compared to pure prompting.

### Optional decision-support layer
Separates interpretation from recommendation logic.

## Future Improvements
Planned improvements include:
* Evaluation harness for decoder consistency
* Multi-step agent reasoning
* Pattern mining across decoded profiles
* Lightweight UI
* Confidence scoring
* Prompt self-critique loop
* Batch processing mode

## Disclaimer
This project is experimental and intended for educational purposes.
Outputs should not be treated as factual personality assessments.
