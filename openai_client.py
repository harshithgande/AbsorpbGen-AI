import os
import json
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI
_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

MEDICATION_SCHEMA = {
    "type": "object",
    "properties": {
        "triage": {
            "type": "object",
            "properties": {
                "red_flag": {"type": "boolean"},
                "level": {"type": "string"},      # "none" | "medium" | "red"
                "reason": {"type": "string"},
                "advice": {"type": "string"}
            },
            "required": ["red_flag", "level", "reason"]
        },
        "selected_medication": {
            "type": "object",
            "properties": {
                "drug_key": {"type": "string"},   # or "none"
                "brand": {"type": "string"},      # or "none"
                "generic": {"type": "string"},    # or "none"
                "reasoning": {"type": "string"},
                "safety_notes": {"type": "string"}
            },
            "required": ["drug_key", "brand", "generic", "reasoning"]
        },
        "dosing": {
            "type": "object",
            "properties": {
                "dose_text": {"type": "string"},  # "-" if none
                "frequency": {"type": "string"},  # "-" if none
                "total_mg": {"type": "number"},   # 0 if none
                "max_daily_mg": {"type": "number"},
                "dose_rationale": {"type": "string"}
            },
            "required": ["dose_text", "frequency", "total_mg"]
        },
        "alternatives": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "drug_key": {"type": "string"},
                    "brand": {"type": "string"},
                    "generic": {"type": "string"},
                    "reason": {"type": "string"},
                    "when_to_consider": {"type": "string"}
                }
            }
        },
        "patient_education": {
            "type": "object",
            "properties": {
                "key_points": {"type": "array", "items": {"type": "string"}},
                "warnings": {"type": "array", "items": {"type": "string"}},
                "when_to_seek_help": {"type": "string"}
            }
        },
        "safety_validation": {
            "type": "object",
            "properties": {
                "dose_within_limits": {"type": "boolean"},
                "contraindications_checked": {"type": "boolean"},
                "age_appropriate": {"type": "boolean"},
                "weight_appropriate": {"type": "boolean"}
            }
        }
    },
    "required": ["triage", "selected_medication", "dosing", "safety_validation"]
}

AI_PHARMACIST_PROMPT = """
You are AbsorpGen AI, an advanced AI pharmacist assistant.

TRIAGE FIRST:
- For emergencies or doctor-only scenarios set:
  triage.red_flag = true, triage.level = "red", triage.reason, triage.advice = "Seek urgent medical care."
- MUST mark red_flag=true for: head trauma/injury/concussion/LOC/seizure; suspected stroke/MI; severe chest pain;
  severe shortness of breath; vomiting/coughing blood; black tarry stools; high fever + stiff neck; anaphylaxis;
  pregnancy emergencies; **any sexually transmitted disease/STD/STI (e.g., chlamydia, gonorrhea, syphilis, herpes,
  trichomoniasis, HIV, HPV, hepatitis B/C via sexual transmission)** or serious complications thereof.

If not red but OTC self-care is inappropriate (complex chronic condition with no benign OTC symptom), set
red_flag=false, level="medium", and choose no medication.

If safe AND in scope for OTC, choose one medication and a conservative dose.

OTC LIST (short):
- Acetaminophen (Tylenol) — pain/fever
- Ibuprofen (Advil/Motrin) — pain/inflammation; avoid with GI/kidney issues
- Dextromethorphan (Delsym) — dry cough; avoid with MAOIs
- Guaifenesin (Mucinex) — chest congestion
- Cetirizine (Zyrtec) — allergies/sneezing/runny nose
- Loratadine (Claritin) — allergies
- Famotidine (Pepcid) — heartburn
- Meclizine (Bonine) — motion sickness/vertigo
- Calcium Carbonate (Tums) — indigestion

SAFETY LIMITS:
- Ibuprofen ≤ 600 mg per single dose. Acetaminophen ≤ 750 mg per single dose.
- Prefer conservative dosing for pediatrics; underweight; liver/kidney/GI disease; pregnancy.

IF NO OTC IS APPROPRIATE:
- selected_medication.drug_key="none", brand="none", generic="none"
- dosing: dose_text="-", frequency="-", total_mg=0

Return JSON ONLY that matches the provided schema.
"""

def get_ai_pharmacist_recommendation(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("AI pharmacist disabled: No valid OpenAI API key configured")
        return None

    patient_context = {
        "demographics": {
            "age": payload.get("age"),
            "sex": payload.get("sex"),
            "height_cm": payload.get("height_cm"),
            "weight_kg": payload.get("weight_kg")
        },
        "symptoms": payload.get("symptoms", []),
        "allergies": payload.get("allergies", []),
        "conditions": payload.get("conditions", []),
        "pain_level": payload.get("pain_level"),
        "notes": payload.get("notes", "")
    }

    try:
        resp = _client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": AI_PHARMACIST_PROMPT},
                {"role": "user", "content": f"JSON schema:\n{json.dumps(MEDICATION_SCHEMA)}"},
                {"role": "user", "content": f"Patient input:\n{json.dumps(patient_context)}"},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        data = json.loads(resp.choices[0].message.content)
        if not isinstance(data, dict): return None
        if "triage" not in data or "selected_medication" not in data or "dosing" not in data:
            return None
        return data
    except Exception as e:
        print(f"AI pharmacist error: {e}")
        return None

def get_llm_dose(payload: Dict[str, Any], suggested_cap_mg: int, chosen_drug: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    ai_rec = get_ai_pharmacist_recommendation(payload)
    if not ai_rec: return None
    return {
        "drug_name": f"{ai_rec['selected_medication']['brand']} ({ai_rec['selected_medication']['generic']})",
        "dose_text": ai_rec["dosing"]["dose_text"],
        "frequency": ai_rec["dosing"]["frequency"],
        "rationale": ai_rec["selected_medication"]["reasoning"],
        "total_mg": ai_rec["dosing"]["total_mg"],
    }
