import requests
from typing import Optional
from config import GEMINI_API_KEY

# Gemini endpoint
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
)

# JSON schemas the model must follow
RECOMMENDATION_SCHEMA = {
    "type": "object",
    "properties": {
        "drug_name": {"type": "string"},     # "Brand (Generic)"
        "dosage": {"type": "string"},        # e.g., "2 tablets (500mg each)"
        "frequency": {"type": "string"},     # e.g., "Every 6 hours as needed"
        "side_effects": {"type": "string"},  # one short sentence
    },
    "required": ["drug_name", "dosage", "frequency", "side_effects"],
}

TRIAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "triage_alert": {"type": "string"},  # e.g., "See a doctor"
        "message": {"type": "string"},       # concise instruction
    },
    "required": ["triage_alert", "message"],
}

# Deterministic generation config
GENERATION_CONFIG = {
    "responseMimeType": "application/json",
    "temperature": 0,
    "topK": 1,
    "topP": 0,
    "candidateCount": 1,
}

# Very strict system prompt to reduce variance and keep responses safe/OTC-only
PROMPT_SYSTEM = """
You are AbsorpGen AI, a cautious U.S. over-the-counter (OTC) medication assistant. SAFETY FIRST.

MANDATORY RULES:
1) If any explicit RED-FLAG symptom exists, return ONLY a TRIAGE object matching TRIAGE_SCHEMA.
2) If symptoms are minor/casual, return ONLY a RECOMMENDATION object matching RECOMMENDATION_SCHEMA.
3) You MUST NOT exceed the provided suggested_single_dose_mg. Do not change it.
4) Use U.S. OTC context only. Do not propose prescription-only drugs.
5) Format drug_name as: "Brand (Generic)". Prefer the first brand listed in preferred_brands_ordered, unless allergy conflicts (if allergies mention a brand/generic, pick the next brand).
6) "dosage" must be a practical instruction (e.g., "2 tablets (500mg each)") without showing calculations.
7) Keep output to a single compact JSON object. No markdown or extra prose.

Return exactly ONE object matching one of the provided schemas.
"""

# User prompt template can include (optionally) the selected OTC details to keep brand/dose stable.
PROMPT_USER_TEMPLATE = """
Patient Profile:
- Age: {age}
- Sex: {sex}
- Height(cm): {height_cm}
- Weight(kg): {weight_kg}
- Symptoms: {symptoms}
- Allergies: {allergies}
- Known Conditions: {conditions}

Selected OTC Context (do not deviate):
- generic: {sel_generic}
- preferred_brands_ordered: {sel_brands}
- typical_unit_mg: {sel_unit}
- single_dose_cap_mg: {sel_cap}

Dosage Constraint:
- suggested_single_dose_mg: {suggested_single_dose_mg}
- cap_reason: {cap_reason}

JSON Schemas (for your reference):
- RECOMMENDATION_SCHEMA = {rec_schema}
- TRIAGE_SCHEMA = {triage_schema}
"""

def ask_gemini(payload_text: str) -> Optional[str]:
    """
    Calls Gemini with strict, deterministic settings.
    Returns the model's raw JSON string (or None on error).
    NOTE: The caller should parse/validate JSON, and never trust the model blindly.
    """
    data = {
        "contents": [
            {"role": "user", "parts": [{"text": PROMPT_SYSTEM}]},
            {"role": "user", "parts": [{"text": payload_text}]},
        ],
        "generationConfig": GENERATION_CONFIG,
    }
    try:
        r = requests.post(GEMINI_URL, json=data, timeout=20)
        r.raise_for_status()
        j = r.json()
        return j["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return None
